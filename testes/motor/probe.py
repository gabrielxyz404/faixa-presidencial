# Lê frases (JSON: lista de strings ou de {"t": ...}) com o motor local e grava um resumo por frase.
# uso: python3 run_sandbox.py probe.py <pasta com index.html> <frases.json> <saida.json> [porta]
import sys, threading, functools, http.server, json, re
from playwright.sync_api import sync_playwright
ROOT = sys.argv[1]; PH = json.load(open(sys.argv[2], encoding='utf-8-sig')); OUT = sys.argv[3]; PORT = int(sys.argv[4]) if len(sys.argv) > 4 else 8790
PH = [p['t'] if isinstance(p, dict) else p for p in PH]
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
def click(pg, t):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(500)
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', 'window.__AL=analisaLocal; window.__M=MOTOR;\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='networkidle'); pg.wait_for_timeout(1200)
    for t in ["Presidente eleito", "Assumir o mandato", "3Personalidade", "Negociador", "Técnico", "Avançar"]: click(pg, t)
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count() == 0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(250)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(250)
    click(pg, "Avançar"); click(pg, "Tomar posse"); pg.wait_for_timeout(800)
    pg.evaluate("()=>{const o=__M.analisar; __M.analisar=function(g){window.__g=g; return o.apply(this,arguments)}}")
    pg.locator('#caixa').scroll_into_view_if_needed(); pg.fill('#caixa', 'Acabar com a escala 6x1')
    click(pg, 'Assinar e enviar'); pg.wait_for_timeout(1500)
    res = pg.evaluate("""(PH)=>PH.map(t=>{try{const p=__AL(window.__g,t); const j=(p.juridico||{});
      return {t, topic:p.topic, inst:p.inst, instDet:p.instDetalhe||null, cost:p.cost, rev:p.rev, once:p.once, extra:p.extra,
        cf:(p.stf||{}).nivel, cfTxt:String((p.stf||{}).parecer||'').slice(0,260), vago:!!(p.qualidade||{}).vago, absurdo:!!p.absurdo, generica:!!(p.qualidade||{}).generica, conf:(p.viabilidade||{}).confianca??null,
        pasta:p.pastaNome, gan:((p.imp||{}).gan||[]).map(x=>x.nome).slice(0,4), per:((p.imp||{}).per||[]).map(x=>x.nome).slice(0,4),
        tecnico:String(p.tecnico||'').slice(0,600), objs:(p.objs||[]).map(o=>o.id+':'+(o.B==null?'':o.B)).slice(0,6), gen:!!(p.qualidade||{}).generica, calc:(p.calculo||[]).slice(0,6), its:((p._A||{}).items||[]).map(i=>i.o.id+'|k'+i.o.k+'|sg'+i.sg+'|B'+(i.B==null?'':Math.round(i.B*100)/100)+'|'+i.role+(i.regul?'|regul':'')+(i.talk?'|talk':'')+(i.jaVigente?'|jv':'')+(i.fora?'|fora':'')), nv:((p._A||{}).normaVigente||{}).id||null, nvx:!!((p._A||{}).normaVigente||{}).exato}}catch(e){return {t, err:String(e)}}})""", PH)
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n'.join(errs) or 'no errs')
    b.close()
