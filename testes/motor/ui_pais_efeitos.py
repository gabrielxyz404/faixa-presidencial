# Teste do lote A+E (sinais e efeitos das ações da aba País): contingenciar/bloquear verba piora a área; cortar a Segurança não reduz homicídios;
# crédito do BNDES não agenda queda de pobreza; "Força Nacional para <UF>" é lida como plano de segurança (sem desmatamento); operações de Segurança
# mexem em mortes violentas; Qualificação/Sine/Trabalho reduzem o desemprego; Ferrovias dão PIB; AFRMM com renúncia lida; cobrança do governador
# com chance proporcional à relação e cartão que explica apoio/cobrar/pacto.
# Lote Justiça (seção 8): PGR de mandato único, punir supersalários, balcão da leniência e sigilo de 100 anos têm o efeito que o texto diz.
# uso: python3 run_sandbox.py ui_pais_efeitos.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8887
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
checks = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:300]) if det != '' else ''), flush=True)
def click(pg, t, ms=500):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(ms)
def start(pg):
    pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='networkidle'); pg.wait_for_timeout(1500)
    for t in ["Presidente eleito", "Assumir o mandato", "3Personalidade", "Negociador", "Técnico", "Avançar"]: click(pg, t)
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count() == 0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(250)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(250)
    click(pg, "Avançar"); click(pg, "Tomar posse", 1000)
