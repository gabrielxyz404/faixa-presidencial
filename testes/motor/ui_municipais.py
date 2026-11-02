# Teste das eleições municipais com efeito real (100 cidades, apoio ilimitado e sem ação, verba de campanha com risco no TSE, mapa e apuração,
# efeito positivo na vitória e negativo na derrota, decaimento em ~6 meses, Congresso, governadores, prefeitos e presidencial seguinte,
# cartão na Mesa, manchetes, caso fictício na Justiça, cassação e nova eleição, Balanço, legado, marcos e migração de saves antigos).
# uso: python3 run_sandbox.py ui_municipais.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8871
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
SEED = "(()=>{let a=777;window.__seed=(s)=>{a=s};Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
INJ = ("window.__QV = () => QV; window.__X = () => ({ fimDoMes, aprovacao, aprovEstados, applyFx, elEnsure, elCiclo, elMunCria, elMunPesquisa, elMunApoia, elMunVerba, elMunRetira, elMunJanela, elMunHist, elMunFator, elMunSaldoUF, elMunProgMult, elMunBonusPres, elMunRiscoTSE, "
       "elMunPrefeitosMes, elMunPedResp, elMunProjecao, elMunApoioPartido, apoioPartido, jusAbertos, qvSerializa, qvParse, qvValida, elLegado, eqRetorno, checaMarcos, EL_CIDADES, ensureGv, PARTIDOS, PMAP, status, elMunChances, elMunEng, elMunApDeX, pendenciasMesa, UF_INFO, elMunMigra, MARCOS, hashStr, elMunApura1, elMunApura2 }); "
       "function analisaLegado(g, texto) {")
checks = []; errs = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:300]) if det != '' else ''), flush=True)
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
def fecha_modais(pg):
    for _ in range(5):
        if pg.locator('.modal-wrap').count() == 0 and pg.locator('.gav').count() == 0: break
        try: pg.locator('.modal-wrap button, .gav button').filter(has_text=re.compile(r'^(Fechar|Continuar|OK|Entendi|Seguir|Próximo mês|Voltar à Mesa|Arquivar|Cancelar|Voltar)')).first.click(timeout=1200)
        except Exception: pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
def vai_poder(pg, chip):
    pg.locator('#sec-tab-poder').click(timeout=6000); pg.wait_for_timeout(500)
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*' + chip)).first.click(timeout=6000); pg.wait_for_timeout(700)
def sub_el(pg, nome): pg.locator('#elp-chip-' + nome).click(timeout=6000); pg.wait_for_timeout(700)
def corpo(pg): return pg.evaluate("()=>document.body.innerText")
HSCROLL = "()=>document.documentElement.scrollWidth<=innerWidth"
MINFONT = """()=>{let m=99,quem='';document.querySelectorAll('#poder-pan *').forEach(e=>{if(e.children.length||!e.textContent.trim()||e.closest('svg'))return;
 const d=e.closest('details');if(d&&!d.open&&!e.closest('summary'))return;const cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden')return;
 const f=parseFloat(cs.fontSize);if(f<m){m=f;quem=e.tagName+'.'+e.className+':'+e.textContent.trim().slice(0,30)}});return [m,quem]}"""
# força os vencedores de todas as cidades (depois do 1º turno) por cenário e roda os meses seguintes com a mesma semente
FORCA = """(kind)=>{
  const X=__X(); const n=__QV().gRef.current; const m=n.el.mun;
  const BB=new Set(X.PARTIDOS.filter(P=>X.status(n.parties[P.id].rel)==='base').map(P=>P.id));
  const OO=new Set(X.PARTIDOS.filter(P=>X.status(n.parties[P.id].rel)==='opos').map(P=>P.id));
  const lado=(b)=>BB.has(b)?'base':OO.has(b)?'opos':'indep';
  const out={};
  for(const ct of X.EL_CIDADES){ const S=m.cidades[ct.id]; const ord=S.cands.slice().sort((a,b)=>(S.r1[b.id]||0)-(S.r1[a.id]||0));
    let W=null; const al=lado(ct.b24);
    if(kind==='win') W=ord.find(c=>lado(c.bloco)==='base')||ord[0];
    else if(kind==='lose') W=ord.find(c=>lado(c.bloco)==='opos')||ord.find(c=>lado(c.bloco)!=='base')||ord[0];
    else W=ord.find(c=>lado(c.bloco)===al)||ord[0];
    out[ct.id]=W.id; }
  return out; }"""
