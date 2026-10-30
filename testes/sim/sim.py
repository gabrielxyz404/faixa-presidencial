# Teste de simulação: "o jogo reage como esperado à ação do jogador?"
# uso: python3 testes/motor/run_sandbox.py testes/sim/sim.py <pasta com index.html> <cenarios.json> <saida.json> [porta] [repeticoes] [--so=id1,id2] [--seq]
#
# MÉTODO (ver testes/sim/LEIAME.md)
#  1. Sobe o jogo no Chromium, passa pelo assistente (mesmo roteiro de testes/regressao/batch3.py) e tira UM retrato do estado `g`
#     logo após "Tomar posse" (mês 1). Todas as rodadas partem de um structuredClone desse retrato.
#  2. O HTML servido recebe um gancho (`.replace` na rota de index.html, como em testes/motor/probe.py) que, imediatamente antes de
#     `ReactDOM.createRoot(...)`, expõe `window.__SIM` com as funções do jogo (executaProposta, fimDoMes, analisaLocal, aprovacao,
#     primario, enviaParaPauta, fechaMP, retiraItem, decideVotacao, quorum...) e `window.__QV` (onde está o `gRef` do React).
#     Se a âncora ou uma função obrigatória não existir, o script para com mensagem clara.
#  3. Math.random é substituído (add_init_script, antes do app) por um PRNG mulberry32 com semente controlável. Antes de CADA
#     fimDoMes a semente é refeita a partir de (repetição, mês). Tratamento e controle da mesma repetição partem do mesmo estado e do
#     mesmo sorteio de eventos/ruído em cada mês; só diverge o que a ação do jogador provoca. g.seed (usado nos hashes de votos do STF,
#     segurança etc.) também varia por repetição.
#  4. Cada rodada executa as ações em JS puro dentro da página (sem digitar na interface): propor = analisaLocal(g, texto) e depois
#     executaProposta (decreto/ato) ou enviaParaPauta + votação forçada (PL/PEC) ou MP (vigora na hora; fechaMP converte ou
#     retiraItem revoga). O resultado do voto é forçado ("aprovada"), ou decidido pelo STF do jogo ("stf"), ou todo pelo jogo ("auto").
#     Ações do painel Medidas e de outras telas (v3.9 do teste): `acelerar`, `ajustar`, `revogar`, `adi` (liminar/julgamento no STF), `podcast`
#     (aceitar ou recusar o convite) e `live` (convite a um famoso); e, em `propor`/`enviar`, `desidratar` e `emendas` (negociação do Parecer).
#     Todas chamam as funções do próprio jogo (medAcelera, medRevoga, entAceita, famLive...), expostas pelo gancho. Ver testes/sim/LEIAME.md.
#  5. Em cada mês-alvo (3, 12, 24 meses depois do início) lê os indicadores e compara tratamento x controle por repetição (pareado).
#     diferença média D, erro-padrão se = dp(d)/sqrt(n); limiar = max(Z*se, materialidade do indicador).
#     sobe/desce: ok se o sinal bate e |D| > limiar; falha se o sinal é oposto e |D| > limiar; senão inconclusivo.
#     estavel: ok se |D| <= max(Z*se, 2*materialidade), senão falha.  qualquer: apenas informa.
#     atenua / persiste / cresce: comparam a diferença do mês com a do primeiro mês da lista (efeito parcialmente desfeito,
#     mantido, ou que se acumula), também pareado.
import sys, os, json, re, math, time, threading, functools, http.server, hashlib
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
args = [a for a in sys.argv[1:] if not a.startswith('--')]
opts = dict(a[2:].split('=', 1) if '=' in a else (a[2:], '1') for a in sys.argv[1:] if a.startswith('--'))
if len(args) < 3:
    print(__doc__ or 'uso: sim.py <pasta> <cenarios.json> <saida.json> [porta] [repeticoes]'); sys.exit(2)
