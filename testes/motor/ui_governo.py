# Teste de interface de Poder → Governo (v2 visual): faixa-resumo, cartões de ministros, ideias pendentes, prioridade do trimestre.
# Confere a faixa com 5 indicadores, ≥10 cartões de ministros (foto, pasta, status, medidores, ações), cartão de ideia com Aprovar/Ajustar/Recusar,
# seletor de prioridade com chips de efeito; executa: escolher a prioridade, reunião com um ministro, recusar uma ideia e ajustar outra;
# sem rolagem horizontal em 1440 e 1280, texto mínimo de 12px e 0 erros de página/console.
# uso: python3 run_sandbox.py ui_governo.py <pasta com index.html> <saida_dir> [porta]
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
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV;\nfunction analisaLegado(g, texto) {', 1)
    pg.add_init_script(SEED)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    # avança um mês para haver ideias de ministros na lista (chegam no início de cada mês)
    if G(pg, "g.minProp.lista.length") == 0: encerra(pg)
    vai_governo(pg)

    # ---------- faixa-resumo ----------
    ok('faixa-resumo com os 5 indicadores', pg.locator('[data-gv=resumo] [data-gv-kpi]').count() == 5, pg.evaluate("()=>[...document.querySelectorAll('[data-gv-kpi]')].map(e=>e.getAttribute('data-gv-kpi'))"))
    ok('faixa mantém data-resumo-esplanada', pg.locator('[data-resumo-esplanada]').count() == 1)
    kp = pg.evaluate("()=>Object.fromEntries([...document.querySelectorAll('[data-gv-kpi]')].map(e=>[e.getAttribute('data-gv-kpi'),e.innerText.replace(/\\n/g,' | ')]))")
    ok('indicador de ministros mostra n/total', re.search(r'\d+/\d+', kp.get('ministros', '')) is not None, kp.get('ministros'))
    nid = G(pg, "g.minProp.lista.length")
    ok('indicador de ideias bate com o estado do jogo', ('| %d |' % nid) in kp.get('ideias', ''), kp.get('ideias'))
    ok('indicador de prioridade fala de escolha pendente ou mês x de 3', 'pendente' in kp.get('prioridade', '').lower() or 'de 3' in kp.get('prioridade', ''), kp.get('prioridade'))

    # ---------- cartões de ministros ----------
    cards = pg.locator('li[data-pasta]')
    n = cards.count()
    NP = G(pg, 'Object.keys(g.cfg.ministros).length'); ok('um cartão por pasta (o jogo tem 9 ministérios; o pedido citava ≥10)', n >= 9 and n == NP, (n, NP))
    ok('cada cartão tem status, 3 medidores e 3 ações', pg.evaluate("()=>[...document.querySelectorAll('li[data-pasta]')].every(e=>e.getAttribute('data-st')&&e.querySelectorAll('[role=meter]').length===3&&e.querySelectorAll('.gv-acts button').length===3)"))
    ok('cartões mostram foto/efígie e logo do partido', pg.evaluate("()=>[...document.querySelectorAll('li[data-pasta]')].filter(e=>e.querySelector('svg,img')).length") >= n and pg.locator('li[data-pasta] [data-logo]').count() >= 1)
    ok('mantém data-desgaste, data-entrega e data-min-leal', pg.locator('[data-desgaste]').count() >= n and pg.locator('[data-entrega]').count() >= n and pg.locator('[data-min-leal]').count() >= n)
    ok('status vem de um conjunto conhecido', pg.evaluate("()=>[...document.querySelectorAll('li[data-pasta]')].every(e=>['estavel','pressao','crise','desgastado','demissionario'].includes(e.getAttribute('data-st')))"))
    ok('detalhes recolhidos por padrão, abrem sob demanda', pg.locator('li[data-pasta] details[open]').count() == 0)
    cards.first.locator('summary').click(); pg.wait_for_timeout(300)
    ok('detalhes abrem com rendimento', 'rendimento' in cards.first.inner_text().lower())
    # ação: reunião com o ministro reduz o desgaste (ou ao menos marca a reunião do mês)
    pk = cards.first.get_attribute('data-pasta'); d0 = G(pg, "g.minEstado['%s'].desgaste" % pk)
    cards.first.locator('.gv-acts button').filter(has_text='Reunião').click(timeout=5000); pg.wait_for_timeout(500)
    ok('Reunião: marca a reunião do mês e reduz o desgaste', G(pg, "g.minEstado['%s'].reuniao" % pk) == G(pg, "g.mes") and G(pg, "g.minEstado['%s'].desgaste" % pk) <= d0, (d0, G(pg, "g.minEstado['%s'].desgaste" % pk)))
    pg.locator('li[data-pasta=%s] .gv-acts button' % pk).filter(has_text='Substituir').click(timeout=5000); pg.wait_for_timeout(600)
    ok('Substituir abre a gaveta de escolha do novo ministro', pg.locator('.gav').count() >= 1)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(400)

    # ---------- ideias pendentes ----------
    ideias = pg.locator('[data-min-card]')
    ok('há ao menos uma ideia pendente em cartão', ideias.count() >= 1, ideias.count())
    c0 = ideias.first
    ok('cartão da ideia tem título, ministro, pasta, texto e chips', c0.locator('[data-min-titulo]').count() == 1 and c0.locator('[data-min-nome]').count() == 1 and c0.locator('[data-min-texto]').count() == 1 and c0.get_attribute('data-min-pasta') and c0.locator('[data-min-prev] .gv-chip').count() >= 1)
    ok('ações Aprovar / Ajustar / Recusar com os data-min-act de sempre', all(c0.locator('[data-min-act=%s]' % a).count() == 1 for a in ('acatar', 'ajustar', 'engavetar')) and 'Aprovar' in c0.inner_text() and 'Recusar' in c0.inner_text())
    ok('ideias continuam com data-min-q e justificativa em dica "?"', c0.locator('[data-min-q]').count() == 1 and c0.locator('[data-gv-tip]').count() >= 1)
    # recusar uma ideia
    id0 = c0.get_attribute('data-min-card'); n0 = G(pg, "g.minProp.lista.length"); h0 = G(pg, "g.minProp.hist.length")
    c0.locator('[data-min-act=engavetar]').click(timeout=5000); pg.wait_for_timeout(700)
    ok('Recusar: a ideia sai da lista e vai ao histórico', G(pg, "g.minProp.lista.length") == n0 - 1 and G(pg, "g.minProp.hist.length") == h0 + 1 and pg.locator('[data-min-card=%s]' % id0).count() == 0)
    ok('histórico de decisões recolhido numa lista', pg.locator('details [data-min-hist]').count() == 1)
    # ajustar outra ideia: leva o texto à caixa da Mesa
    if pg.locator('[data-min-card]').count():
        txt = pg.locator('[data-min-card]').first.locator('[data-min-texto]').inner_text()
        pg.locator('[data-min-card]').first.locator('[data-min-act=ajustar]').click(timeout=5000); pg.wait_for_timeout(1200)
        ok('Ajustar leva o texto para a caixa de decisão da Mesa', pg.evaluate("()=>document.getElementById('caixa')&&document.getElementById('caixa').value") == txt or txt[:40] in (pg.evaluate("()=>document.getElementById('caixa')?document.getElementById('caixa').value:''") or ''))
        vai_governo(pg)

    # ---------- prioridade do trimestre ----------
    pri = pg.locator('[data-prioridade=pendente]')
    ok('prioridade pendente: 5 cartões com chips de efeito', pri.count() == 1 and pri.locator('[data-pri]').count() == 5 and pri.locator('[data-pri] .gv-chip').count() >= 5, pri.locator('[data-pri]').count())
    pri.locator('[data-pri=comunicacao] button').click(timeout=5000); pg.wait_for_timeout(700)
    ok('Escolher: grava a prioridade no jogo', G(pg, "g.prioridade.k") == 'comunicacao', G(pg, "g.prioridade.k"))
    ok('painel vira "ativa" com mês x de 3', pg.locator('[data-prioridade=ativa]').count() == 1 and 'de 3' in pg.locator('[data-prioridade=ativa]').inner_text())
    ok('faixa mostra a prioridade escolhida', 'Comunicação' in pg.locator('[data-gv-kpi=prioridade]').inner_text())

    # ---------- layout ----------
    pg.screenshot(path=OUT + '/governo_1440.png', full_page=True)
    ok('sem rolagem horizontal em 1440', pg.evaluate("()=>document.documentElement.scrollWidth<=innerWidth"))
    mini = pg.evaluate("()=>{let m=99;document.querySelectorAll('[data-gv=governo] *').forEach(e=>{if(e.children.length===0&&e.textContent.trim()&&getComputedStyle(e).display!=='none'){const f=parseFloat(getComputedStyle(e).fontSize);if(f<m)m=f}});return m}")
    ok('texto mínimo de 12px na aba', mini >= 12, mini)
    pg.set_viewport_size({'width': 1280, 'height': 800}); pg.wait_for_timeout(600)
    pg.screenshot(path=OUT + '/governo_1280.png', full_page=True)
    ok('sem rolagem horizontal em 1280', pg.evaluate("()=>document.documentElement.scrollWidth<=innerWidth"), pg.evaluate("()=>document.documentElement.scrollWidth"))

    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    b.close()
falhas = [n for c, n in checks if not c]
print('\nRESULTADO: %d/%d ok' % (len(checks) - len(falhas), len(checks)), '| falhas:', falhas)
sys.exit(1 if falhas else 0)
