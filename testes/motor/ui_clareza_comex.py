# Teste de clareza do Comércio exterior e da Indústria: volume contratado soma certo, coluna "se fechar" bate com o Δ real do preço interno,
# linha do tempo com o mês de término certo, cancelar mostra a multa, listas com unidade, previsão da Indústria e atalho para vender.
# uso: python3 run_sandbox.py ui_clareza_comex.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8886
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
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__AL = analisaLocal; window.__X = () => ({ executaProposta, ensureIC, IC_IMP });\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    SET(pg, "n.acoes=5;n.pes.energia=90")
    secao(pg, 'Mundo'); chip(pg, 'Comércio exterior')
    pg.locator('[data-com-aba=comprar]').click(); pg.wait_for_timeout(400)
    # ---------- Comprar ----------
    itens = pg.locator('[data-com-picker=comprar] [data-com-imp]'); n = itens.count()
    sem = [t for t in itens.all_inner_texts() if not (re.search(r'US\$ [\d.,]+ bi/ano', t) and re.search(r'\d+% em acordo do governo', t) and re.search(r'preço no Brasil (no nível de 2025|[\d,]+% mais (barato|caro) que em 2025)', t))]
    ok('Comprar: %d itens da lista com "US$ X bi/ano", "%% em acordo do governo" e "preço no Brasil X%% mais barato/caro que em 2025"' % n, n >= 25 and not sem, sem[:2])
    pg.locator('[data-com-imp=trigo]').click(); pg.wait_for_timeout(500)
    sit = pg.locator('[data-com-sit=compra]')
    ok('Painel "Situação do Trigo" aparece', sit.count() == 1 and 'situação do trigo' in sit.inner_text().lower(), sit.inner_text()[:80])
    ok('Sem contrato: contratado = 0', float(pg.locator('[data-com-sit-contratado]').get_attribute('data-com-sit-contratado')) == 0)
    cols = [c.lower() for c in pg.locator('[data-com-comprar] .ic-tbl th').all_inner_texts()]
    ok('Colunas: Preço entregue no Brasil (US$/t), Comparado ao preço mundial, Preço do trigo no Brasil se fechar', any('preço entregue no brasil' in c and 'us$/t' in c for c in cols) and any('comparado ao preço mundial' in c for c in cols) and any('no brasil se fechar' in c for c in cols), cols)
    ok('Tooltips (?) nas colunas e no painel', pg.locator('[data-com-comprar] .ic-tbl [data-gv-tip]').count() >= 3 and pg.locator('[data-com-sit] [data-gv-tip]').count() >= 3)
    ok('Comparação em texto (mais barato / mais caro)', 'mais barato' in pg.locator('[data-com-vendedor=ARG]').inner_text() and 'mais caro' in pg.locator('[data-com-vendedor=USA]').inner_text(), pg.locator('[data-com-vendedor=ARG]').inner_text().replace('\n', ' '))
    esp = float(pg.locator('[data-com-se-fechar=ARG]').get_attribute('data-delta'))
    seta = pg.locator('[data-com-se-fechar=ARG]').inner_text()
    ok('Seta ↓ quando o preço cai e ↑ quando sobe', ('↓' in seta) == (esp < 0) and ('↑' in pg.locator('[data-com-se-fechar=USA]').inner_text()) == (float(pg.locator('[data-com-se-fechar=USA]').get_attribute('data-delta')) > 0), seta.replace('\n', ' '))
    pd0 = G(pg, 'g.comex.fl.trigo.pdom')
    pg.locator('[data-com-comprar-de=ARG]').click(); pg.wait_for_timeout(400)
    linha = pg.locator('[data-com-linha=compra]').inner_text()
    ok('Linha do tempo: começa este mês, entrega, vale até, preço (cai/sobe X%, fica Y% abaixo/acima do nível de 2025), IPCA, 1 ação, multa', all(x in linha for x in ['Ao assinar', 'começa este mês', 'entrega em ~', 'vale até', 'preço de trigo no Brasil:', 'nível de 2025', 'IPCA', 'custa 1 ação', 'cancelar antes custa multa']), linha)
    fimtxt = pg.locator('[data-com-linha=compra] [data-com-fim]').inner_text()
    mm = re.match(r'(\S{3})/(\d\d)', fimtxt); mi = re.search(r'começa este mês \((\S{3})/(\d\d)\)', linha)
    ok('Linha do tempo: término = mesmo mês, 2 anos depois (%s -> %s)' % (mi.group(0) if mi else '?', fimtxt), bool(mm and mi and mm.group(1) == mi.group(1) and int(mm.group(2)) == int(mi.group(2)) + 2), fimtxt)
    pg.locator('[data-com-fechar-compra]').click(); pg.wait_for_timeout(700)
    pd1 = G(pg, 'g.comex.fl.trigo.pdom'); real = (pd1 / pd0 - 1) * 100
    ok('Coluna "se fechar" bate com o Δ real (%.4f%% x %.4f%%)' % (esp, real), abs(esp - real) < 0.02, (esp, real))
    a = G(pg, "g.comex.acordos.filter(x=>x.estado=='ativo'&&x.k=='trigo')[0]")
    ok('Contrato ativo: fim = início + 24 meses', a['mFim'] - a['m0'] == 24, a)
    c1 = float(pg.locator('[data-com-sit-contratado]').get_attribute('data-com-sit-contratado'))
    ok('Volume contratado aparece após fechar (%.2f)' % c1, abs(c1 - a['qtd']) < 1e-3 and pg.locator('[data-com-sit-contrato]').count() == 1, (c1, a['qtd']))
    ate = pg.locator('[data-com-sit-contrato]').inner_text(); fimA = pg.locator('[data-com-sit-ate]').get_attribute('data-com-sit-ate')
    ok('Contrato listado: país, "até %s" e meses restantes' % fimA, 'Argentina' in ate and ('até ' + fimA) in ate and 'faltam 24 meses' in ate, ate.replace('\n', ' '))
    ok('O fim listado é o mesmo da linha do tempo (%s)' % fimA, fimA == fimtxt)
    esp2 = float(pg.locator('[data-com-se-fechar=PRY]').get_attribute('data-delta')); pd1 = G(pg, 'g.comex.fl.trigo.pdom')
    pg.locator('[data-com-comprar-de=PRY]').click(); pg.wait_for_timeout(300); pg.locator('[data-com-fechar-compra]').click(); pg.wait_for_timeout(700)
    pd2 = G(pg, 'g.comex.fl.trigo.pdom'); real2 = (pd2 / pd1 - 1) * 100
    ok('Segundo contrato: "se fechar" era o Δ real (%.4f%% x %.4f%%)' % (esp2, real2), abs(esp2 - real2) < 0.02, (esp2, real2))
    soma = G(pg, "g.comex.acordos.filter(x=>x.estado=='ativo'&&x.k=='trigo').reduce((s,x)=>s+x.qtd,0)")
    c2 = float(pg.locator('[data-com-sit-contratado]').get_attribute('data-com-sit-contratado'))
    ok('Volume contratado soma os dois contratos (%.2f)' % soma, abs(c2 - soma) < 1e-3 and pg.locator('[data-com-sit-contrato]').count() == 2, (c2, soma))
    it = pg.locator('[data-com-imp=trigo]').inner_text()
    pct = G(pg, "Math.round(g.comex.acordos.filter(x=>x.estado=='ativo'&&x.k=='trigo').reduce((s,x)=>s+x.qtd,0)/__X().IC_IMP.trigo.imp_usd_bi*100)")
    ok('Lista do trigo mostra "%d%% em acordo do governo"' % pct, ('%d%% em acordo do governo' % pct) in it, it.replace('\n', ' '))
    pg.locator('[data-com-sit-cancelar]').first.click(); pg.wait_for_timeout(300)
    mt = pg.locator('[data-com-sit-multa]').inner_text()
    ok('Cancelar mostra a multa em R$ e a piora da relação', re.search(r'Multa de R\$ [\d,]+ bi', mt) and 'piora' in mt, mt)
    pg.locator('[data-com-sit-cancelar-ok]').first.click(); pg.wait_for_timeout(600)
    ok('Confirmar: sobra 1 contrato ativo e há multa registrada', G(pg, "g.comex.acordos.filter(x=>x.estado=='ativo'&&x.k=='trigo').length") == 1 and G(pg, "g.comex.acordos.some(x=>x.estado=='cancelado'&&x.multa>0)"))
    # ---------- Vender ----------
    pg.locator('[data-com-aba=vender]').click(); pg.wait_for_timeout(400)
    itens = pg.locator('[data-com-picker=vender] [data-com-prod]'); n = itens.count()
    sem = [t for t in itens.all_inner_texts() if not (re.search(r'exportamos US\$ [\d.,]+ bi/ano', t) and re.search(r'\d+% da sobra já vendido', t) and re.search(r'preço mundial (US\$ [\d.,]+|índice \d+ \(2025 = 100\))', t))]
    ok('Vender: %d itens com unidade (bi/ano, %% da sobra, preço mundial)' % n, n >= 30 and not sem, sem[:2])
    pg.locator('[data-com-prod=soja_grao]').click(); pg.wait_for_timeout(500)
    sv = pg.locator('[data-com-sit=venda]')
    ok('Vender: situação com produção, sobra para vender e já vendido', all(x in sv.inner_text() for x in ['Produção nacional', 'Sobra para vender', 'Vendido em acordos do governo']), sv.inner_text()[:100].replace('\n', ' '))
    cols = [c.lower() for c in pg.locator('[data-com-vender] .ic-tbl th').all_inner_texts()]
    ok('Vender: coluna do efeito no preço interno por comprador', any('no brasil se fechar' in c for c in cols) and pg.locator('[data-com-se-fechar]').count() >= 5, cols)
    e = float(pg.locator('[data-com-se-fechar=CHN]').get_attribute('data-delta')); p0 = G(pg, 'g.comex.fl.soja_grao.pdom')
    pg.locator('[data-com-propor=CHN]').click(); pg.wait_for_timeout(300)
    lv = pg.locator('[data-com-linha=venda]').inner_text()
    ok('Vender: linha do tempo antes de assinar', 'vale até' in lv and 'começa este mês' in lv, lv)
    pg.locator('[data-com-preco]').fill('100'); pg.locator('[data-com-preco]').blur(); pg.locator('[data-com-enviar]').click(); pg.wait_for_timeout(400)
    if pg.locator('[data-com-fechar]').count():
        pg.locator('[data-com-fechar]').click(); pg.wait_for_timeout(700)
        p1 = G(pg, 'g.comex.fl.soja_grao.pdom'); r = (p1 / p0 - 1) * 100
        ok('Vender: "se fechar" bate com o Δ real (%.4f%% x %.4f%%)' % (e, r), abs(e - r) < 0.02, (e, r))
        c = float(pg.locator('[data-com-sit=venda] [data-com-sit-falta]').get_attribute('data-com-sit-falta'))
        ok('Vender: o volume vendido em contrato aparece (%.2f)' % c, abs(c - G(pg, "g.comex.acordos.filter(x=>x.estado=='ativo'&&x.k=='soja_grao').reduce((s,x)=>s+x.qtd,0)")) < 1e-3)
    else:
        ok('Vender: proposta aceita a 100%% do preço', False)
    SET(pg, "n.comex.props.push({id:'prZ1',pais:'JPN',k:'milho',qtd:1.5,preco:n.comex.idx.milho*1.01,anos:2,mes:n.mes,exp:n.mes+3,grande:true,rodada:0,estado:'aberta'})")
    pg.locator('[data-com-aba=geral]').click(); pg.wait_for_timeout(500)
    pr = pg.locator('[data-com-proposta=prZ1]').inner_text()
    ok('Proposta recebida: vs. preço mundial, sobra, preço no Brasil e linha do tempo', all(x in pr for x in ['preço mundial', 'sobra', 'Preço de milho no Brasil', 'Ao assinar', 'vale até']), pr.replace('\n', ' ')[:300])
    # ---------- Indústria ----------
    secao(pg, 'País'); chip(pg, 'Indústria')
    c0 = pg.locator('[data-ind-prod=soja_grao]').inner_text()
    ok('Indústria: cartão com estoque em meses e preço mundial com tendência', 'meses' in c0 and 'Preço mundial: US$' in c0 and 'em 12 meses' in c0, c0.replace('\n', ' '))
    pg.locator('[data-ind-prod=soja_grao]').click(); pg.wait_for_timeout(700)
    num = pg.locator('[data-ind-numeros]').inner_text()
    ok('Indústria: números com unidade e tooltips', 'por ano' in num and '% do PIB' in num and 'mi t' in num and pg.locator('[data-ind-numeros] [data-gv-tip]').count() >= 4, num.replace('\n', ' ')[:200])
    pg.locator('[data-ind-acao=inv]').click(); pg.locator('[data-ind-bi="5"]').click(); pg.wait_for_timeout(700)
    q = pg.locator('[data-ind-prev-quando]').inner_text(); pr_ = pg.locator('[data-ind-prev-prod]').inner_text(); ex = pg.locator('[data-ind-prev-exp]').inner_text()
    ok('Previsão: custo, quando, produção, exportação, empregos, fiscal e Congresso', all(pg.locator('[data-ind-prev-%s]' % k).count() == 1 for k in ['custo', 'quando', 'prod', 'exp', 'emp', 'fiscal', 'cong']) and re.search(r'em \S{3}/\d\d', q) and '%' in pr_, (q, pr_))
    ok('Previsão: produção sobe com o investimento e traz US$ bi/ano', re.search(r'\+\d', pr_) is not None and 'bi a mais por ano' in pr_ and 'US$' in ex, (pr_, ex))
    pg.locator('[data-ind-vender=soja_grao]').click(); pg.wait_for_timeout(900)
    ok('Atalho "Vender soja" abre Comércio > Vender já na soja', pg.locator('[data-com-produto=soja_grao]').count() == 1 and pg.locator('[data-com-vender]').count() == 1)
    secao(pg, 'País'); chip(pg, 'Indústria')
    pg.evaluate("""()=>{const X=__X();__QV().setG(p=>{const n=structuredClone(p);X.ensureIC(n);const prop=__AL(n,'Investir R$ 5 bilhões na produção de soja em grão');prop.icHook={tipo:'inv',k:'soja_grao',v:5,pct:null};prop.scale=1;X.executaProposta(n,prop,'aprovada');return n})}""")
    pg.wait_for_timeout(800)
    tx = pg.locator('[data-ind-andamento]').inner_text() if pg.locator('[data-ind-andamento]').count() else ''
    ok('Projetos em andamento: "fica pronto em <mês/ano>" e progresso', re.search(r'fica pronto em \S{3}/\d\d \(\d+%\)', tx) is not None, tx[:160])
    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    b.close()
falhas = [n for c, n in checks if not c]
print('\n%d/%d verificações OK' % (len(checks) - len(falhas), len(checks)))
if falhas: print('FALHAS:', falhas)