ROOT, CEN, OUT = args[0], args[1], args[2]
PORT = int(args[3]) if len(args) > 3 else 8841
NREP = int(args[4]) if len(args) > 4 else 8
Z = float(opts.get('z', 2.3))
SEM_IMP = 'com-impeachment' not in opts  # por padrão o impeachment não encerra a rodada (a passividade do controle o provocaria em ~1/3 das repetições)
MESES = [3, 12, 24]

# materialidade: diferença mínima (na unidade do indicador) para contar como efeito, abaixo disso é ruído de arredondamento do jogo
MAT = {'pib': .03, 'ipca': .03, 'selic': .05, 'des': .03, 'dol': .02, 'risco': 2, 'conf': .3, 'divida': .05, 'prim': .5, 'ap': .15, 'pob': .03,
       'hom': .1, 'desm': 20, 'idh': .0005, 'stf': .3, 'esc': .3, 'imp': .5, 'receita': .3, 'custo': .3, 'extra': .3, 'n_medidas': .5,
       'n_ativas': .5, 'n_susp': .5, 'n_derr': .5, 'n_revog': .5, 'cred': .3, 'feitas': .5, 'recusas': .5, 'fam_neg': .5, 'fam_pos': .5}
MAT_GRUPO = .15

cenarios = json.load(open(CEN, encoding='utf-8-sig'))
if opts.get('so'):
    ids = set(opts['so'].split(',')); cenarios = [c for c in cenarios if c['id'] in ids]

# ---------------------------------------------------------------- gancho no HTML
FUNCS_OBR = ['executaProposta', 'fimDoMes', 'analisaLocal', 'aprovacao', 'primario', 'enviaParaPauta']
FUNCS_OPC = ['fechaMP', 'retiraItem', 'decideVotacao', 'quorum', 'minMarca', 'gvMarca', 'tbMarca', 'riscoImpeachment',
             # ações do jogador nas telas Medidas, Parecer, entrevistas e X (cenários da v3.9 do teste; opcionais para rodar versões antigas)
             'custoEmenda', 'medL', 'medPodeAcelerar', 'medAcelera', 'medPodeAjustar', 'medAjusta', 'medPodeRevogar', 'medRevoga', 'medAddProb',
             'entEnsure', 'entAceita', 'entRecusa', 'entRespondeEntrev', 'entAvancaEntrev', 'entConcluiEntrev', 'famLive']
OBJ_OPC = ['PARTIDOS', 'ENT_VEIC', 'FAMOSOS']
ANCORA = "ReactDOM.createRoot(document.getElementById('root'))"
GANCHO = ("(function(){const S={};" +
          ''.join("try{S.%s=%s}catch(e){}" % (n, n) for n in FUNCS_OBR + FUNCS_OPC + OBJ_OPC) +
          "window.__SIM=S;try{window.__QV=QV}catch(e){window.__QV=null}})();\n")
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
if src.count(ANCORA) != 1:
    print('ERRO: âncora do gancho não encontrada (ou repetida) em index.html: %s' % ANCORA); sys.exit(3)
src = src.replace(ANCORA, GANCHO + ANCORA, 1)
VERSAO = {'arquivo': os.path.join(ROOT, 'index.html'), 'bytes': len(src), 'sha1': hashlib.sha1(src.encode('utf-8')).hexdigest()[:10],
          'tem_g_medidas': 'g.medidas' in src}

INIT_PRNG = """(()=>{let s=1;function m(){s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}
window.__seedRand=(n)=>{s=(n|0)||1};Math.random=m})();"""

