# Estratégias jogadas por JS (rápido): mede aprovação, risco de impeachment, inflação e confiança em 48 meses, com 3 sementes.
# Evolui o simulador do relatório de equilíbrio: as votações usam decideVotacao (a mesma do jogo) em vez de 50/50.
# uso: python3 testes/motor/run_sandbox.py testes/motor/balance_estrategias.py <pasta com index.html> <saida.json> <porta> [estrategia,estrategia,...] [modo: lua|brasilia|raiz] [dificuldade: facil|realista|brutal]
import sys, threading, functools, http.server, json, re
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3])
ESTR = sys.argv[4].split(',') if len(sys.argv) > 4 else ['omisso', 'fiscalista', 'equilibrado', 'gastador', 'gastador_repete', 'spam_com', 'articulador', 'autoritario']
SEEDS = [11, 22, 33]
MODO = sys.argv[5] if len(sys.argv) > 5 else None; DIF = sys.argv[6] if len(sys.argv) > 6 else None
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
INJ = "window.__QV = () => QV; window.__AL = analisaLocal; window.__X = () => ({ fimDoMes, executaProposta, aprovacao, primario, riscoImpeachment, EV, fazArticulacao, decideVotacao, quorum, precisaCongresso }); function analisaLegado(g, texto) {"
def click(pg, t, ms=400):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(ms)
def start(pg):
    pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='networkidle'); pg.wait_for_timeout(1200)
    for t in ["Presidente eleito", "Assumir o mandato", "3Personalidade", "Negociador", "Técnico", "Avançar"]: click(pg, t)
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count() == 0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(200)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(200)
    click(pg, "Avançar"); click(pg, "Tomar posse", 1000)
