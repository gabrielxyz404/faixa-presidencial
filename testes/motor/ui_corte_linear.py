# Motor 5, etapa 0: corte de gastos vago vira contingenciamento linear (R$ 3 bi, custo nos ministros e grupos).
# uso: python3 run_sandbox.py ui_corte_linear.py <pasta com index.html> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8861
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
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
        try: pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^(Fechar|Continuar|OK|Entendi|Seguir|Próximo mês|Voltar à Mesa)')).first.click(timeout=1200)
        except Exception: pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
def propoe(pg, texto):
    fecha_modais(pg)
    pg.locator('#caixa').scroll_into_view_if_needed()
    if texto: pg.fill('#caixa', texto)
    click(pg, 'Assinar e enviar', 2200)
    if SHOT:
        AV.append(pg.locator('[data-parecer-corte-linear]').count())
        pg.screenshot(path=OUT + '/' + SHOT[0] + '.png'); SHOT.clear()
    btns = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
    for alvo in ['Assinar e publicar no DOU', 'Votar agora']:
        if alvo in btns:
            pg.locator('.modal-wrap button').filter(has_text=alvo).first.click(timeout=4000); pg.wait_for_timeout(1500); break
    else:
        print('  sem botão de aprovar:', btns[:6]); return False
    # votação ao vivo: tenta concluir
    for _ in range(6):
        b = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
        pick = next((x for x in b if re.match(r'^(Ver resultado|Concluir|Apurar|Aplicar|Fechar|Continuar|Encerrar votação|Pular)', x)), None)
        if not pick: break
        try: pg.locator('.modal-wrap button').filter(has_text=pick).first.click(timeout=3000)
        except Exception: pass
        pg.wait_for_timeout(900)
    fecha_modais(pg)
    return True
def encerra(pg, n=1):
    for _ in range(n):
        fecha_modais(pg)
        pg.locator('button').filter(has_text=re.compile(r'^\s*Encerrar m')).first.click(timeout=8000); pg.wait_for_timeout(900)
        fecha_modais(pg)
def estado(pg):
    return pg.evaluate("()=>{const e=document.querySelector('[data-secao-medidas]');return e?e.innerText.length:-1}")

SHOT = []; AV = []
checks = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:300]) if det != '' else ''), flush=True)
def G(pg, e): return pg.evaluate("()=>{const g=__QV().gRef.current;return (" + e + ")}")
def SET(pg, js): pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);" + js + ";return n})"); pg.wait_for_timeout(600)
ESTADO = "({custo:g.fiscal.custo, leal:Object.assign({},(g.minProp||{}).leal||{}), serv:g.groups.servidores, univ:g.groups.universitarios, v5:(g.v5lin||[]).slice(), mes:g.mes})"
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__AL = analisaLocal;\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    SET(pg, "n.acoes=9;n.props=9;n.pes.energia=90")
    a = pg.evaluate("()=>{const g=__QV().gRef.current;const r=t=>{const p=__AL(g,t);return {inst:p.inst,cost:p.cost,topic:p.topic,lin:!!p.v5lin,tec:String(p.tecnico||'').slice(0,900)}};return ['corta gastos','Cortar R$ 30 bilhões do orçamento','cortar gastos da educação','Cortar R$ 50 bilhões em emendas parlamentares'].map(r)}")
    fxg = pg.evaluate("()=>{const p=__AL(__QV().gRef.current,'corta gastos');return {g:p.fx.g,ap:p.fx.ap||0,e:p.fx.e}}"); print('fx corta gastos:', fxg)
    ok('"corta gastos" vira contingenciamento linear de R$ 3 bi por decreto', a[0]['lin'] and 'corte linear' in a[0]['topic'] and a[0]['inst'] == 'DEC' and abs(a[0]['cost'] + 3) < .01, a[0])
    ok('O parecer explica que é vago e pede para dizer onde cortar', 'diga onde cortar' in a[0]['tec'], a[0]['tec'])
    ok('Com valor no texto (R$ 30 bi) o corte vale, linear, e exige projeto de lei', a[1]['lin'] and a[1]['inst'] == 'PL' and abs(a[1]['cost'] + 30) < .01, a[1])
    ok('"cortar gastos da educação" não soma pacote de R$ 12 bi nem reforço', not a[2]['lin'] and a[2]['cost'] <= 0 and 'investimento' not in a[2]['topic'], a[2])
    ok('Corte com alvo (emendas) não é linear', not a[3]['lin'] and abs(a[3]['cost'] + 50) < .01, a[3])
    e0 = G(pg, ESTADO)
    SHOT.append('corte_vago_parecer')
    r1 = propoe(pg, 'corta gastos')
    e1 = G(pg, ESTADO)
    ok('Aviso de proposta vaga aparece no parecer, logo abaixo do valor', AV == [1], AV)
    ok('Aprovado: entra no caixa como economia (até R$ 3 bi, pela rampa)', r1 and -3.01 <= e1['custo'] - e0['custo'] < 0, (e0['custo'], e1['custo']))
    dl = [e1['leal'].get(k, 0) - e0['leal'].get(k, 0) for k in ['saude', 'educacao', 'defesa', 'infra']]
    ok('Ministros (exceto Fazenda) perdem lealdade', all(d < -1 for d in dl) and abs(e1['leal'].get('fazenda', 0) - e0['leal'].get('fazenda', 0)) < .01, dl)
    ok('Servidores e universitários perdem apoio', e1['serv'] < e0['serv'] and e1['univ'] < e0['univ'], (e0['serv'], e1['serv'], e0['univ'], e1['univ']))
    ok('Histórico do corte linear registrado', len(e1['v5']) == 1, e1['v5'])
    a2 = pg.evaluate("()=>{const p=__AL(__QV().gRef.current,'corta gastos');return {cost:p.cost,rep:p.v5lin&&p.v5lin.rep,tec:String(p.tecnico||'').slice(0,900)}}")
    ok('Segundo corte linear no ano rende metade (R$ 1,5 bi) e avisa', abs(a2['cost'] + 1.5) < .01 and a2['rep'] == 1 and 'metade' in a2['tec'], a2)
    feed = G(pg, "g.feed.slice(0,6).map(f=>f.txt).join(' | ')")
    ok('Notícia do corte linear no feed', 'Corte linear' in feed, feed[:200])
    pg.evaluate("()=>window.scrollTo(0,0)")
    a3 = pg.evaluate("()=>{const p=__AL(__QV().gRef.current,'Cortar R$ 30 bilhões do orçamento');return {cost:p.cost}}")
    ok('Corte de R$ 30 bi logo depois rende R$ 15 bi', abs(a3['cost'] + 15) < .01, a3)
    print('erros de página:', errs[:3])
    falhas = [n for c, n in checks if not c]
    print('RESUMO: %d/%d' % (len(checks) - len(falhas), len(checks)), '| falhas:', falhas)
    b.close()
