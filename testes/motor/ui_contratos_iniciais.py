# Teste dos acordos reais já ativos (Itaipu e gás da Bolívia), da clareza do 0% contratado, da negociação de contratos
# (renegociar preço, reduzir/aumentar volume, renovar, aviso na Mesa, sem multa) e do novo formato da mudança de preço.
# uso: python3 run_sandbox.py ui_contratos_iniciais.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, re, os
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
def fecha_modais(pg):
    for _ in range(4):
        if pg.locator('.modal-wrap').count() == 0: break
        try: pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^(Fechar|Continuar|OK|Entendi|Seguir|Próximo mês|Voltar à Mesa|Arquivar|Cancelar|Desistir)')).first.click(timeout=1200)
        except Exception: pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
def G(pg, expr): return pg.evaluate("()=>{const g=__QV().gRef.current;return (" + expr + ")}")
def SET(pg, js): pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);const X=__X();" + js + ";return n})"); pg.wait_for_timeout(600)
def J(pg, js):  # roda em um clone do estado, com ensureIC e 9 ações; devolve o que o código retornar
    return pg.evaluate("()=>{const X=__X();const g=structuredClone(__QV().gRef.current);X.ensureIC(g);g.acoes=9;g.pes.energia=90;" + js + "}")
def secao(pg, nome): pg.locator('#sec-tab-' + nome.lower().replace('í', 'i')).click(timeout=6000); pg.wait_for_timeout(500)
def chip(pg, nome):
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*' + nome + r'\s*$')).first.click(timeout=6000); pg.wait_for_timeout(600)
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__X = () => ({ ensureIC, IC_IMP, IC_PAIS, icCancela, icReduz, icAumenta, icRenova, icRenegocia, icAceitaContra, icSimAcPreco, icSemMulta, icMulta, icMultaDe, icVencendo, icPendencias, icPodeRenovar, fimDoMes, pendenciasMesa });\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    SET(pg, "n.acoes=9;n.pes.energia=90")

    # ---------- save novo ----------
    SET(pg, "X.ensureIC(n)")
    ac = G(pg, "g.comex.acordos.filter(a=>a.estado=='ativo')")
    ks = sorted(a['k'] for a in ac)
    ok('Save novo: 2 acordos ativos (Itaipu e gás da Bolívia) com origem "tratado"', len(ac) == 2 and ks == ['energia_eletrica', 'gas_natural'] and all(a['origem'] == 'tratado' and a['real'] and a['est'] for a in ac), ac)
    it = [a for a in ac if a['k'] == 'energia_eletrica'][0]; gs = [a for a in ac if a['k'] == 'gas_natural'][0]
    ok('Itaipu: com o Paraguai, preço fixo, prazo longo; gás: Bolívia, prazo curto (1–2 anos)', it['pais'] == 'PRY' and it['semCancelar'] and it['mFim'] - it['m0'] >= 36 and gs['pais'] == 'BOL' and not gs['semCancelar'] and 12 <= gs['mFim'] - gs['m0'] <= 24, (it, gs))
    pd = G(pg, "[g.comex.fl.gas_natural.pdom, g.comex.fl.energia_eletrica.pdom, g.comex.mac.ipca]")
    ok('Estado inicial sem choque: preço interno do gás e da energia = 1,000 e IPCA do comércio = 0', abs(pd[0] - 1) < 1e-6 and abs(pd[1] - 1) < 1e-6 and abs(pd[2]) < 1e-6, pd)

    # ---------- telas ----------
    secao(pg, 'Mundo'); chip(pg, 'Comércio exterior')
    geral = pg.locator('[data-com-privado]').inner_text()
    ok('Visão geral: linha sobre comércio privado x contratos de governo a governo', 'quase tudo é feito por empresas privadas' in geral and 'governo a governo' in geral, geral)
    pg.locator('[data-com-aba=acordos]').click(); pg.wait_for_timeout(500)
    selos = pg.locator('[data-com-lista-ativos] [data-com-real]')
    ok('Contratos ativos: os 2 acordos aparecem com o selo "acordo real (estimativa de valores)"', selos.count() == 2 and all('acordo real (estimativa de valores)' in t for t in selos.all_inner_texts()), selos.all_inner_texts())
    pg.locator('[data-com-aba=comprar]').click(); pg.wait_for_timeout(400)
    pg.locator('[data-com-imp=gas_natural]').click(); pg.wait_for_timeout(500)
    sit = pg.locator('[data-com-sit=compra]').inner_text()
    pctg = float(pg.locator('[data-com-sit-contratado]').get_attribute('data-com-sit-contratado'))
    ok('Gás: o acordo real conta no "já contratado" e aparece na lista com o selo', pctg > 0.9 and pg.locator('[data-com-sit] [data-com-real]').count() == 1 and 'Bolívia' in sit, (pctg, sit[:200]))
    item = pg.locator('[data-com-imp=gas_natural]').inner_text()
    m = re.search(r'(\d+)% em acordo do governo', item)
    ok('Lista do gás mostra a % já contratada (> 0)', m and int(m.group(1)) >= 20, item.replace('\n', ' '))
    ok('Preço interno em palavras (sem "−2,6%" solto)', re.search(r'(\d+,\d+% mais (barato|caro) que em 2025|nível de 2025)', pg.locator('[data-com-sit-interno]').inner_text()), pg.locator('[data-com-sit-interno]').inner_text())
    # produto sem contrato: texto de 0%
    pg.locator('[data-com-imp=trigo]').click(); pg.wait_for_timeout(500)
    z = pg.locator('[data-com-sit-zero]')
    ok('Produto sem contrato (trigo): texto do 0% contratado', z.count() == 1 and '0% em acordo do governo: tudo é comprado por empresas privadas no mercado, ao preço do dia. Contratos de governo são opcionais: fixam preço e volume, mas prendem o Brasil.' in z.inner_text().replace('\n', ' '), z.inner_text() if z.count() else '')
    ok('Barra: rótulo "mercado (empresas, preço do dia)"', 'mercado (empresas, preço do dia)' in pg.locator('[data-com-sit=compra] .ic-leg').inner_text(), pg.locator('[data-com-sit=compra] .ic-leg').inner_text())
    pg.screenshot(path=OUT + '/trigo.png')
    # coluna "se fechar": novo formato
    cel = pg.locator('[data-com-se-fechar=ARG]'); tx = cel.inner_text().strip(); tt = cel.get_attribute('title') or ''
    ok('Coluna "se fechar": só "↓ cai X%" / "↑ sobe X%" e o detalhe no title', re.fullmatch(r'(↓ cai|↑ sobe) \d+,\d+%|≈ sem mudança', tx) and re.search(r'hoje [+\-−]?[\d,]+% vs\. 2025 → depois [+\-−]?[\d,]+% vs\. 2025', tt), (tx, tt))
    pg.locator('[data-com-comprar-de=ARG]').click(); pg.wait_for_timeout(400)
    lin = pg.locator('[data-com-linha=compra]').inner_text()
    ok('Linha do tempo: "cai X% (fica Y% abaixo/acima do nível de 2025)"', re.search(r'preço de trigo no Brasil: (cai|sobe) [\d,]+% \(fica [\d,]+% (abaixo|acima) do nível de 2025\)', lin), lin)

    # ---------- Itaipu: não cancela nem reduz ----------
    pg.locator('[data-com-imp=energia_eletrica]').click(); pg.wait_for_timeout(500)
    iid = it['id']
    ok('Itaipu: sem botões de reduzir/aumentar volume', pg.locator('[data-com-neg-reduz=%s]' % iid).count() == 0 and pg.locator('[data-com-neg-aumenta=%s]' % iid).count() == 0 and pg.locator('[data-com-neg-preco=%s]' % iid).count() == 1)
    pg.locator('[data-com-sit-cancelar=%s]' % iid).click(); pg.wait_for_timeout(300)
    msg = pg.locator('[data-com-sit-tratado]').inner_text()
    ok('Itaipu: Cancelar mostra "Tratado internacional: não pode ser cancelado, só renegociado (Anexo C)"', msg.strip() == 'Tratado internacional: não pode ser cancelado, só renegociado (Anexo C)', msg)
    ok('Itaipu: o botão de confirmar cancelamento não existe e o contrato segue ativo', pg.locator('[data-com-sit-cancelar-ok]').count() == 0 and G(pg, "g.comex.acordos.find(a=>a.id=='%s').estado" % iid) == 'ativo')
    r = J(pg, "const a=g.comex.acordos.find(x=>x.k=='energia_eletrica');return [X.icCancela(g,a.id), X.icReduz(g,a.id,.5), X.icAumenta(g,a.id,.5), a.estado, a.qtd]")
    ok('Itaipu: icCancela, icReduz e icAumenta recusam (null) e nada muda', r[0] is None and r[1] is None and r[2] is None and r[3] == 'ativo' and abs(r[4] - it['qtd']) < 1e-9, r)

    # ---------- gás: cancela com multa ----------
    pg.locator('[data-com-imp=gas_natural]').click(); pg.wait_for_timeout(500)
    gid = gs['id']
    pg.locator('[data-com-sit-cancelar=%s]' % gid).click(); pg.wait_for_timeout(300)
    mt = pg.locator('[data-com-sit-multa]').inner_text()
    ok('Gás: Cancelar mostra multa em R$ e piora da relação', re.search(r'Multa de R\$ [\d,]+ bi', mt) and 'piora' in mt, mt)
    pg.screenshot(path=OUT + '/gas_cancelar.png')
    pg.locator('[data-com-sit-cancelar-ok=%s]' % gid).click(); pg.wait_for_timeout(700)
    g2 = G(pg, "g.comex.acordos.find(a=>a.id=='%s')" % gid)
    ok('Gás: cancelado com multa registrada', g2['estado'] == 'cancelado' and g2['multa'] > 0, g2)

    # ---------- save antigo: migra ----------
    SET(pg, "delete n.comex.iniAc;n.comex.acordos=n.comex.acordos.filter(a=>a.origem!='tratado');for(const c of ['idx','est','cut','scar','hist','fl'])delete n.comex[c].energia_eletrica;X.ensureIC(n)")
    ac2 = G(pg, "g.comex.acordos.filter(a=>a.estado=='ativo'&&a.origem=='tratado').map(a=>a.k).sort()")
    ok('Save antigo sem os acordos (e sem o mercado de energia): migra e recebe os 2 acordos', ac2 == ['energia_eletrica', 'gas_natural'] and G(pg, "g.comex.fl.energia_eletrica.pdom") > 0, ac2)
    SET(pg, "X.ensureIC(n)")
    ok('Migração acontece uma vez só (não duplica)', G(pg, "g.comex.acordos.filter(a=>a.origem=='tratado'&&a.estado=='ativo').length") == 2)

    # ---------- negociar: preço ----------
    base = "const a=g.comex.acordos.find(x=>x.k=='gas_natural'&&x.estado=='ativo');const p0=a.preco;const ac0=g.acoes;"
    r = J(pg, base + "const R=X.icRenegocia(g,a.id,95,0);return [R.res,a.preco/p0,ac0-g.acoes]")
    ok('Renegociar: aceita (sorteio baixo) leva o preço a 95% e custa 1 ação', r[0] == 'aceita' and abs(r[1] - .95) < .002 and r[2] == 1, r)
    r = J(pg, base + "const R=X.icRenegocia(g,a.id,95,.999);return [R.res,a.preco/p0,ac0-g.acoes,a.estado]")
    ok('Renegociar: recusa (sorteio alto) não muda o preço, custa 1 ação e não cobra multa', r[0] == 'recusa' and abs(r[1] - 1) < 1e-9 and r[2] == 1 and r[3] == 'ativo', r)
    r = J(pg, base + "const Q=g.comex; const R=X.icRenegocia(g,a.id,95,.60);const n1=a.neg&&a.neg.pct;const ac1=g.acoes;const R2=X.icAceitaContra(g,a.id);return [R.res,n1,a.preco/p0,ac1==g.acoes,a.neg]")
    ok('Renegociar: contraproposta no meio do caminho; aceitar não custa ação', r[0] == 'contra' and abs(r[1] - 97.5) < .11 and abs(r[2] - .975) < .002 and r[3] and r[4] is None, r)
    r = J(pg, base + "const c=X.IC_PAIS.BOL; g.comex.rel.BOL=-30; const rel0=g.comex.rel.BOL; const R=X.icRenegocia(g,a.id,90,.999);return [R.res,rel0,g.comex.rel.BOL, (g.mundo&&g.mundo.pais)?1:0]")
    ok('Pedir muito desconto com relação fria piora a relação (−1 a −3)', r[0] == 'recusa' and (r[2] - r[1]) <= -1 and (r[2] - r[1]) >= -3.01, r)
    r = J(pg, base + "const S=X.icSimAcPreco(g,a,{preco:p0*.95});X.icRenegocia(g,a.id,95,0);const F=g.comex.fl.gas_natural;return [S.d,(F.pdom/S.F0.pdom-1)*100]")
    ok('Renegociar: a prévia (contrato alterado + icFlow) bate com o Δ real do preço interno', abs(r[0] - r[1]) < .001, r)

    # ---------- negociar: reduzir volume ----------
    r = J(pg, base + "a.qtd=4;a.preco=.9;a.mFim=g.mes+24;const m1=X.icMultaDe(g,a,1),m25=X.icMultaDe(g,a,.25),m50=X.icMultaDe(g,a,.5);const f0=g.fiscal.extra;const q0=a.qtd;const S=X.icSimAcPreco(g,a,{qtd:q0*.5});const pd0=g.comex.fl.gas_natural.pdom;const R=X.icReduz(g,a.id,.5);return [m1,m25,m50,a.qtd/q0,(g.fiscal.extra-f0)/g.eco.dol,R.multa,S.d,(g.comex.fl.gas_natural.pdom/pd0-1)*100]")
    ok('Reduzir 50%%: multa proporcional (cancelar %.3f; 25%% %.3f; 50%% %.3f), cobrada só sobre o cortado' % (r[0], r[1], r[2]), abs(r[2] - r[0] * .5) < 1e-6 and abs(r[1] - r[0] * .25) < 1e-6 and abs(r[3] - .5) < 1e-6 and abs(r[4] - r[2]) < 1e-6 and abs(r[5] - r[2]) < 1e-6, r)
    ok('Reduzir: a prévia bate com o Δ real do preço interno', abs(r[6] - r[7]) < .001, (r[6], r[7]))
    # ---------- aumentar ----------
    r = J(pg, base + "const q0=a.qtd;const S=X.icSimAcPreco(g,a,{qtd:q0*1.5,preco:p0*(1+(.04-Math.max(0,Math.min(100,(g.comex.rel.BOL!=null?g.comex.rel.BOL:10)))/2500))});const pd0=g.comex.fl.gas_natural.pdom;X.icAumenta(g,a.id,.5);return [a.qtd/q0,a.preco/p0,ac0-g.acoes,(g.comex.fl.gas_natural.pdom/pd0-1)*100,S.d]")
    ok('Aumentar volume +50%%: o volume muda, o preço sobe de 0 a 4%% e custa 1 ação (preço ×%.4f)' % r[1], abs(r[0] - 1.5) < 1e-3 and 1 <= r[1] <= 1.0401 and r[2] == 1, r)
    ok('Aumentar: a prévia bate com o Δ real do preço interno', abs(r[3] - r[4]) < .02, (r[3], r[4]))

    # ---------- renovar ----------
    r = J(pg, base + "const a0=a.mFim-g.mes;return [X.icPodeRenovar(g,a), X.icRenova(g,a.id,2)===null, a0]")
    ok('Renovar: com mais de 6 meses faltando não é possível', r[0] is False and r[1] is True, r)
    r = J(pg, base + "a.mFim=g.mes+6;const m0=a.mFim;const ok6=X.icPodeRenovar(g,a);a.mFim=g.mes+7;const ok7=X.icPodeRenovar(g,a);a.mFim=g.mes+6;X.icRenova(g,a.id,2);return [ok6,ok7,a.mFim-m0,a.renovado,ac0-g.acoes,a.estado]")
    ok('Renovar: só nos últimos 6 meses; estende o mFim em 24 meses e custa 1 ação', r[0] is True and r[1] is False and r[2] == 24 and r[3] == 1 and r[4] == 1 and r[5] == 'ativo', r)
    SET(pg, "const a=n.comex.acordos.find(x=>x.k=='gas_natural'&&x.estado=='ativo');if(a)a.mFim=n.mes+5;n.acoes=9")
    # a tela: botão Renovar e painel
    pg.locator('[data-com-aba=comprar]').click(); pg.wait_for_timeout(300); pg.locator('[data-com-imp=gas_natural]').click(); pg.wait_for_timeout(500)
    gid2 = G(pg, "g.comex.acordos.find(x=>x.k=='gas_natural'&&x.estado=='ativo').id")
    ok('Tela: botão "Renovar (1, 2 ou 4 anos)" aparece nos últimos 6 meses', pg.locator('[data-com-neg-renova=%s]' % gid2).count() == 1)
    pg.locator('[data-com-neg-renova=%s]' % gid2).click(); pg.wait_for_timeout(300)
    pg.locator('[data-com-neg-anos="4"]').click(); pg.wait_for_timeout(200)
    fimN = G(pg, "g.comex.acordos.find(x=>x.k=='gas_natural'&&x.estado=='ativo').mFim")
    ok('Tela: renovar mostra o novo preço, o novo fim e a prévia em "cai/sobe"', 'terminar em' in pg.locator('[data-com-neg-renova-txt]').inner_text() and re.search(r'(cai|sobe) [\d,]+%|sem mudança', pg.locator('[data-com-neg-painel=renova]').inner_text()), pg.locator('[data-com-neg-painel=renova]').inner_text().replace('\n', ' '))
    pg.screenshot(path=OUT + '/gas_renovar.png')
    pg.locator('[data-com-neg-renova-ok=%s]' % gid2).click(); pg.wait_for_timeout(700)
    ok('Tela: renovar por 4 anos estende o mFim em 48 meses', G(pg, "g.comex.acordos.find(x=>x.k=='gas_natural'&&x.estado=='ativo').mFim") == fimN + 48, (fimN, G(pg, "g.comex.acordos.find(x=>x.k=='gas_natural'&&x.estado=='ativo').mFim")))
    # tela: renegociar com mensagem de resultado
    pg.locator('[data-com-neg-preco=%s]' % gid2).click(); pg.wait_for_timeout(300)
    ok('Tela: renegociar mostra chance de aceite e prévia', 'chance de' in pg.locator('[data-com-neg-chance]').inner_text() and pg.locator('[data-com-neg-previa]').count() == 1)
    pg.locator('[data-com-neg-propor=%s]' % gid2).click(); pg.wait_for_timeout(700)
    resn = pg.locator('[data-com-neg-res], [data-com-neg-contra]')
    ok('Tela: após propor aparece aceite, contraproposta ou recusa', resn.count() >= 1, resn.all_inner_texts())

    # ---------- aviso na Mesa 3 meses antes ----------
    r = J(pg, base + "const out=[];for(const r of [5,4,3,2,1]){a.mFim=g.mes+r;out.push(X.icPendencias(g).filter(p=>p.id=='comfim-'+a.id).length)};a.mFim=g.mes+3;const P=X.icPendencias(g).find(p=>p.id=='comfim-'+a.id);return [out,P&&P.titulo,P&&P.tipo,P&&P.abrir]")
    ok('Aviso: só aparece com 3 meses ou menos para o fim (5,4 -> 0; 3,2,1 -> 1)', r[0] == [0, 0, 1, 1, 1], r[0])
    ok('Aviso: "Contrato de <produto> com <país> termina em <mês/ano>: renovar, renegociar ou deixar acabar?"', re.fullmatch(r'Contrato de gás natural com Bolívia termina em \S{3}/\d\d: renovar, renegociar ou deixar acabar\?', r[1] or ''), r[1])
    ok('Aviso: tipo "comercio" (chip Comércio na seção Mundo)', r[2] == 'comercio' and r[3] == 'comercio')
    SET(pg, "const a=n.comex.acordos.find(x=>x.k=='gas_natural'&&x.estado=='ativo');a.mFim=n.mes+3")
    pg.locator('#sec-tab-mesa').click(timeout=6000); pg.wait_for_timeout(800)
    txt = pg.locator('body').inner_text()
    ok('Mesa > Precisa de você: o cartão do contrato aparece', 'termina em' in txt and 'renovar, renegociar ou deixar acabar?' in txt, re.findall(r'Contrato de [^\n]*', txt)[:2])
    pg.screenshot(path=OUT + '/mesa_aviso.png')
    SET(pg, "const a=n.comex.acordos.find(x=>x.k=='gas_natural'&&x.estado=='ativo');a.mFim=n.mes+4")
    pg.wait_for_timeout(300)
    ok('Mesa: com 4 meses faltando, o cartão não aparece', 'renovar, renegociar ou deixar acabar?' not in pg.locator('body').inner_text())

    # ---------- fim do prazo ----------
    r = J(pg, "const a=g.comex.acordos.find(x=>x.k=='gas_natural'&&x.estado=='ativo');a.mFim=g.mes;X.fimDoMes(g);return [a.estado, g.comex.news.map(n=>n.txt), g.mes]")
    ok('Fim do prazo do gás: notícia "O contrato do gás boliviano terminou: o Brasil volta a comprar no mercado"', r[0] == 'encerrado' and any('O contrato do gás boliviano terminou: o Brasil volta a comprar no mercado' in t for t in r[1]), r)

    # ---------- sem multa por sanção / relação fria ----------
    r = J(pg, base + "const m0=X.icMulta(g,a);g.mundo.sanc=g.mundo.sanc||[];const s0=X.icSemMulta(g,a);g.comex.rel.BOL=-60;const mot=X.icSemMulta(g,a);const m1=X.icMulta(g,a);const f0=g.fiscal.extra;X.icCancela(g,a.id);return [m0>0,s0,mot,m1,g.fiscal.extra-f0,a.estado,a.semMultaPor]")
    ok('Sem multa: relação muito fria permite romper sem multa, mostrando o motivo', r[0] and r[1] is None and r[2] and 'fria' in r[2] and r[3] == 0 and r[4] == 0 and r[5] == 'cancelado' and r[6], r)
    r = J(pg, "const a=g.comex.acordos.find(x=>x.k=='gas_natural'&&x.estado=='ativo');a.pais='USA';g.mundo.sanc.push({ev:'tarifa_eua',pais:'EUA',nome:'sobretaxa de 25% dos EUA (Seção 301)',ate:g.mes+6});return [X.icSemMulta(g,a),X.icMulta(g,a)]")
    ok('Sem multa: sanção/tarifa do país (EUA) também libera, com o motivo', r[0] and 'sanção' in r[0] and r[1] == 0, r)

    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    b.close()
falhas = [n for c, n in checks if not c]
print('%d/%d verificações OK' % (len(checks) - len(falhas), len(checks)))
if falhas: print('FALHAS:', falhas); sys.exit(1)
