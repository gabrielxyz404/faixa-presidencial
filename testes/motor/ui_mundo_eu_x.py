# Teste de interface de Mundo, Eu e X (v2 visual, mesma linguagem do Poder → Governo): faixas-resumo, cartões, uma ação em Eu (agenda privada) e uma em X (filtro e post);
# sem rolagem horizontal em 1440 e 1280, texto mínimo de 12px, selo 'simulado' mantido e 0 erros de página/console.
# uso: python3 run_sandbox.py ui_mundo_eu_x.py <pasta com index.html> <saida_dir> [porta]
import sys, threading, functools, http.server, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8895
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
def vai_governo(pg):
    pg.locator('#sec-tab-poder').click(timeout=6000); pg.wait_for_timeout(500)
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*Governo')).first.click(timeout=6000); pg.wait_for_timeout(700)
def encerra(pg):
    fecha_modais(pg)
    pg.locator('button').filter(has_text=re.compile(r'^\s*Encerrar m')).first.click(timeout=8000); pg.wait_for_timeout(900)
    fecha_modais(pg)
SEED = "(()=>{let a=" + os.environ.get("SEED_N", "20271030") + ";Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
errs = []
ABAS = (('mundo', ['Panorama', 'Países', 'Visitas de Estado', 'Blocos', 'Tratados', 'Mesa diplomática', 'Terras raras']), ('eu', ['Condição', 'Bem-estar e agenda', 'Família e partido', 'Bastidores', 'Conquistas']), ('x', [None]))
def vai(pg, sec, chip=None):
    pg.locator('#sec-tab-' + sec).click(timeout=6000); pg.wait_for_timeout(500)
    if chip: pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*' + re.escape(chip))).first.click(timeout=6000); pg.wait_for_timeout(600)
def minfont(pg):
    return pg.evaluate("()=>{let m=99;document.querySelectorAll('[role=tabpanel] *, main *').forEach(e=>{if(e.children.length===0&&e.textContent.trim()&&e.offsetParent!==null&&!e.closest('.gv-tipbox')&&!e.closest('style,script')){const f=parseFloat(getComputedStyle(e).fontSize);if(f<m)m=f}});return m}")