# ---------------------------------------------------------------- roteiro executado dentro da página
JS = r"""
(() => {
const S = window.__SIM;
const IND = (g) => {
  const o = { pib: g.eco.pib, ipca: g.eco.ipca, selic: g.eco.selic, des: g.eco.des, dol: g.eco.dol, risco: g.eco.risco, conf: g.eco.conf, divida: g.eco.divida,
    prim: S.primario(g), ap: S.aprovacao(g), pob: g.soc.pob, hom: g.soc.hom, desm: g.soc.desm, idh: g.soc.idh, stf: g.stf, esc: g.escandalo,
    imp: S.riscoImpeachment ? S.riscoImpeachment(g) : null, receita: g.fiscal.receita, custo: g.fiscal.custo, extra: g.fiscal.extra,
    n_medidas: Array.isArray(g.medidas) ? g.medidas.length : 0 };
  const ML = Array.isArray(g.medidas) ? g.medidas : [];
  o.n_ativas = ML.filter(m => m.estado === 'ativa').length; o.n_susp = ML.filter(m => m.estado === 'suspensa').length;
  o.n_derr = ML.filter(m => m.estado === 'derrubada').length; o.n_revog = ML.filter(m => m.estado === 'revogada').length;
  o.cred = g.ent && g.ent.cred != null ? g.ent.cred : 50; o.feitas = g.ent ? (g.ent.feitas || 0) : 0; o.recusas = g.ent ? (g.ent.recusas || 0) : 0;
  const FP = g.x && g.x.fam && g.x.fam.posts ? g.x.fam.posts : [];
  o.fam_neg = FP.filter(p => p.tom === 'neg').length; o.fam_pos = FP.filter(p => p.tom === 'pos').length;
  for (const k of Object.keys(g.groups)) o['g_' + k] = g.groups[k];
  return o;
};
const resumo = (p) => ({ topic: p.topic, inst: p.inst, instDet: p.instDetalhe || null, cost: p.cost, rev: p.rev, once: p.once, extra: p.extra,
  stf: (p.stf || {}).nivel || null, vago: !!(p.qualidade || {}).vago, escala: p.scale });
function monta(g, a) {
  const p = S.analisaLocal(g, a.texto);
  try { S.minMarca && S.minMarca(p, a.texto); } catch (e) { }
  try { S.gvMarca && S.gvMarca(g, p, a.texto); } catch (e) { }
  p.fromEvento = false;
  try { S.tbMarca && S.tbMarca(p, a.texto); } catch (e) { }
  // negociação da tela Parecer (iguais aos botões do jogo): "Desidratar o texto (-40% de impacto)" e "Emendas p/ partido"
  for (let i = 0; i < (a.desidratar || 0); i++) {
    p.scale *= .6; p.iv = { eco: p.iv.eco * .5, soc: p.iv.soc * .5 }; p.desidratada = (p.desidratada || 0) + 1;
    for (const P of (S.PARTIDOS || [])) p.bonus[P.id] = (p.bonus[P.id] || 0) + 6;
  }
  if (a.emendas) {
    if (!S.custoEmenda || !S.PARTIDOS) throw new Error('custoEmenda/PARTIDOS indisponíveis (emendas)');
    const ids = Array.isArray(a.emendas) ? a.emendas : S.PARTIDOS.filter(P => P.id !== g.cfg.partido).sort((x, y) => y.cam - x.cam).slice(0, a.emendas).map(P => P.id);
    p.emendasCusto = 0; g.negMes = g.negMes || {};
    for (const pid of ids) { const c = S.custoEmenda(g, pid); g.fiscal.extra += c; g.negMes[pid] = (g.negMes[pid] || 0) + 1; p.bonus[pid] = (p.bonus[pid] || 0) + 14; p.emendasCusto += c; }
  }
  return p;
}
function medDe(g, refs, ref) {  // medida (g.medidas) criada pela proposta de uma ação anterior
  const r = refs[ref]; if (!r || !r.prop) return null;
  return (S.medL(g) || []).find(m => m.pid === r.prop.id) || null;
}
function resultado(g, p, modo, congresso) {
  if (modo === 'aprovada' || modo == null) return 'aprovada';
  if (modo === 'derrubada') return 'derrubada';
  if (!S.decideVotacao || !S.quorum) throw new Error('decideVotacao/quorum indisponíveis para modo ' + modo);
  return S.decideVotacao(g, p, modo === 'auto' ? congresso : false, S.quorum(p.inst)).res;
}
function aplica(g, a, refs) {
  const L = { tipo: a.tipo, id: a.id || null };
  if (a.tipo === 'propor' || a.tipo === 'enviar') {
    const p = monta(g, a); Object.assign(L, resumo(p), { texto: a.texto });
    const cong = ['PL', 'PEC', 'MP'].includes(p.inst);
    if (p.inst === 'PL' || p.inst === 'PEC' || p.inst === 'MP') {
      const r = S.enviaParaPauta(g, p);
      if (!r.ok) { L.erro = 'não enviou: ' + (r.msg || '?'); return L; }
      refs[a.id || ('#' + Object.keys(refs).length)] = { item: r.item, prop: p }; L.destino = r.destino;
      if (a.tipo === 'enviar') { L.res = 'tramitando'; return L; }
      if (r.destino !== 'pauta') { L.erro = 'ficou na gaveta'; return L; }
      L.res = votar(g, r.item, a.resultado, L);
    } else {
      L.res = resultado(g, p, a.resultado || 'stf', cong);
      refs[a.id || ('#' + Object.keys(refs).length)] = { prop: p };
      const ex = S.executaProposta(g, p, L.res); L.agendados = ex && ex.agendados;
    }
    if (p.emendasCusto) L.emendas_custo = Math.round(p.emendasCusto * 100) / 100;
    if (p.desidratada) L.desidratada = p.desidratada;
    const FM = g.x && g.x.fam && g.x.fam.posts ? g.x.fam.posts.filter(q => q.mes === g.mes) : [];
    if (FM.length) L.famosos = FM.map(q => q.nome + ':' + q.tom);
    const M0 = S.medL ? (S.medL(g) || []).find(m => m.pid === p.id) : null; if (M0) { L.medida = { tipo: M0.tipo, estado: M0.estado, dReg: M0.dReg, mPleno: M0.mPleno - g.mes }; }
    return L;
  }
  if (['acelerar', 'ajustar', 'revogar', 'adi'].includes(a.tipo)) {
    if (!S.medL) { L.erro = 'o jogo não tem g.medidas (versão anterior à v3.6)'; return L; }
    const M = medDe(g, refs, a.ref); if (!M) { L.erro = 'a medida de ' + a.ref + ' não existe (proposta não aprovada, ou sem ciclo de vida)'; return L; }
    L.topic = M.topic; L.medida = { tipo: M.tipo, estado: M.estado };
    if (a.tipo === 'acelerar') { const pa = S.medPodeAcelerar(g, M); if (!pa.ok) { L.erro = 'não pôde acelerar: ' + pa.t; return L; } S.medAcelera(g, M.id); L.res = 'acelerada'; return L; }
    if (a.tipo === 'ajustar') { const pa = S.medPodeAjustar(g, M); if (!pa.ok) { L.erro = 'não pôde ajustar: ' + pa.t; return L; } S.medAjusta(g, M.id); L.res = 'ajustada'; return L; }
    if (a.tipo === 'revogar') {
      const pr = S.medPodeRevogar(g, M); if (!pr.ok) { L.erro = 'não pôde revogar: ' + pr.t; return L; }
      const precisaLei = S.medRevoga(g, M.id);
      if (!precisaLei) { L.res = 'revogada por ato próprio'; return L; }
      // decreto/ato próprio: já revogou. MP/PL/PEC: o painel leva o texto "Revogar…" à Mesa e o jogador o propõe como qualquer proposta
      const sub = aplica(g, { tipo: 'propor', texto: g.revogPend.texto, resultado: a.resultado || 'aprovada', id: (a.id || a.ref) + '_rev' }, refs);
      L.res = 'revogação levada à Mesa: ' + (sub.res || sub.erro); L.inst_revogacao = sub.inst; if (sub.erro) L.erro = sub.erro; return L;
    }
    // adi: ação no STF contra a medida (liminar ou não); o julgamento sai em `meses` meses pelo próprio jogo (medProblemas). nivel força o nível de risco
    // constitucional que o plenário enxerga ('ok' => rejeita; 'inconstitucional' => derruba na maioria das sementes).
    if (a.nivel) M.stfNivel = a.nivel;
    const fim = g.mes + (a.meses || 2), lim = a.liminar !== false;
    S.medAddProb(M, 'adi', g.mes, fim, { lim, autor: 'um partido de oposição' });
    if (lim) { M.estado = 'suspensa'; M.susp = g.mes; }
    L.res = lim ? 'suspensa por liminar até o mês ' + fim : 'ação no STF sem liminar'; return L;
  }
  if (a.tipo === 'podcast') {  // convite de entrevista/podcast: aceitar (responde todas as perguntas) ou recusar
    if (!S.entEnsure || !S.ENT_VEIC) { L.erro = 'o jogo não tem entrevistas (v3.8)'; return L; }
    const E = S.entEnsure(g), vk = a.veic || 'flow', cid = 'sim' + g.mes + vk;
    if (!S.ENT_VEIC[vk]) { L.erro = 'veículo desconhecido: ' + vk; return L; }
    E.convites.push({ id: cid, veic: vk, mes: g.mes, estado: 'pendente' });
    if (a.aceitar === false) { S.entRecusa(g, cid); L.res = 'recusado'; L.cred = E.cred; return L; }
    if (!S.entAceita(g, cid)) { L.erro = 'não aceitou o convite (sem ação no mês?)'; return L; }
    const R = E.entrev; const arq = a.resposta || 'ajuste'; let dap = 0;
    for (let i = 0; i < R.qs.length; i++) {
      const q = R.qs[i], op = (q.ops.find(o => o.k === arq) || q.ops[0]).k;
      const res = S.entRespondeEntrev(g, op, ''); if (res) dap += res.dap; S.entAvancaEntrev(g);
    }
    S.entConcluiEntrev(g); L.res = 'aceito'; L.perguntas = R.qs.length; L.dap = Math.round(dap * 100) / 100; L.cred = E.cred; return L;
  }
  if (a.tipo === 'live') {  // convite a um famoso para uma live (suaviza o próximo ataque dele)
    if (!S.famLive) { L.erro = 'o jogo não tem famLive (v3.8)'; return L; }
    let nome = a.nome;
    if (nome === 'auto') {  // o famoso que mais seguidores tem entre os que já criticaram alguma medida
      const FP = (g.x && g.x.fam && g.x.fam.posts ? g.x.fam.posts : []).filter(q => q.tom === 'neg').sort((x, y) => y.s - x.s);
      if (!FP.length) { L.erro = 'nenhum famoso criticou ainda'; return L; }
      nome = FP[0].nome;
    }
    L.nome = nome; L.res = S.famLive(g, nome) ? 'live feita' : 'live não feita'; return L;
  }
  if (a.tipo === 'votar' || a.tipo === 'retirar') {
    const ref = refs[a.ref]; if (!ref) { L.erro = 'referência desconhecida ' + a.ref; return L; }
    const it = g.pauta.find(x => x.id === ref.item.id);
    if (!it) { L.erro = 'item não está mais na pauta (arquivado ou caducou)'; L.res = 'ausente'; return L; }
    Object.assign(L, { topic: it.prop.topic, inst: it.prop.inst });
    if (a.tipo === 'retirar') { L.res = S.retiraItem(g, it.id) ? 'retirada' : 'falhou'; return L; }
    L.res = votar(g, it, a.resultado, L); return L;
  }
  L.erro = 'tipo de ação desconhecido: ' + a.tipo; return L;
}
function votar(g, it, modo, L) {
  const p = it.prop; const cong = true;
  if (it.mp) {
    let res = resultado(g, p, modo, cong);
    if (!S.fechaMP) throw new Error('fechaMP indisponível');
    g.pauta = g.pauta.filter(x => x !== it);
    S.fechaMP(g, Object.assign({}, p, { jaPaga: true }), res === 'aprovada' ? 'aprovada' : res, null); return res === 'aprovada' ? 'convertida' : res;
  }
  const res = resultado(g, p, modo, cong);
  g.pauta = g.pauta.filter(x => x !== it);
  const ex = S.executaProposta(g, Object.assign({}, p, { jaPaga: true }), res); L.agendados = ex && ex.agendados;
  return res;
}
window.__run = (acoes, rep, alvos, semImp) => {
  const g = structuredClone(window.__base);
  g.seed = (g.seed || 0) + rep * 977 + 13;
  const log = [], refs = {}, snaps = {}, impMes = []; let over = null; const maxK = Math.max(...alvos);
  for (let k = 0; k <= maxK; k++) {
    if (alvos.includes(k)) snaps[k] = IND(g);
    if (k === maxK) break;
    for (const a of acoes) if ((a.mes || 0) === k) {
      try { const r = aplica(g, a, refs); r.mes = k; log.push(r); } catch (e) { log.push({ tipo: a.tipo, mes: k, erro: String(e).slice(0, 240) }); }
    }
    window.__seedRand(rep * 100003 + k * 7919 + 17);
    S.fimDoMes(g);
    if (g.over && semImp && g.over.tipo === 'impeachment') { impMes.push(k + 1); g.over = null; g.impStreak = 0; } // segue jogando: só queremos medir os indicadores
    if (g.over) { over = g.over.tipo || 'fim'; break; }
  }
  return { snaps, log, over, impMes };
};
return true;
})()
"""

