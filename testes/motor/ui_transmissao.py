# Teste da transmissão de preços: peso efetivo no IPCA, reação dos grupos, fertilizantes com defasagem, diesel, TEC zero, Conab, crédito, leilão,
# prévia = efeito real e save novo sem mudança. Também confere as telas (Comprar do arroz, do trigo e do potássio).
# uso: python3 run_sandbox.py ui_transmissao.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8893
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
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__X = () => ({ ensureIC, IC_IMP, IC_BASE, IC_BAS, IC_IND, IC_RX, icContrata, icPrecoPedidoCompra, icSimPreco, fimDoMes, aprovacao, icFlow, icTecZero, icTecRevoga, icConabCompra, icConabVende, icCreditoProdutor, icLeilaoImport, icAbastPrev, icAbastFaz, icMkDe, icTick, icPesoInfo });\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    SET(pg, "n.acoes=9;n.props=9;n.pes.energia=90")

    # ---------- save novo ----------
    SET(pg, "X.ensureIC(n)")
    r = G(pg, "(()=>{const X=__X();const f=g.comex.fl;return {pd:['trigo','leite_po','arroz','medicamentos','combustiveis','fert_potassio','fert_nitrogenados','fert_fosfatados'].map(k=>f[k].pdom), mac:g.comex.mac.ipca, ab:Object.keys(g.comex.abast||{}).length, w:[X.IC_BASE.trigo.ipca,X.IC_BASE.leite_po.ipca,X.IC_BASE.arroz.ipca,X.IC_BASE.medicamentos.ipca]}})()")
    ok('Save novo: todos os preços internos em 1,000, IPCA do comércio 0 e nenhum instrumento ativo', all(abs(v - 1) < 1e-6 for v in r['pd']) and abs(r['mac']) < 1e-6 and r['ab'] == 0, r)
    ok('Pesos efetivos no IPCA: trigo 1,2 (2,0 x 60%), leite 1,6 (2,0 x 80%), arroz 0,75 e remédios 3,2', [round(v, 3) for v in r['w']] == [1.2, 1.6, .75, 3.2], r['w'])

    # ---------- telas ----------
    secao(pg, 'Mundo'); chip(pg, 'Comércio exterior')
    pg.locator('[data-com-aba=comprar]').click(); pg.wait_for_timeout(500)
    pg.locator('[data-com-imp=trigo]').click(); pg.wait_for_timeout(600)
    ch = pg.locator('[data-com-peso]').inner_text()
    ok('Trigo: chip "peso no IPCA com derivados" mostra o peso efetivo e o repasse', re.search(r'peso no IPCA com derivados: 1,2% \(de 2,0%, repasse de 60%\)', ch), ch)
    ok('Trigo: seção Abastecimento com os 4 instrumentos e o estoque público', pg.locator('[data-com-abast=trigo] [data-ab-card]').count() == 4 and pg.locator('[data-ab-estoque]').count() == 1)
    pg.locator('[data-com-imp=fert_potassio_imp]').click(); pg.wait_for_timeout(600)
    ch = pg.locator('[data-com-peso]').inner_text()
    ok('Potássio: chip mostra o peso indireto e a defasagem de 6 a 9 meses; sem instrumentos de abastecimento', re.search(r'0,7% indireto \(nos alimentos, 6 a 9 meses depois\)', ch) and pg.locator('[data-com-abast]').count() == 0, ch)
    pg.locator('[data-com-imp=diesel]').click(); pg.wait_for_timeout(600)
    ch = pg.locator('[data-com-peso]').inner_text()
    ok('Diesel: chip mostra o frete de 1,2% com defasagem de 1 a 3 meses', re.search(r'1,2% de frete \(1 a 3 meses depois\)', ch), ch)
    pg.locator('[data-com-imp=medicamentos_imp]').click(); pg.wait_for_timeout(600)
    ok('Medicamentos: peso 3,2% mantido', '3,2%' in pg.locator('[data-com-peso]').inner_text(), pg.locator('[data-com-peso]').inner_text())

    # ---------- fertilizante barato: IPCA cai só depois de ~6 meses ----------
    D = DIFF(pg, 'fert_potassio', 14, "const q=Math.max(X.IC_IMP.fert_potassio_imp.imp_usd_bi*.5,.05)*4;const pr=X.icPrecoPedidoCompra(g,'fert_potassio_imp','CAN',2,q)*.85;X.icContrata(g,{tipo:'compra',k:'fert_potassio_imp',iso:'CAN',qtd:q,preco:pr,anos:2})")
    dm = [round(D[i][1], 4) for i in range(15)]
    ok('Fertilizante: contrato grande e barato (4x o volume, 15% abaixo): preço interno do potássio cai >10% logo', D[1][7] < -.10, D[1][7])
    ok('Fertilizante: nos 3 primeiros meses o IPCA do comércio quase não se mexe (defasagem)', max(abs(v) for v in dm[1:4]) < .012, dm[:5])
    ok('Fertilizante: aos 9-12 meses o termo de inflação chega a cerca de −0,05 pp (−0,04 a −0,08)', -.08 < dm[10] < -.04 and -.08 < dm[12] < -.04, dm)
    ok('Fertilizante: já aos 6-8 meses o efeito começa (entre −0,005 e −0,05)', -.05 < dm[8] < -.005, dm[6:10])
    ok('Fertilizante: o IPCA oficial fica abaixo do controle (média de 6 sementes) aos 14 meses', D[14][0] < -.008, D[14][0])
    ok('Fertilizante: grupo agro sobe (custo menor) e o termo C.mac.agro fica positivo', D[6][3] > .5 and D[6][11] > .003, (D[6][3], D[6][11]))

    # ---------- diesel caro: caminhoneiros reagem; frete defasado ----------
    D = DIFF(pg, 'combustiveis', 8, "g.comex.idx.combustiveis=1.9"); D2 = DIFF(pg, 'combustiveis', 8, "g.comex.idx.combustiveis=1.25")
    fr = [D2[i][1] - .6 * 5.5 * D2[i][7] for i in range(9)] # parte do IPCA que não é o efeito direto do preço = frete defasado
    ok('Diesel caro (preço mundial +90%): caminhoneiros ficam bem abaixo do controle em 4 meses', D[4][4] < -1.2, D[4][4])
    ok('Diesel caro: o IPCA sobe e o frete entra com 1 a 3 meses de atraso (zero no 1º mês, positivo depois)', D[5][1] > .15 and abs(fr[1]) < .01 and fr[4] > .03, ([round(v, 3) for v in fr], D[5][1]))

    # ---------- TEC zero do arroz pela tela ----------
    pg.locator('[data-com-imp=arroz_imp]').click(); pg.wait_for_timeout(700)
    ch = pg.locator('[data-com-peso]').inner_text()
    ok('Arroz: peso efetivo 0,75%', '0,75%' in ch, ch)
    pg.screenshot(path=OUT + '/arroz_abastecimento.png', full_page=True)
    pg.locator('[data-ab-meses="12"]').click(); pg.wait_for_timeout(400)
    prev = pg.locator('[data-ab-prev=tec]'); d_ui = float(prev.get_attribute('data-delta')); ptxt = prev.inner_text()
    ok('TEC zero: prévia mostra queda do preço, IPCA, perda de arrecadação e pressão sobre a produção', d_ui < -2 and 'arrecadação' in ptxt and 'IPCA' in ptxt and 'produção nacional' in ptxt, ptxt)
    PH = lambda hz: G(pg, "(()=>{const X=__X();const g2=structuredClone(g);g2.mes+=%d;return X.icFlow(g2,'arroz').pdom})()" % hz)
    pwo = PH(2); rec0 = G(pg, "g.fiscal.receita"); ag0 = G(pg, "g.groups.agro"); ac0 = G(pg, "g.acoes")
    pg.locator('[data-ab-tec]').click(); pg.wait_for_timeout(900)
    r = G(pg, "({tec:g.comex.abast.arroz.tec,acoes:g.acoes,agro:g.groups.agro})")
    d_real = (PH(2) / pwo - 1) * 100
    ok('TEC zero: prévia = efeito real (diferença < 0,001 ponto percentual)', abs(d_real - d_ui) < .001, (d_ui, d_real))
    ok('TEC zero: gasta 1 ação, fica em vigor por 12 meses e o agro reclama na hora', r['tec'] and r['tec']['meses'] == 12 and r['acoes'] == ac0 - 1 and r['agro'] < ag0 - .3, (r['tec'], r['acoes'], ac0, r['agro'], ag0))
    ok('TEC zero: a tela passa a mostrar "Em vigor até" e o botão de revogar', pg.locator('[data-ab-tec-ativa]').count() == 1 and pg.locator('[data-ab-tec-fim]').count() == 1)
    pg.screenshot(path=OUT + '/arroz_tec.png', full_page=True)
    D = DIFF(pg, 'arroz', 12, "X.icTecZero(g,'arroz',12)", "delete g.comex.abast.arroz;X.icTick(g,null,'calc')")
    ok('TEC zero: o preço do arroz fica mais de 2% abaixo do controle em 3 meses', D[3][7] < -.02, D[3][7])
    ok('TEC zero: agro e agricultura familiar caem em relação ao controle e a produção nacional encolhe', D[8][3] < -.4 and D[8][10] < -.15 and D[8][8] > .015, (D[8][3], D[8][10], D[8][8]))
    ok('TEC zero: a periferia ganha (preço do arroz mais baixo)', D[6][5] > .1, D[6][5])
    r = J(pg, "const a=g.comex.abast.arroz.tec;g.acoes=9;g.props=9;const e0=g.acoes;X.icTecRevoga(g,'arroz');return [g.comex.abast.arroz.tec.ate===g.mes, e0-g.acoes, g.comex.fl.arroz.pdom]")
    ok('TEC zero pode ser revogada (1 ação) e o preço volta a subir', r[0] and r[1] == 1, r)
    pg.screenshot(path=OUT + '/arroz_abastecimento_tec.png', full_page=True)

    # ---------- Conab: compra e vende ----------
    fx0 = G(pg, "g.fiscal.extra"); pdc = PH(0)
    pg.locator('[data-ab-x="0.5"]').click(); pg.wait_for_timeout(300)
    d_ui = float(pg.locator('[data-ab-prev=compra]').get_attribute('data-delta'))
    pg.locator('[data-ab-compra]').click(); pg.wait_for_timeout(900)
    r = G(pg, "({est:g.comex.abast.arroz.conab,fx:g.fiscal.extra,p:g.comex.fl.arroz.pdom})")
    ok('Conab compra: estoque público sobe 0,5 mês, o custo sai do caixa e a prévia bate com o preço real', abs(r['est'] - .5) < 1e-9 and r['fx'] > fx0 + .3 and abs((r['p'] / pdc - 1) * 100 - d_ui) < .001, (r, fx0, d_ui, (r['p'] / pdc - 1) * 100))
    ok('Conab: a tela mostra o estoque em meses e toneladas', re.search(r'0,50 meses de consumo.*mi t', pg.locator('[data-ab-estoque]').inner_text()), pg.locator('[data-ab-estoque]').inner_text())
    fx1 = r['fx']; pdv = PH(0)
    d_ui = float(pg.locator('[data-ab-prev=venda]').get_attribute('data-delta'))
    pg.locator('[data-ab-venda]').click(); pg.wait_for_timeout(900)
    r = G(pg, "({est:g.comex.abast.arroz.conab,fx:g.fiscal.extra,p:g.comex.fl.arroz.pdom})")
    ok('Conab vende: estoque zera, entra receita e o preço interno cai como a prévia mostrou', r['est'] < 1e-9 and r['fx'] < fx1 - .3 and d_ui < -2 and abs((r['p'] / pdv - 1) * 100 - d_ui) < .001, (r, fx1, d_ui, (r['p'] / pdv - 1) * 100))
    ok('Conab: sem estoque, o botão de vender fica desativado', pg.locator('[data-ab-venda]').is_disabled())
    pg.screenshot(path=OUT + '/arroz_conab.png', full_page=True)

    # ---------- leilão ----------
    d_ui = float(pg.locator('[data-ab-prev=leilao]').get_attribute('data-delta')); pdl = PH(0); fl0 = G(pg, "g.fiscal.extra"); ag0 = G(pg, "g.groups.agro")
    pg.locator('[data-ab-leilao]').click(); pg.wait_for_timeout(900)
    r = G(pg, "({p:g.comex.fl.arroz.pdom,fx:g.fiscal.extra,agro:g.groups.agro,leil:g.comex.abast.arroz.leil})")
    ok('Leilão: o preço cai rápido (prévia = real), custa dinheiro e o agro reclama', d_ui < -4 and abs((r['p'] / pdl - 1) * 100 - d_ui) < .001 and r['fx'] > fl0 + .5 and r['agro'] < ag0 - .3, (d_ui, (r['p'] / pdl - 1) * 100, r['fx'] - fl0, r['agro'] - ag0))
    ok('Leilão: um novo leilão fica bloqueado por 6 meses', pg.locator('[data-ab-leilao]').is_disabled() and 'Próximo leilão possível em 6 meses' in pg.locator('[data-ab-card=leilao]').inner_text(), pg.locator('[data-ab-card=leilao]').inner_text()[-80:])

    # ---------- crédito (prévia = real) ----------
    d_ui = float(pg.locator('[data-ab-prev=cred]').get_attribute('data-delta')); pcr = PH(12); pnow0 = PH(0); fc0 = G(pg, "g.fiscal.extra")
    pg.locator('[data-ab-cred]').click(); pg.wait_for_timeout(900)
    r = G(pg, "({fx:g.fiscal.extra})"); p12 = PH(12); pnow1 = PH(0)
    ok('Crédito: custo fiscal já; nada muda no preço agora e a prévia (12 meses) bate com o efeito real', abs(pnow1 / pnow0 - 1) < 1e-9 and r['fx'] > fc0 + .3 and d_ui < -1.5 and abs((p12 / pcr - 1) * 100 - d_ui) < .001, (d_ui, (p12 / pcr - 1) * 100, r['fx'] - fc0))
    D = DIFF(pg, 'arroz', 16, "X.icCreditoProdutor(g,'arroz',1)", "delete g.comex.abast.arroz;X.icTick(g,null,'calc')")
    ok('Crédito: o preço só cai depois de 6 a 12 meses (nos 3 primeiros ~ igual, aos 14 meses bem abaixo)', abs(D[3][7]) < .005 and D[14][7] < -.015, (D[3][7], D[14][7]))

    # ---------- remédio caro pesa nos aposentados; reação decai e tem teto ----------
    D = DIFF(pg, 'medicamentos', 24, "const q=Math.max(X.IC_IMP.medicamentos_imp.imp_usd_bi*.5,.05)*3;const pr=X.icPrecoPedidoCompra(g,'medicamentos_imp','DEU',2,q);X.icContrata(g,{tipo:'compra',k:'medicamentos_imp',iso:'DEU',qtd:q,preco:pr,anos:2})")
    da = [D[i][6] for i in range(25)]
    ok('Remédio mais caro: aposentados caem em relação ao controle', min(da) < -.6, [round(v, 2) for v in da[::4]])
    pas = [da[i] - da[i - 1] for i in range(1, 25)]
    ok('Reação a preço de item básico tem teto mensal e decai (volta a se recuperar, não soma sem fim)', min(pas) >= -1.0 and da[24] > min(da) + .4, (round(min(pas), 2), round(min(da), 2), round(da[24], 2)))
    nf = J(pg, "const q=Math.max(X.IC_IMP.medicamentos_imp.imp_usd_bi*.5,.05)*3;const pr=X.icPrecoPedidoCompra(g,'medicamentos_imp','DEU',2,q);X.icContrata(g,{tipo:'compra',k:'medicamentos_imp',iso:'DEU',qtd:q,preco:pr,anos:2});for(let i=0;i<6;i++){X.fimDoMes(g)}return (g.feed||[]).slice(0,12).map(f=>f.txt).concat(g.comex.news.map(n=>n.txt))")
    ok('Manchete ocasional quando a variação é grande (remédio mais caro pesa no bolso dos aposentados)', any('aposentados' in t or 'Remédio' in t or 'REMÉDIO' in t for t in nf), nf[:4])

    # ---------- contrato de trigo: dano ao produtor e reação do Sul ----------
    TG = "const q=Math.max(X.IC_IMP.trigo.imp_usd_bi*.5,.05)*2;const pr=X.icPrecoPedidoCompra(g,'trigo','ARG',2,q)*.9;X.icContrata(g,{tipo:'compra',k:'trigo',iso:'ARG',qtd:q,preco:pr,anos:2})"
    D = DIFF(pg, 'trigo', 12, TG)
    sul0 = G(pg, "g.regOff.S")
    ex = J(pg, RUN + TG + ";run(g,12,'trigo',13);return {sul:g.regOff.S,feed:(g.feed||[]).map(f=>f.txt)}")
    ok('Trigo importado muito e barato: a produção nacional encolhe (cut) acima do limiar menor dos itens básicos', D[12][8] > .012, D[12][8])
    ok('Trigo: o agro reclama e a reação regional do Sul aparece (aprovação regional e feed)', D[12][3] < -1 and ex['sul'] < sul0 - .5 and any('Sul' in t for t in ex['feed']), (D[12][3], ex['sul'], sul0, ex['feed'][:3]))

    # ---------- prévia da compra (se fechar) = efeito real, com o novo peso ----------
    r = J(pg, "const q=Math.max(X.IC_IMP.trigo.imp_usd_bi*.5,.05);const pr=Math.round(X.icPrecoPedidoCompra(g,'trigo','ARG',2,q)*1000)/1000;const S=X.icSimPreco(g,'compra','trigo','ARG',q,pr,2);const m0=g.comex.mac.ipca,p0=g.comex.fl.trigo.pdom;X.icContrata(g,{tipo:'compra',k:'trigo',iso:'ARG',qtd:q,preco:pr,anos:2});return [S.d,(g.comex.fl.trigo.pdom/p0-1)*100,S.ipca,g.comex.mac.ipca-m0]")
    ok('Compra de trigo: prévia do preço e do IPCA = efeito real do contrato', abs(r[0] - r[1]) < 1e-6 and abs(r[2] - r[3]) < 1e-6, r)

    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    b.close()
falhas = [n for c, n in checks if not c]
print('%d/%d verificações OK' % (len(checks) - len(falhas), len(checks)))
if falhas: print('FALHAS:', falhas); sys.exit(1)
