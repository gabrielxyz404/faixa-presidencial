# Feijão e carne bovina com instrumentos de abastecimento (TEC zero, Conab, crédito, leilão): mercado novo do feijão, tela de compra da carne,
# pesos no IPCA, sinais das prévias, efeito real, reação dos grupos, saves antigos e prints (1440 px).
# uso: python3 run_sandbox.py ui_feijao_carne.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8897
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
def fecha_modais(pg):
    for _ in range(4):
        if pg.locator('.modal-wrap').count() == 0: break
        try: pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^(Fechar|Continuar|OK|Entendi|Seguir|Próximo mês|Voltar à Mesa|Arquivar|Cancelar|Desistir)')).first.click(timeout=1200)
        except Exception: pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
def G(pg, expr): return pg.evaluate("()=>{const g=__QV().gRef.current;return (" + expr + ")}")
def SET(pg, js): pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);const X=__X();" + js + ";return n})"); pg.wait_for_timeout(600)
def J(pg, js):
    return pg.evaluate("()=>{const X=__X();const g=structuredClone(__QV().gRef.current);X.ensureIC(g);g.acoes=9;g.props=9;g.pes.energia=90;" + js + "}")
def secao(pg, nome): pg.locator('#sec-tab-' + nome.lower().replace('í', 'i')).click(timeout=6000); pg.wait_for_timeout(500)
def chip(pg, nome):
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*' + nome + r'\s*$')).first.click(timeout=6000); pg.wait_for_timeout(600)
# roda n meses com o mesmo ruído nos dois braços; devolve a série de [ipca, mac.ipca, ap, agro, caminhoneiros, periferia, aposentados, pdom(mk), cut(mk), extra]
RUN = """const run=(g,n,mk,sd)=>{const S=[];const snap=()=>[g.eco.ipca,g.comex.mac.ipca,X.aprovacao(g),g.groups.agro,g.groups.caminhoneiros,g.groups.periferia,g.groups.aposentados,g.comex.fl[mk].pdom,g.comex.cut[mk]||0,g.fiscal.extra,g.groups.agfam,g.comex.mac.agro];S.push(snap());
 for(let m=0;m<n;m++){const st=Math.random;let x=(sd*9301+m*49297)%233280;Math.random=()=>{x=(x*9301+49297)%233280;return x/233280};try{X.fimDoMes(g)}finally{Math.random=st}S.push(snap())}return S};"""