JS = r"""
(args) => {
  const { estrategia, seed, meses, modo, dif } = args; const X = __X();
  let a = seed; Math.random = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const g = structuredClone(window.__G0); g.seed = seed; if (modo) g.cfg.modo = modo; if (dif) g.cfg.dif = dif;
  const EQ = ['Zerar o IPI de carros elétricos por decreto', 'Cortar 10% das despesas discricionárias por decreto', 'Programa de creches em tempo integral para 500 mil crianças', 'Taxar dividendos em 10%', 'Contratar 5 mil peritos para o INSS', 'Duplicar a BR-116 entre Curitiba e São Paulo', 'Ampliar o Pé-de-Meia em R$ 50', 'Reajuste real de 2% do salário mínimo', 'Aumentar o orçamento do SUS em R$ 10 bilhões', 'Ampliar o Bolsa Família em R$ 50 por família', 'Criar a Guarda Nacional com 10 mil agentes para a fronteira', 'Zerar a fila do INSS contratando peritos', 'Cortar 5% dos subsídios por decreto', 'Reforma administrativa para novos servidores', 'Aumentar a CSLL dos bancos para 25%', 'Criar programa de saneamento básico em 100 municípios', 'Ampliar a merenda escolar em 10%', 'Programa de capacitação de jovens aprendizes', 'Taxar bets em 18%', 'Ampliar o Farmácia Popular'];
  const FISC = ['Cortar 20% de todas as despesas discricionárias por decreto', 'Congelar o salário dos servidores por 4 anos', 'Aumentar a CSLL dos bancos para 30%', 'Taxar dividendos em 15%', 'Cortar 10% dos subsídios por decreto', 'Reforma administrativa para novos servidores', 'Taxar bets em 25%', 'Privatizar os Correios', 'Cortar 15% das despesas discricionárias por decreto', 'Taxar grandes fortunas em 1%'];
  const GAS = ['Aumentar o Bolsa Família para R$ 1.200 por família', 'Aumentar o salário dos servidores públicos em 30%', 'Zerar o imposto de renda para todo mundo', 'Dobrar a merenda escolar', 'Criar bolsa de R$ 300 para jovens aprendizes', 'Reajustar o Bolsa Família em R$ 200 por família', 'Zerar o IPI de todos os carros por decreto', 'Aumentar o orçamento do SUS em R$ 100 bilhões', 'Reajuste real de 10% do salário mínimo', 'Pagar um 13º do Bolsa Família em dezembro', 'Baixar a conta de luz de todo mundo pela metade', 'Zerar o imposto de importação dos alimentos por decreto', 'Contratar 100 mil servidores federais', 'Criar o Vale-Gás de R$ 300 para todas as famílias', 'Duplicar o Pé-de-Meia', 'Zerar a tarifa do transporte público por decreto', 'Construir 2 milhões de casas pelo Minha Casa Minha Vida', 'Ampliar o Farmácia Popular para todos os remédios', 'Perdoar as dívidas do Fies', 'Zerar o PIS e a Cofins da cesta básica', 'Aumentar o orçamento da educação em R$ 80 bilhões', 'Criar auxílio de R$ 1.000 para caminhoneiros', 'Subsidiar o diesel em R$ 1 por litro', 'Desonerar a folha de pagamento de todas as empresas', 'Aumentar em 50% o salário dos policiais federais', 'Zerar o IPI das motos por decreto', 'Reduzir a jornada para 36 horas sem redução de salário', 'Criar renda básica universal de R$ 600', 'Duplicar o orçamento da segurança pública', 'Congelar o preço dos combustíveis por decreto'];
  const GAS_R = GAS.slice(0, 3);
  const AUT = ['Fechar o STF por decreto', 'Censurar a imprensa que criticar o governo', 'Decretar estado de sítio e adiar as eleições', 'Prender os líderes da oposição', 'Intervenção militar nos estados governados pela oposição', 'Cancelar as eleições de 2030 por decreto'];
  const COM = ['Fazer um pronunciamento em cadeia nacional sobre a economia', 'Reunir os governadores para discutir segurança pública', 'Visitar obras do Minha Casa Minha Vida no Nordeste', 'Fazer uma live sobre o Bolsa Família', 'Discurso sobre o combate à fome'];
  let nAprov = 0, nRej = 0; const serie = [];
  const propor = (texto, forca) => {
    try {
      const p = window.__AL(g, texto); if (!p) return;
      const cong = X.precisaCongresso(p.inst); const q = X.quorum(p.inst);
      const res = forca ? 'aprovada' : X.decideVotacao(g, p, cong, q).res; // forca = gasto sem freio (Congresso e STF sempre aprovam), para testar o canal macro
      X.executaProposta(g, p, res); if (res === 'aprovada') nAprov++; else nRej++;
    } catch (e) { }
  };
  const lista = (L, n, m, forca) => { for (let i = 0; i < n && g.acoes > 0; i++) propor(L[((m - 1) * n + i) % L.length], forca); };
  for (let m = 1; m <= meses && !g.over; m++) {
    const ev = X.EV(g);
    if (estrategia !== 'omisso' && ev && !g.eventoOk) { // responde à crise com a 1ª opção dela
      const o = (ev.opcoes || ev.ops || [])[0];
      if (o && o.t) { try { const p = window.__AL(g, o.t); p.fromEvento = true; X.executaProposta(g, p, 'aprovada'); } catch (e) { } }
      g.eventoOk = true;
    }
    if (estrategia === 'equilibrado') { if (m % 2 === 1) lista(EQ, 1, (m + 1) / 2); }
    else if (estrategia === 'fiscalista') { if (m % 2 === 1) lista(FISC, 1, (m + 1) / 2); }
    else if (estrategia === 'gastador') lista(GAS, 3, m);
    else if (estrategia === 'gastador_forca') lista(GAS, 3, m, true);
    else if (estrategia === 'gastador_repete') lista(GAS_R, 3, 1);
    else if (estrategia === 'autoritario') propor(AUT[(m - 1) % AUT.length]);
    else if (estrategia === 'spam_com') lista(COM, 4, m);
    else if (estrategia === 'so_crises') { /* só responde às crises, sem outras ações (controle) */ }
    else if (estrategia === 'articulador') {
      try { for (const pid of Object.keys(g.parties).slice(0, 6)) X.fazArticulacao(g, 'bancada', pid); } catch (e) { }
      if (m % 2 === 1) lista(EQ, 1, (m + 1) / 2);
    }
    const r = X.fimDoMes(g);
    serie.push({ mes: m, ap: +X.aprovacao(g).toFixed(1), imp: Math.round(X.riscoImpeachment(g)), esc: Math.round(g.escandalo), prim: Math.round(X.primario(g)), pib: +g.eco.pib.toFixed(2), ipca: +g.eco.ipca.toFixed(2), conf: Math.round(g.eco.conf), base: Object.values(g.parties).filter(p => p.rel >= 62).length, est: Math.round(g.pes.estresse), sau: Math.round(g.pes.saude), over: g.over ? g.over.tipo : null });
    if (g.over) break;
  }
  return { estrategia, seed, nAprov, nRej, serie, fim: g.over ? (g.over.tipo === 'personagem' ? 'sobreviveu' : g.over.tipo) : 'sobreviveu', mesFim: g.mes }  // 'personagem' = mandato de 48 meses concluído (fase eleitoral);
}
"""
res = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    errs = []
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:200]))
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', INJ, 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg)
    pg.evaluate("()=>{window.__G0=structuredClone(__QV().gRef.current)}")
    for est in ESTR:
        for seed in SEEDS:
            r = pg.evaluate(JS, {'estrategia': est, 'seed': seed, 'meses': 48, 'modo': MODO, 'dif': DIF}); res.append(r)
            s = r['serie']; pts = {m: next((x for x in s if x['mes'] == m), None) for m in (12, 24, 36, 48)}
            med = sum(x['ap'] for x in s) / max(1, len(s))
            print('%-15s seed %2d: %-12s mês %2d | ap m12/24/36/48: %s | média %.0f | imp: %s | ipca fim %s conf fim %s pib fim %s | ok/rej %d/%d' % (est, seed, r['fim'], r['mesFim'], ' '.join('%s' % (pts[m]['ap'] if pts[m] else '-') for m in pts), med, ' '.join('%s' % (pts[m]['imp'] if pts[m] else '-') for m in pts), s[-1]['ipca'], s[-1]['conf'], s[-1]['pib'], r['nAprov'], r['nRej']), flush=True)
    print('erros', errs[:5])
    b.close()
json.dump(res, open(OUT, 'w'), ensure_ascii=False)
