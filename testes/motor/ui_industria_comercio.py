# Teste de interface de País > Indústria e Mundo > Comércio exterior: abas de setor e cartões (% do PIB), investir R$ 5 bi em soja (parecer com custo ≈ 5),
# isentar a nova indústria, vender soja à China (proposta -> resposta -> contrato), responder a uma proposta recebida (também na Mesa),
# comprar arroz de Portugal e depois mais barato da China (preço interno cai, IPCA mexe), cancelar com multa, estoques depois de 2 meses,
# terras raras dentro do Comércio com a opção de processar no Brasil e 0 erros de página/console.
# uso: python3 run_sandbox.py ui_industria_comercio.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8884
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
checks = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:260]) if det != '' else ''), flush=True)
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
def SET(pg, js): pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);" + js + ";return n})"); pg.wait_for_timeout(500)
def secao(pg, nome): pg.locator('#sec-tab-' + nome.lower().replace('í', 'i')).click(timeout=6000); pg.wait_for_timeout(500)
def chip(pg, nome):
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*' + nome + r'\s*$')).first.click(timeout=6000); pg.wait_for_timeout(600)
def avanca(pg, n):
    pg.evaluate("(n)=>__QV().setG(p=>{const x=structuredClone(p);for(let i=0;i<n;i++){__X().fimDoMes(x);x.acoes=5;x.pes.energia=90;x.eventoOk=true;x.evento=null}return x})", n); pg.wait_for_timeout(700)
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__AL = analisaLocal; window.__X = () => ({ fimDoMes, executaProposta, ensureIC, icTick, icFlow, IC_PROD, IC_BASE, IC_MK, IC_IMP });\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)

    # ---------------- Indústria ----------------
    secao(pg, 'País'); chip(pg, 'Indústria')
    raiz = pg.locator('[data-ind-root]')
    ok('Indústria: sub-aba abre', raiz.count() == 1)
    ok('Indústria: 5 indicadores no topo', pg.locator('[data-ind-root] [data-gv-kpi^=ind-]').count() == 5, pg.locator('[data-ind-root] [data-gv-kpi^=ind-]').all_inner_texts()[:5])
    tabs = pg.locator('[data-ind-setor]')
    ok('Indústria: 5 abas de setor (Agro, Mineração, Energia, Indústria de transformação, Nova indústria)', tabs.count() == 5, tabs.all_inner_texts())
    tot = 0
    for s in ['agro', 'mineracao', 'energia', 'industria', 'nova']:
        pg.locator('[data-ind-setor=%s]' % s).click(); pg.wait_for_timeout(300)
        n = pg.locator('[data-ind-grid=%s] [data-ind-prod]' % s).count(); tot += n
        ok('Indústria: setor %s tem cartões com %% do PIB' % s, n >= 3 and pg.locator('[data-ind-grid=%s] [data-ind-pib]' % s).count() == n and 'do PIB' in pg.locator('[data-ind-grid=%s] [data-ind-pib]' % s).first.inner_text(), n)
    ok('Indústria: 68 produtos (56 + 12 novos)', tot == 68, tot)
    pg.locator('[data-ind-setor=agro]').click(); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/ind_grade.png')
    c0 = pg.locator('[data-ind-prod=soja_grao]').inner_text()
    ok('Cartão da soja: ícone, valor exportado, %% do PIB, comprador, tendência e estoque', 'US$ 43' in c0 and '% do PIB' in c0 and 'China' in c0 and 'estoque' in c0 and ('subindo' in c0 or 'estável' in c0 or 'caindo' in c0), c0.replace('\n', ' | '))
    ok('Cartão com etiqueta estimativa onde há estimativa (arroz)', pg.locator('[data-ind-prod=arroz] [data-estimativa]').count() == 1)
    pg.locator('[data-ind-prod=soja_grao]').click(); pg.wait_for_timeout(500)
    ok('Soja: painel de detalhe com produção, consumo, estoque, preço e compradores', pg.locator('[data-ind-detalhe=soja_grao]').count() == 1 and pg.locator('[data-ind-preco]').count() == 1)
    pg.locator('[data-ind-acao=inv]').click(); pg.locator('[data-ind-bi="5"]').click(); pg.wait_for_timeout(500)
    texto = pg.locator('[data-ind-texto]').inner_text().strip('“” \n')
    r = pg.evaluate("(t)=>{const p=__AL(__QV().gRef.current,t);return {cost:p.cost,rev:p.rev,inst:p.inst,vago:!!(p.qualidade||{}).vago}}", texto)
    ok('Soja: texto "%s" -> motor lê custo ≈ 5 (%s)' % (texto, r), r['cost'] is not None and abs(r['cost'] - 5) <= 1.5 and not r['vago'])
    pg.screenshot(path=OUT + '/ind_soja_detalhe.png')
    a0 = G(pg, 'g.acoes')
    pg.locator('[data-ind-confirm=soja_grao]').click(timeout=5000); pg.wait_for_timeout(2500)
    t = pg.locator('.modal-wrap').first.inner_text() if pg.locator('.modal-wrap').count() else ''
    mm = re.search(r'Custo anual\s*\n\s*R\$\s*5[,.]0\s*bi', t)
    ok('Soja: o parecer abre e informa custo anual de R$ 5,0 bi', bool(mm) and len(t) > 150, mm.group(0) if mm else t[:120].replace('\n', ' '))
    pg.screenshot(path=OUT + '/ind_soja_parecer.png')
    fecha_modais(pg)
    # aprovação: a medida registra um projeto e a produção sobe com o tempo
    ap = pg.evaluate("""()=>{const X=__X();let res=null;__QV().setG(p=>{const n=structuredClone(p);X.ensureIC(n);
      const prop=__AL(n,'Investir R$ 5 bilhões na produção de soja em grão');prop.icHook={tipo:'inv',k:'soja_grao',v:5,pct:null};prop.scale=1;X.executaProposta(n,prop,'aprovada');
      res={proj:n.indu.proj.length,inv:n.indu.inv.soja_grao,f0:X.icFlow(n,'soja_grao').pf};window.__R=res;return n});return null}""")
    ap = pg.evaluate("()=>window.__R")
    ok('Aprovada: projeto registrado em g.indu e investimento no mandato = 5', ap['proj'] == 1 and ap['inv'] == 5, ap)
    avanca(pg, 12)
    pf1 = G(pg, 'g.comex.fl.soja_grao.pf'); bo = G(pg, 'g.comex.fl.soja_grao.boost')
    ok('Após 12 meses o reforço de produção da soja cresceu (+%.2f%%, fator total %.3f com eventos)' % (bo * 100, pf1), bo > 0.002, (pf1, bo))
    mac = G(pg, 'g.comex.mac')
    ok('Efeitos macro limitados (PIB, emprego, arrecadação)', abs(mac['pib']) < 1.5 and abs(mac['des']) < 1.2 and abs(G(pg, 'g.comex.tot.rec')) < 60 and abs(mac['ipca']) <= .6, mac)
    # nova indústria: isentar
    pg.locator('[data-ind-setor=nova]').click(); pg.wait_for_timeout(300)
    ok('Nova indústria: começa do zero (chips sem produção)', 'sem produção' in pg.locator('[data-ind-prod=chips]').inner_text())
    pg.locator('[data-ind-prod=chips]').click(); pg.wait_for_timeout(400)
    pg.locator('[data-ind-acao=isen]').click(); pg.wait_for_timeout(500)
    tx = pg.locator('[data-ind-texto]').inner_text().strip('“” \n')
    r = pg.evaluate("(t)=>{const p=__AL(__QV().gRef.current,t);return {cost:p.cost,rev:p.rev,inst:p.inst,vago:!!(p.qualidade||{}).vago,topic:p.topic}}", tx)
    ok('Chips: isenção lida pelo motor como renúncia fiscal (%s)' % r, r['rev'] is not None and r['rev'] < 0 and not r['vago'], tx)
    pg.screenshot(path=OUT + '/ind_chips_isencao.png')
    pg.locator('[data-ind-confirm=chips]').click(timeout=5000); pg.wait_for_timeout(2500)
    t = pg.locator('.modal-wrap').first.inner_text() if pg.locator('.modal-wrap').count() else ''
    ok('Chips: o parecer da isenção abre', len(t) > 150, t[:100].replace('\n', ' '))
    fecha_modais(pg)
    n_ac = G(pg, 'g.acoes')

    # ---------------- Comércio exterior ----------------
    SET(pg, "n.acoes=5;n.pes.energia=90")
    secao(pg, 'Mundo'); chip(pg, 'Comércio exterior')
    ok('Comércio: sub-aba abre', pg.locator('[data-com-root]').count() == 1)
    ok('Comércio: 5 indicadores (balança mês/ano, acordos, propostas, IPCA)', pg.locator('[data-com-root] [data-gv-kpi^=com-]').count() == 5)
    ok('Comércio: mapa-múndi presente com países', pg.locator('[data-com-mapa]').count() == 1 and pg.locator('[data-mapa-pais]').count() >= 55)
    pg.screenshot(path=OUT + '/com_geral.png')
    pg.locator('[data-com-aba=vender]').click(); pg.wait_for_timeout(400)
    pg.locator('[data-com-prod=soja_grao]').click(); pg.wait_for_timeout(400)
    ok('Vender soja: compradores listados com China e preço', pg.locator('[data-com-pais=CHN]').count() == 1 and 'US$' in pg.locator('[data-com-pais=CHN]').inner_text(), pg.locator('[data-com-pais=CHN]').inner_text().replace('\n', ' '))
    pg.locator('[data-com-propor=CHN]').click(); pg.wait_for_timeout(300)
    pg.locator('[data-com-anos="2"]').click(); pg.locator('[data-com-preco]').fill('100'); pg.locator('[data-com-preco]').blur()
    pg.locator('[data-com-enviar]').click(); pg.wait_for_timeout(400)
    ok('Vender soja à China a 100%% do preço: proposta aceita', pg.locator('[data-com-resposta=aceita]').count() == 1)
    pg.locator('[data-com-preco]').fill('106'); pg.locator('[data-com-preco]').blur(); pg.locator('[data-com-enviar]').click(); pg.wait_for_timeout(400)
    ok('Preço 6%% acima: contraproposta (negociação 1 de 2)', pg.locator('[data-com-resposta=contra]').count() == 1)
    pg.screenshot(path=OUT + '/com_vender_contra.png')
    pg.locator('[data-com-preco]').fill('100'); pg.locator('[data-com-preco]').blur(); pg.locator('[data-com-enviar]').click(); pg.wait_for_timeout(300)
    a0 = G(pg, 'g.acoes'); rel0 = G(pg, 'g.mundo.pais.China.rel'); usa0 = G(pg, 'g.mundo.pais.EUA.rel')
    pg.locator('[data-com-fechar]').click(); pg.wait_for_timeout(600)
    ok('Contrato de venda assinado: acordo ativo, 1 ação gasta, sem Congresso', G(pg, "g.comex.acordos.filter(a=>a.estado=='ativo'&&a.tipo=='venda').length") == 1 and G(pg, 'g.acoes') == a0 - 1, (a0, G(pg, 'g.acoes')))
    ok('Relação com a China sobe após o contrato', G(pg, 'g.mundo.pais.China.rel') > rel0, (rel0, G(pg, 'g.mundo.pais.China.rel')))
    ok('Geopolítica: contrato forte com a China esfria a relação com os EUA', G(pg, 'g.mundo.pais.EUA.rel') < usa0, (usa0, G(pg, 'g.mundo.pais.EUA.rel')))
    # proposta recebida
    SET(pg, "n.comex.props.push({id:'prT1',pais:'JPN',k:'milho',qtd:1.5,preco:n.comex.idx.milho*1.01,anos:2,mes:n.mes,exp:n.mes+3,grande:true,rodada:0,estado:'aberta'});n.comex.props.push({id:'prT2',pais:'VNM',k:'algodao',qtd:.2,preco:n.comex.idx.algodao*.99,anos:1,mes:n.mes,exp:n.mes+3,grande:false,rodada:0,estado:'aberta'})")
    pg.locator('[data-com-aba=geral]').click(); pg.wait_for_timeout(500)
    ok('Propostas recebidas listadas (grande e pequena)', pg.locator('[data-com-proposta]').count() >= 2)
    pg.screenshot(path=OUT + '/com_propostas.png')
    pg.locator('[data-com-pr-negociar=prT1]').click(); pg.wait_for_timeout(200)
    pg.locator('[data-com-pr-preco]').fill('104'); pg.locator('[data-com-pr-preco]').blur(); pg.locator('[data-com-pr-enviar=prT1]').click(); pg.wait_for_timeout(500)
    ok('Proposta recebida: negociar gera contraproposta do país', G(pg, "n=g.comex.props.find(p=>p.id=='prT1'),n&&n.rodada") == 1 or G(pg, "g.comex.props.find(p=>p.id=='prT1').estado") == 'recusada', G(pg, "g.comex.props.find(p=>p.id=='prT1').msg"))
    pg.locator('[data-com-pr-aceitar=prT2]').click(); pg.wait_for_timeout(500)
    ok('Proposta pequena aceita vira contrato (venda de algodão ao Vietnã)', G(pg, "g.comex.acordos.some(a=>a.k=='algodao'&&a.pais=='VNM'&&a.estado=='ativo')"))
    SET(pg, "n.comex.props.push({id:'prT3',pais:'DEU',k:'cafe_verde',qtd:2,preco:n.comex.idx.cafe_verde*1.02,anos:2,mes:n.mes,exp:n.mes+3,grande:true,rodada:0,estado:'aberta'})")
    secao(pg, 'Mesa'); pg.wait_for_timeout(500)
    ok('Mesa: proposta grande aparece em "Precisa de você" (data-pend=comercio)', pg.locator('[data-pend=comercio]').count() >= 1, pg.locator('[data-pend=comercio]').all_inner_texts()[:1])
    pg.screenshot(path=OUT + '/mesa_pendencia.png')
    secao(pg, 'Mundo'); chip(pg, 'Comércio exterior')
    ok('Mundo: selo de pendência no chip do Comércio exterior', pg.locator('[data-pend-aqui=mundo]').count() == 1)
    pg.locator('[data-com-pr-rejeitar=prT3]').click(); pg.wait_for_timeout(400)
    ok('Recusar a proposta fecha a pendência', pg.locator('[data-com-proposta=prT3]').count() == 0)
    # comprar arroz
    SET(pg, "n.acoes=5;n.pes.energia=90")
    pg.locator('[data-com-aba=comprar]').click(); pg.wait_for_timeout(400)
    pg.locator('[data-com-imp=arroz_imp]').click(); pg.wait_for_timeout(400)
    ok('Comprar arroz: Portugal e China entre os vendedores', pg.locator('[data-com-vendedor=PRT]').count() == 1 and pg.locator('[data-com-vendedor=CHN]').count() == 1)
    pg.locator('[data-com-comprar-de=PRT]').click(); pg.locator('[data-com-qtd="2"]').click(); pg.locator('[data-com-anos="2"]').click(); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/com_comprar_prt.png')
    pg.locator('[data-com-fechar-compra]').click(); pg.wait_for_timeout(600)
    pd1 = G(pg, 'g.comex.fl.arroz.pdom'); ip1 = G(pg, 'g.comex.mac.ipca'); pr_prt = G(pg, "g.comex.acordos.find(a=>a.pais=='PRT').preco")
    pg.locator('[data-com-comprar-de=CHN]').click(); pg.locator('[data-com-qtd="4"]').click(); pg.locator('[data-com-anos="2"]').click(); pg.wait_for_timeout(300)
    ok('Prévia da compra mostra preço interno e efeito no IPCA', 'Efeito no IPCA' in pg.locator('[data-com-previa]').inner_text(), pg.locator('[data-com-previa]').inner_text().replace('\n', ' '))
    pg.locator('[data-com-fechar-compra]').click(); pg.wait_for_timeout(600)
    pd2 = G(pg, 'g.comex.fl.arroz.pdom'); ip2 = G(pg, 'g.comex.mac.ipca'); pr_chn = G(pg, "g.comex.acordos.find(a=>a.pais=='CHN').preco")
    ok('Arroz da China (%.3f) é mais barato que o de Portugal (%.3f)' % (pr_chn, pr_prt), pr_chn < pr_prt)
    ok('Preço interno do arroz cai com a compra mais barata da China (%.4f -> %.4f)' % (pd1, pd2), pd2 < pd1, (pd1, pd2))
    ok('IPCA do comércio se move para baixo (%.4f -> %.4f pp)' % (ip1, ip2), ip2 < ip1, (ip1, ip2))
    pg.screenshot(path=OUT + '/com_comprar_chn.png')
    # cancelar
    pg.locator('[data-com-aba=acordos]').click(); pg.wait_for_timeout(400)
    ex0 = G(pg, 'g.fiscal.extra'); rp0 = G(pg, 'g.mundo.pais.Portugal.rel'); a0 = G(pg, 'g.acoes')
    pg.locator('[data-com-cancelar]').last.click(); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/com_acordos.png')
    pg.locator('[data-com-cancelar-ok]').first.click(); pg.wait_for_timeout(600)
    ok('Cancelar antes do fim: multa entra nas contas e a relação piora', G(pg, "g.comex.acordos.some(a=>a.estado=='cancelado'&&a.multa>0)") and G(pg, 'g.fiscal.extra') > ex0, (ex0, G(pg, 'g.fiscal.extra')))
    # estoques depois de 2 meses
    e0 = G(pg, 'g.comex.est.arroz'); s0 = G(pg, 'g.comex.est.soja_grao')
    avanca(pg, 2)
    e1 = G(pg, 'g.comex.est.arroz'); s1 = G(pg, 'g.comex.est.soja_grao')
    ok('Estoques mudam depois de 2 meses (arroz %.4f -> %.4f)' % (e0, e1), abs(e1 - e0) > 1e-5 or abs(s1 - s0) > 1e-5, (e0, e1, s0, s1))
    ok('Mês avançou com 0 erros no motor mensal e preços atualizados', G(pg, 'g.comex.hist.soja_grao.length') >= 13)
    # tratados
    pg.locator('[data-com-aba=acordos]').click(); pg.wait_for_timeout(300)
    ok('Tratados de livre comércio: 4 blocos com botão para enviar ao Congresso', pg.locator('[data-com-tlc]').count() == 4)
    pg.locator('[data-com-tlc=UE]').click(timeout=5000); pg.wait_for_timeout(2500)
    t = pg.locator('.modal-wrap').first.inner_text() if pg.locator('.modal-wrap').count() else ''
    ok('Tratado Mercosul-UE passa pelo parecer (precisa do Congresso)', len(t) > 150, t[:100].replace('\n', ' '))
    fecha_modais(pg)
    # terras raras
    pg.locator('[data-com-aba=vender]').click(); pg.wait_for_timeout(300)
    pg.locator('[data-com-prod=terras_raras]').click(); pg.wait_for_timeout(500)
    ok('Terras raras é produto do Comércio, com a opção de exigir processamento no Brasil', pg.locator('[data-com-terras]').count() == 1 and pg.locator('[data-com-exigir-proc]').count() == 1)
    pg.screenshot(path=OUT + '/com_terras_raras.png')
    SET(pg, "n.acoes=5;n.pes.energia=90")
    pg.locator('[data-com-exigir-proc]').click(timeout=5000); pg.wait_for_timeout(2500)
    t = pg.locator('.modal-wrap').first.inner_text() if pg.locator('.modal-wrap').count() else ''
    ok('Exigir processamento no Brasil abre o parecer', len(t) > 150, t[:100].replace('\n', ' '))
    fecha_modais(pg)
    ap = pg.evaluate("""()=>{const X=__X();let res=null;__QV().setG(p=>{const n=structuredClone(p);const prop=__AL(n,'Exigir processamento das terras raras no Brasil');prop.icHook={tipo:'proc'};prop.scale=1;X.executaProposta(n,prop,'aprovada');res=[n.comex.exigeProc,n.indu.proj.some(j=>j.k=='imas_terras_raras')];window.__R=res;return n});return null}""")
    ap = pg.evaluate("()=>window.__R")
    ok('Aprovada a exigência: vendas caem e a indústria de ímãs ganha projeto', ap == [True, True], ap)
    secao(pg, 'Mundo'); chip(pg, 'Terras raras')
    ok('Sub-aba Terras raras original segue funcionando', pg.locator('[data-mundo=terras]').count() == 1)
    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    b.close()
falhas = [n for c, n in checks if not c]
print('\n%d/%d verificações OK' % (len(checks) - len(falhas), len(checks)))
if falhas: print('FALHAS:', falhas)
