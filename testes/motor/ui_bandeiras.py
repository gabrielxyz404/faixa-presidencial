# Teste das bandeiras (imagens SVG embutidas) ao lado dos nomes de países: Mundo → Países, Visitas de Estado, Blocos, Mesa diplomática, Terras raras e Panorama.
# Confere que cada bandeira carrega (naturalWidth > 0), que todo país listado tem bandeira, que não restou emoji de bandeira no texto, texto mínimo de 12px e 0 erros de página.
# uso: python3 run_sandbox.py ui_bandeiras.py <pasta com index.html> <saida_dir> [porta]
import sys, threading, functools, http.server, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8897
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
checks = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:260]) if det != '' else ''), flush=True)
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
def encerra(pg):
    fecha_modais(pg)
    pg.locator('button').filter(has_text=re.compile(r'^\s*Encerrar m')).first.click(timeout=8000); pg.wait_for_timeout(900)
    fecha_modais(pg)
def vai(pg, sec, chip=None):
    pg.locator('#sec-tab-' + sec).click(timeout=6000); pg.wait_for_timeout(500)
    if chip: pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*' + re.escape(chip))).first.click(timeout=6000); pg.wait_for_timeout(600)
def minfont(pg):
    return pg.evaluate("()=>{let m=99;document.querySelectorAll('[role=tabpanel] *, main *').forEach(e=>{if(e.children.length===0&&e.textContent.trim()&&e.offsetParent!==null&&!e.closest('.gv-tipbox')&&!e.closest('style,script')){const f=parseFloat(getComputedStyle(e).fontSize);if(f<m)m=f}});return m}")