def sem_rolagem(pg): return pg.evaluate("()=>document.documentElement.scrollWidth<=innerWidth")
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV;\nfunction analisaLegado(g, texto) {', 1)
    pg.add_init_script(SEED)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    encerra(pg); encerra(pg)

    # ---------- Mundo ----------
    vai(pg, 'mundo', 'Panorama')
    ok('Mundo: faixa-resumo com 5 indicadores', pg.locator('[data-gv=mundo-resumo] [data-gv-kpi]').count() == 5, pg.evaluate("()=>[...document.querySelectorAll('[data-gv-kpi]')].map(e=>e.getAttribute('data-gv-kpi'))"))
    ok('Mundo: medidores de sempre (alin, isol, econ)', pg.locator('[data-medidor=alin]').count() == 1 and pg.locator('[data-medidor=isol]').count() == 1 and pg.locator('[data-econ-mundo]').count() == 1)
    ok('Mundo: 6 cartões de relação e 6 missões da agenda externa', pg.locator('[data-rel]').count() == 6 and pg.locator('[data-secao-mundo=agenda] .mx-card').count() == 6, pg.locator('[data-secao-mundo=agenda] .mx-card').count())
    ok('Mundo: dicas "?" no lugar dos parágrafos', pg.locator('[data-gv-tip]').count() >= 3)
    pg.screenshot(path=OUT + '/mundo_panorama.png', full_page=True)
    vai(pg, 'mundo', 'Países')
    ok('Países: um cartão por país, detalhes recolhidos', pg.locator('[data-pais]').count() >= 8 and pg.locator('[data-pais] details[open]').count() == 0, pg.locator('[data-pais]').count())
    vai(pg, 'mundo', 'Visitas de Estado')
    ok('Visitas: destino, chance de acordo e agendar', pg.locator('#viag-pais').count() == 1 and pg.locator('[data-chance]').count() == 1)
    vai(pg, 'mundo', 'Blocos')
    ok('Blocos: cartões de organismos com ações', pg.locator('[data-org]').count() >= 6 and pg.locator('[data-acao-org]').count() >= 6, pg.locator('[data-org]').count())
    vai(pg, 'mundo', 'Tratados')
    ok('Tratados: contador presente', pg.locator('[data-n-tratados]').count() == 1)
    vai(pg, 'mundo', 'Terras raras')
    ok('Terras raras: faixa-resumo e seções de sempre', pg.locator('[data-gv=terras-resumo] [data-gv-kpi]').count() == 5 and pg.locator('[data-tr=cadeia]').count() == 1 and pg.locator('[data-tr=mesa]').count() == 1 and pg.locator('[data-tr=conselho]').count() == 1)
    vai(pg, 'mundo', 'Mesa diplomática')
    ok('Mesa diplomática: opções como cartões', pg.locator('[data-opcao-dip]').count() >= 2, pg.locator('[data-opcao-dip]').count())
    if pg.locator('[data-opcao-dip]:not([disabled])').count():
        pg.locator('[data-opcao-dip]:not([disabled])').first.click(timeout=5000); pg.wait_for_timeout(600)
        ok('Mesa diplomática: decidir resolve a decisão do mês', G(pg, "g.mundo.mesa.resolvida") == True)

    # ---------- Eu ----------
    vai(pg, 'eu', 'Condição')
    ok('Eu: faixa-resumo com 5 indicadores', pg.locator('[data-gv=eu-resumo] [data-gv-kpi]').count() == 5)
    ok('Eu: cartões de condição e efeitos', pg.locator('[data-secao-eu=condicao] .mx-card').count() >= 8 and pg.locator('[data-aprov-pes]').count() == 1 and pg.locator('[data-mult-plenario]').count() == 1 and pg.locator('[data-embalo]').count() == 1, pg.locator('[data-secao-eu=condicao] .mx-card').count())
    pg.screenshot(path=OUT + '/eu_condicao.png', full_page=True)
    vai(pg, 'eu', 'Bem-estar e agenda')
    ok('Eu: agenda privada (data-bem) e articulação (data-art) em cartões', pg.locator('[data-bem]').count() >= 5 and pg.locator('[data-art]').count() >= 4, (pg.locator('[data-bem]').count(), pg.locator('[data-art]').count()))
    c0 = G(pg, "g.pes.conta")
    k = pg.locator('[data-bem]:not([disabled])').first.get_attribute('data-bem')
    pg.locator('[data-bem=%s]' % k).click(timeout=5000); pg.wait_for_timeout(600)
    ok('Eu: atividade de bem-estar marca o mês, cobra da conta e desabilita o cartão', G(pg, "!!g.pesMes['%s']" % k) == True and G(pg, "g.pes.conta") <= c0 and pg.locator('[data-bem=%s][disabled]' % k).count() == 1, (k, c0, G(pg, "g.pes.conta")))
    vai(pg, 'eu', 'Família e partido')
    ok('Eu: família e filiação', pg.locator('[data-secao-eu=familia]').count() == 1 and pg.locator('[data-secao-eu=filiacao]').count() == 1 and pg.locator('[data-partido-opcao]').count() >= 3)
    vai(pg, 'eu', 'Bastidores')
    ok('Eu: bastidores', pg.locator('[data-secao-eu=bastidores]').count() == 1)
    vai(pg, 'eu', 'Conquistas')
    ok('Eu: conquistas em cartões', pg.locator('[data-conq]').count() >= 10, pg.locator('[data-conq]').count())

    # ---------- X ----------
    vai(pg, 'x')
    ok('X: faixa-resumo com 5 indicadores', pg.locator('[data-gv=x-resumo] [data-gv-kpi]').count() == 5)
    ok('X: caixa de postar, filtros e feed', pg.locator('[data-secao=x-postar] textarea').count() == 1 and pg.locator('[data-secao=x-feed] .chipnav button').count() == 5 and pg.locator('[data-secao=x-feed] [data-post]').count() >= 1, pg.locator('[data-secao=x-feed] [data-post]').count())
    ok('X: posts em cartões com avatar e contagens', pg.locator('.x-post .x-av').count() >= 1 and pg.locator('.x-post .x-eng').count() >= 1)
    ok('X: selo "simulado" escrito em todo selo-sim', pg.evaluate("()=>[...document.querySelectorAll('.selo-sim')].every(e=>/simulado/.test(e.innerText))"))
    n_todos = pg.locator('[data-secao=x-feed] .x-post').count()
    pg.locator('[data-secao=x-feed] .chipnav button').filter(has_text='Imprensa').click(timeout=4000); pg.wait_for_timeout(500)
    n_imp = pg.locator('[data-secao=x-feed] .x-post').count()
    ok('X: filtro Imprensa reduz o feed e marca aria-selected', n_imp <= n_todos and pg.locator('[data-secao=x-feed] .chipnav button[aria-selected=true]').filter(has_text='Imprensa').count() == 1, (n_todos, n_imp))
    pg.locator('[data-secao=x-feed] .chipnav button').filter(has_text='Todos').click(timeout=4000); pg.wait_for_timeout(300)
    np0 = G(pg, "g.x.posts.length")
    pg.locator('[data-secao=x-postar] textarea').fill('Trabalhando por um Brasil melhor.'); pg.wait_for_timeout(200)
    pg.locator('[data-secao=x-postar] button').filter(has_text='Postar').click(timeout=5000); pg.wait_for_timeout(700)
    ok('X: postar publica e limpa a caixa', G(pg, "g.x.posts.length") > np0 and pg.locator('[data-secao=x-postar] textarea').input_value() == '', (np0, G(pg, "g.x.posts.length")))
    ok('X: famosos, assuntos, humor, campanha e grupos presentes', all(pg.locator('[data-secao=%s]' % s).count() == 1 for s in ('x-famosos', 'x-assuntos', 'x-humor', 'x-grupos', 'x-campanha')))
    pg.screenshot(path=OUT + '/x_1440.png', full_page=True)

    # ---------- layout em todas as abas ----------
    por_aba = {}
    for sec, chips in ABAS:
        for c in chips:
            vai(pg, sec, c); por_aba[sec + '/' + str(c)] = (sem_rolagem(pg), minfont(pg))
    ok('sem rolagem horizontal em 1440 (todas as abas)', all(v[0] for v in por_aba.values()), [k for k, v in por_aba.items() if not v[0]])
    ok('texto mínimo de 12px (todas as abas)', all(v[1] >= 12 for v in por_aba.values()), {k: v[1] for k, v in por_aba.items() if v[1] < 12})
    pg.set_viewport_size({'width': 1280, 'height': 800}); pg.wait_for_timeout(500)
    r1280 = {}
    for sec, chips in ABAS:
        for c in chips:
            vai(pg, sec, c); r1280[sec + '/' + str(c)] = sem_rolagem(pg)
    ok('sem rolagem horizontal em 1280 (todas as abas)', all(r1280.values()), [k for k, v in r1280.items() if not v])

    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    b.close()
falhas = [n for c, n in checks if not c]
print('\nRESULTADO: %d/%d ok' % (len(checks) - len(falhas), len(checks)), '| falhas:', falhas)
sys.exit(1 if falhas else 0)
