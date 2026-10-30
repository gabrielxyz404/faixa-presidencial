import sys, threading, functools, http.server, json, re
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]
STEPS = json.load(open(sys.argv[3], encoding='utf-8')) if len(sys.argv) > 3 else []
PORT = 8766

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

errs, cons = [], []
INFO = """() => ({
  fotos: document.querySelectorAll('svg[data-foto]').length,
  stfFotos: [...document.querySelectorAll('svg[aria-label^="Foto (Wikimedia"]')].length,
  generic: document.querySelectorAll('svg[aria-label^="Rosto genérico"]').length,
  buttons: [...new Set([...document.querySelectorAll('button')].map(b => b.innerText.trim().replace(/\\s+/g,' ')).filter(t => t && t.length < 40))].slice(0, 60)
})"""
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: cons.append(m.text) if m.type == 'error' else None)
    pg.goto(f'http://127.0.0.1:{PORT}/index.html', wait_until='networkidle')
    pg.wait_for_timeout(1500)
    for i, st in enumerate(STEPS):
        kind, val = st[0], st[1]
        try:
            if kind == 'text':
                loc = pg.locator('button, [role=tab], a, summary, label').filter(has_text=val)
                loc.first.click(timeout=5000)
            elif kind == 'minis':
                for _ in range(40):
                    bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
                    if bt.count() == 0: break
                    bt.first.click(timeout=5000); pg.wait_for_timeout(300)
                    pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(300)
            elif kind == 'mes':
                for _ in range(int(val)):
                    pg.locator('button').filter(has_text='Encerrar mês').first.click(timeout=8000); pg.wait_for_timeout(700)
                    for _ in range(3):
                        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
                print('DATA', pg.evaluate("() => document.querySelector('.vitais') && document.querySelector('.vitais').innerText.replace(/\\s+/g,' ').slice(0,200)"))
            elif kind == 'eval':
                print('EVAL', json.dumps(pg.evaluate(val), ensure_ascii=False)[:3000])
            elif kind == 'shot':
                pg.screenshot(path=OUT + '/' + val + '.png')
            elif kind == 'full':
                pg.screenshot(path=OUT + '/' + val + '.png', full_page=True)
            elif kind == 'vp':
                w, hh = val.split('x'); pg.set_viewport_size({'width': int(w), 'height': int(hh)})
            elif kind == 'css':
                pg.locator(val).first.click(timeout=5000)
            elif kind == 'scroll':
                pg.get_by_text(val, exact=False).first.scroll_into_view_if_needed(timeout=5000)
            pg.wait_for_timeout(900)
        except Exception as e:
            print(f'STEP {i} {st} FAILED: {str(e)[:200]}')
            break
        print(f'STEP {i} {st} ->', json.dumps(pg.evaluate(INFO), ensure_ascii=False)[:1500])
    pg.screenshot(path=OUT + '/deep.png')
    b.close()
srv.shutdown()
print('PAGE ERRORS:', len(errs))
for e in errs: print('  ', e[:300])
print('CONSOLE ERRORS:', len(cons))
for c in cons[:10]: print('  ', c[:300])