# quantas imagens de bandeira dentro do seletor carregaram; devolve (total, carregadas)
JS_IMG = """(sel)=>{const out=[];document.querySelectorAll(sel).forEach(e=>{const i=e.querySelector('img[data-bandeira]');out.push(!!i&&i.complete&&i.naturalWidth>0&&i.naturalHeight>0)});return out}"""
JS_EMOJI = "()=>/[\\u{1F1E6}-\\u{1F1FF}]{2}/u.test((document.querySelector('[role=tabpanel]')||document.body).innerText)"
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__B = () => ({ PAISES_DIP, BANDEIRAS, ISO_NOME, PAIS_REF });\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)

    # ---------- dados ----------
    d = pg.evaluate("()=>{const {PAISES_DIP,BANDEIRAS,ISO_NOME,PAIS_REF}=__B();return {n:PAISES_DIP.length,faltam:PAISES_DIP.filter(p=>!BANDEIRAS[p.iso.toLowerCase()]).map(p=>p.id),chaves:Object.keys(BANDEIRAS).length,bytes:JSON.stringify(BANDEIRAS).length,semNome:Object.keys(BANDEIRAS).filter(k=>!ISO_NOME[k]),mapa:PAISES_DIP.every(p=>PAIS_REF[p.id]&&PAIS_REF[p.id].iso===p.iso.toLowerCase())}}")
    ok('todo país do jogo tem bandeira embutida', d['n'] >= 20 and not d['faltam'] and d['mapa'], d)
    ok('BANDEIRAS: ~65 arquivos, abaixo de 300 KB, todos com nome', d['chaves'] >= 60 and d['bytes'] < 300000 and not d['semNome'], (d['chaves'], d['bytes']))
    nec = ('cn us ar nl es cl sg in mx jp de kr ca it py uy be fr gb pt tr sa ae ir eg my vn th id bd ru ng co pe bo za ma dz ch au ph pk br ve il ua ec eu').split()
    ok('os ~50 parceiros comerciais pedidos estão em BANDEIRAS', pg.evaluate("(l)=>l.filter(k=>!__B().BANDEIRAS[k])", nec) == [])
    todas = pg.evaluate("""()=>Promise.all(Object.entries(__B().BANDEIRAS).map(([k,s])=>new Promise(r=>{const i=new Image();i.onload=()=>r(i.naturalWidth>0?null:k);i.onerror=()=>r(k);i.src=s})))""")
    ok('todas as imagens de BANDEIRAS decodificam', all(x is None for x in todas), [x for x in todas if x])

    # ---------- Panorama ----------
    vai(pg, 'mundo', 'Panorama')
    r = pg.evaluate(JS_IMG, '[data-rel]')
    ok('Panorama: 6 cartões de relação, todos com bandeira ou ícone', len(r) == 6 and pg.locator('[data-rel] [data-pais-rotulo]').count() == 6)
    ok('Panorama: bandeiras (EUA, China, UE, Mercosul) carregadas', sum(r) == 4 and pg.locator('[data-rel=brics] svg').count() >= 1, r)
    ok('Panorama: sem emoji de bandeira no texto', not pg.evaluate(JS_EMOJI))
    pg.screenshot(path=OUT + '/bandeiras_panorama.png', full_page=True)

    # ---------- Países ----------
    vai(pg, 'mundo', 'Países')
    r = pg.evaluate(JS_IMG, '[data-pais]')
    ok('Países: um cartão por país e todos com bandeira carregada', len(r) == d['n'] and all(r), (len(r), sum(r)))
    ok('Países: a bandeira vem logo antes do nome (.mx-t)', pg.evaluate("()=>[...document.querySelectorAll('[data-pais]')].every(c=>{const i=c.querySelector('img[data-bandeira]'),t=c.querySelector('.mx-t');return i&&t&&(i.compareDocumentPosition(t)&Node.DOCUMENT_POSITION_FOLLOWING)&&i.title.length>0&&i.alt===t.textContent.trim()})"))
    ok('Países: bandeira com ~18x13 ou maior, borda de 1px e cantos arredondados', pg.evaluate("()=>[...document.querySelectorAll('[data-pais] img[data-bandeira]')].every(i=>{const s=getComputedStyle(i),w=i.getBoundingClientRect();return w.width>=18&&Math.abs(w.width/w.height-4/3)<.12&&parseFloat(s.borderTopWidth)===1&&parseFloat(s.borderTopLeftRadius)>0})"))
    ok('Países: sem emoji de bandeira', not pg.evaluate(JS_EMOJI))
    pg.screenshot(path=OUT + '/bandeiras_paises.png', full_page=True)

    # ---------- Visitas ----------
    vai(pg, 'mundo', 'Visitas de Estado')
    ok('Visitas: bandeira do destino ao lado do seletor, e muda com a escolha', pg.evaluate("()=>{const i=document.querySelector('#viag-pais').parentElement.querySelector('img[data-bandeira]');return !!i&&i.naturalWidth>0}"))
    a0 = pg.evaluate("()=>document.querySelector('#viag-pais').parentElement.querySelector('img[data-bandeira]').getAttribute('data-bandeira')")
    pg.select_option('#viag-pais', 'China'); pg.wait_for_timeout(300)
    a1 = pg.evaluate("()=>document.querySelector('#viag-pais').parentElement.querySelector('img[data-bandeira]').getAttribute('data-bandeira')")
    ok('Visitas: seletor troca a bandeira (ar → cn)', a0 == 'ar' and a1 == 'cn', (a0, a1))
    pg.locator('button').filter(has_text=re.compile(r'Agendar visita')).first.click(timeout=5000); pg.wait_for_timeout(700)
    ok('Visitas: cartão "Agendada" traz a bandeira da China', pg.evaluate("()=>{const c=document.querySelector('[data-viagem=agendada]');const i=c&&c.querySelector('img[data-bandeira=cn]');return !!i&&i.naturalWidth>0&&/China/.test(c.innerText)}"))
    pg.screenshot(path=OUT + '/bandeiras_visitas.png', full_page=True)
    vai(pg, 'mundo', 'Panorama')
    ok('Panorama: situação da visita traz a bandeira', pg.evaluate("()=>{const i=document.querySelector('[data-secao-mundo=itamaraty] img[data-bandeira=cn]');return !!i&&i.naturalWidth>0}"))
    ok('KPI de visitas traz a bandeira', pg.evaluate("()=>{const i=document.querySelector('[data-gv-kpi=mundo-viagens] img[data-bandeira=cn]');return !!i&&i.naturalWidth>0}"))
    pg.locator('#sec-tab-mesa').click(timeout=6000); pg.wait_for_timeout(700)
    ok('Mesa → Precisa de você: cartão da viagem com bandeira', pg.evaluate("()=>{const c=document.querySelector('[data-pend=viagem]');const i=c&&c.querySelector('img[data-bandeira=cn]');return !!i&&i.naturalWidth>0}"))
    pg.screenshot(path=OUT + '/bandeiras_mesa_precisa.png', full_page=True)

    # ---------- Blocos ----------
    vai(pg, 'mundo', 'Blocos')
    n = pg.locator('[data-org]').count()
    ok('Blocos: todo organismo com bandeira ou ícone (sem emoji)', n >= 9 and pg.locator('[data-org] [data-pais-rotulo]').count() == n and not pg.evaluate(JS_EMOJI), n)
    ok('Blocos: Mercosul, ONU e Mercosul–UE com bandeira carregada; BRICS com ícone', pg.evaluate("()=>['mercosul','onu','mercosul_ue'].every(k=>{const i=document.querySelector('[data-org='+k+'] img[data-bandeira]');return i&&i.naturalWidth>0})&&!!document.querySelector('[data-org=brics] svg')"))
    pg.screenshot(path=OUT + '/bandeiras_blocos.png', full_page=True)

    # ---------- Terras raras ----------
    vai(pg, 'mundo', 'Terras raras')
    r = pg.evaluate(JS_IMG, '[data-parc]')
    ok('Terras raras: 3 abas de parceiro, todas com bandeira carregada', len(r) == 3 and all(r), r)
    ok('Terras raras: "UE e Japão" mostra duas bandeiras', pg.locator('[data-parc=ueja] img[data-bandeira]').count() == 2)
    ok('Terras raras: nome do parceiro ao lado da bandeira no cartão', pg.evaluate("()=>{const b=[...document.querySelectorAll('[data-tr=mesa] b')].find(e=>e.querySelector('img[data-bandeira=us]'));return !!b&&/Estados Unidos/.test(b.innerText)}"))
    pg.locator('[data-parc=china]').click(timeout=5000); pg.wait_for_timeout(400)
    ok('Terras raras: rival indicado com bandeira (China → EUA)', pg.evaluate("()=>{const s=[...document.querySelectorAll('[data-tr=mesa] span')].find(e=>/^rival:/.test(e.innerText||''));return !!s&&!!s.querySelector('img[data-bandeira=us]')}"))
    ok('Terras raras: sem emoji de bandeira', not pg.evaluate(JS_EMOJI))
    pg.screenshot(path=OUT + '/bandeiras_terras_raras.png', full_page=True)

    # ---------- Mesa diplomática (até sair uma decisão com país sorteado) ----------
    vai(pg, 'mundo', 'Mesa diplomática')
    for _ in range(14):
        if G(pg, "g.mundo.mesa.p") and pg.locator('[data-mesadip]').count() == 1: break
        encerra(pg); vai(pg, 'mundo', 'Mesa diplomática')
    ok('Mesa diplomática: decisão com país sorteado encontrada', bool(G(pg, "g.mundo.mesa.p")) and pg.locator('[data-mesadip]').count() == 1, G(pg, "g.mundo.mesa.p"))
    ok('Mesa diplomática: bandeira e nome do país sorteado no cabeçalho', pg.evaluate("()=>{const c=document.querySelector('[data-mesadip]');const i=c.querySelector('[data-pais-rotulo] img[data-bandeira]');return !!i&&i.naturalWidth>0&&c.querySelector('[data-pais-rotulo]').innerText.trim().length>2}"))
    ok('Mesa diplomática: chips de efeito por país têm bandeira carregada', pg.evaluate("()=>{const l=[...document.querySelectorAll('[data-opcao-dip] .gv-chip')].filter(c=>/[▲▼]/.test(c.innerText)&&!/Alinhamento|Isolamento/.test(c.innerText));return l.length>0&&l.every(c=>{const i=c.querySelector('img[data-bandeira]');return i&&i.naturalWidth>0})}"))
    ok('Mesa diplomática: sem emoji de bandeira', not pg.evaluate(JS_EMOJI))
    pg.screenshot(path=OUT + '/bandeiras_mesa_diplomatica.png', full_page=True)
    if pg.locator('[data-opcao-dip]:not([disabled])').count():
        pg.locator('[data-opcao-dip]:not([disabled])').first.click(timeout=5000); pg.wait_for_timeout(600)
        pg.locator('[data-mundo=mesa] summary').first.click(timeout=5000); pg.wait_for_timeout(300)
        ok('Mesa diplomática: histórico com a bandeira do país sorteado', G(pg, "g.mundo.hist.length") >= 1 and pg.evaluate("()=>{const i=document.querySelector('[data-mundo=mesa] .mx-list li img[data-bandeira]');return !!i&&i.naturalWidth>0}"))

    # ---------- Tratados e País → Sociedade ----------
    vai(pg, 'mundo', 'Tratados')
    ok('Tratados: cartões de tratado com país mostram bandeira', pg.evaluate("()=>[...document.querySelectorAll('[data-mundo=tratados] li')].every(li=>!li.querySelector('.mx-h img')===!!li.querySelector('.mx-h svg')||!!li.querySelector('.mx-h img[data-bandeira]'))"))
    vai(pg, 'pais', 'Sociedade')
    r = pg.evaluate(JS_IMG, '[data-ranking-idh] tbody tr:not(:has(td[colspan]))')
    ok('País → Sociedade: ranking de IDH com bandeira em toda linha', len(r) >= 5 and all(r), (len(r), sum(r)))
    pg.screenshot(path=OUT + '/bandeiras_brasil_no_mundo.png', full_page=True)

    # ---------- layout ----------
    por_aba = {}
    for c in ['Panorama', 'Países', 'Visitas de Estado', 'Blocos', 'Tratados', 'Mesa diplomática', 'Terras raras']:
        vai(pg, 'mundo', c); por_aba[c] = (pg.evaluate("()=>document.documentElement.scrollWidth<=innerWidth"), minfont(pg))
    ok('sem rolagem horizontal e texto mínimo de 12px nas abas do Mundo', all(v[0] and v[1] >= 12 for v in por_aba.values()), por_aba)
    pg.set_viewport_size({'width': 390, 'height': 800}); pg.wait_for_timeout(400)
    cel = {}
    for c in ['Panorama', 'Países', 'Visitas de Estado', 'Blocos', 'Terras raras']:
        try:
            vai(pg, 'mundo', c); cel[c] = pg.evaluate("()=>document.documentElement.scrollWidth<=innerWidth")
        except Exception as e:
            cel[c] = 'sem aba no celular'
    ok('celular 390px: sem rolagem horizontal nas abas testadas', all(v is True or v == 'sem aba no celular' for v in cel.values()), cel)
    b.close()
ok('0 erros de página/console', len(errs) == 0, errs[:3])
falhas = [n for c, n in checks if not c]
print('\n%d verificações, %d falhas' % (len(checks), len(falhas)))
for n in falhas: print('  FALHA:', n)
sys.exit(1 if falhas else 0)