errs = []
INJ = ("window.__QV = () => QV; window.__P = () => ({ JUS_GOV, jusProgMensal, jusProgAtivo, jusMensal, jusNovoCaso, eqEscDecaimento, medSyncFiscal, medL, analisaLocal, ORC_AREAS, orcFmtV, IC_PROD, icTextoAcao, segPrevia, executaProposta, ensureIC, convAbre, convResponde, convChanceCobrar, INFRA_GRUPOS, TB_LEV });\n"
       "function analisaLegado(g, texto) {")
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', INJ, 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg)

    # 1. A1: todo "Contingenciar" tem o mesmo sinal do "Cortar" (despesa negativa, nenhum efeito social positivo)
    r = pg.evaluate("""() => { const P = __P(); const g = __QV().gRef.current; const out = [];
      for (const area in P.ORC_AREAS) for (const al of P.ORC_AREAS[area].alvos) { if (al.nc) continue;
        const v = P.orcFmtV(5); const c = P.analisaLocal(g, al.cont.replace('{V}', v)), k = P.analisaLocal(g, al.cut.replace('{V}', v)); const s = c.fx.s || {};
        out.push({ id: area + '|' + al.k, cost: c.cost, costCut: k.cost, pob: s.pob || 0, hom: s.hom || 0, idh: s.idh || 0, des: (c.fx.e || {}).des || 0, pol: c.entendimento && c.entendimento.polaridade }); }
      return out; }""")
    ruins = [x for x in r if not (x['cost'] < 0 and x['pob'] >= 0 and x['hom'] >= 0 and x['idh'] <= 0 and x['des'] >= 0)]
    ok('A1: %d textos de contingenciamento com despesa negativa e sem efeito social positivo' % len(r), len(r) >= 22 and not ruins, ruins[:3])
    ok('A1: contingenciar custa o mesmo que cortar (a dotação é reduzida)', all(abs(x['cost'] - x['costCut']) < .3 for x in r), [(x['id'], x['cost'], x['costCut']) for x in r if abs(x['cost'] - x['costCut']) >= .3][:3])
    r = pg.evaluate("""() => { const P = __P(); const g = __QV().gRef.current; return ['Bloquear R$ 8 bilhões do orçamento da atenção básica do SUS', 'Contingenciar R$ 3 bilhões do orçamento da Polícia Federal', 'Bloquear o Telegram no Brasil'].map(t => { const p = P.analisaLocal(g, t); return [t, p.cost, (p.objs || []).map(o => o.id + ':' + o.sg).join(',')]; }); }""")
    ok('A1: "Bloquear R$ 8 bi do orçamento da atenção básica" é corte (-8)', r[0][1] == -8 and 'agentes_saude:-1' in r[0][2], r[0])
    ok('A1: "Bloquear o Telegram" continua sendo regulação de rede, sem despesa', r[2][1] == 0 and 'redes_regulacao' in r[2][2], r[2])

    # 2. A2: cortar a verba da Segurança piora a taxa de homicídios; investir melhora
    r = pg.evaluate("""() => { const P = __P(); const g = __QV().gRef.current; const f = (t) => { const p = P.analisaLocal(g, t); const pv = P.segPrevia(g, p); return pv ? pv.efeitos.reduce((a, e) => a + e.mviD + e.mviP, 0) : null; };
      return { corte: f('Cortar R$ 5 bilhões da Polícia Federal'), cont: f('Contingenciar R$ 5 bilhões do orçamento da Força Nacional de Segurança Pública'), inv: f('Ampliar em R$ 5 bilhões por ano o orçamento da Polícia Federal'), presidios: f('Cortar R$ 5 bilhões do orçamento do sistema penitenciário federal e dos presídios') }; }""")
    ok('A2: cortar a PF aumenta as mortes violentas na prévia (efeito > 0)', r['corte'] is not None and r['corte'] > 0, r)
    ok('A2: contingenciar a Força Nacional e cortar presídios também (> 0)', r['cont'] > 0 and r['presidios'] > 0, r)
    ok('A2: investir na PF continua reduzindo (< 0)', r['inv'] < 0, r)

    # 3. A3: crédito do BNDES não agenda queda de pobreza (antes: "programa social" -1,2 p.p. 6 meses depois)
    r = pg.evaluate("""() => { const P = __P(); const g0 = __QV().gRef.current; const g = structuredClone(g0); P.ensureIC(g);
      const pz = P.IC_PROD['soja_grao']; const out = {};
      for (const ac of ['cred', 'inv']) { const gg = structuredClone(g); const t = P.icTextoAcao(pz, ac, 5); const p = P.analisaLocal(gg, t); p.icHook = { tipo: ac, k: 'soja_grao', v: 5, pct: .5 }; P.executaProposta(gg, p, 'aprovada');
        out[ac] = { cost: p.cost, pend: (gg.pendentes || []).filter(x => /pobreza/.test(x.txt || '')).length, s: JSON.stringify((p.fx || {}).s || {}) }; }
      return out; }""")
    ok('A3: crédito do BNDES R$ 5 bi: sem evento agendado de queda da pobreza', r['cred']['pend'] == 0, r)
    ok('A3: crédito lido como subsídio coerente (R$ 0,5 bi para R$ 5 bi)', abs(r['cred']['cost'] - .5) < .11 and r['inv']['cost'] == 5, r)

    # 4. A4: Força Nacional para <UF> é plano de segurança (não "administração geral"/desenvolvimento) e mexe em mortes violentas
    r = pg.evaluate("""() => { const P = __P(); const g = __QV().gRef.current; const out = [];
      for (const t of ['Enviar a Força Nacional para Pernambuco', 'Enviar a Força Nacional para o Rio de Janeiro', 'Decretar GLO em Pernambuco e enviar as Forças Armadas', 'Transferir lideranças de Pernambuco para presídios federais',
        'Equipar as polícias estaduais com 100 mil câmeras corporais, com gravação ininterrupta nas abordagens, R$ 600 milhões', 'Criar 2 mil Centros de Juventude com esporte e cultura nos bairros com mais homicídios, R$ 2 bilhões por ano']) {
        const p = P.analisaLocal(g, t); const pv = P.segPrevia(g, p); out.push({ t: t.slice(0, 40), cats: (p.cats || []).join(','), objs: (p.objs || []).map(o => o.id).join(','), mvi: pv ? pv.efeitos.reduce((a, e) => a + e.mviD + e.mviP, 0) : null }); }
      return out; }""")
    fn = r[0]; fn2 = r[1]
    ok('A4: Força Nacional para PE: plano de segurança, sem categoria de desenvolvimento/ambiente', fn['objs'] == 'plano_seguranca' and 'desenvolvimento' not in fn['cats'] and 'ambiente' not in fn['cats'], fn)
    ok('A4: Força Nacional para o Rio de Janeiro também (antes lia como ambiente)', fn2['objs'] == 'plano_seguranca' and 'ambiente' not in fn2['cats'], fn2)
    ok('A4: GLO, transferência, câmeras, Centros de Juventude e Força Nacional reduzem mortes violentas', all(x['mvi'] is not None and x['mvi'] < 0 for x in r), [(x['t'], x['mvi']) for x in r])

    # 5. E1/E2: Qualificação, Sine e Trabalho reduzem o desemprego; Ferrovias dão PIB
    r = pg.evaluate("""() => { const P = __P(); const g = __QV().gRef.current; const f = (area, k, m) => { const al = P.ORC_AREAS[area].alvos.find(a => a.k === k); const p = P.analisaLocal(g, al[m].replace('{V}', P.orcFmtV(5))); return { des: p.fx.e.des, pib: p.fx.e.pib, cost: p.cost }; };
      return { qual: f('trabalho', 'qual', 'inv'), sine: f('trabalho', 'int', 'inv'), geral: f('trabalho', 'geral', 'inv'), qualCut: f('trabalho', 'qual', 'cut'), sineCut: f('trabalho', 'int', 'cut'), fer: f('infra', 'fer', 'inv'), ferCut: f('infra', 'fer', 'cut') }; }""")
    ok('E1: investir R$ 5 bi em Qualificação, Sine e Todo o Trabalho reduz o desemprego (e.des <= -0,05)', all(r[k]['des'] <= -.05 for k in ('qual', 'sine', 'geral')), r)
    ok('E1: cortar esses alvos aumenta o desemprego', all(r[k]['des'] > 0 for k in ('qualCut', 'sineCut')), r)
    ok('E2: Ferrovias dão PIB (+) ao investir e tiram ao cortar', r['fer']['pib'] >= .08 and r['ferCut']['pib'] < 0, r)

    # 6. E3: AFRMM lido como renúncia fiscal (receita negativa), com o crédito como segundo passo
    r = pg.evaluate("""() => { const P = __P(); const g = __QV().gRef.current; let it = null, it2 = null; for (const G of P.INFRA_GRUPOS) for (const a of G.itens) if (/afrmm/i.test(a.t)) { it = a; it2 = a.p2; }
      if (!it) return null; const p = P.analisaLocal(g, it.t), p2 = it2 ? P.analisaLocal(g, it2.t) : null; return { t: it.t, rev: p.rev, cost: p.cost, p2t: it2 && it2.t, p2cost: p2 && p2.cost }; }""")
    ok('E3: texto do AFRMM fala em renúncia de R$ 1,5 bi e o motor lê receita -1,5', r and 'renúncia' in r['t'] and abs(r['rev'] + 1.5) < .01, r)
    ok('E3: o crédito de R$ 3 bi é o próximo passo e custa a equalização (> 0)', r and r['p2t'] and r['p2cost'] > 0, r)

    # 7. E4: cobrança com chance proporcional à relação e cartão explicativo
    r = pg.evaluate("() => { const f = __P().convChanceCobrar; return [30, 50, 60, 80, 95].map(x => +f(x).toFixed(2)); }")
    ok('E4: chance da cobrança cresce com a relação (30: 5%, 60 > 50%, 95: 95%)', r == sorted(r) and r[0] == .05 and r[-1] == .95 and .5 < r[2] < .6 and len(set(r)) == 5, r)
    r = pg.evaluate("""() => { const P = __P(); const g0 = __QV().gRef.current; let c = 0, n = 0; for (const rel of [20, 50, 80]) { let a = 0; for (let m = 1; m <= 40; m++) { const g = structuredClone(g0); g.mes = m; g.seed = 100 + m; g.govs = g.govs || {}; const U = 'SP'; P.convAbre(g, 'edu', U, 'alfa'); g.govs.uf[U].rel = rel; P.convResponde(g, 'edu', U, 'cobrar'); if (/surtiu efeito/.test(g.conv.ult['edu|' + U].res)) a++; } (n++, c = c); (window['__r' + rel] = a); } return [window.__r20, window.__r50, window.__r80]; }""")
    ok('E4: em 40 sorteios, mais cobranças surtem efeito com relação alta (20 < 50 < 80)', r[0] < r[1] < r[2] and r[0] <= 12, r)
    pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);n.mes=Math.max(n.mes,2);return n})"); pg.wait_for_timeout(400)
    pg.locator('#sec-tab-pais').click(timeout=6000); pg.wait_for_timeout(500)
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*Educação\s*$')).first.click(timeout=6000); pg.wait_for_timeout(900)
    try:
        pg.locator('[data-conv=edu] [data-conv-tema]').first.click(timeout=5000); pg.wait_for_timeout(500)
        t = pg.locator('[data-conv=edu] [data-conv-resps]').inner_text()
        ok('E4: cartão mostra a chance da cobrança em %', re.search(r'\d+% de chance de surtir efeito', t) is not None, t[:300])
        ok('E4: cartão explica o efeito do pacto (1,6 vez o apoio, % ao mês, indicador do estado)', re.search(r'1,6 vez o apoio', t) and re.search(r'indicador do estado melhora [\d,]+% ao mês', t), t[:400])
    except Exception as e:
        ok('E4: cartão da conversa abre', False, str(e)[:200])
    # 8. Justiça: os 4 programas que não mexiam em indicador algum agora têm o efeito do texto (hook mensal jusProgMensal, lido da medida em vigor)
    JP = """(id, setup) => { const P = __P(); const g = structuredClone(__QV().gRef.current); g.seed = 7; const J = P.JUS_GOV.find(x => x.jus === id); const p = P.analisaLocal(g, J.t); P.executaProposta(g, p, 'aprovada');
      const M = P.medL(g).find(m => m.pid === p.id); if (!M) return { erro: 'sem medida' }; g.mes = M.mPleno + 2; const k = M.k;
      const a0 = { e: Object.assign({}, g.eco), gr: Object.assign({}, g.groups), stf: g.stf, fc: g.fiscal.custo, fr: g.fiscal.receita, div: g.eco.divida };
      P.jusProgMensal(g); const fim = { f: P.jusProgAtivo(g, id), k };
      P.medSyncFiscal(g, M, 1);
      const dg = (kk) => +(g.groups[kk] - a0.gr[kk]).toFixed(3);
      return Object.assign(fim, { conf: +(g.eco.conf - a0.e.conf).toFixed(3), pib: +(g.eco.pib - a0.e.pib).toFixed(3), stf: +(g.stf - a0.stf).toFixed(3), custo: +(g.fiscal.custo - a0.fc).toFixed(3), receita: +(g.fiscal.receita - a0.fr).toFixed(3),
        once: M.once, div: +(g.eco.divida - a0.div).toFixed(4), merc: dg('mercado'), cm: dg('classemedia'), uni: dg('universitarios'), serv: dg('servidores'), emp: dg('empresariado') }); }"""
    r = pg.evaluate("() => (%s)('pgr')" % JP)
    ok('J1 PGR (PEC): em vigor, mercado +1,5, classe média e universitários +1, confiança +1,5, sem custo fiscal', r.get('f', 0) > .3 and abs(r['merc'] - 1.5 * r['f']) < .05 and abs(r['cm'] - r['f']) < .05 and abs(r['uni'] - r['f']) < .05 and abs(r['conf'] - 1.5 * r['f']) < .1 and r['custo'] == 0 and r['receita'] == 0, r)
    r = pg.evaluate("""() => { const P = __P(); const g0 = structuredClone(__QV().gRef.current); const out = {};
      for (const on of [0, 1]) { let av = 0, n = 0; for (let s = 1; s <= 3000; s++) { const g = structuredClone(g0); g.seed = s * 7 + 1; g.mes = 20; g.over = false; g.evento = null; g.jusProg = on ? { _ult: 20, pgr: { f: 1, mid: 'x' } } : {};
          g.jus = { ver: 1, seq: 1, casos: [{ id: 'j1', nome: 'Teste', mes: 10, faseMes: 17, orgao: 'PF', orgaos: ['PF'], fase: 'inquérito', valor: 100, prova: 40, alvo: 'assessores do Planalto', p: null, gov: true, casa: null, cargo: null, sig: null, esquema: 'x', pend: false, pendMes: 10, trava: 0, sigilo: false, rastro: 0, acel: 0, forca: false, reab: 0, ult: 0, log: [] }], ultQuebra: 20, ult: null, pfCorte: 0, pfOrc: 0, nBloq: 0, nAvan: 0, ev: {}, suplentes: [], reacoes: [], cpiMes: 0 };
          P.jusMensal(g, []); n++; if (g.jus.casos[0].fase === 'denúncia') av++; } out[on] = av / n; } return out; }""")
    ok('J1 PGR (PEC): casos que atingem o governo avançam ~15% mais (3000 sorteios por braço)', 1.08 < r['1'] / r['0'] < 1.24, r)
    r = pg.evaluate("() => (%s)('teto')" % JP)
    ok('J2 Punir quem paga acima do teto: corta R$ 3 bi/ano, devolução única de R$ 1 bi, servidores −2, STF +2, classe média +1', r.get('f', 0) > .3 and abs(r['custo'] + 3) < .35 and r['once'] == r['k'] and abs(r['serv'] + 2 * r['f']) < .05 and abs(r['stf'] - 2 * r['f']) < .05 and abs(r['cm'] - r['f']) < .05 and r['div'] < 0, r)
    r = pg.evaluate("() => (%s)('lenc')" % JP)
    ok('J3 Balcão único da leniência: receita de R$ 2 bi/ano, empresariado +2, PIB levemente positivo', r.get('f', 0) > .3 and abs(r['receita'] - 2) < .25 and abs(r['emp'] - 2 * r['f']) < .05 and 0 < r['pib'] <= .08, r)
    r = pg.evaluate("""() => { const P = __P(); const g0 = structuredClone(__QV().gRef.current); const o = {};
      for (const on of [0, 1]) { const g = structuredClone(g0); g.escAberto = null; g.escRef = null; g.oposicao = g.oposicao || {}; g.oposicao.pedidoImp = null; if (g.eu && g.eu.bast) g.eu.bast.inv = false; g.mes = 30; g.jusProg = on ? { _ult: 30, sigilo: { f: 1, mid: 'x' } } : {}; o['dec' + on] = 1 - P.eqEscDecaimento(g); }
      for (const on of [0, 1]) { const g = structuredClone(g0); g.seed = 5; g.mes = 12; g.escandalo = 5; g.jusProg = on ? { _ult: 12, sigilo: { f: 1, mid: 'x' } } : {}; const e0 = g.escandalo; P.jusNovoCaso(g, { gov: true, silencio: false }); o['imp' + on] = g.escandalo - e0; }
      return o; }""")
    ok('J4 Sigilo de 100 anos vetado para gastos: escândalo decai +20% sem caso novo, caso novo pesa +10%', abs(r['dec1'] / r['dec0'] - 1.2) < .02 and 1.07 < r['imp1'] / r['imp0'] < 1.13, r)
    r = pg.evaluate("() => (%s)('sigilo')" % JP)
    ok('J4 Sigilo: classe média e universitários (imprensa) +1 e confiança sobe levemente', r.get('f', 0) > .3 and abs(r['cm'] - r['f']) < .05 and abs(r['uni'] - r['f']) < .05 and 0 < r['conf'] <= .6, r)
    pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);n.mes=Math.max(n.mes,2);return n})"); pg.wait_for_timeout(400)
    pg.locator('#sec-tab-pais').click(timeout=6000); pg.wait_for_timeout(500)
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*Justiça\s*$')).first.click(timeout=6000); pg.wait_for_timeout(900)
    ef = pg.locator('[data-jus=acoes-gov] [data-prog-ef]'); tx = ef.all_inner_texts()
    ok('J: cartões dos 4 programas mostram o efeito esperado em uma linha', len(tx) == 4 and any('3 bi' in t and 'supersal' in t for t in tx) and all(t.startswith('Efeito:') for t in tx), tx)
    ok('0 erros de página/console', not errs, errs[:3])
    b.close()
falhas = [n for c, n in checks if not c]
print('\n%d/%d checagens ok' % (len(checks) - len(falhas), len(checks)))
sys.exit(1 if falhas else 0)