# diferença média (tratamento menos controle, 6 sementes) de cada indicador da série RUN, mês a mês. pre_js muda os dois braços; trat_js só o tratado.
def DIFF(pg, mk, n, trat_js, pre_js='', seeds=(11, 22, 33, 44, 55, 66)):
    return J(pg, RUN + "const mk='%s';const R=[];for(const sd of %s){const gc=structuredClone(g),gt=structuredClone(g);gc.seed=sd;gt.seed=sd;(()=>{const g=gc;%s})();(()=>{const g=gt;%s})();(()=>{const g=gt;%s})();const A=run(gc,%d,mk,sd),B=run(gt,%d,mk,sd);R.push(B.map((r,i)=>r.map((v,j)=>v-A[i][j])))}return R[0].map((_,i)=>R[0][i].map((_,j)=>R.reduce((s,r)=>s+r[i][j],0)/R.length))" % (mk, list(seeds), pre_js, pre_js, trat_js, n, n))
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__X = () => ({ ensureIC, IC_IMP, IC_BASE, IC_BAS, IC_RX, fimDoMes, aprovacao, icFlow, icTecZero, icConabCompra, icConabVende, icCreditoProdutor, icLeilaoImport, icAbastPrev, icTick, icPesoInfo });\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    SET(pg, "n.acoes=9;n.props=9;n.pes.energia=90;X.ensureIC(n)")

    # ---------- save novo e pesos ----------
    r = G(pg, "(()=>{const X=__X();const f=g.comex.fl;return {pd:['feijao','bovina','arroz','trigo'].map(k=>f[k].pdom), mac:g.comex.mac.ipca, w:[X.IC_BASE.feijao.ipca,X.IC_BASE.bovina.ipca], sh:X.IC_BASE.bovina.shI, im:X.IC_BASE.bovina.IM0, ev:X.IC_BASE.bovina.EV0}})()")
    ok('Save novo: preço interno do feijão e da carne em 1,000 e IPCA do comércio 0', all(abs(v - 1) < 1e-6 for v in r['pd']) and abs(r['mac']) < 1e-6, r)
    ok('Pesos efetivos no IPCA: feijão 0,4 e carne 2,21 (2,6 x 85%, quase o 2,2 de antes)', [round(v, 3) for v in r['w']] == [.4, 2.21], r['w'])
    ok('Carne: a importação do Mercosul entra no mesmo mercado da exportação (US$ 0,4 bi; parte importada pequena)', abs(r['im'] - .4) < 1e-9 and 0 < r['sh'] < .03 and abs(r['ev'] - 16.6) < 1e-9, r)

    # ---------- telas ----------
    secao(pg, 'Mundo'); chip(pg, 'Comércio exterior')
    pg.locator('[data-com-aba=comprar]').click(); pg.wait_for_timeout(500)
    ok('Comprar: feijão e carne bovina aparecem na lista de importados', pg.locator('[data-com-imp=feijao]').count() == 1 and pg.locator('[data-com-imp=carne_imp]').count() == 1)
    pg.locator('[data-com-imp=feijao]').click(); pg.wait_for_timeout(800)
    t = pg.locator('[data-com-produto=feijao]').inner_text()
    pg.evaluate("()=>{const e=document.querySelector('[data-com-picker=comprar]');window.scrollTo(0,e.getBoundingClientRect().top+window.scrollY-90)}"); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/0_comprar_feijao_topo.png', full_page=False)
    ok('Feijão: tela com vendedores (Argentina, China), peso no IPCA e abastecimento', pg.locator('[data-com-abast=feijao]').count() == 1 and pg.locator('[data-com-vendedor=ARG]').count() == 1 and pg.locator('[data-com-vendedor=CHN]').count() == 1 and '0,40%' in t, t[:300])
    d = {k: float(pg.locator('[data-com-abast=feijao] [data-ab-prev=%s]' % k).get_attribute('data-delta')) for k in ['tec', 'compra', 'cred', 'leilao']}
    ok('Feijão: prévias com o sinal certo (TEC, crédito e leilão baixam o preço; compra da Conab sobe)', d['tec'] < -1 and d['cred'] < -1 and d['leilao'] < -1 and d['compra'] > 0, d)
    ac0 = G(pg, 'g.acoes')
    pg.locator('[data-com-abast=feijao] [data-ab-meses="6"]').click(); pg.locator('[data-com-abast=feijao] [data-ab-tec]').click(); pg.wait_for_timeout(900)
    r = G(pg, "({tec:g.comex.abast.feijao&&g.comex.abast.feijao.tec, ac:g.acoes, news:g.comex.news[0]&&g.comex.news[0].txt})")
    ok('Feijão: zerar a TEC por 6 meses gasta 1 ação e entra no noticiário', r['tec'] and r['tec']['meses'] == 6 and r['ac'] == ac0 - 1 and 'feijão' in (r['news'] or ''), r)
    pg.locator('[data-com-abast=feijao] [data-ab-x="0.5"]').click(); pg.locator('[data-com-abast=feijao] [data-ab-compra]').click(); pg.wait_for_timeout(900)
    pg.locator('[data-com-abast=feijao]').scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/1_comprar_feijao.png', full_page=False)

    pg.locator('[data-com-imp=carne_imp]').click(); pg.wait_for_timeout(800)
    ok('Carne: tela de compra com Paraguai, Uruguai e Argentina e o abastecimento do mercado da carne', pg.locator('[data-com-abast=bovina]').count() == 1 and all(pg.locator('[data-com-vendedor=%s]' % c).count() == 1 for c in ['PRY', 'URY', 'ARG']))
    ok('Carne: o cartão da Conab avisa que hoje não há estoque público de carne', 'anos 1980' in pg.locator('[data-com-abast=bovina] [data-ab-card=conab]').inner_text())
    d = {k: float(pg.locator('[data-com-abast=bovina] [data-ab-prev=%s]' % k).get_attribute('data-delta')) for k in ['tec', 'compra', 'cred', 'leilao']}
    ok('Carne: a tarifa aparece com vírgula (10,8%)', 'tarifa de 10,8%' in pg.locator('[data-com-abast=bovina] [data-ab-card=tec]').inner_text())
    ok('Carne: prévias com o sinal certo', d['tec'] < -.5 and d['cred'] < -.5 and d['leilao'] < -.5 and d['compra'] > 0, d)
    pg.locator('[data-com-abast=bovina]').scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/2_comprar_carne.png', full_page=False)
    pg.locator('[data-com-aba=vender]').click(); pg.wait_for_timeout(500)
    pg.locator('[data-com-prod=bovina]').first.click(); pg.wait_for_timeout(800)
    ok('Vender carne bovina: o mesmo bloco de abastecimento aparece abaixo da venda', pg.locator('[data-com-abast=bovina]').count() == 1)
    pg.locator('[data-com-abast=bovina]').scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/3_vender_carne.png', full_page=False)

    # ---------- efeito real (média de 6 sementes, tratado menos controle) ----------
    D = DIFF(pg, 'feijao', 6, "g.acoes=9;g.props=9;X.icTecZero(g,'feijao',12)", "delete g.comex.abast.feijao;X.icTick(g,null,'calc')")
    ok('Feijão: TEC zero deixa o preço mais de 1,5% abaixo do controle em 3 meses', D[3][7] < -.015, D[3][7])
    D = DIFF(pg, 'feijao', 4, "g.acoes=9;g.props=9;X.icLeilaoImport(g,'feijao',.6)", "delete g.comex.abast.feijao;X.icTick(g,null,'calc')")
    ok('Feijão: leilão baixa o preço na hora e a periferia melhora', D[1][7] < -.04 and D[2][5] > .3, (D[1][7], D[2][5]))
    D = DIFF(pg, 'bovina', 6, "g.acoes=9;g.props=9;X.icTecZero(g,'bovina',12)")
    ok('Carne: TEC zero deixa o preço mais de 1% abaixo do controle em 3 meses e o IPCA do comércio cai', D[3][7] < -.01 and D[3][1] < -.01, (D[3][7], D[3][1]))
    D = DIFF(pg, 'bovina', 14, "g.acoes=9;g.props=9;X.icCreditoProdutor(g,'bovina',2)")
    ok('Carne: crédito ao produtor só baixa o preço depois de 6 meses', abs(D[3][7]) < .005 and D[14][7] < -.01, (D[3][7], D[14][7]))

    # ---------- save antigo (sem o mercado do feijão) e 24 meses sem NaN ----------
    r = J(pg, "delete g.comex.abast.feijao;delete g.comex.idx.feijao;delete g.comex.est.feijao;delete g.comex.fl.feijao;X.ensureIC(g);const ok1=g.comex.fl.feijao&&Math.abs(g.comex.fl.feijao.pdom-1)<1e-6;X.icConabCompra(g,'bovina',1);g.acoes=9;g.props=9;X.icLeilaoImport(g,'feijao',.3);for(let m=0;m<24;m++){g.acoes=9;g.props=9;if(m===8)X.icConabVende(g,'bovina',.5);X.fimDoMes(g)}const v=[g.eco.ipca,g.comex.mac.ipca,g.comex.fl.feijao.pdom,g.comex.fl.bovina.pdom,g.fiscal.extra];return {ok1, v, fin:v.every(Number.isFinite)}")
    ok('Save antigo ganha o mercado do feijão no preço inicial; 24 meses com os instrumentos sem NaN', r['ok1'] and r['fin'], r)
    ok('Sem erros de página', not errs, errs[:3])
    print('\n%d/%d checagens' % (sum(c for c, _ in checks), len(checks))); b.close()
