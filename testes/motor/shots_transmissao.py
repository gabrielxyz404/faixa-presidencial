# Screenshots (1440x900) do Comprar do arroz (com os instrumentos de abastecimento) e do Comprar do fertilizante (com a prévia), usando o Tailwind compilado.
# uso: python3 run_sandbox.py shots_transmissao.py <pasta com index.html (com <link rel="stylesheet" href="tw.css">), tw.css, fotos.json, logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8894
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
def click(pg, t, ms=500):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(ms)
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV;\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='networkidle'); pg.wait_for_timeout(1500)
    for t in ["Presidente eleito", "Assumir o mandato", "3Personalidade", "Negociador", "Técnico", "Avançar"]: click(pg, t)
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count() == 0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(250)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(250)
    click(pg, "Avançar"); click(pg, "Tomar posse", 1000)
    for _ in range(4):
        if pg.locator('.modal-wrap').count() == 0: break
        try: pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^(Fechar|Continuar|OK|Entendi|Seguir|Próximo mês|Voltar à Mesa|Arquivar|Cancelar|Desistir)')).first.click(timeout=1200)
        except Exception: pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
    pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);n.acoes=9;n.props=9;n.pes.energia=90;return n})"); pg.wait_for_timeout(500)
    pg.locator('#sec-tab-mundo').click(timeout=6000); pg.wait_for_timeout(500)
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*Comércio exterior\s*$')).first.click(timeout=6000); pg.wait_for_timeout(700)
    pg.locator('[data-com-aba=comprar]').click(); pg.wait_for_timeout(500)
    # arroz: instrumentos de abastecimento (com um estoque público formado, para mostrar os dois lados da Conab)
    pg.locator('[data-com-imp=arroz_imp]').click(); pg.wait_for_timeout(700)
    pg.locator('[data-ab-x="0.5"]').click(); pg.locator('[data-ab-compra]').click(); pg.wait_for_timeout(900)
    pg.locator('[data-com-abast=arroz]').scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/comprar_arroz_abastecimento.png', full_page=True)
    # fertilizante: contrato grande com a prévia
    pg.locator('[data-com-imp=fert_potassio_imp]').click(); pg.wait_for_timeout(700)
    pg.locator('[data-com-comprar-de=RUS]').click(); pg.wait_for_timeout(500)
    pg.locator('[data-com-form=compra] [data-com-qtd="2"]').click(); pg.wait_for_timeout(500)
    pg.locator('[data-com-form=compra]').scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/comprar_fertilizante_previa.png', full_page=True)
    print('erros de página:', errs[:3]); b.close()
