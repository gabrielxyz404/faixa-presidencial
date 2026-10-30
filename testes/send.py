import sys, threading, functools, http.server, json, re
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT=sys.argv[1]; OUT=sys.argv[2]
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8772), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
def click(pg,t):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(600)
def start(pg):
    pg.goto('http://127.0.0.1:8772/index.html', wait_until='networkidle'); pg.wait_for_timeout(1500)
    for t in ["Presidente eleito","Assumir o mandato","3Personalidade","Negociador","Técnico","Avançar"]: click(pg,t)
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count()==0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(300)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(300)
    click(pg,"Avançar"); click(pg,"Tomar posse"); pg.wait_for_timeout(1000)
TEXT=sys.argv[3] if sys.argv[3]!='-' else ''
tag=sys.argv[4]
VIT="()=>{const v=document.querySelector('.vitais');return v?v.innerText.replace(/\\s+/g,' '):document.body.innerText.slice(0,300)}"
NEWS="()=>{const t=document.body.innerText;const i=t.indexOf('DIÁRIO');return i>=0?t.slice(i,i+900).replace(/\\n+/g,' | '):'sem diario'}"
log=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1440,'height':900})
    start(pg)
    log.append(('0 antes',pg.evaluate(VIT)))
    if TEXT:
        pg.locator('#caixa').scroll_into_view_if_needed(); pg.fill('#caixa',TEXT)
        click(pg,'Assinar e enviar'); pg.wait_for_timeout(2500)
        print('BTNS',pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim()).filter(x=>x)"))
        for lab in ['Enviar como está','Assinar e publicar no DOU','Enviar e tramitar']:
            loc=pg.locator('.modal-wrap button').filter(has_text=re.compile('^\\s*'+lab+'\\s*$'))
            if loc.count():
                loc.first.click(); print('CLICK',lab); pg.wait_for_timeout(1500); break
        print('MODAL AFTER',pg.evaluate("()=>{const e=document.querySelector('.modal-wrap');return e?e.innerText.slice(0,1500).replace(/\\n+/g,' | '):'none'}"))
        for lab in ['Enviar e tramitar','Votar agora']:
            loc=pg.locator('.modal-wrap button').filter(has_text=re.compile('^\\s*'+lab+'\\s*$'))
            if loc.count():
                loc.first.click(); print('CLICK2',lab); pg.wait_for_timeout(1500); break
        print('MODAL AFTER2',pg.evaluate("()=>{const e=document.querySelector('.modal-wrap');return e?e.innerText.slice(0,1500).replace(/\\n+/g,' | '):'none'}"))
        vb=pg.locator('button').filter(has_text='Voltar ao gabinete')
        if vb.count(): vb.first.click(); pg.wait_for_timeout(500)
        for _ in range(3): pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        log.append(('1 enviado',pg.evaluate(VIT)))
    for m in range(1,5):
        try:
            click(pg,'Encerrar mês'); pg.wait_for_timeout(1000)
            print(f'M{m} MODAL',pg.evaluate("()=>{const e=document.querySelector('.modal-wrap');return e?e.innerText.slice(0,1800).replace(/\\n+/g,' | '):'none'}"))
            full=pg.evaluate("()=>document.querySelector('.modal-wrap')?document.querySelector('.modal-wrap').innerText.replace(/\\n+/g,' | '):''")
            print(f'M{m} KEY',[x for x in full.split(' | ') if re.search(r'Isen|Bolsa|IRPF|Imposto de Renda|Congresso|Câmara|Senado|aprovad|MP |medida provis',x)])
            for _ in range(4): pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
            log.append((f'mes+{m}',pg.evaluate(VIT)))
            print(f'M{m} NEWS',pg.evaluate(NEWS)[:900])
        except Exception as e:
            print('ERR',str(e)[:200]); break
    for l in log: print(l)
    b.close()



