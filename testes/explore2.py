import sys, threading, functools, http.server, json, re
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT=sys.argv[1]; OUT=sys.argv[2]
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8771), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
def click(pg,t):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(600)
def start(pg):
    pg.goto('http://127.0.0.1:8771/index.html', wait_until='networkidle'); pg.wait_for_timeout(1500)
    for t in ["Presidente eleito","Assumir o mandato","3Personalidade","Negociador","Técnico","Avançar"]: click(pg,t)
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count()==0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(300)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(300)
    click(pg,"Avançar"); click(pg,"Tomar posse"); pg.wait_for_timeout(1000)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1440,'height':900})
    start(pg)
    pg.locator('#caixa').scroll_into_view_if_needed()
    pg.fill('#caixa','Isentar do imposto de renda quem ganha até R$ 6 mil')
    print(pg.evaluate("()=>document.getElementById('caixa').closest('section').innerText"))
    print(pg.evaluate("()=>[...document.getElementById('caixa').closest('section').querySelectorAll('button')].map(b=>b.innerText+'|'+b.disabled)"))
    b.close()

