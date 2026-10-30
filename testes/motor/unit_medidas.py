# Testes headless do ciclo de vida das medidas (v3.6): criação, rampa, revogação, MP caducando, ações, ADI/liminar, save antigo.
# uso: python3 run_sandbox.py unit_medidas.py <pasta com index.html> [porta]
import sys, threading, functools, http.server, json, re
from playwright.sync_api import sync_playwright
ROOT = sys.argv[1]; PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8890
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
def click(pg, t):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(400)
JS = """()=>{
  const V = window.__V, out = []; let a = 7;
  Math.random = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const novo = () => { const c = JSON.parse(window.__cfg0); c.modo = 'lua'; c.seed = Math.floor(Math.random() * 4294967296); const g = V.novoJogo(c); g.acoes = 5; return g; };
  const fis = (g) => +(g.fiscal.custo + g.fiscal.extra - g.fiscal.receita).toFixed(2);
  const ok = (n, c, d) => out.push((c ? 'OK   ' : 'FALHA ') + n + (d !== undefined ? ' | ' + d : ''));
  // a) decreto (IPI): ciclo, rampa e revogação direta
  let g = novo(); let f0 = fis(g);
  let p = V.analisaLocal(g, 'Zerar o IPI de carros elétricos'); V.executaProposta(g, p, 'aprovada');
  let M = g.medidas[0];
  ok('a1 medida criada', !!M && M.tipo === 'tributo' && M.inst === 'DEC', M && (M.tipo + ' ' + M.inst + ' reg=' + M.mReg + ' pleno=' + M.mPleno + ' mat=' + M.mMat));
  const f1 = fis(g); const alvo = (M.fis.custo + M.fis.extra - M.fis.receita);
  for (let i = 0; i < 8; i++) V.fimDoMes(g);
  ok('a2 fiscal chega perto do previsto (x' + M.mCusto.toFixed(2) + '/' + M.mRec.toFixed(2) + ')', Math.abs((fis(g) - f0) - alvo * (M.mCusto) ) < Math.abs(alvo) * .6 + .5, 'previsto ' + alvo.toFixed(2) + ' aplicado ' + (fis(g) - f0).toFixed(2) + ' (inicial ' + (f1 - f0).toFixed(2) + ')');
  g.acoes = 5; const f2 = fis(g); V.medRevoga(g, M.id);
  ok('a3 revogação direta', M.estado === 'revogada' && Math.abs(fis(g) - f0) < Math.abs(alvo) * .25 + .3, 'estado ' + M.estado + ' fis ' + (fis(g) - f0).toFixed(2) + ' (antes ' + (f2 - f0).toFixed(2) + ')');
  // b) lei + revogação por proposta
  g = novo(); f0 = fis(g);
  p = V.analisaLocal(g, 'Taxar dividendos em 15%'); V.executaProposta(g, p, 'aprovada'); M = g.medidas[0];
  ok('b1 PL criado', !!M && M.inst === 'PL', M && (M.tipo + ' reg=' + M.mReg + ' vig=' + M.vigMes));
  g.acoes = 5; const dirOk = V.medRevoga(g, M.id); ok('b2 PL pede proposta (revogPend)', dirOk === true && !!g.revogPend && /^Revogar/.test(g.revogPend.texto), g.revogPend && g.revogPend.texto);
  const p2 = V.analisaLocal(g, g.revogPend.texto); const n0 = g.medidas.length; V.executaProposta(g, p2, 'aprovada');
  ok('b3 revogação aprovada marca a original e não cria outra', M.estado === 'revogada' && g.medidas.length === n0 && !g.revogPend, M.estado);
  // c) MP: caduca sem votação
  g = novo(); f0 = fis(g);
  p = V.analisaLocal(g, 'Aumentar o Bolsa Família para R$ 800'); const r = V.enviaParaPauta(g, p); M = g.medidas[0];
  ok('c1 MP em vigor com medida', r.ok && !!M && M.mp === true, r.ok + ' ' + (M && M.inst));
  for (let i = 0; i < 6; i++) V.fimDoMes(g);
  ok('c2 MP caducou: medida encerrada', M.estado === 'caducada' && g.pauta.length === 0, M.estado + ' pauta=' + g.pauta.length);
  // d) acelerar e ajustar
  g = novo(); p = V.analisaLocal(g, 'Criar um programa de creches em tempo integral para 1 milhão de crianças'); V.executaProposta(g, p, 'aprovada'); M = g.medidas[0];
  const pl0 = M.mPleno, ac0 = g.acoes; V.medAcelera(g, M.id);
  ok('d1 acelerar antecipa o efeito pleno e gasta ação', M.mPleno < pl0 && g.acoes === ac0 - 1, pl0 + ' -> ' + M.mPleno);
  M.probs.push({ k: 'estouro', mes: g.mes, fim: g.mes + 8 }); M.mCusto = 1.3; V.medAjusta(g, M.id);
  ok('d2 ajustar reduz estouro', M.mCusto < 1.2 && !M.probs.some(x => x.k === 'estouro'), M.mCusto.toFixed(2));
  // e) ADI / liminar / julgamento: força nível alto e varre sementes
  let achou = { lim: 0, der: 0, val: 0, n: 0 };
  for (let s = 0; s < 40; s++) {
    a = 100 + s * 13; g = novo(); g.stf = 75; p = V.analisaLocal(g, 'Zerar o IPI de carros elétricos'); V.executaProposta(g, p, 'aprovada'); M = g.medidas[0]; M.stfNivel = 'inconstitucional';
    let susp = false, val = false; for (let i = 0; i < 14; i++) { V.fimDoMes(g); if (g.over) { g.over = null; } if (M.estado === 'suspensa') susp = true; if (M.not.some(x => /rejeita a ação/.test(x.x))) val = true; }
    achou.n++; if (M.cont.adi) { achou.lim += susp ? 1 : 0; achou.der += (M.estado === 'derrubada' ? 1 : 0); achou.val += val ? 1 : 0; }
  }
  ok('e1 ADI/liminar/julgamento ocorrem', achou.lim > 0 && (achou.der + achou.val) > 0, JSON.stringify(achou));
  // f) save antigo (sem g.medidas) e ida-e-volta em JSON
  g = novo(); delete g.medidas; V.fimDoMes(g); ok('f1 save sem g.medidas segue', true);
  g = novo(); p = V.analisaLocal(g, 'Criar um programa de creches em tempo integral para 1 milhão de crianças'); V.executaProposta(g, p, 'aprovada');
  const g2 = JSON.parse(JSON.stringify(g)); for (let i = 0; i < 5; i++) V.fimDoMes(g2); ok('f2 save JSON ida-e-volta segue', g2.medidas.length === 1 && g2.medidas[0].aplic > 0, 'aplic ' + g2.medidas[0].aplic.toFixed(2));
  return out;
}"""
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' or (m.type == 'warning' and re.search('medida|Medida', m.text)) else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function novoJogo(cfg) {', 'function novoJogo(cfg) { if (!window.__cfg0) window.__cfg0 = JSON.stringify(cfg);', 1)
    src = src.replace('function analisaLegado(g, texto) {', 'window.__V = { novoJogo, fimDoMes, executaProposta, analisaLocal, enviaParaPauta, medRevoga, medAcelera, medAjusta };\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='networkidle'); pg.wait_for_timeout(1200)
    for t in ["Presidente eleito", "Assumir o mandato", "3Personalidade", "Negociador", "Técnico", "Avançar"]: click(pg, t)
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count() == 0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(200)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(200)
    click(pg, "Avançar"); click(pg, "Tomar posse"); pg.wait_for_timeout(800)
    try: print('\n'.join(pg.evaluate(JS)))
    except Exception as e: print('EXCECAO', str(e)[:600])
    print('ERRS', errs[:6]); b.close()
