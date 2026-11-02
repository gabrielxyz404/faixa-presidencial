# Teste de interface do painel "Orçamento da área" (País > Educação, Infraestrutura, Saúde e demais abas): investir R$ 5 bi em um alvo e cortar R$ 2 bi
# abrem o parecer com o custo certo (+5 / -2), a prévia aparece antes de confirmar, os controles travam sem ação e há 0 erros de página/console.
# uso: python3 run_sandbox.py ui_orcamento.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8883
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
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*' + nome + r'\s*$')).first.click(timeout=6000); pg.wait_for_timeout(500)
def custo_parecer(pg):
    # lê o custo que o motor calculou para a proposta que abriu o parecer (hook em MOTOR.analisar, instalado antes do envio)
    return pg.evaluate("()=>window.__ULT||null")
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__AL = analisaLocal;\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)

    def abre(nome):
        secao(pg, 'País'); chip(pg, nome); pg.wait_for_timeout(300)

    def pega_parecer(area_sel, desc):
        # o parecer abre num modal; o texto mostra o custo em R$ bi. Também lemos a proposta do motor pelo texto enviado
        pg.wait_for_timeout(2200)
        t = pg.locator('.modal-wrap').first.inner_text() if pg.locator('.modal-wrap').count() else ''
        return t

    def custo_do_texto(txt):
        r = pg.evaluate("(t)=>{const p=__AL(__QV().gRef.current,t);return {cost:p.cost,inst:p.inst,topic:p.topic,vago:!!(p.qualidade||{}).vago}}", txt)
        return r

    def ciclo(chip_nome, area, alvo, modo, bi, esperado):
        abre(chip_nome)
        raiz = pg.locator('[data-orcamento=%s]' % area)
        ok('%s: painel Orçamento da área presente' % chip_nome, raiz.count() == 1)
        raiz.locator('[data-orc-modo=%s]' % modo).click(timeout=5000)
        raiz.locator('[data-orc-alvo=%s]' % alvo).click(timeout=5000)
        raiz.locator('[data-orc-bi="%d"]' % bi).click(timeout=5000); pg.wait_for_timeout(400)
        texto = raiz.locator('[data-orc-texto]').inner_text().strip('“” \n')
        ok('%s: prévia mostra instrumento, despesa e primário antes de confirmar' % chip_nome, raiz.locator('[data-orc-motor]').count() == 1 and raiz.locator('[data-orc-primario]').count() == 1 and raiz.locator('[data-orc-ef]').count() == 1, raiz.locator('[data-orc-motor]').inner_text().replace('\n', ' '))
        r = custo_do_texto(texto)
        ok('%s: motor lê %s %d bi com custo ≈ %+d (%s, %s)' % (chip_nome, modo, bi, esperado, r['inst'], r['cost']), r['cost'] is not None and abs(r['cost'] - esperado) <= 0.35 * abs(esperado) and not r['vago'], texto)
        pg.screenshot(path=OUT + '/orc_%s_%s_%s.png' % (area, alvo, modo), full_page=False)
        a0 = G(pg, 'g.acoes')
        btn = raiz.locator('[data-orc-confirm]')
        ok('%s: botão Confirmar habilitado' % chip_nome, btn.is_enabled(), btn.inner_text())
        btn.click(timeout=5000); pg.wait_for_timeout(2500)
        t = pega_parecer(None, chip_nome)
        ok('%s: o parecer abre (modal com análise da proposta)' % chip_nome, pg.locator('.modal-wrap').count() >= 1 and len(t) > 150, t[:100].replace('\n', ' '))
        m = re.search(r'R\$\s*([\d.,]+)\s*bi', t)
        ok('%s: o parecer cita o valor escolhido (R$ %d bi)' % (chip_nome, bi), bool(re.search(r'R\$\s*%d[,.]?0?\s*bi' % bi, t)) or bool(re.search(r'%d[,.]0 bi|%d bilh' % (bi, bi), t)), (m.group(0) if m else t[:80]))
        rx = (r'Custo anual\s*\n\s*R\$\s*%d[,.]0\s*bi' % bi) if esperado > 0 else (r'(?:Ganho anual|Economia anual)\s*\n\s*R\$\s*%d[,.]0\s*bi' % bi)
        mm = re.search(rx, t)
        ok('%s: o parecer informa custo %+d bi no financiamento' % (chip_nome, esperado), bool(mm), mm.group(0) if mm else re.findall(r'(?:[^\n]*\n){0,2}[^\n]{0,30}R\$ \d,\d bi', t)[:2])
        pg.screenshot(path=OUT + '/orc_%s_%s_parecer.png' % (area, modo))
        fecha_modais(pg)
        return t

    # --- Educação: investir R$ 5 bi nas universidades e IFs
    ciclo('Educação', 'educacao', 'univ', 'inv', 5, 5)
    # --- Infraestrutura: investir R$ 5 bi em ferrovias
    ciclo('Infraestrutura e transportes', 'infra', 'fer', 'inv', 5, 5)
    # --- Saúde: cortar R$ 2 bi em hospitais federais (R$ 2 bi não é preset; usa o campo "outro")
    abre('Saúde')
    raiz = pg.locator('[data-orcamento=saude]')
    raiz.locator('[data-orc-modo=cut]').click(timeout=5000); raiz.locator('[data-orc-alvo=hosp]').click(timeout=5000)
    raiz.locator('[data-orc-outro]').fill('2'); raiz.locator('[data-orc-outro]').blur(); pg.wait_for_timeout(500)
    texto = raiz.locator('[data-orc-texto]').inner_text().strip('“” \n')
    ok('Saúde: texto do corte tem R$ 2 bilhões e hospitais', 'R$ 2 bilhões' in texto and 'hospita' in texto, texto)
    r = custo_do_texto(texto)
    ok('Saúde: motor lê corte de R$ 2 bi com custo ≈ -2 (%s, %s)' % (r['inst'], r['cost']), r['cost'] is not None and abs(r['cost'] + 2) <= .7 and not r['vago'])
    raiz.locator('[data-orc-confirm]').click(timeout=5000); pg.wait_for_timeout(2500)
    t = pega_parecer(None, 'Saúde')
    ok('Saúde: o parecer abre para o corte', pg.locator('.modal-wrap').count() >= 1 and len(t) > 150, t[:100].replace('\n', ' '))
    mm = re.search(r'(?:Ganho anual|Economia anual)\s*\n\s*R\$\s*2[,.]0\s*bi', t)
    ok('Saúde: o parecer informa ganho anual de R$ 2,0 bi (custo -2, corte)', bool(mm), mm.group(0) if mm else re.findall(r'(?:[^\n]*\n){0,2}[^\n]{0,30}R\$ \d,\d bi', t)[:2])
    pg.screenshot(path=OUT + '/orc_saude_cut_parecer.png'); fecha_modais(pg)

    # --- as demais abas têm o painel, com Fontes e notas citando o orçamento
    for nome, area in [('Segurança', 'seguranca'), ('Trabalho', 'trabalho'), ('Sociedade', 'sociedade'), ('Justiça', 'justica'), ('Educação', 'educacao'), ('Saúde', 'saude'), ('Infraestrutura e transportes', 'infra')]:
        abre(nome)
        ok('%s: painel com R$ bi, ajustes, alvos e valores' % nome, pg.locator('[data-orcamento=%s]' % area).count() == 1 and pg.locator('[data-orcamento=%s] [data-orc-alvo]' % area).count() >= 3 and pg.locator('[data-orcamento=%s] [data-orc-num]' % area).count() == 1)
        ok('%s: Fontes e notas cita o orçamento da área' % nome, pg.locator('[data-orc-fonte=%s]' % area).count() == 1 and 'LOA' in pg.locator('[data-orc-fonte=%s]' % area).first.text_content() or area == 'justica' and pg.locator('[data-orc-fonte=justica]').count() == 1)
    # ordem: Educação = KPIs, Orçamento, Programas, mapa, ranking, fontes
    abre('Educação')
    ordem = pg.evaluate("()=>{const r=document.querySelector('[data-pais=educacao]');return [...r.children].map(c=>c.getAttribute('data-orcamento')?'orc':c.getAttribute('data-programas')?'prog':c.getAttribute('data-fontes')?'fontes':c.tagName.toLowerCase())}")
    ok('Educação: ordem KPIs, orçamento, programas antes do mapa', ordem[:3] == ['section', 'orc', 'prog'] and ordem[-1] == 'fontes', ordem)
    ok('Educação: programas mantidos (10 botões)', pg.locator('[data-pais=educacao] button[data-prog]').count() == 10)

    # --- travas: sem ações ou energia baixa
    SET(pg, "n.acoes=0;n.props=0")
    pg.wait_for_timeout(400)
    ok('sem ações: Confirmar desabilitado', pg.locator('[data-orcamento=educacao] [data-orc-confirm]').is_disabled())
    SET(pg, "n.acoes=5;n.props=5;n.pes.energia=5")
    ok('energia baixa: Confirmar desabilitado', pg.locator('[data-orcamento=educacao] [data-orc-confirm]').is_disabled())
    SET(pg, "n.pes.energia=80")
    ok('com ação e energia: Confirmar habilitado', pg.locator('[data-orcamento=educacao] [data-orc-confirm]').is_enabled())
    # Justiça: alvo só-corte desliga Investir
    abre('Justiça')
    pg.locator('[data-orcamento=justica] [data-orc-alvo=jud]').click(timeout=5000); pg.wait_for_timeout(300)
    ok('Justiça: penduricalhos só aceita Cortar (Investir desligado)', pg.locator('[data-orcamento=justica] [data-orc-modo=inv]').is_disabled() and pg.locator('[data-orcamento=justica] [data-orc-confirm]').inner_text().startswith('Cortar'))
    # porcentagem e contingenciamento
    abre('Sociedade')
    r = pg.locator('[data-orcamento=sociedade]')
    r.locator('[data-orc-alvo=bf]').click(timeout=5000); r.locator('[data-orc-pct="5"]').click(timeout=5000); pg.wait_for_timeout(300)
    ok('Sociedade: 5% do Bolsa Família = R$ 8 bi (158,63 × 5%)', 'R$ 8 bilhões' in r.locator('[data-orc-texto]').inner_text(), r.locator('[data-orc-texto]').inner_text())
    abre('Segurança')
    r = pg.locator('[data-orcamento=seguranca]')
    r.locator('[data-orc-modo=cut]').click(timeout=5000); r.locator('[data-orc-alvo=pf]').click(timeout=5000); r.locator('[data-orc-bi="5"]').click(timeout=5000)
    r.locator('[data-orc-cont]').check(timeout=5000); pg.wait_for_timeout(400)
    tx = r.locator('[data-orc-texto]').inner_text()
    ok('Segurança: contingenciamento troca o verbo e o motor lê como decreto', 'Contingenciar' in tx and 'DEC' in r.locator('[data-orc-motor]').inner_text() or 'Decreto' in r.locator('[data-orc-motor]').inner_text(), r.locator('[data-orc-motor]').inner_text().replace('\n', ' '))

    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    b.close()
falhas = [n for c, n in checks if not c]
print('\n%d/%d verificações OK' % (len(checks) - len(falhas), len(checks)))
if falhas: print('FALHAS:', falhas)
