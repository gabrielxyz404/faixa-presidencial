# Teste do lote D (interface e textos): embalo formatado, rótulo de mandato nos slots, manchetes da banca, selo do balão,
# contraste do modal de votação e dos motores, cartão único do STF, crise fixa no topo, title nos truncados, slots em 2 colunas,
# toast em fila no topo direito, modo leve como cartão, herança de pendências na posse e nome do repórter fictício.
# Também tira os prints em 1440x900 e 1280x800.
# uso: python3 run_sandbox.py ui_lote_d.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8871
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
SEED = "(()=>{let a=777;Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
INJ = ("window.__QV = () => QV; window.__X = () => ({ fimDoMes, qvMetaDe, qvSerializa, elEnsure, elPosse, nomeCurto: (typeof nomeCurto === 'function' ? nomeCurto : null), PROMESSAS, bancaFrase, X_IMPRENSA, pendenciasMesa, MARCOMAP }); "
       "function analisaLegado(g, texto) {")
checks = []; errs = []
def ok(nome, cond, det=''):
    checks.append(bool(cond)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:300]) if det != '' else ''), flush=True)
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
    click(pg, "Avançar"); click(pg, "Tomar posse", 1200)
def G(pg, expr): return pg.evaluate("()=>{const g=__QV().gRef.current; if(!g) return null; return (" + expr + ")}")
def SET(pg, js): pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);" + js + ";return n})"); pg.wait_for_timeout(500)
def overlay(pg): return pg.evaluate("()=>[...document.querySelectorAll('.cn,.modal-wrap,.gav-wrap')].some(e=>e.getClientRects().length)")
def fecha(pg):
    for _ in range(8):
        if not overlay(pg): return
        pg.evaluate("""()=>{const L=[...document.querySelectorAll('.cn,.modal-wrap,.gav-wrap')].filter(e=>e.getClientRects().length);const r=L[L.length-1];
          const b=[...r.querySelectorAll('button:not([disabled])')].find(b=>/^(Fechar|Voltar ao gabinete|Arquivar|Voltar(?! ao menu)|Continuar|Entendi|OK|Marcar como|Começar |Ver o desfecho|Cancelar|Seguir|Próximo mês|Voltar à Mesa|Concluir|Retirar proposta)/.test(b.innerText.trim()));
          if(b) b.click(); }""")
        pg.wait_for_timeout(350)
        if overlay(pg): pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
def vai(pg, sec, chip=None):
    pg.locator('#sec-tab-' + sec).click(timeout=5000); pg.wait_for_timeout(400)
    if chip:
        pg.locator('#%s-chip-%s' % (sec, chip)).click(timeout=5000); pg.wait_for_timeout(500)
def corpo(pg): return pg.evaluate("()=>document.body.innerText")
AUDIT = """(raiz)=>{
  const R=document.querySelector(raiz); if(!R) return null;
  const parse=c=>{const m=c.match(/rgba?\\(([^)]+)\\)/); if(!m) return [0,0,0,0]; const p=m[1].split(',').map(Number); return [p[0],p[1],p[2],p.length>3?p[3]:1]};
  const lum=([r,g,b])=>{const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(r)+.7152*f(g)+.0722*f(b)};
  const bgDe=el=>{let acc=[0,0,0],a=1,stack=[];for(let e=el;e;e=e.parentElement){const c=parse(getComputedStyle(e).backgroundColor);if(c[3]>0)stack.push(c);if(c[3]>=.99)break}
    let base=[5,6,10];for(let i=stack.length-1;i>=0;i--){const c=stack[i];base=[0,1,2].map(k=>c[k]*c[3]+base[k]*(1-c[3]))}return base};
  const out=[];
  for(const el of R.querySelectorAll('*')){
    if(!el.getClientRects().length) continue;
    const t=[...el.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent.trim()).join(' ').trim(); if(t.length<2) continue;
    const cs=getComputedStyle(el); if(cs.visibility==='hidden'||cs.display==='none') continue;
    let op=1; for(let e=el;e&&e!==R.parentElement;e=e.parentElement){op*=parseFloat(getComputedStyle(e).opacity)}
    const fg=parse(cs.color); const bg=bgDe(el);
    const fgm=[0,1,2].map(k=>fg[k]*fg[3]*op+bg[k]*(1-fg[3]*op));
    const L1=lum(fgm),L2=lum(bg); const r=(Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);
    if(r<4.5 && !el.matches('.selo-sim,.selo-sim *')) out.push({sel:el.tagName.toLowerCase()+(el.className&&typeof el.className==='string'?'.'+el.className.split(' ').filter(Boolean).slice(0,3).join('.'):''),t:t.slice(0,40),r:Math.round(r*100)/100});
  }
  return out;}"""
