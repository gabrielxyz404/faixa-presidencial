# Motor 5: quando falta número, o parecer pergunta quem recebe e quanto, e recalcula com a escolha.
# uso: python3 run_sandbox.py ui_falta_numero.py <pasta com index.html> <saida_dir> [porta]
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


checks = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:300]) if det != '' else ''), flush=True)
def abre(pg, t):
    fecha_modais(pg); pg.locator('#caixa').scroll_into_view_if_needed(); pg.fill('#caixa', t); click(pg, 'Assinar e enviar', 2200)
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    start(pg); fecha_modais(pg)
    abre(pg, 'bolsa p morador de rua')
    cx = pg.locator('[data-falta-numero]')
    ok('Proposta sem número mostra a caixa "Faltou número"', cx.count() == 1)
    ok('Recalcular começa desabilitado', pg.locator('[data-falta-recalc]').is_disabled())
    cx.locator('button').filter(has_text='100 mil de pessoas').click(); cx.locator('button').filter(has_text='R$ 600/mês').click(); pg.wait_for_timeout(300)
    cx.scroll_into_view_if_needed(); pg.screenshot(path=OUT + '/falta_numero.png')
    pg.locator('[data-falta-recalc]').click(); pg.wait_for_timeout(1200)
    txt = pg.locator('.modal-wrap').first.inner_text()
    ok('Depois de recalcular, a ementa traz os números escolhidos', 'R$ 600 por mês a 100 mil' in txt, txt[txt.find('EMENTA'):txt.find('EMENTA') + 160])
    ok('Valor exato: R$ 600 × 12 × 100 mil = R$ 0,7 bi', 'R$ 720 mi' in txt or 'R$ 0,7 bi' in txt, txt[txt.find('ANUAL') - 20:txt.find('ANUAL') + 40])
    ok('A caixa some depois de recalcular', pg.locator('[data-falta-numero]').count() == 0)
    pg.screenshot(path=OUT + '/falta_numero_depois.png')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(500); fecha_modais(pg)
    abre(pg, 'Construir 1.000 novos CRAS')
    ok('Com número no texto, a caixa não aparece', pg.locator('[data-falta-numero]').count() == 0)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(500); fecha_modais(pg)
    abre(pg, 'corta gastos')
    ok('No corte linear, a caixa não aparece', pg.locator('[data-falta-numero]').count() == 0)
    print('erros:', errs[:3])
    ok('0 erros de página', not errs, errs[:2])
    falhas = [n for c, n in checks if not c]
    print('RESUMO: %d/%d' % (len(checks) - len(falhas), len(checks)), '| falhas:', falhas)
    b.close()
