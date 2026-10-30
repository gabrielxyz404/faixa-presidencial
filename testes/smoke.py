import sys, threading, functools, http.server, json
from playwright.sync_api import sync_playwright

ROOT = sys.argv[1]
OUT = sys.argv[2]
PORT = 8765

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

errs, cons = [], []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: cons.append(m.text) if m.type == 'error' else None)
    pg.goto(f'http://127.0.0.1:{PORT}/index.html', wait_until='networkidle')
    pg.wait_for_timeout(2500)
    pg.screenshot(path=OUT + '/start.png')
    info = pg.evaluate("""() => ({
        fotos: document.querySelectorAll('svg[data-foto]').length,
        retratos: document.querySelectorAll('svg[role=img]').length,
        botoes: [...document.querySelectorAll('button')].slice(0, 40).map(b => b.innerText.trim()).filter(Boolean)
    })""")
    print(json.dumps(info, ensure_ascii=False))
    b.close()
srv.shutdown()
print('PAGE ERRORS:', len(errs))
for e in errs: print('  ', e[:300])
print('CONSOLE ERRORS:', len(cons))
for c in cons[:10]: print('  ', c[:300])