# ---------------------------------------------------------------- servidor e partida
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()

def click(pg, t):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(400)

def inicia(pg):
    pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='networkidle'); pg.wait_for_timeout(1200)
    for t in ["Presidente eleito", "Assumir o mandato", "3Personalidade", "Negociador", "Técnico", "Avançar"]: click(pg, t)
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count() == 0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(250)
        # gabinete fixo entre versões: escolhe sempre pela aba "Técnicos" (lista estática), não pela ordem da indicação partidária
        tab = pg.locator('[role=tab]').filter(has_text=re.compile(r'^\s*Técnicos\s*$'))
        if tab.count(): tab.first.click(timeout=3000); pg.wait_for_timeout(200)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(250)
    click(pg, "Avançar"); click(pg, "Tomar posse"); pg.wait_for_timeout(800)

def media(v): return sum(v) / len(v)
def dp(v):
    if len(v) < 2: return 0.0
    m = media(v); return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))
def sinal(x): return (x > 0) - (x < 0)

def veredito(dirx, mes, ind, dif, dif_ref):
    """dif, dif_ref: listas pareadas (por repetição) de tratamento-controle no mês e no mês de referência."""
    mat = MAT.get(ind, MAT_GRUPO if ind.startswith('g_') else .1)
    D = media(dif); se = dp(dif) / math.sqrt(len(dif)); lim = max(Z * se, mat)
    info = {'D': D, 'se': se, 'lim': lim}
    if dirx == 'qualquer': return 'info', info
    if dirx == 'estavel': return ('ok' if abs(D) <= max(Z * se, 2 * mat) else 'falha'), info
    if dirx in ('sobe', 'desce'):
        s = 1 if dirx == 'sobe' else -1
        if s * D > lim: return 'ok', info
        if s * D < -lim: return 'falha', info
        return 'inconclusivo', info
    if dirx in ('atenua', 'persiste', 'cresce'):
        D0 = media(dif_ref); se0 = dp(dif_ref) / math.sqrt(len(dif_ref)); lim0 = max(Z * se0, MAT.get(ind, MAT_GRUPO if ind.startswith('g_') else .1))
        info['D_ref'] = D0
        sem_ref = abs(D0) <= lim0
        if sem_ref and dirx != 'cresce': return 'inconclusivo', dict(info, nota='sem efeito de referência para comparar')
        sg = sinal(D) if sem_ref else sinal(D0); d = [sg * (a - (0 if sem_ref else b)) for a, b in zip(dif, dif_ref)]
        X = media(d); sx = dp(d) / math.sqrt(len(d)); lx = max(Z * sx, MAT.get(ind, MAT_GRUPO if ind.startswith('g_') else .1)); info['X'] = X
        if dirx == 'atenua': return ('ok' if X < -lx else 'falha' if X > lx else 'inconclusivo'), info
        if dirx == 'cresce':  # sem crescimento só vale como falha quando o ruído é pequeno diante do efeito
            return ('ok' if X > lx else 'falha' if Z * sx <= .25 * max(abs(D0), abs(D)) else 'inconclusivo'), info
        return ('ok' if abs(X) <= max(lx, .25 * abs(D0)) else 'falha'), info
    return 'inconclusivo', dict(info, nota='direção desconhecida: ' + dirx)

