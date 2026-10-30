import sys, threading, functools, http.server, json, re
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT=sys.argv[1]; PH=json.load(open(sys.argv[2],encoding='utf-8-sig')); OUT=sys.argv[3]
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8783), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
def click(pg,t):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(600)
def start(pg):
    pg.goto('http://127.0.0.1:8783/index.html', wait_until='networkidle'); pg.wait_for_timeout(1500)
    for t in ["Presidente eleito","Assumir o mandato","3Personalidade","Negociador","Técnico","Avançar"]: click(pg,t)
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count()==0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(300)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(300)
    click(pg,"Avançar"); click(pg,"Tomar posse"); pg.wait_for_timeout(1000)
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1440,'height':900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR '+str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE '+m.text[:300]) if m.type=='error' else None)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=open(ROOT+'/index.html',encoding='utf-8').read().replace('function analisaLegado(g, texto) {','window.__AL=analisaLocal; window.__M=MOTOR;\nfunction analisaLegado(g, texto) {',1)))
    start(pg)
    pg.evaluate("()=>{const o=__M.analisar; __M.analisar=function(g){window.__g=g; return o.apply(this,arguments)}}")
    pg.locator('#caixa').scroll_into_view_if_needed(); pg.fill('#caixa','Acabar com a escala 6x1')
    click(pg,'Assinar e enviar'); pg.wait_for_timeout(2000)
    res=[]
    for t in PH:
        r=pg.evaluate("""(t)=>{try{const p=__AL(window.__g,t);
          return {inst:p.instrumento||p.inst, keys:Object.keys(p).join(','), p:JSON.stringify(p,(k,v)=>typeof v==='string'&&v.length>400?v.slice(0,400):v).slice(0,3000)}}catch(e){return {err:String(e)}}}""",t)
        res.append({'t':t,**r})
    json.dump(res,open(OUT,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print('\n'.join(errs) or 'no errs')
    b.close()