def contraste(pg, raiz): return pg.evaluate(AUDIT, raiz) or []

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' and 'Failed to load resource' not in m.text else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', INJ, 1)
    pg.add_init_script(SEED)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha(pg)
    SET(pg, "n.acoes=5;n.pes.energia=90;n.eu.embalo=-0.3999999999999999;n.mes=13")
    # três cadeiras vagas no STF
    SET(pg, "let k=0;for(const c of n.stfCadeiras){ if(!c.vaga && k<2){ c.vaga=true; c.de=c.nome; c.desde='2026-06'; k++ } }")

    # ---------- D1: Embalo sem número cru ----------
    vai(pg, 'mesa'); fecha(pg)
    eb = pg.evaluate("()=>{const e=document.querySelector('[data-vital-v=embalo]');return e?e.innerText:null}")
    ok('D1: barra mostra o embalo com 1 casa (-0,4)', eb is not None and re.fullmatch(r'[-−]0,4', eb.strip()), eb)
    SET(pg, "n.eu.embalo=2.6000000000000005")
    ok('D1: Mesa sem número cru (4+ casas decimais)', not re.search(r'\d[.,]\d{4,}', corpo(pg)), re.findall(r'.{20}\d[.,]\d{4,}.{10}', corpo(pg))[:2])
    SET(pg, "n.eu.embalo=-0.3999999999999999")

    # ---------- D6: cartão único do STF; crise do mês fixa no topo ----------
    nv = G(pg, '(n=>n)((g.stfCadeiras||[]).filter(c=>c.vaga).length)')
    stf = pg.locator('[data-pend=stf]')
    ok('D6: um único cartão do STF com %d vagas' % nv, stf.count() == 1 and nv >= 3, (stf.count(), nv))
    ok('D6: o cartão diz "STF: N cadeiras vagas"', stf.count() == 1 and re.search(r'STF: %d cadeiras vagas' % nv, stf.first.inner_text()), stf.first.inner_text()[:80] if stf.count() else '')
    ev = G(pg, 'g.evento')
    primeiro = pg.evaluate("()=>{const e=document.querySelector('.fila-cards [data-pend]');return e?e.getAttribute('data-pend'):null}")
    ok('D6: a crise do mês é o primeiro cartão da Mesa', ev is None or primeiro == 'crise', (primeiro, bool(ev)))
    ok('D6: nenhum cartão "Vaga no STF" repetido', pg.locator('.fila-cards [data-pend=stf]').count() <= 1)
    stf.first.locator('button').filter(has_text='Indicar').first.click(timeout=4000) if stf.count() else None
    pg.wait_for_timeout(700)
    ok('D6: "Indicar" abre a seleção para uma das cadeiras', pg.locator('.modal-wrap, .gav-wrap').count() >= 1)
    fecha(pg)
    pg.evaluate("()=>{const e=document.querySelector('[data-precisa]');if(e)e.scrollIntoView({block:'start'})}"); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/d6_mesa_1440.png')

    # ---------- D3: manchetes ----------
    r = pg.evaluate("""()=>{const X=__X(); const n=['Rui','Costa','Lula'];
      return [X.bancaFrase('APROVAÇÃO DE LULA DESPENCA PARA 55%', ['Rui','Costa']), X.bancaFrase('RUI COSTA PROMETE AMPLIAR A ISENÇÃO DO IR ACIMA DE R$ 5 MIL', ['Rui','Costa']),
        X.bancaFrase('STF DERRUBA MP DA ISENÇÃO DO IR; PT E PL COMEMORAM EM SP/SP', []), X.bancaFrase('TARCÍSIO ENTRA NA DISPUTA E PSD ESPERA', ['Tarcísio']), X.bancaFrase('PCDOB E REPUBLICANOS FECHAM COM O PIB', [])]}""")
    print('   bancaFrase:', r)
    ok('D3: "Lula" preservado', r[0].startswith('Aprovação de Lula despenca'), r[0])
    ok('D3: nome, IR e R$ preservados', 'Rui Costa' in r[1] and ' IR ' in r[1] and 'R$ 5 mil' in r[1], r[1])
    ok('D3: STF, IR, PT, PL e UF preservados', 'STF' in r[2] and ' IR' in r[2] and 'PT e PL' in r[2] and 'SP/SP' in r[2], r[2])
    ok('D3: nome com acento preservado', r[3].startswith('Tarcísio'), r[3])
    ok('D3: siglas de partidos e PIB', 'PCdoB' in r[4] and 'Republicanos' in r[4] and 'PIB' in r[4], r[4])
    # posse: promessa curta, sem parêntese e com siglas
    pos = pg.evaluate("""()=>{const X=__X(); const out={curta:{}};
      for(const pm of X.PROMESSAS){ out.curta[pm.k]=X.nomeCurto?X.nomeCurto(pm):null }
      const g=structuredClone(__QV().gRef.current); const E=X.elEnsure(g); g.minProp={lista:[{id:1}],hist:[{a:1}],eng:{justica:3},leal:{},vazou:{},usados:[],seq:5,ger:null,aj:null};
      let txt=null; for(let i=0;i<30&&!(txt&&/isenção/.test(txt));i++){ const h=structuredClone(g); X.elPosse(h,{nome:'Fulano Teste'+i,sigla:'PSD',uf:'SP',bloco:'PSD'}); txt=h.feed[0].txt; out.eng=h.minProp.eng; out.lista=h.minProp.lista.length; out.hist=h.minProp.hist.length }
      out.txt=txt; return out}""")
    print('   posse:', pos['txt'])
    ok('D3: promessa da posse sem parêntese e com IR/R$ preservados', pos['txt'] and '(' not in pos['txt'] and ('isenção do IR acima de R$ 5 mil' in pos['txt'] or 'isenção' not in pos['txt']), pos['txt'])
    ok('D3: nomeCurto existe', pos['curta'].get('isencao_ir') == 'ampliar a isenção do IR acima de R$ 5 mil', pos['curta'].get('isencao_ir'))
    ok('B12: a posse de um sucessor zera ideias engavetadas e propostas do governo anterior', pos['eng'] == {} and pos['lista'] == 0 and pos['hist'] == 0, (pos['eng'], pos['lista'], pos['hist']))
    rep = pg.evaluate("()=>__X().X_IMPRENSA.map(x=>x[0])")
    ok('Conformidade: repórter fictício "Rodrigo Tavares" foi trocado', 'Rodrigo Tavares' not in rep, rep)

    # ---------- D4: selo do balão ----------
    pg.evaluate("()=>{const c=document.createElement('div');c.className='cn';c.id='tst-cn';c.style.display='none';const b=document.createElement('div');b.className='cn-bal';b.style.fontSize='20px';b.innerHTML='<span class=\"selo-sim\" id=\"tst-selo\">simulado</span>';c.appendChild(b);document.body.appendChild(c)}")
    fs = pg.evaluate("()=>getComputedStyle(document.getElementById('tst-selo')).fontSize")
    ok('D4: selo "simulado" do balão com 12px', fs == '12px', fs)
    pg.evaluate("()=>document.getElementById('tst-cn').remove()")

    # ---------- D9: toast na fila, topo direito, nunca sobre gaveta ou modal ----------
    ids = pg.evaluate("()=>Object.keys(__X().MARCOMAP).slice(0,2)")
    SET(pg, "n.novoMarco=%s" % json.dumps(ids[:1]))
    pg.wait_for_timeout(600)
    t = pg.locator('[data-toast]')
    box = t.first.bounding_box() if t.count() else None
    ok('D9: toast de conquista aparece', t.count() == 1, t.first.inner_text()[:60] if t.count() else '')
    if box: ok('D9: toast no topo direito', box['y'] < 140 and box['x'] + box['width'] > 1440 - 40 and box['x'] > 700, box)
    pg.screenshot(path=OUT + '/d9_toast_1440.png')
    # com a gaveta aberta, o próximo aviso espera
    pg.wait_for_timeout(6300)
    ok('D9: toast some depois de 6 s', pg.locator('[data-toast]').count() == 0)
    stf.first.click(timeout=3000) if stf.count() else None
    pg.wait_for_timeout(600)
    ok('D9: gaveta aberta', pg.locator('.gav-wrap').count() >= 1)
    SET(pg, "n.novoMarco=%s" % json.dumps(ids[1:2]))
    pg.wait_for_timeout(1500)
    ok('D9: com gaveta aberta o toast não aparece por cima', pg.locator('[data-toast]').count() == 0)
    fecha(pg); pg.wait_for_timeout(1500)
    ok('D9: ao fechar a gaveta o toast da fila aparece', pg.locator('[data-toast]').count() == 1)
    z = pg.evaluate("()=>{const t=document.querySelector('[data-toast]');return t?parseInt(getComputedStyle(t).zIndex):null}")
    ok('D9: z-index do toast abaixo das gavetas (55) e dos modais', z is not None and z < 55, z)
    pg.wait_for_timeout(6300)

    # ---------- D2, D8, D5: Configurações ----------
    SET(pg, "n.mes=49;n.el.mandatos=1")
    pg.locator('button[aria-label^="Configurações"]').click(timeout=4000); pg.wait_for_timeout(900)
    lab = pg.evaluate("()=>{const s=document.querySelector('.modal-wrap [data-qv-slot].border-ouro, .modal-wrap [data-qv-slot]');return s?s.innerText:null}")
    ok('D2: slot de presidente recém-empossado diz "1º mandato"', lab and 'mês 1 do 1º mandato' in lab, (lab or '')[:120].replace('\n', ' | '))
    r1 = pg.evaluate("()=>{const L=[...document.querySelectorAll('.modal-wrap [data-qv-slot]')].map(e=>e.getBoundingClientRect());return L.map(r=>[Math.round(r.x),Math.round(r.y)])}")
    ok('D8: slots em grade de 2 colunas', len(r1) >= 4 and r1[0][1] == r1[1][1] and r1[1][0] > r1[0][0] and r1[2][1] > r1[0][1] and r1[2][0] == r1[0][0], r1)
    pg.evaluate("()=>{const e=document.querySelector('.modal-wrap [data-qv-saves]');if(e)e.scrollIntoView({block:'start'})}"); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/d8_config_1440.png')
    cc = contraste(pg, '.modal-wrap')
    ok('D5: Configurações sem texto abaixo de 4,5:1', not cc, cc[:6])
    mot = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap *')].filter(e=>/Motor local|Motor de|descri/i.test(e.textContent)&&e.children.length===0).length")
    fecha(pg)
    SET(pg, "n.mes=13;n.el.mandatos=0")

    # ---------- D5: modal de votação ----------
    SET(pg, "n.acoes=5;n.pes.energia=90")
    pg.fill('#caixa', 'Ampliar a isenção do Imposto de Renda para quem ganha até R$ 7 mil'); click(pg, 'Assinar e enviar', 2200)
    for _ in range(4):
        bb = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
        pick = next((x for x in bb if re.match(r'^(Levar a voto|Votar agora|Enviar ao Congresso|Votar)', x)), None)
        if not pick: break
        try: pg.locator('.modal-wrap button').filter(has_text=pick).first.click(timeout=3000)
        except Exception: break
        pg.wait_for_timeout(1200)
        if pg.locator('.modal-wrap ul.text-xs li b').count(): break
    tr = pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^3×'))
    if tr.count(): tr.first.click(timeout=3000)
    pg.wait_for_timeout(2500)
    pg.screenshot(path=OUT + '/d5_votacao_1440.png')
    cc = contraste(pg, '.modal-wrap')
    print('   lista de votos em curso:', pg.evaluate("()=>document.querySelectorAll('.modal-wrap ul.text-xs li').length"))
    ok('D5: modal de votação (apuração em curso) sem texto abaixo de 4,5:1', not cc, cc[:6])
    sk = pg.locator('.modal-wrap button:not([disabled])').filter(has_text='Pular para o resultado')
    if sk.count(): sk.first.click(timeout=3000); pg.wait_for_timeout(1800)
    pg.screenshot(path=OUT + '/d5_votacao_resultado_1440.png')
    cc = contraste(pg, '.modal-wrap')
    ok('D5: modal de votação (resultado) sem texto abaixo de 4,5:1', not cc, cc[:8])
    for _ in range(6):
        sk = pg.locator('.modal-wrap button:not([disabled])').filter(has_text=re.compile(r'^(Pular para o resultado|Continuar)'))
        if not sk.count(): break
        sk.first.click(timeout=3000); pg.wait_for_timeout(1500)
    for _ in range(4):
        bb = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button:not([disabled])')].map(b=>b.innerText.trim())")
        pick = next((x for x in bb if re.match(r'^(Concluir|Aplicar|Fechar|Continuar|Encerrar|Ver resultado|Apurar|Entendi|OK|Voltar|Retirar proposta)', x)), None)
        if not pick: break
        try: pg.locator('.modal-wrap button').filter(has_text=pick).first.click(timeout=3000)
        except Exception: break
        pg.wait_for_timeout(900)
    print('   botões ao fechar a votação:', pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim()).slice(0,10)"))
    fecha(pg)

    # ---------- D7: title nos truncados ----------
    falta = {}
    for sec, chip in [('pais', 'mapa'), ('pais', 'seguranca'), ('poder', 'congresso'), ('mesa', None)]:
        try:
            vai(pg, sec, chip); fecha(pg)
            falta[sec + '/' + str(chip)] = pg.evaluate("()=>[...document.querySelectorAll('#root .truncate')].filter(e=>e.getClientRects().length&&!e.getAttribute('title')&&(e.textContent||'').trim()!=='—').map(e=>(e.textContent||'').trim().slice(0,30))")
        except Exception as e: falta[sec + '/' + str(chip)] = ['ERRO ' + str(e)[:60]]
    ok('D7: todo span.truncate visível tem title (mapa, segurança, Congresso, Mesa)', all(not v for v in falta.values()), {k: v[:4] for k, v in falta.items() if v})
    vai(pg, 'pais', 'mapa'); pg.screenshot(path=OUT + '/d7_mapa_1440.png')

    # ---------- D10: modo leve ----------
    vai(pg, 'mesa')
    SET(pg, "n.el.pj={id:'teste',nome:'Fulana Oposição',sigla:'PSD',bloco:'PSD',uf:'SP',ideo:{eco:20,soc:20},camp:'centro'}")
    ok('D10: modo leve mostra o cartão com atalhos', pg.locator('[data-modo-leve]').count() == 1 and pg.locator('[data-modo-leve] button').count() >= 3, pg.locator('[data-modo-leve]').inner_text()[:100] if pg.locator('[data-modo-leve]').count() else '')
    ok('D10: sem a caixa de decisão cinza nem "Assinar e enviar"', pg.locator('#caixa').count() == 0 and pg.locator('button').filter(has_text='Assinar e enviar').count() == 0)
    pg.screenshot(path=OUT + '/d10_modo_leve_1440.png')
    if pg.locator('[data-modo-leve] [data-ml=x]').count(): pg.locator('[data-modo-leve] [data-ml=x]').click(timeout=3000); pg.wait_for_timeout(500)
    ok('D10: atalho "Abrir o X" leva à seção X', G(pg, 'g.ui.sec') == 'x', G(pg, 'g.ui.sec'))
    SET(pg, "n.el.pj=null;n.ui.sec='mesa'")
    pg.set_viewport_size({'width': 1280, 'height': 800}); pg.wait_for_timeout(300); SET(pg, "n.el.pj={id:'teste',nome:'Fulana Oposição',sigla:'PSD',bloco:'PSD',uf:'SP',ideo:{eco:20,soc:20},camp:'centro'}"); pg.screenshot(path=OUT + '/d10_modo_leve_1280.png'); SET(pg, "n.el.pj=null;n.ui.sec='mesa'"); pg.set_viewport_size({'width': 1440, 'height': 900})
    ok('D10: fora do modo leve a caixa de decisão volta', pg.locator('#caixa').count() == 1)

    # ---------- 1280x800 ----------
    pg.set_viewport_size({'width': 1280, 'height': 800}); pg.wait_for_timeout(400)
    vai(pg, 'mesa'); pg.evaluate("()=>{const e=document.querySelector('[data-precisa]');if(e)e.scrollIntoView({block:'start'})}"); pg.wait_for_timeout(300); pg.screenshot(path=OUT + '/d6_mesa_1280.png')
    pg.locator('button[aria-label^="Configurações"]').click(timeout=4000); pg.wait_for_timeout(900); pg.evaluate("()=>{const e=document.querySelector('.modal-wrap [data-qv-saves]');if(e)e.scrollIntoView({block:'start'})}"); pg.wait_for_timeout(300); pg.screenshot(path=OUT + '/d8_config_1280.png')
    r2 = pg.evaluate("()=>{const L=[...document.querySelectorAll('.modal-wrap [data-qv-slot]')].map(e=>e.getBoundingClientRect());return L.map(r=>[Math.round(r.x),Math.round(r.y)])}")
    ok('D8: 2 colunas também em 1280', len(r2) >= 4 and r2[0][1] == r2[1][1] and r2[2][0] == r2[0][0], r2)
    fecha(pg)
    vai(pg, 'pais', 'mapa'); pg.screenshot(path=OUT + '/d7_mapa_1280.png')
    falta = pg.evaluate("()=>[...document.querySelectorAll('#root .truncate')].filter(e=>e.getClientRects().length&&!e.getAttribute('title')&&(e.textContent||'').trim()!=='—').map(e=>(e.textContent||'').trim().slice(0,30))")
    ok('D7: sem truncado sem title em 1280 (mapa)', not falta, falta[:5])
    SET(pg, "n.novoMarco=%s" % json.dumps(ids[:1])); pg.wait_for_timeout(600); pg.screenshot(path=OUT + '/d9_toast_1280.png')
    ok('0 erros de página e de console', not errs, errs[:3])
    b.close()
print('\nRESULTADO: %d/%d verificações OK' % (sum(checks), len(checks)))
sys.exit(0 if all(checks) else 1)
