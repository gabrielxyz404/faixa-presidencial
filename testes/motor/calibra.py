# Calibração por simulação headless: roda N partidas (semente fixa por partida) sobre o estado do jogo, sem UI.
# uso: python3 run_sandbox.py calibra.py <pasta com index.html> <saida.json> <porta> <passivo|pacote> <N> [lua|brasilia|raiz]
import sys, threading, functools, http.server, json, re
from playwright.sync_api import sync_playwright
ROOT, OUT, PORT, MODO, N = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
DIF = sys.argv[6] if len(sys.argv) > 6 else 'brasilia'  # modo da partida: lua | brasilia | raiz
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
def click(pg, t):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(400)
PACOTE = ["Criar um programa de creches em tempo integral para 1 milhão de crianças", "Zerar o IPI de carros elétricos", "Isentar do imposto de renda quem ganha até R$ 6 mil",
          "Aumentar o Bolsa Família para R$ 800", "Regulamentar o trabalho por aplicativo com salário mínimo por hora", "Privatizar os Correios"]
AMPLO = PACOTE + ["Congelar o preço da gasolina", "Criar uma ferrovia ligando o Centro-Oeste aos portos do Norte", "Regulamentar as redes sociais e responsabilizar as big techs", "Privatizar a Petrobras",
          "Criar um imposto sobre carbono", "Acabar com a escala 6x1", "Construir 500 mil casas populares pelo Minha Casa Minha Vida", "Aumentar o salário mínimo para R$ 2 mil", "Criar o Desenrola 2 para renegociar dívidas", "Contratar 50 mil médicos para o SUS"]
JS = """([modo, seed, pacote, dif]) => {
  const V = window.__V; let a = seed >>> 0;
  Math.random = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const cfg = JSON.parse(window.__cfg0); cfg.modo = dif; cfg.seed = (seed * 2654435761) >>> 0; const g = V.novoJogo(cfg); const out = { seed, snaps: {}, over: null, nmed: 0, ev: 0 };
  const snap = () => ({ ap: V.aprovacao(g), ipca: g.eco.ipca, des: g.eco.des, div: g.eco.divida, prim: V.primario(g), imp: V.riscoImpeachment(g), pib: g.eco.pib, risco: g.eco.risco });
  for (let m = 1; m <= 48; m++) {
    if ((modo === 'pacote' || modo === 'amplo') && g.mes === 1) {
      for (const t of (modo === 'amplo' ? window.__amplo : pacote)) { g.acoes = 5; try { const p = V.analisaLocal(g, t); V.executaProposta(g, p, 'aprovada'); } catch (e) { out.err = String(e).slice(0, 200); } }
    }
    try { V.fimDoMes(g); } catch (e) { out.err = String(e.stack).slice(0, 400); break; }
    if ([6, 12, 24, 48].includes(m)) out.snaps[m] = snap();
    if (g.over) { if (!out.over) { out.over = g.over.tipo; out.overMes = m; } g.over = null; g.impStreak = 0; if (g.pes) { g.pes.saude = Math.max(g.pes.saude, 60); g.pes.estresse = Math.min(g.pes.estresse, 60); } } // a partida segue só para comparar a trajetória macro (o fim da partida fica registrado em over/overMes)
  }
  out.nmed = (g.medidas || []).length; out.ev = (g.medidas || []).reduce((s, x) => s + (x.not ? x.not.length - 1 : 0), 0);
  out.probs = (g.medidas || []).map(x => x.estado + ':' + x.tipo); out.cont = {}; for (const x of (g.medidas || [])) for (const k in x.cont) out.cont[k] = (out.cont[k] || 0) + x.cont[k];
  return out;
}"""
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' or (m.type == 'warning' and re.search('medida|Medida', m.text)) else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function novoJogo(cfg) {', 'function novoJogo(cfg) { if (!window.__cfg0) window.__cfg0 = JSON.stringify(cfg);', 1)
    src = src.replace('function analisaLegado(g, texto) {', 'window.__V = { novoJogo, fimDoMes, executaProposta, analisaLocal, aprovacao, primario, riscoImpeachment };\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='networkidle'); pg.wait_for_timeout(1200)
    for t in ["Presidente eleito", "Assumir o mandato", "3Personalidade", "Negociador", "Técnico", "Avançar"]: click(pg, t)
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count() == 0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(200)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(200)
    click(pg, "Avançar"); click(pg, "Tomar posse"); pg.wait_for_timeout(800)
    pg.evaluate('(a)=>{window.__amplo=a}', AMPLO)
    res = []
    for i in range(N):
        r = pg.evaluate(JS, [MODO, 1000 + i * 7919, PACOTE, DIF]); res.append(r)
        print(i, r.get('over'), r.get('overMes'), r.get('nmed'), r.get('err', '')[:150], flush=True)
    json.dump({'res': res, 'errs': errs}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('ERRS', errs[:5]); b.close()
