# Teste de interface do País v2 (mesma linguagem do Poder → Governo): abre todas as sub-abas, confere a faixa de 5 indicadores,
# os cartões, "Fontes e notas" recolhidas, os "?" de ajuda, a ausência de rolagem horizontal em 1440 e 1280 e o clique em um cartão de programa.
# uso: python3 run_sandbox.py ui_pais_v2.py <pasta com index.html> <saida_dir> [porta]
import sys, threading, functools, http.server, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8887
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
checks = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:200]) if det != '' else ''), flush=True)
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
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*' + nome + r'\s*$')).first.click(timeout=6000); pg.wait_for_timeout(700)
ABAS = [('Mapa', 'mapa'), ('Economia', 'economia'), ('Segurança', 'seguranca'), ('Saúde', 'saude'), ('Educação', 'educacao'), ('Trabalho', 'trabalho'),
        ('Infraestrutura e transportes', 'infraestrutura'), ('Sociedade', 'sociedade'), ('Justiça', 'justica')]
JS_FONTE_MIN = "()=>{let n=0;const out=[];for(const e of document.querySelectorAll('main *, [role=tabpanel] *')){if(!e.childNodes.length||e instanceof SVGElement)continue;let t=false;for(const c of e.childNodes)if(c.nodeType===3&&c.textContent.trim())t=true;if(!t)continue;const cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden')continue;const r=e.getBoundingClientRect();if(!r.width||!r.height)continue;if(parseFloat(cs.fontSize)<11.9){n++;if(out.length<5)out.push(e.className+':'+cs.fontSize+':'+e.textContent.trim().slice(0,20))}}return [n,out]}"
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV;\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    secao(pg, 'País')
    for nome, dp in ABAS:
        chip(pg, nome)
        raiz = pg.locator('[data-pais=%s]' % dp)
        ok('%s: a aba abre' % nome, raiz.count() >= 1 or pg.locator('[data-pd-area=%s]' % dp).count() >= 1, pg.locator('[data-pais]').count())
        faixa = pg.locator('[data-pd=resumo][data-pd-area] .gv-kpi')
        ok('%s: faixa com 5 indicadores' % nome, faixa.count() == 5, faixa.count())
        ic = pg.evaluate("()=>[...document.querySelectorAll('[data-pd=resumo] .gv-kpi')].every(k=>k.querySelector('.gv-ic svg')&&k.querySelector('.gv-kpi-k')&&k.querySelector('.gv-kpi-v')&&k.querySelector('.gv-kpi-s'))")
        ok('%s: cada indicador tem ícone, rótulo, número e legenda' % nome, ic)
        cards = pg.locator('.mx-card, .pd-card, .mx-act').count()
        ok('%s: tem cartões' % nome, cards >= 3, cards)
        ok('%s: blocos com "?" de ajuda' % nome, pg.locator('.gv-sec-h .gv-tip').count() >= 1, pg.locator('.gv-sec-h .gv-tip').count())
        fontes = pg.locator('details[data-fontes], footer[data-rodape-fontes] details')
        if fontes.count():
            ok('%s: "Fontes e notas" recolhidas' % nome, pg.evaluate("()=>[...document.querySelectorAll('details[data-fontes], footer[data-rodape-fontes] details')].every(d=>!d.open)"))
        ok('%s: sem rolagem horizontal em 1440' % nome, not pg.evaluate("()=>document.documentElement.scrollWidth>document.documentElement.clientWidth"))
        if os.path.exists(ROOT + '/tw.css'):  # só faz sentido com o Tailwind compilado (pasta "styled")
            fm = pg.evaluate(JS_FONTE_MIN)
            ok('%s: texto visível com pelo menos 12px' % nome, fm[0] == 0, fm)
        pg.screenshot(path=OUT + '/pais_v2_%s.png' % dp, full_page=True)
    pg.set_viewport_size({'width': 1280, 'height': 800})
    for nome, dp in ABAS:
        chip(pg, nome)
        ok('%s: sem rolagem horizontal em 1280' % nome, not pg.evaluate("()=>document.documentElement.scrollWidth>document.documentElement.clientWidth"))
    pg.set_viewport_size({'width': 1440, 'height': 900})
    # cartões de programa: Saúde, Segurança e Justiça
    SET(pg, "n.acoes=5;n.props=5"); fecha_modais(pg)
    chip(pg, 'Saúde')
    ok('Saúde: programas viram cartões (botões data-prog)', pg.locator('[data-pais=saude] button.mx-act[data-prog=saude]').count() == 6, pg.locator('[data-pais=saude] button[data-prog]').count())
    a0 = G(pg, 'g.acoes')
    pg.locator('[data-pais=saude] button.mx-act[data-prog=saude]').filter(has_text='Farmácia Popular').first.click(timeout=6000); pg.wait_for_timeout(2200)
    t = pg.evaluate("()=>{const e=document.querySelector('.modal-wrap');return e?e.innerText:''}")
    ok('Saúde: clicar no cartão manda a proposta ao motor (abre o parecer)', len(t) > 150, t[:80].replace('\n', ' '))
    fecha_modais(pg)
    chip(pg, 'Justiça')
    ok('Justiça: 10 cartões de programa e casos em cartões', pg.locator('[data-jus=acoes-gov] button.mx-act[data-prog]').count() == 10 and pg.locator('[data-caso].pd-card').count() >= 1, pg.locator('[data-caso]').count())
    chip(pg, 'Segurança')
    ok('Segurança: operações e programas viram cartões', pg.locator('[data-seg=operacoes] button.mx-act[data-prog]').count() == 6, pg.locator('[data-seg=operacoes] button[data-prog]').count())
    ok('Segurança: conversa com governador em cartões', pg.locator('[data-conv=seg] button.mx-act[data-conv-tema]').count() >= 3)
    chip(pg, 'Trabalho')
    ok('Trabalho: alavancas em cartões com botão primário', pg.locator('.tb-lev .btn-pri[data-tb-act]').count() >= 10, pg.locator('.tb-lev').count())
    print('ERRS', errs[:8])
    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    print('RESUMO: %d ok, %d falhas' % (sum(1 for c in checks if c[0]), sum(1 for c in checks if not c[0])))
    b.close()
