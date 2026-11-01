# Teste de interface das abas do País com ações: Educação, Infraestrutura e transportes (fundidas) e Justiça.
# Confere KPIs, programas federais (botões que mandam a proposta ao motor: abre o parecer), conversa com governador, ranking, fontes,
# Justiça com casos desde o começo e a seção "Ações do governo", save antigo (sem g.jus; chip 'transportes') e 0 erros de página/console.
# uso: python3 run_sandbox.py ui_pais_abas.py <pasta com index.html> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8883
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
checks = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:220]) if det != '' else ''), flush=True)
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
        try: pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^(Fechar|Continuar|OK|Entendi|Seguir|Próximo mês|Voltar à Mesa|Arquivar|Cancelar|Voltar)')).first.click(timeout=1200)
        except Exception: pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
def G(pg, expr): return pg.evaluate("()=>{const g=__QV().gRef.current;return (" + expr + ")}")
def SET(pg, js): pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);" + js + ";return n})"); pg.wait_for_timeout(500)
def secao(pg, nome): pg.locator('#sec-tab-' + nome.lower().replace('í', 'i')).click(timeout=6000); pg.wait_for_timeout(500)
def chip(pg, nome):
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*' + nome + r'\s*$')).first.click(timeout=6000); pg.wait_for_timeout(600)
def modal(pg): return pg.evaluate("()=>{const e=document.querySelector('.modal-wrap');return e?e.innerText:''}")
def clica_programa(pg, dp, rotulo, nome):
    fecha_modais(pg)
    a0 = G(pg, "g.acoes")
    pg.locator('[data-pais=%s] button[data-prog]' % dp).filter(has_text=rotulo).first.click(timeout=6000); pg.wait_for_timeout(2200)
    t = modal(pg)
    ok('%s: o programa manda a proposta ao motor (abre o parecer)' % nome, len(t) > 150 and pg.locator('.modal-wrap').count() >= 1, t[:90].replace('\n', ' '))
    fecha_modais(pg)
    return t
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__P = () => ({ ensureJus, migraSave, jusAbertos, CHIPS });\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    secao(pg, 'País')
    nomes = pg.evaluate("()=>[...document.querySelectorAll('.chipnav [role=tab]')].map(e=>e.innerText.trim())")
    ok('chips do País: Transportes some e Infraestrutura vira "Infraestrutura e transportes"', 'Transportes' not in nomes and 'Infraestrutura e transportes' in nomes and 'Educação' in nomes and 'Justiça' in nomes, nomes)

    # ---------- Educação ----------
    chip(pg, 'Educação')
    ok('Educação abre', pg.locator('[data-pais=educacao]').count() == 1)
    ok('Educação: KPIs nacionais (5 do Ideb/IBGE + tempo integral)', pg.locator('[data-pais=educacao] [data-kpi]').count() >= 6, pg.locator('[data-pais=educacao] [data-kpi]').count())
    t = pg.locator('[data-pais=educacao]').inner_text()
    tl = t.lower()
    ok('Educação: Ideb, analfabetismo e superior completo nos KPIs', all(x in tl for x in ['ideb anos iniciais', 'analfabetismo', 'superior completo']))
    ok('Educação: tempo integral 25,8% com fonte INEP', '25,8' in t and 'matrículas em tempo integral' in tl)
    ok('Educação: 10 programas federais', pg.locator('[data-pais=educacao] button[data-prog]').count() == 10, pg.locator('[data-pais=educacao] button[data-prog]').count())
    ok('Educação: mapa por estado, conversa com governador, ranking e fontes', pg.locator('[data-puf=educacao]').count() == 1 and pg.locator('[data-conv=edu]').count() == 1 and pg.locator('[data-rank-uf]').count() >= 2 and pg.locator('[data-fontes=educacao]').count() == 1)
    pg.screenshot(path=OUT + '/educacao.png', full_page=True)
    # conversa com governador: tema, apoio federal, o indicador do estado passa a derivar
    a0 = G(pg, "g.acoes")
    pg.locator('[data-conv=edu] [data-conv-tema=alfa]').click(timeout=5000); pg.wait_for_timeout(500)
    ok('Educação: conversa gasta 1 ação e mostra a fala simulada', G(pg, "g.acoes") == a0 - 1 and pg.locator('[data-conv=edu] [data-conv-fala]').count() == 1)
    pg.locator('[data-conv=edu] [data-conv-resp=apoio]').click(timeout=5000); pg.wait_for_timeout(500)
    ok('Educação: apoio federal registra a deriva no indicador do estado', G(pg, "g.conv.dr.filter(d=>d.area==='edu').length") == 1)
    clica_programa(pg, 'educacao', 'Pé-de-Meia', 'Educação')

    # ---------- Infraestrutura e transportes ----------
    chip(pg, 'Infraestrutura e transportes')
    ok('Infraestrutura e transportes abre', pg.locator('[data-pais=infraestrutura]').count() == 1)
    t = pg.locator('[data-pais=infraestrutura]').inner_text()
    tl = t.lower()
    ok('Infra: KPIs de rodovias, mortes, internet, água, esgoto e energia', all(x.lower() in tl for x in ['Rodovias em estado geral', 'Mortes no trânsito', 'Domicílios com utilização de internet', 'Água por rede geral', 'Esgoto por rede coletora', 'energia pela rede geral', 'Extensão pavimentada']), pg.locator('[data-pais=infraestrutura] [data-kpi]').count())
    ok('Infra: pelo menos 7 KPIs e rodovias ótimo/bom é o primeiro', pg.locator('[data-pais=infraestrutura] [data-kpi]').count() >= 7 and 'rodovias em estado geral' in pg.locator('[data-pais=infraestrutura] [data-kpi]').first.inner_text().lower())
    ok('Infra: o indicador padrão do mapa é rodovias ótimo/bom', 'rodovias em estado geral' in pg.locator('[data-puf=infratransp] [data-puf-painel]').inner_text().lower())
    ok('Infra: os indicadores de transportes e infra estão no mesmo seletor', pg.locator('[data-puf-inds] button').count() >= 4, pg.locator('[data-puf-inds] button').count())
    ok('Infra: 12 a 15 programas em 4 grupos, com "Rodovias" e "Ferrovias, portos e mobilidade"', pg.locator('[data-pais=infraestrutura] button[data-prog]').count() >= 12 and all(x.lower() in tl for x in ['Saneamento e moradia', 'Energia e comunicações', 'Rodovias', 'Ferrovias, portos e mobilidade']), pg.locator('[data-pais=infraestrutura] button[data-prog]').count())
    ok('Infra: conversa, ranking e um bloco de fontes', pg.locator('[data-conv=infra]').count() == 1 and pg.locator('[data-fontes=infratransp]').count() == 1 and pg.locator('[data-rank-uf]').count() >= 2)
    pg.locator('[data-fontes=infratransp] summary').click(); pg.wait_for_timeout(300)
    ft = pg.locator('[data-fontes=infratransp]').inner_text()
    ok('Infra: Fontes e notas cita SINISA, CNT, IBGE e DataSUS', all(x in ft for x in ['SINISA', 'CNT', 'IBGE', 'DataSUS']))
    pg.screenshot(path=OUT + '/infra.png', full_page=True)
    pg.locator('[data-conv=infra] [data-conv-tema=rod]').click(timeout=5000); pg.wait_for_timeout(400)
    ok('Infra: conversa sobre rodovias mostra a fala', pg.locator('[data-conv=infra] [data-conv-fala]').count() == 1)
    clica_programa(pg, 'infraestrutura', 'Duplicar trechos de BRs', 'Infra (rodovias)')
    SET(pg, "n.acoes=5")
    clica_programa(pg, 'infraestrutura', 'Minha Casa Minha Vida', 'Infra (moradia)')

    # ---------- Justiça ----------
    SET(pg, "n.acoes=5")
    chip(pg, 'Justiça')
    ok('Justiça: 1 ou 2 casos abertos desde o começo da partida', 1 <= pg.locator('[data-pais=justica] [data-caso]').count() <= 2, pg.locator('[data-pais=justica] [data-caso]').count())
    ok('Justiça: os casos iniciais têm alvo genérico (cargo + partido, sem estado)', G(pg, "g.jus.casos.every(c=>!/\\b(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\\b/.test(c.alvo) && !c.gov)"), G(pg, "g.jus.casos.map(c=>c.alvo).join('; ')"))
    ok('Justiça: ações do caso visíveis desde o começo', pg.locator('[data-pais=justica] [data-caso] [data-jus-acao]').count() >= 3)
    ok('Justiça: seção "Ações do governo" com 10 botões', pg.locator('[data-jus=acoes-gov] button[data-prog]').count() == 10 and 'ações do governo' in pg.locator('[data-jus=acoes-gov]').inner_text().lower())
    pg.screenshot(path=OUT + '/justica.png', full_page=True)
    clica_programa(pg, 'justica', 'cargos na PF', 'Justiça')
    SET(pg, "n.acoes=5")
    clica_programa(pg, 'justica', 'Cortar penduricalhos', 'Justiça (PLP)')
    # sem casos abertos: explicação com dica
    SET(pg, "n.jus.casos=[]")
    t = pg.locator('[data-pais=justica]').inner_text()
    ok('Justiça sem casos: mostra explicação com dica', 'Nenhuma investigação aberta agora' in t and 'ações acima' in t)
    # ---------- saves antigos ----------
    SET(pg, "delete n.jus")
    ok('save antigo sem g.jus: Justiça abre sem casos forçados e com Ações do governo', 'Nenhuma investigação aberta agora' in pg.locator('[data-pais=justica]').inner_text() and pg.locator('[data-jus=acoes-gov]').count() == 1)
    ok('migraSave não força casos em save antigo', pg.evaluate("()=>{const g=structuredClone(__QV().gRef.current);delete g.jus;__P().migraSave(g);return !g.jus||g.jus.casos.length===0}"))
    SET(pg, "n.ui=n.ui||{};n.ui.chip=n.ui.chip||{};n.ui.chip.pais='transportes'")
    secao(pg, 'Mesa'); secao(pg, 'País'); pg.wait_for_timeout(500)
    ok('save antigo com chip "transportes" abre a aba fundida', pg.locator('[data-pais=infraestrutura]').count() == 1, pg.locator('[data-pais]').count())
    # painéis por estado antigos ainda funcionam e o jogo avança
    for _ in range(2):
        fecha_modais(pg)
        pg.locator('button').filter(has_text=re.compile(r'^\s*Encerrar m')).first.click(timeout=8000); pg.wait_for_timeout(900); fecha_modais(pg)
    secao(pg, 'País'); chip(pg, 'Educação'); chip(pg, 'Infraestrutura e transportes'); chip(pg, 'Justiça')
    ok('depois de fechar meses as 3 abas seguem abrindo', pg.locator('[data-pais=justica]').count() == 1)
    print('ERRS', errs[:8])
    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    print('RESUMO: %d ok, %d falhas' % (sum(1 for c in checks if c[0]), sum(1 for c in checks if not c[0])))
    b.close()