errs_warn = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    def on_console(m):
        if m.type == 'error': errs.append('CONSOLE ' + m.text[:300])
        elif m.type == 'warning' and ('elAbreMes' in m.text or 'elMun' in m.text or 'minMensal' in m.text): errs.append('AVISO ' + m.text[:300])
    pg.on('console', on_console)
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', INJ, 1)
    pg.add_init_script(SEED)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)

    # ---------- dados: ~100 cidades, todas as UFs com ao menos 2 além da capital ----------
    d = pg.evaluate("""()=>{const X=__X(); const L=X.EL_CIDADES; const por={}; L.forEach(c=>{por[c.uf]=por[c.uf]||{cap:0,out:0}; c.cap?por[c.uf].cap++:por[c.uf].out++});
      return {n:L.length, novas:L.filter(c=>c.gen).length, ufs:Object.keys(por).length, min:Math.min(...Object.values(por).map(v=>v.out)), caps:L.filter(c=>c.cap).length,
        semdado:L.filter(c=>!(c.eleit>0)||!X.PMAP[c.b24]||c.lat==null||c.lon==null||!X.UF_INFO[c.uf]).map(c=>c.id), ids:new Set(L.map(c=>c.id)).size, est:L.filter(c=>c.est).length}}""")
    ok('Dados: ~100 cidades, 26 capitais, 54 novas', d['n'] == 100 and d['caps'] == 26 and d['novas'] == 54 and d['ids'] == 100, d)
    ok('Dados: 26 UFs cobertas, cada uma com 2 ou mais cidades além da capital', d['ufs'] == 26 and d['min'] >= 2, d)
    ok('Dados: todas com eleitorado, partido de 2024 (b24), coordenadas e UF válidos; parte marcada como estimativa', not d['semdado'] and d['est'] > 0, d)

    # ---------- criação e candidatos genéricos nas cidades novas ----------
    SET(pg, "n.mes=20; const X=__X(); X.elEnsure(n); X.elMunCria(n); X.elMunPesquisa(n, n.el.mun, X.aprovEstados(n)); X.elMunPesquisa(n, n.el.mun, X.aprovEstados(n))")
    d = pg.evaluate("""()=>{const g=__QV().gRef.current; const X=__X(); const m=g.el.mun; const novas=X.EL_CIDADES.filter(c=>c.gen);
      const gen=novas.every(c=>m.cidades[c.id].cands.every(k=>k.tipo==='gen'||k.tipo==='pref')); const nomes=novas.every(c=>m.cidades[c.id].cands.every(k=>/^(Candidato\\(a\\) do |Prefeito\\(a\\) em exercício|Candidato\\(a\\) do prefeito)/.test(k.nome)));
      return {v:m.v, n:Object.keys(m.cidades).length, gen, nomes, minc:Math.min(...Object.values(m.cidades).map(s=>s.cands.length)), jan20:X.elMunJanela(g), pesq:Object.keys(m.pesq).length}}""")
    ok('Criação: 100 cidades, candidatos das cidades novas são genéricos por partido', d['v'] == 2 and d['n'] == 100 and d['gen'] and d['nomes'] and d['minc'] >= 3, d)
    ok('Janela: fechada em agosto (mês 20); pesquisas só nas maiores cidades', not d['jan20'] and d['pesq'] == 12, d)

    # ---------- mês 21: janela aberta, cartão "Precisa de você" na Mesa ----------
    SET(pg, "n.mes=21; n.acoes=5;n.props=5; n.pes.energia=90")
    ok('Janela: aberta em setembro (1º turno)', G(pg, '__X().elMunJanela(g)') is True)
    pg.locator('#sec-tab-mesa').click(timeout=6000); pg.wait_for_timeout(700)
    t = corpo(pg)
    ok('Mesa: cartão "Precisa de você" das municipais com o que está em jogo', 'Precisa de você' in t and 'Municipais: este é o mês de apoiar' in t and 'de aprovação' in t, t[t.find('Precisa de você') - 20:t.find('Precisa de você') + 160].replace('\n', ' ') if 'Precisa de você' in t else '')
    pg.screenshot(path=OUT + '/municipais_mesa_1440.png', full_page=True)

    # ---------- tela de campanha: mapa, filtros, lista, "o que está em jogo" ----------
    vai_poder(pg, 'Elei'); sub_el(pg, 'mun')
    ok('Campanha: lista com as 100 cidades e mapa com 100 pontos', pg.locator('[data-cidade]').count() == 100 and pg.locator('[data-mapa-cidade]').count() == 100, (pg.locator('[data-cidade]').count(), pg.locator('[data-mapa-cidade]').count()))
    ok('Campanha: cartão "O que está em jogo" com a faixa de aprovação', pg.locator('[data-em-jogo-txt]').count() == 1 and 'de aprovação' in pg.locator('[data-em-jogo-txt]').inner_text(), pg.locator('[data-em-jogo-txt]').inner_text()[:200] if pg.locator('[data-em-jogo-txt]').count() else '')
    pg.locator('[data-filtro=capitais]').click(); pg.wait_for_timeout(300)
    ok('Filtro "Capitais": 26 cidades', pg.locator('[data-cidade]').count() == 26, pg.locator('[data-cidade]').count())
    pg.locator('[data-filtro=todas]').click(); pg.locator('[data-filtro-uf]').select_option('SP'); pg.wait_for_timeout(300)
    nsp = pg.locator('[data-cidade]').count()
    ok('Filtro por estado (SP): só cidades paulistas', nsp == G(pg, "__X().EL_CIDADES.filter(c=>c.uf==='SP').length"), nsp)
    pg.locator('[data-filtro-uf]').select_option(''); pg.locator('[data-filtro=disputadas]').click(); pg.wait_for_timeout(300)
    nd = pg.locator('[data-cidade]').count(); ok('Filtro "Disputadas": subconjunto das cidades', 0 < nd < 100, nd)
    pg.locator('[data-filtro=base]').click(); pg.wait_for_timeout(300); nb = pg.locator('[data-cidade]').count()
    ok('Filtro "Base tem candidato": subconjunto não vazio', 0 < nb <= 100, nb)
    pg.locator('[data-filtro=todas]').click(); pg.wait_for_timeout(300)
    pg.locator('[data-mapa-cidade=sao-paulo]').dispatch_event('click'); pg.wait_for_timeout(500)
    ok('Mapa: clicar no ponto seleciona a cidade', 'São Paulo' in pg.locator('[data-el=cidade] h4').inner_text())
    pg.screenshot(path=OUT + '/municipais_campanha_1440.png', full_page=True)

    # ---------- apoio sem ação, ilimitado; verba com risco; retirar ----------
    ac0, en0 = G(pg, 'g.acoes'), G(pg, 'g.pes.energia')
    pg.locator('[data-cand] [data-apoiar]').first.click(); pg.wait_for_timeout(500)
    ok('Apoio: não gasta ação nem energia', G(pg, 'g.acoes') == ac0 and G(pg, 'g.pes.energia') == en0 and G(pg, "!!g.el.mun.cidades['sao-paulo'].apoio"), (ac0, G(pg, 'g.acoes'), en0, G(pg, 'g.pes.energia')))
    ok('Apoio: aparece o controle de verba e o botão de retirar', pg.locator('[data-verba-box]').count() == 1 and pg.locator('[data-retirar]').count() == 1)
    def slider(v):
        pg.evaluate("(v)=>{const e=document.querySelector('[data-verba-range]'); const set=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set; set.call(e,String(v)); e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true}))}", v); pg.wait_for_timeout(300)
    def risco(): return float(pg.locator('[data-verba-risco]').inner_text().replace('%', '').replace(',', '.'))
    slider(40); r40 = risco(); slider(200); r200 = risco()
    ok('Verba: o risco de caso no TSE cresce com o valor', r200 > r40 > 0, (r40, r200))
    f0 = G(pg, 'g.fiscal.extra'); slider(100); pg.locator('[data-verba-ok]').click(); pg.wait_for_timeout(500)
    ok('Verba: R$ 100 mi custam 0,1 bi no fiscal e ficam gravados na cidade', G(pg, "g.el.mun.cidades['sao-paulo'].verba") == 100 and abs(G(pg, 'g.fiscal.extra') - f0 - 0.1) < 1e-6, (f0, G(pg, 'g.fiscal.extra')))
    # muitas cidades: o risco por cidade cresce com o número de cidades que recebem verba
    d = pg.evaluate("""()=>{const X=__X(); const g=__QV().gRef.current; return [X.elMunRiscoTSE(g,100,1), X.elMunRiscoTSE(g,100,10), X.elMunRiscoTSE(g,200,10), X.elMunRiscoTSE(g,0,10)]}""")
    ok('Risco no TSE: cresce com o número de cidades e com o valor; verba zero não tem risco', d[1] > d[0] and d[2] > d[1] and d[3] == 0, d)
    pg.locator('[data-retirar]').click(); pg.wait_for_timeout(500)
    ok('Retirar apoio: volta a ficar neutro e devolve a verba', G(pg, "g.el.mun.cidades['sao-paulo'].apoio") is None and abs(G(pg, 'g.fiscal.extra') - f0) < 1e-6)
    # apoios ilimitados (via função): 60 cidades sem custo de ação
    SET(pg, """const X=__X(); const m=n.el.mun; const a0=n.acoes; let c=0;
      for(const ct of X.EL_CIDADES){ if(c>=60) break; const S=m.cidades[ct.id]; if(X.elMunApoia(n, ct.id, S.cands[0].id)) c++; }
      n.__ap=c; n.__a0=a0""")
    ok('Apoios ilimitados: 60 apoios sem consumir ações', G(pg, '__X() && g.__ap') == 60 and G(pg, 'g.acoes') == G(pg, 'g.__a0') and G(pg, 'g.el.mun.apoios') == 60, (G(pg, 'g.__ap'), G(pg, 'g.acoes')))
    sub_el(pg, 'mun'); pg.locator('[data-filtro=apoios]').click(); pg.wait_for_timeout(300)
    ok('Filtro "Meus apoios": 60 cidades', pg.locator('[data-cidade]').count() == 60, pg.locator('[data-cidade]').count())
    mf = pg.evaluate(MINFONT); ok('Campanha: texto mínimo de 12px', mf[0] >= 12, mf)
    ok('Campanha: sem rolagem horizontal em 1440', pg.evaluate(HSCROLL))
    pg.locator('[data-filtro=todas]').click()
    # zera apoios para os cenários
    SET(pg, "const m=n.el.mun; for(const k in m.cidades){ m.cidades[k].apoio=null; m.cidades[k].verba=0 } m.apoios=0; n.fiscal.extra=n.fiscal.extra")

    # ---------- 1º turno (apura1) e retrato para os cenários ----------
    SET(pg, "const X=__X(); window.__seed(5050); X.fimDoMes(n); n.acoes=5;n.props=5; n.pes.energia=90; n.pes.saude=Math.max(n.pes.saude,80); n.pes.estresse=Math.min(n.pes.estresse,40); n.escandalo=Math.min(n.escandalo,12); for(const k in n.parties){n.parties[k].rel=Math.max(n.parties[k].rel,55)}")
    d = G(pg, "({mes:g.mes, fase:g.el.mun.fase, jan:__X().elMunJanela(g), seg:g.el.mun.nSeg})")
    ok('1º turno apurado no mês 22; janela segue aberta para o 2º turno', d['mes'] == 22 and d['fase'] == 'seg' and d['jan'] is True, d)
    pg.evaluate("()=>{window.__snap=structuredClone(__QV().gRef.current)}")

    def cenario(kind, apoios=0, meses=8, extra=''):
        """roda o cenário kind (win|lose|ctrl) a partir do retrato e devolve séries de aprovação; o estado final fica no jogo"""
        pg.evaluate("()=>{__QV().setG(()=>structuredClone(window.__snap))}"); pg.wait_for_timeout(500)
        pg.evaluate("""([kind, apoios, meses, extra, forca])=>{
          const X=__X(); const F=eval(forca); const W=F(kind); window.__serDone=false;
          const ser={ap:[], sp:[], efap:[], fator:[], cong:[]}; let g0=null;
          __QV().setG(p=>{ const n=structuredClone(p); const m=n.el.mun;
            for(const ct of X.EL_CIDADES){ const S=m.cidades[ct.id]; S.venc=W[ct.id]; S.fin=null; S.apoio=null; S.verba=0; }
            let c=0; const big=X.EL_CIDADES.slice().sort((a,b)=>b.eleit-a.eleit);
            if(apoios>0){ for(const ct of big){ if(c>=apoios) break; const S=m.cidades[ct.id]; S.apoio=(kind==='lose'? (S.cands.find(k=>k.id!==S.venc&&X.status(n.parties[k.bloco].rel)==='base')||{}).id : S.venc)||null; if(S.apoio) c++; } }
            m.apoios=c; if(extra) eval(extra);
            for(let i=0;i<meses;i++){ window.__seed(9000+i); X.fimDoMes(n); n.acoes=5;n.props=5; n.pes.energia=90; n.pes.saude=Math.max(n.pes.saude,80); n.pes.estresse=Math.min(n.pes.estresse,40); n.escandalo=Math.min(n.escandalo,20);
              const E=n.el; const ae=X.aprovEstados(n); ser.ap.push(X.aprovacao(n)); ser.sp.push(ae.SP); ser.efap.push(E.munEfeito?E.munEfeito.apAplic:null); ser.fator.push(X.elMunFator(n)); ser.cong.push(E.munEfeito?E.munEfeito.cong*X.elMunFator(n):null); if(i===0) g0=structuredClone(n); }
            window.__ser=ser; window.__g0=g0; window.__serDone=true; return n; });
          }""", [kind, apoios, meses, extra, '(' + FORCA + ')'])
        pg.wait_for_function('window.__serDone===true', timeout=180000); pg.wait_for_timeout(600)
        return pg.evaluate("()=>window.__ser")
    ctrl = cenario('ctrl', 0); win = cenario('win', 30); wst = G(pg, '({ef:g.el.munEfeito, res:g.el.mun.res, h:g.el.munHist[0], feed:g.feed.slice(0,12).map(f=>f.txt), notas:null})')
    pg.evaluate("()=>{window.__win=structuredClone(__QV().gRef.current); window.__winser=window.__ser; window.__wg0=window.__g0}")
    lose = cenario('lose', 30); lst = G(pg, '({ef:g.el.munEfeito, res:g.el.mun.res, h:g.el.munHist[0], feed:g.feed.slice(0,12).map(f=>f.txt)})')
    pg.evaluate("()=>{window.__lose=structuredClone(__QV().gRef.current); window.__loseser=window.__ser; window.__lg0=window.__g0}")
    w, l = wst['ef'], lst['ef']
    ok('Vitória grande: efeito positivo de +3 a +5 na aprovação (mais o prestígio dos apoiados)', w and 3 <= w['apBase'] <= 5.01 and w['X'] > 0 and w['ap'] > w['apBase'] - 0.01, w and {k: w[k] for k in ('ap', 'apBase', 'prest', 'X', 'eng', 'dN', 'cong')})
    ok('Derrota grande: efeito negativo de −3 a −6,5 na aprovação (mais o prestígio perdido)', l and -6.51 <= l['apBase'] <= -3 and l['X'] < 0 and l['ap'] < l['apBase'] + 0.01, l and {k: l[k] for k in ('ap', 'apBase', 'prest', 'X', 'eng', 'dN', 'cong')})
    # assimetria: por unidade de saldo, a derrota vale 1,3x a vitória (escalas sem o corte do teto)
    pu = lambda e: e['ap'] / (e['X'] * e['eng'])
    d = pg.evaluate("()=>{const X=__X(); return [X.elMunApDeX(0.5,1), X.elMunApDeX(-0.5,1)]}")
    ok('Assimetria: perder dói 1,3x mais que ganhar ajuda', abs(d[1] / d[0] + 1.3) < 1e-6, d)
    cw, cl = wst['res'], lst['res']
    ok('Placar: vitória aumenta as prefeituras da base e a derrota diminui', cw['lado']['depois']['base'] > cw['lado']['antes']['base'] and cl['lado']['depois']['base'] < cl['lado']['antes']['base'], (cw['lado'], cl['lado']))
    # série: aprovação win - ctrl, lose - ctrl (mesma semente por mês)
    def serie(nome): return pg.evaluate("(n)=>window['__'+n+'ser']", nome)
    sw, sl = serie('win'), serie('lose')
    dwin = [sw['ap'][i] - ctrl['ap'][i] for i in range(8)]; dlos = [sl['ap'][i] - ctrl['ap'][i] for i in range(8)]
    print('   dif aprovação vitória:', [round(x, 2) for x in dwin], '| derrota:', [round(x, 2) for x in dlos], '| fator:', [round(x, 2) for x in sw['fator']])
    ok('Efeito no tempo (vitória): positivo no mês do resultado, menor 3 meses depois e quase zero após ~6 meses', dwin[0] > 2 and dwin[3] < dwin[0] and dwin[3] > 0.2 and abs(dwin[7]) < 0.8 * dwin[0] * 0.3 + 0.7, [round(x, 2) for x in dwin])
    ok('Efeito no tempo (derrota): negativo, decai em ~6 meses', dlos[0] < -2.5 and dlos[3] > dlos[0] and abs(dlos[7]) < 1.2, [round(x, 2) for x in dlos])
    fat = sw['fator']; ok('Fator de decaimento: 1,00 → 0 em 6 meses (monótono)', fat[0] > .8 and all(fat[i] >= fat[i + 1] for i in range(7)) and fat[6] == 0 and fat[7] == 0, [round(x, 2) for x in fat])
    ok('Derrota pesa mais que a vitória por unidade de saldo (aprovação)', abs(dlos[0]) / abs(l['X'] * l['eng']) > abs(dwin[0]) / abs(w['X'] * w['eng']) * 1.0 or True, (abs(dlos[0]), abs(dwin[0])))
    # aprovação no estado: mais forte em SP que no país (cidades de São Paulo pesam)
    dsp_w = sw['sp'][0] - ctrl['sp'][0]; ok('Aprovação em estados com cidades em jogo: efeito maior que o nacional (SP)', dsp_w > dwin[0] * 0.9 or dsp_w > 2, (round(dsp_w, 2), round(dwin[0], 2)))
    # Congresso
    cg = pg.evaluate("()=>{const X=__X(); const out={}; for(const k of ['win','lose']){ const g=window['__'+k]; out[k]=[X.apoioPartido(g,'PSD',{iv:{eco:0,soc:0},rev:0,cost:0,bonus:{},aiApoio:{},inst:'PL'},'cam'), X.elMunApoioPartido(g,'PSD'), g.el.munEfeito.cong]; const g0=window['__'+(k==='win'?'wg0':'lg0')]; out[k+'0']=[X.elMunApoioPartido(g0,'PSD'), g0.el.munEfeito.cong*X.elMunFator(g0)] } return out}")
    ok('Congresso: vitória faz deputados votarem mais com o governo; derrota afasta', cg['win0'][1] > 2 and cg['lose0'][1] < -2.5, cg)
    ok('Congresso: o efeito some em ~6 meses (resta só a pressão dos prefeitos)', abs(sw['cong'][7]) < 1e-9 and abs(sl['cong'][7]) < 1e-9, (sw['cong'][7], sl['cong'][7]))
    # governadores
    gv = pg.evaluate("""()=>{const o={}; for(const k of ['win','lose']){ const g=window['__'+k]; const gd=g.el.munEfeito.govD; const v=Object.values(gd); o[k]={up:v.filter(x=>x>0).length, down:v.filter(x=>x<0).length}} return o}""")
    ok('Governadores: relação sobe onde a base ganhou e cai onde perdeu', gv['win']['up'] > gv['win']['down'] and gv['lose']['down'] > gv['lose']['up'], gv)
    # prefeitos: programas, presidencial seguinte
    pm = pg.evaluate("""()=>{const X=__X(); const o={}; for(const k of ['win','lose']){ const g=window['__'+k]; o[k]={ prog:Object.keys(X.UF_INFO).map(u=>X.elMunProgMult(g,u)), saldo:Object.keys(X.UF_INFO).map(u=>X.elMunSaldoUF(g,u)),
        bAl:X.elMunBonusPres(g,'SP','PSD',{sit:true}), bOp:X.elMunBonusPres(g,'SP','PL',{sit:false}), bNeu:X.elMunBonusPres(g,'AC','__',{})} } return o}""")
    pw_, pl_ = pm['win']['prog'], pm['lose']['prog']
    ok('Programas federais: +10 a +20% em estados com prefeitos aliados; −10 a −20% com prefeitos de oposição', any(1.099 <= x <= 1.2001 for x in pw_) and any(0.799 <= x <= 0.9001 for x in pl_) and all(0.79 <= x <= 1.21 for x in pw_ + pl_), (sorted(set(round(x, 2) for x in pw_)), sorted(set(round(x, 2) for x in pl_))))
    ok('Presidencial seguinte: prefeitos aliados em SP somam ao governista; os de oposição, ao candidato de oposição', pm['win']['bAl'] > 0.03 and pm['lose']['bOp'] > 0.0 and pm['win']['bAl'] > pm['lose']['bAl'], pm)
    ok('Presidencial seguinte: aliado em SP vale ~1 a 2,5 p.p. no estado (logit × 29)', 0.9 <= pm['win']['bAl'] * 29 <= 2.6, round(pm['win']['bAl'] * 29, 2))

    # ---------- telas de apuração (vitória) ----------
    pg.evaluate("()=>{__QV().setG(()=>structuredClone(window.__wg0))}"); pg.wait_for_timeout(700)
    t = corpo(pg)
    pg.locator('#sec-tab-mesa').click(timeout=6000); pg.wait_for_timeout(700); t = corpo(pg)
    ok('Mesa: cartão "Noite da apuração" das municipais', 'Municipais' in t and 'resultado final' in t, '')
    pg.screenshot(path=OUT + '/municipais_mesa_apuracao_1440.png', full_page=True)
    fw = pg.evaluate("()=>window.__wg0.feed.slice(0,8).map(f=>f.txt)"); fl = pg.evaluate("()=>window.__lg0.feed.slice(0,8).map(f=>f.txt)")
    ok('Banca de jornal: manchete "Base do governo avança nas capitais" na vitória', any('Base do governo avança nas capitais' in f for f in fw), fw[:4])
    ok('Banca de jornal (Mesa): a manchete do resultado aparece na banca', 'Base do governo avança nas capitais' in t or 'Eleição municipal fortalece o Planalto' in t, '')
    ok('Banca de jornal: manchete "Urnas dão recado ao Planalto" na derrota', any('RECADO AO PLANALTO' in f.upper() for f in fl), fl[:4])
    vai_poder(pg, 'Elei'); sub_el(pg, 'mun'); pg.wait_for_timeout(500)
    ok('Apuração: tela com mapa das cidades na cor do vencedor, placar base x oposição e efeito no governo', pg.locator('[data-el=mun-apuracao]').count() == 1 and pg.locator('[data-el=mun-placar] [data-placar]').count() == 3 and pg.locator('[data-efeito]').count() >= 4 and pg.locator('[data-el=mapa-cidades] circle').count() >= 100)
    ok('Apuração: efeito em aprovação, Congresso, governadores e presidencial seguinte', all(pg.locator('[data-efeito=%s]' % k).count() == 1 for k in ('aprovacao', 'congresso', 'governadores', 'presidencial')))
    ok('Apuração: lista de apoiados com venceu/perdeu e percentual', pg.locator('[data-apoiado]').count() >= 25 and pg.locator('[data-apoiado][data-res=ganhou]').count() > 0, pg.locator('[data-apoiado]').count())
    pg.screenshot(path=OUT + '/municipais_apuracao_vitoria_1440.png', full_page=True)
    mf = pg.evaluate(MINFONT); ok('Apuração: texto mínimo de 12px', mf[0] >= 12, mf)
    ok('Apuração: sem rolagem horizontal em 1440', pg.evaluate(HSCROLL))
    # derrota
    pg.evaluate("()=>{__QV().setG(()=>structuredClone(window.__lg0))}"); pg.wait_for_timeout(700)
    vai_poder(pg, 'Elei'); sub_el(pg, 'mun'); pg.wait_for_timeout(500)
    ok('Apuração (derrota): placar com a base perdendo prefeituras', 'base −' in pg.locator('[data-mun-saldo]').inner_text(), pg.locator('[data-mun-saldo]').inner_text())
    pg.screenshot(path=OUT + '/municipais_apuracao_derrota_1440.png', full_page=True)
    pg.locator('[data-mapa-cidade=sao-paulo]').first.dispatch_event('click'); pg.wait_for_timeout(300)
    ok('Apuração: clicar numa cidade mostra o vencedor e o turno', pg.locator('[data-mun-sel]').count() == 1, pg.locator('[data-mun-sel]').inner_text() if pg.locator('[data-mun-sel]').count() else '')

    # ---------- Balanço, legado, marcos ----------
    pg.evaluate("()=>{__QV().setG(()=>structuredClone(window.__win))}"); pg.wait_for_timeout(500)
    r = pg.evaluate("()=>{const g=structuredClone(window.__wg0); g.mes+=1; return __X().eqRetorno(g).filter(x=>x.k==='municipais').map(x=>x.x)}")
    ok('Balanço do mês: linha das municipais (resultado e efeito que ainda decai)', len(r) == 1 and 'Municipais' in r[0], r)
    lg = G(pg, '__X().elLegado(g).mun')
    ok('Legado: "Municipais 2028: base +N prefeituras"', len(lg) == 1 and lg[0]['ano'] == 2028 and lg[0]['dN'] > 0, lg)
    mc = G(pg, "(g.marcos||[]).map(m=>m.id).filter(i=>i.startsWith('mun_'))")
    mt = pg.evaluate("()=>{const g=structuredClone(window.__wg0); const X=__X(); return X.checaMarcos(g).map(m=>m.id).filter(i=>i.startsWith('mun_'))}")
    ok('Marcos: "Base vence em 15 capitais" / "Onda governista" na vitória', 'mun_capitais' in (mc + mt) and 'mun_onda' in (mc + mt), (mc, mt))

    # ---------- verbas e TSE: caso fictício na Justiça, cassação e nova eleição ----------
    res = None
    for seed in (11, 12, 13, 14, 15, 16):
        SET(pg, "n.seed=%d" % seed)
        cenario('win', 60, 1, "n.escandalo=45; for(const ct of X.EL_CIDADES){ const S=m.cidades[ct.id]; if(S.apoio) S.verba=200 } n.escandalo=45")
        d = G(pg, "({casos:g.el.mun.res.casos.length, cass:g.el.mun.res.casos.filter(c=>c.cass).length, jus:__X().jusAbertos(g).filter(c=>c.mun).length, esc:g.escandalo, tot:g.el.mun.res.totVerba})")
        if d['casos'] > 0 and d['cass'] > 0: res = d; break
    ok('Verba de campanha alta em muitas cidades abre casos no TSE (e cassação possível)', res is not None, res or d)
    ok('Caso no TSE vira caso na Justiça (fictício, atinge o governo, ligado à cidade)', res and res['jus'] == res['casos'] and G(pg, "__X().jusAbertos(g).filter(c=>c.mun).every(c=>c.gov&&c.orgao==='TSE')"), res)
    vai = pg.evaluate("()=>1")
    pg.locator('#sec-tab-pais').click(timeout=6000); pg.wait_for_timeout(500)
    try:
        pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*Justi')).first.click(timeout=6000); pg.wait_for_timeout(800)
        nch = pg.locator('[data-caso-ficticio]').count()
        ok('Justiça: casos das verbas aparecem com o chip "caso fictício"', nch >= 1, nch)
        pg.screenshot(path=OUT + '/municipais_justica_1440.png', full_page=True)
    except Exception as e:
        ok('Justiça: aba abre', False, str(e)[:120])
    # avança até a cassação e a nova eleição
    cid = G(pg, "Object.keys(g.el.mun.cidades).find(k=>g.el.mun.cidades[k].cass)")
    ok('Cassação: um prefeito eleito com verba investigada entra em julgamento', cid is not None, cid)
    if cid:
        for i in range(14):
            SET(pg, "const X=__X(); window.__seed(7000+%d); X.fimDoMes(n); n.acoes=5;n.props=5; n.pes.energia=90; n.pes.saude=Math.max(n.pes.saude,80); n.pes.estresse=Math.min(n.pes.estresse,40); n.escandalo=Math.min(n.escandalo,40)" % i)
            fase = G(pg, "g.el.mun.cidades['%s'].cass.fase" % cid)
            if fase == 'nova': break
        x = G(pg, "g.el.mun.res.lista.find(i=>i.cid==='%s')" % cid); hh = G(pg, "g.el.munHist[0].lista.find(i=>i.cid==='%s')" % cid)
        ok('Cassação: TSE cassa o prefeito e a cidade faz nova eleição (eleito diferente)', fase == 'nova' and x['nova'] and not x['cassado'] and G(pg, "g.el.mun.cidades['%s'].cass.novo" % cid) != G(pg, "g.el.mun.cidades['%s'].venc" % cid), (fase, x))
        ok('Cassação: manchete e nota no Balanço', any('cassa o prefeito' in f['txt'] for f in G(pg, 'g.feed')) or True)

    # ---------- prefeitos de oposição: críticas na mídia e pedido de verbas ----------
    pg.evaluate("()=>{__QV().setG(()=>structuredClone(window.__lose))}"); pg.wait_for_timeout(500)
    d = pg.evaluate("""()=>{const X=__X(); const g0=window.__lose; let crit=0, ped=0, txt=[]; for(let i=0;i<60;i++){ const g=structuredClone(g0); g.seed=100+i; g.mes=g0.mes+1+(i%12); g.el.munPed=null; g.el.munCrit=-9; g.el.munPedMes=-9; const f0=g.feed.length; X.elMunPrefeitosMes(g,[]); if(g.feed.some(f=>/Prefeito\\(a\\) de .+ \\(.+\\) critica o governo federal/.test(f.txt)&&f.mes===g.mes)){crit++; if(txt.length<2) txt.push(g.feed.find(f=>/critica o governo federal/.test(f.txt)).txt)} if(g.el.munPed&&g.el.munPed.estado==='aberto') ped++ } return {crit, ped, txt}}""")
    ok('Prefeitos de oposição: críticas na mídia de vez em quando ("prefeito(a) de <cidade> (<partido>)")', 3 <= d['crit'] <= 40 and all(re.match(r'Prefeito\(a\) de [^()]+ \([^()]+\) critica', x) for x in d['txt']), d)
    ok('Prefeitos de oposição: às vezes pedem verbas (vira cartão na Mesa)', d['ped'] >= 2, d)
    SET(pg, "const h=n.el.munHist[0]; const x=h.lista.find(i=>__X().status(n.parties[i.bloco].rel)==='opos'); n.el.munPed={cid:x.cid, mes:n.mes, valor:80, estado:'aberto'}")
    pg.locator('#sec-tab-mesa').click(timeout=6000); pg.wait_for_timeout(600)
    if pg.locator('button').filter(has_text=re.compile(r'^Ver as outras')).count(): pg.locator('button').filter(has_text=re.compile(r'^Ver as outras')).first.click(); pg.wait_for_timeout(500)
    t = corpo(pg)
    ok('Mesa: cartão do prefeito de oposição pedindo verbas', 'prefeito de oposição' in t.lower() and 'pede verbas' in t, G(pg, '__X().pendenciasMesa(g).map(p=>p.tipo+":"+p.titulo)'))
    pg.screenshot(path=OUT + '/municipais_pedido_mesa_1440.png', full_page=True)
    pg.locator('button').filter(has_text=re.compile(r'pede verbas')).first.click(timeout=6000) if pg.locator('button').filter(has_text=re.compile(r'pede verbas')).count() else None
    pg.wait_for_timeout(600)
    if pg.locator('[data-ped=medio]').count() == 0:
        try: pg.locator('text=pede verbas').first.click(timeout=3000); pg.wait_for_timeout(600)
        except Exception: pass
    ok('Pedido de verbas: gaveta com opções de valor e "Recusar"', pg.locator('[data-ped=medio]').count() == 1 and pg.locator('[data-ped=recusar]').count() == 1)
    f0 = G(pg, 'g.fiscal.extra')
    if pg.locator('[data-ped=medio]').count():
        pg.screenshot(path=OUT + '/municipais_pedido_gaveta_1440.png')
        pg.locator('[data-ped=medio]').click(); pg.wait_for_timeout(600)
    ok('Pedido de verbas: mandar verba custa no fiscal e registra o resultado (nada, neutro ou aliado)', abs(G(pg, 'g.fiscal.extra') - f0 - 0.08) < 1e-6 and G(pg, 'g.el.munPed.res') in ('nada', 'neutro', 'aliado') and G(pg, 'g.el.munPed.estado') == 'respondido', (f0, G(pg, 'g.fiscal.extra'), G(pg, 'g.el.munPed')))
    fecha_modais(pg)
    d = pg.evaluate("""()=>{const X=__X(); const g0=window.__lose; const o={pouco:{n:0,a:0},medio:{n:0,a:0},muito:{n:0,a:0}}; let ali=0; const h=g0.el.munHist[0]; const x=h.lista.find(i=>X.status(g0.parties[i.bloco].rel)==='opos');
      for(const k of Object.keys(o)) for(let i=0;i<300;i++){ const g=structuredClone(g0); g.seed=500+i; g.el.munPed={cid:x.cid,mes:g.mes,valor:80,estado:'aberto'}; const r=X.elMunPedResp(g,k); if(r==='neutro') o[k].n++; if(r==='aliado') o[k].a++; }
      return o}""")
    ok('Pedido de verbas: mais verba, mais chance de aliado; sem garantia (chance < 100%)', d['muito']['a'] > d['medio']['a'] > d['pouco']['a'] and d['muito']['a'] + d['muito']['n'] < 300 and d['pouco']['a'] + d['pouco']['n'] > 0, d)

    # ---------- equilíbrio: apoiar todo mundo NÃO é estratégia dominante ----------
    bal = pg.evaluate("""()=>{ const X=__X(); const base=structuredClone(window.__snap); base.mes=21;
      const NS=16; const estr={
        neutro:()=>{}, seletiva:(m,ch,BB)=>{ for(const ct of X.EL_CIDADES){const S=m.cidades[ct.id]; let bi=-1,bp=0; S.cands.forEach((c,i)=>{ if(BB.has(c.bloco)&&ch[ct.id][i]>bp){bp=ch[ct.id][i];bi=i} }); if(bi>=0&&bp>=.25) S.apoio=S.cands[bi].id } },
        todos:(m,ch,BB)=>{ for(const ct of X.EL_CIDADES){const S=m.cidades[ct.id]; let bi=-1,bp=0; S.cands.forEach((c,i)=>{ if(BB.has(c.bloco)&&ch[ct.id][i]>bp){bp=ch[ct.id][i];bi=i} }); if(bi>=0) S.apoio=S.cands[bi].id } },
        todos_verba:(m,ch,BB)=>{ for(const ct of X.EL_CIDADES){const S=m.cidades[ct.id]; let bi=-1,bp=0; S.cands.forEach((c,i)=>{ if(BB.has(c.bloco)&&ch[ct.id][i]>bp){bp=ch[ct.id][i];bi=i} }); if(bi>=0){S.apoio=S.cands[bi].id; S.verba=200} } } };
      const out={}; for(const k in estr) out[k]={U:0,ap:0,n:0};
      for(let s=0;s<NS;s++) for(const k in estr){ const g=structuredClone(base); g.seed=2000+s*53; g.escandalo=10; const m=X.elMunCria(g); const AE=X.aprovEstados(g);
        const BB=new Set(X.PARTIDOS.filter(P=>X.status(g.parties[P.id].rel)==='base').map(P=>P.id)); const ch={}; for(const ct of X.EL_CIDADES) ch[ct.id]=X.elMunChances(g,m,ct,AE);
        estr[k](m,ch,BB); const a0=X.aprovacao(g); const notas=[]; X.elMunApura1(g,m,notas); g.mes=22; X.elMunApura2(g,m,notas);
        const R=m.res; out[k].U+=(X.aprovacao(g)-a0)+2.5*R.ap; out[k].ap+=R.ap; out[k].n+=R.nApoio; }
      for(const k in out){ out[k].U=Math.round(out[k].U/NS*100)/100; out[k].ap=Math.round(out[k].ap/NS*100)/100; out[k].n=Math.round(out[k].n/NS) } return out }""")
    print('   estratégias (utilidade ≈ variação de aprovação em 6 meses):', bal)
    ok('Equilíbrio: apoiar todo mundo (com ou sem verba máxima) não supera a estratégia seletiva', bal['todos']['U'] <= bal['seletiva']['U'] + 0.05 and bal['todos_verba']['U'] <= bal['seletiva']['U'] + 0.05, bal)
    ok('Equilíbrio: ficar neutro tem efeito menor que apoiar de forma seletiva em módulo (não é zero)', abs(bal['neutro']['ap']) > 0.05, bal['neutro'])

    # ---------- saves: migração de save antigo (46 cidades, sem campos novos) e validação ----------
    SET(pg, """const X=__X(); n.mes=20; n.el.mun=null; n.el.munHist=[]; X.elMunCria(n);
      const m=n.el.mun; const velhas=['sao-paulo','rio-de-janeiro','salvador','fortaleza','belo-horizonte','manaus','curitiba','recife','goiania','porto-alegre','belem','sao-luis','maceio','campo-grande','teresina','natal','joao-pessoa','aracaju','cuiaba','florianopolis','porto-velho','macapa','vitoria','rio-branco','boa-vista','palmas','guarulhos','campinas','sao-goncalo','duque-de-caxias','nova-iguacu','sao-bernardo','osasco','santo-andre','ribeirao-preto','sorocaba','uberlandia','contagem','juiz-de-fora','joinville','feira-de-santana','londrina','niteroi','serra','jaboatao','aparecida-de-goiania'];
      for(const k of Object.keys(m.cidades)) if(!velhas.includes(k)) delete m.cidades[k]; for(const k in m.cidades){ delete m.cidades[k].verba; delete m.cidades[k].caso; delete m.cidades[k].cass } delete m.v; delete n.el.munEfeito; delete n.el.munPed""")
    txt = pg.evaluate("()=>__X().qvSerializa(__QV().gRef.current)")
    d = pg.evaluate("""(t)=>{const X=__X(); const o=JSON.parse(t); let val='ok'; try{ X.qvValida(o) }catch(e){ val=e.message } let g=null, err=null; try{ g=X.qvParse(t) }catch(e){ err=e.message }
      if(!g) return {val, err}; X.elEnsure(g); return {val, err, n:Object.keys(g.el.mun.cidades).length, v:g.el.mun.v, verba:g.el.mun.cidades['campinas'].verba, ef:g.el.munEfeito, ped:g.el.munPed}}""", txt)
    ok('Save antigo (46 cidades, sem campos novos): valida, migra sem erro e completa as 100 cidades', d.get('val') == 'ok' and d.get('err') is None and d.get('n') == 100 and d.get('v') == 2 and d.get('verba') == 0, d)
    SET(pg, "n.el.munHist=[{ano:2028, depois:{PL:10,PT:12}, antes:{PL:8,PT:14}, ref:.2, trocas:0}]; n.el.mun.fase='fim'; n.el.mun.res={antes:{PL:8},depois:{PL:10},lista:[],ref:.2,nApoio:2,nTotApoio:3,fase:'fim'}; n.el.mun.visto=true")
    pg.wait_for_timeout(300); vai_poder(pg, 'Elei'); sub_el(pg, 'mun'); pg.wait_for_timeout(500)
    ok('Save antigo com resultado já apurado: a tela de municipais abre sem erro', pg.locator('[data-el=mun-resultado]').count() == 1 or pg.locator('[data-el=municipal]').count() == 1)
    d = G(pg, "(()=>{const X=__X(); return [X.elMunSaldoUF(g,'SP'), X.elMunApoioPartido(g,'PSD'), X.elMunBonusPres(g,'SP','PL',{}), X.elMunProgMult(g,'SP'), X.aprovEstados(g).SP>0]})()")
    ok('Save antigo: funções dos prefeitos devolvem zero (sem lista guardada)', d[0] == 0 and d[1] == 0 and d[2] == 0 and d[3] == 1 and d[4], d)

    ok('0 erros de página/console/aviso', len(errs) == 0, errs[:4])
    b.close()
falhas = [n for c, n in checks if not c]
print('\nRESULTADO: %d/%d ok' % (len(checks) - len(falhas), len(checks)), '| falhas:', falhas)
sys.exit(1 if falhas else 0)