t0 = time.time()
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    errs = []
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.add_init_script(INIT_PRNG)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    inicia(pg)
    faltam = pg.evaluate("(o)=>o.filter(n=>typeof (window.__SIM||{})[n]!=='function')", FUNCS_OBR)
    if faltam:
        print('ERRO: o gancho não achou funções obrigatórias do jogo: %s. A versão mudou os nomes? Ajuste FUNCS_OBR/ANCORA em sim.py.' % faltam); sys.exit(3)
    ausentes_opc = pg.evaluate("(o)=>o.filter(n=>typeof (window.__SIM||{})[n]!=='function')", FUNCS_OPC) + pg.evaluate("(o)=>o.filter(n=>typeof (window.__SIM||{})[n]!=='object')", OBJ_OPC)
    ok = pg.evaluate("()=>{const q=window.__QV; if(!q||!q.gRef||!q.gRef.current) return false; window.__base=structuredClone(q.gRef.current); return true}")
    if not ok:
        print('ERRO: não consegui ler o estado do jogo (window.__QV.gRef.current). A partida não iniciou?'); sys.exit(3)
    pg.evaluate(JS)
    pg.evaluate("()=>{window.__seedRand(7)}")
    print('versão: %s  g.medidas=%s  opcionais ausentes: %s  reps=%d  cenários=%d' % (VERSAO['sha1'], VERSAO['tem_g_medidas'], ausentes_opc or 'nenhum', NREP, len(cenarios)))
    cache = {}
    def roda(acoes, rep):
        k = (json.dumps(acoes, sort_keys=True), rep)
        if k not in cache: cache[k] = pg.evaluate("([a,r,m,i])=>window.__run(a,r,m,i)", [acoes, rep, MESES, SEM_IMP])
        return cache[k]
    if opts.get('traj'):  # depuração: trajetória mês a mês da diferença tratamento-controle (média das repetições) de um cenário
        cid, _, lista = opts['traj'].partition(':'); lista = lista.split(',') if lista else ['prim', 'custo', 'receita', 'pob', 'ipca', 'ap']
        c = next(x for x in cenarios if x['id'] == cid); todos = list(range(0, 25))
        A = [pg.evaluate("([a,r,m,i])=>window.__run(a,r,m,i)", [c['acoes'], r, todos, SEM_IMP]) for r in range(NREP)]
        B = [pg.evaluate("([a,r,m,i])=>window.__run(a,r,m,i)", [c.get('controle', []), r, todos, SEM_IMP]) for r in range(NREP)]
        print('%-4s' % 'mês' + ''.join('%12s' % i for i in lista))
        for m in todos:
            row = []
            for i in lista:
                v = [a['snaps'][str(m)][i] - b2['snaps'][str(m)][i] for a, b2 in zip(A, B) if a['snaps'].get(str(m)) and b2['snaps'].get(str(m))]
                row.append('%12.3f' % media(v) if v else '%12s' % '-')
            print('%-4d' % m + ''.join(row))
        sys.exit(0)
    saida = []; tot = {'ok': 0, 'falha': 0, 'inconclusivo': 0, 'info': 0}
    for c in cenarios:
        ts = time.time()
        tr = [roda(c['acoes'], r) for r in range(NREP)]
        ct = [roda(c.get('controle', []), r) for r in range(NREP)]
        res = []; cnt = {'ok': 0, 'falha': 0, 'inconclusivo': 0, 'info': 0}
        for e in c['esperado']:
            ind = e['ind']
            meses = [m for m in MESES if ('m%d' % m) in e]
            ref_m = meses[0] if meses else MESES[0]
            def dif(m, m2):
                """diferenças tratamento-controle (por repetição) no mês m e no mês m2, só nas repetições que têm os dois meses nos dois braços"""
                o1, o2 = [], []
                for a, b2 in zip(tr, ct):
                    xs = [a['snaps'].get(str(q)) for q in (m, m2)] + [b2['snaps'].get(str(q)) for q in (m, m2)]
                    if any(x is None or x.get(ind) is None for x in xs): continue
                    o1.append(xs[0][ind] - xs[2][ind]); o2.append(xs[1][ind] - xs[3][ind])
                return o1, o2
            for m in meses:
                d, d0 = dif(m, ref_m)
                if len(d) < 2:
                    res.append({'ind': ind, 'mes': m, 'esperado': e['m%d' % m], 'veredito': 'inconclusivo', 'nota': 'poucas repetições com o indicador no mês (partida terminou antes)', 'just': e.get('just')}); cnt['inconclusivo'] += 1; continue
                v, info = veredito(e['m%d' % m], m, ind, d, d0)
                cnt[v] += 1
                res.append(dict({'ind': ind, 'mes': m, 'esperado': e['m%d' % m], 'veredito': v, 'media_trat': media([a['snaps'][str(m)][ind] for a in tr if a['snaps'].get(str(m))]),
                                 'media_ctrl': media([a['snaps'][str(m)][ind] for a in ct if a['snaps'].get(str(m))]), 'n': len(d), 'just': e.get('just')},
                                **{k: round(x, 4) if isinstance(x, float) else x for k, x in info.items()}))
        for k in cnt: tot[k] += cnt[k]
        saida.append({'id': c['id'], 'descricao': c['descricao'], 'acoes_executadas': tr[0]['log'], 'acoes_controle': ct[0]['log'], 'over': [a['over'] for a in tr if a['over']], 'impeachment_evitado_tratamento': sum(1 for a in tr if a.get('impMes')), 'impeachment_evitado_controle': sum(1 for a in ct if a.get('impMes')),
                      'erros': sorted({l['erro'] for a in tr for l in a['log'] if l.get('erro')}), 'resumo': cnt, 'resultados': res, 'segundos': round(time.time() - ts, 1)})
        print('%-22s ok=%-2d falha=%-2d inconcl=%-2d info=%-2d  (%.0fs)%s' % (c['id'], cnt['ok'], cnt['falha'], cnt['inconclusivo'], cnt['info'], time.time() - ts,
              ('  ERROS: ' + '; '.join(saida[-1]['erros'])) if saida[-1]['erros'] else ''))
    json.dump({'versao': VERSAO, 'repeticoes': NREP, 'z': Z, 'meses': MESES, 'totais': tot, 'segundos': round(time.time() - t0, 1), 'cenarios': saida, 'erros_pagina': errs[:20]},
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\nTOTAL ok=%d falha=%d inconclusivo=%d info=%d   tempo=%.0fs   erros de página: %d' % (tot['ok'], tot['falha'], tot['inconclusivo'], tot['info'], time.time() - t0, len(errs)))
    b.close()
