# Congresso vivo (v92): eleição da Mesa, sanção e veto (com sessão de derrubada), pedido de ministério, líderes de grupos, PLOA/LOA/contingenciamento, TCU, impeachment com base jurídica, pauta travada, conduta vedada e cassação.
# uso: python3 run_sandbox.py ui_congresso.py <pasta com index.html> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8864
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
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
        try: pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^(Fechar|Continuar|OK|Entendi|Seguir|Próximo mês|Voltar à Mesa)')).first.click(timeout=1200)
        except Exception: pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
def propoe(pg, texto):
    fecha_modais(pg)
    pg.locator('#caixa').scroll_into_view_if_needed()
    if texto: pg.fill('#caixa', texto)
    click(pg, 'Assinar e enviar', 2200)
    if SHOT:
        AV.append(pg.locator('[data-parecer-corte-linear]').count())
        pg.screenshot(path=OUT + '/' + SHOT[0] + '.png'); SHOT.clear()
    btns = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
    for alvo in ['Assinar e publicar no DOU', 'Votar agora']:
        if alvo in btns:
            pg.locator('.modal-wrap button').filter(has_text=alvo).first.click(timeout=4000); pg.wait_for_timeout(1500); break
    else:
        print('  sem botão de aprovar:', btns[:6]); return False
    # votação ao vivo: tenta concluir
    for _ in range(6):
        b = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
        pick = next((x for x in b if re.match(r'^(Ver resultado|Concluir|Apurar|Aplicar|Fechar|Continuar|Encerrar votação|Pular)', x)), None)
        if not pick: break
        try: pg.locator('.modal-wrap button').filter(has_text=pick).first.click(timeout=3000)
        except Exception: pass
        pg.wait_for_timeout(900)
    fecha_modais(pg)
    return True
def encerra(pg, n=1):
    for _ in range(n):
        fecha_modais(pg)
        pg.locator('button').filter(has_text=re.compile(r'^\s*Encerrar m')).first.click(timeout=8000); pg.wait_for_timeout(900)
        fecha_modais(pg)
def estado(pg):
    return pg.evaluate("()=>{const e=document.querySelector('[data-secao-medidas]');return e?e.innerText.length:-1}")


checks = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:300]) if det != '' else ''), flush=True)
def SET(pg, js): pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);" + js + ";return n})"); pg.wait_for_timeout(500)
def G(pg, e): return pg.evaluate("()=>{const g=__QV().gRef.current;return (" + e + ")}")
def EV(pg, js): return pg.evaluate("()=>{const X=__C();const g=structuredClone(__QV().gRef.current);" + js + "}")
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    pg.on('dialog', lambda d: d.accept())
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__C = () => ({ cvEnsure, cvMensal, cvResolve, cvCrime, cvCondutaVedada, cvCassacao, fimDoMes, analisaLocal, executaProposta, primario, bancadas, status, riscoImpeachment });\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    encerra(pg, 1)
    ok('Fevereiro: eleição da Mesa da Câmara e do Senado vira decisão pendente', G(pg, "g.cv && g.cv.dec.filter(d=>d.k==='mesa').length") == 2, G(pg, "g.cv && g.cv.dec.map(d=>d.tit)"))
    ok('A Mesa lista a decisão em "Precisa de você"', pg.locator('text=Eleição da presidência da Câmara').count() >= 1)
    SET(pg, "n.acoes=6")
    fecha_modais(pg); pg.screenshot(path=OUT + '/pos_enc.png')
    pg.locator('#sec-tab-poder').click(); pg.wait_for_timeout(400); pg.locator('#poder-chip-casas').click(); pg.wait_for_timeout(700)
    ok('Poder > Câmara e Senado: presidências, base de impeachment, orçamento, TCU, vetos, TSE', pg.locator('[data-cv-painel]').count() == 1 and pg.locator('[data-cv-pres]').count() == 2 and pg.locator('[data-cv-tcu]').count() == 1)
    pg.screenshot(path=OUT + '/casas.png')
    a0 = G(pg, 'g.acoes'); pg.locator('[data-cv-dec=mesa]').first.locator('[data-cv-op=aliado]').click(); pg.wait_for_timeout(600)
    h = G(pg, 'g.cv.pres.cam.humor')
    ok('Candidato aliado na Câmara: gasta 1 ação e o humor vai a 78 (vitória) ou 22 (derrota)', G(pg, 'g.acoes') == a0 - 1 and h in (78, 22), (a0, G(pg, 'g.acoes'), h))
    h0 = G(pg, 'g.cv.pres.cam.humor'); pg.locator('[data-cv-emendas]').click(); pg.wait_for_timeout(500)
    ok('Liberar emendas: R$ 3 bi e humor da Câmara +12', G(pg, 'g.cv.pres.cam.humor') == min(100, h0 + 12), (h0, G(pg, 'g.cv.pres.cam.humor')))
    # sanção e veto + sessão de derrubada
    r = EV(pg, "const C=X.cvEnsure(g);C.dec=[];C.prox.pauta=g.mes;const nt=[];X.cvMensal(g,nt);const d=C.dec.find(x=>x.k==='veto');if(!d)return {d:null};const h0=C.pres.cam.humor;g.acoes=3;const r=X.cvResolve(g,d.id,'vetar');const h1=C.pres.cam.humor;g.mes++;const nt2=[];X.cvMensal(g,nt2);return {d:d.tit,r:r.msg,h0,h1,res:C.vetos[0].res,nota:nt2.map(x=>x.x).filter(x=>/veto/i.test(x)).join(' ')}")
    ok('Congresso aprova pauta própria: sanção ou veto', r['d'] is not None and r['d'].startswith('Sanção ou veto'), r)
    ok('Vetar irrita a Câmara e o veto vai à sessão do mês seguinte (derrubado ou mantido)', r['h1'] < r['h0'] and r['res'] in ('derrubado', 'mantido') and r['nota'] != '', r)
    r = EV(pg, "const C=X.cvEnsure(g);C.dec=[];C.prox.pauta=g.mes;X.cvMensal(g,[]);const d=C.dec.find(x=>x.k==='veto');const c0=g.fiscal.custo;g.mes+=2;X.cvMensal(g,[]);return {c0,c1:g.fiscal.custo,pend:C.dec.some(x=>x.id===d.id)}")
    ok('Sem decisão no prazo, vira sanção tácita (custo entra)', r['c1'] > r['c0'] and not r['pend'], r)
    # pedido de ministério
    r = EV(pg, "const C=X.cvEnsure(g);C.dec=[];C.prox.min=g.mes;C.prox.pauta=999;C.prox.lider=999;g.mes=Math.max(g.mes,5);X.cvMensal(g,[]);const d=C.dec.find(x=>x.k==='ministerio');if(!d)return {d:null};g.parties[d.partido].rel=70;const r0=g.parties[d.partido].rel;X.cvResolve(g,d.id,'recusar');return {d:d.tit,r0,r1:g.parties[d.partido].rel,st:X.status(g.parties[d.partido].rel)}")
    ok('Partido da base pede ministério; recusar faz o partido desembarcar', r['d'] is not None and r['r1'] == r['r0'] - 22, r)
    # líder de grupo
    r = EV(pg, "const C=X.cvEnsure(g);C.dec=[];C.prox.lider=g.mes;C.prox.pauta=999;C.prox.min=999;X.cvMensal(g,[]);const d=C.dec.find(x=>x.k==='lider');if(!d)return {d:null};const k=d.ref.replace(/\\d+$/,'');const v0=g.groups[k];X.cvResolve(g,d.id,'atender');return {d:d.tit,k,v0,v1:g.groups[k]}")
    ok('Líder de grupo faz pedido com prazo; atender dá +6 ao grupo', r['d'] is not None and abs(r['v1'] - min(99, r['v0'] + 6)) < .01, r)
    # orçamento
    r = EV(pg, "const C=X.cvEnsure(g);C.dec=[];C.prox={pauta:999,min:999,lider:999};g.mes=7;X.cvMensal(g,[]);const d=C.dec.find(x=>x.k==='ploa');X.cvResolve(g,d.id,'ajuste');g.mes=12;const c0=g.fiscal.custo;X.cvMensal(g,[]);const c1=g.fiscal.custo;g.mes=13;X.cvMensal(g,[]);return {d:d.tit,loa:C.loa,c0,c1,c2:g.fiscal.custo}")
    ok('PLOA em agosto; LOA em dezembro soma emendas; em janeiro vale o ajuste (−R$ 20 bi)', r['d'].startswith('Projeto de Lei Orçamentária') and r['loa'] and r['c1'] > r['c0'] and abs((r['c2'] - r['c1']) + 20) < .01, r)
    # TCU e impeachment com base jurídica
    r = EV(pg, "const C=X.cvEnsure(g);C.dec=[];C.prox={pauta:999,min:999,lider:999};g.mes=18;C.pedaladas=2;X.cvMensal(g,[]);return {tcu:C.tcu[0],crime:X.cvCrime(g)}")
    ok('TCU rejeita contas com pedaladas e isso vira crime de responsabilidade', r['tcu']['res'] == 'rejeitadas' and 'TCU' in (r['crime'] or ''), r)
    r = EV(pg, "X.cvEnsure(g);g.cv.pres.cam.humor=60;g.cv.crime=null;for(const k in g.groups)g.groups[k]=3;g.escandalo=90;const s=[];for(let i=0;i<5&&!g.over;i++){X.fimDoMes(g);s.push(g.impStreak);g.acoes=3;g.pes.saude=90;}const sem={s,over:g.over&&g.over.tipo};return sem")
    ok('Sem crime de responsabilidade, a presidência da Câmara engaveta o impeachment', r['over'] != 'impeachment' and max(r['s']) <= 2, r)
    r = EV(pg, "X.cvEnsure(g);g.cv.pres.cam.humor=60;g.cv.crime='contas rejeitadas pelo TCU';for(const k in g.groups)g.groups[k]=3;g.escandalo=90;const s=[];for(let i=0;i<6&&!(g.over&&g.over.tipo==='impeachment');i++){X.fimDoMes(g);s.push(g.impStreak);g.acoes=3;g.pes.saude=90;}return {s,over:g.over&&g.over.tipo,ri:X.riscoImpeachment(g)}")
    ok('Com crime de responsabilidade, o processo anda até a votação', max(r['s']) >= 3 or r['over'] == 'impeachment', r)
    # conduta vedada e cassação
    r = EV(pg, "X.cvEnsure(g);g.el.mandatos=1;g.mes=44;const p=window.__QV&&X.analisaLocal(g,'Criar uma bolsa de R$ 300 por mês para 2 milhões de jovens aprendizes');const n=X.cvCondutaVedada(g,p);return {n,tse:g.cv.tse,cost:p.cost}")
    ok('Gasto novo perto da eleição vira processo no TSE (conduta vedada)', r['tse'] == 1 and r['n'], r)
    r = EV(pg, "X.cvEnsure(g);g.cv.tse=6;let k=0;for(let m=40;m<120;m++){g.mes=m;if(X.cvCassacao(g))k++;}g.cv.tse=0;let z=0;for(let m=40;m<120;m++){g.mes=m;if(X.cvCassacao(g))z++;}return {k,z}")
    ok('Com processos no TSE, a reeleição pode ser cassada; sem processos, nunca', r['k'] > 20 and r['z'] == 0, r)
    # pauta travada
    SET(pg, "n.cv.pres.cam.humor=15")
    pg.locator('#sec-tab-mesa').click(); pg.wait_for_timeout(400)
    SET(pg, "n.pauta=(n.pauta||[]).concat([{id:'tst1',prop:__C().analisaLocal(n,'Projeto de lei criando o programa Farmácia Popular para todos os remédios'),inst:'PL',mes:n.mes,meses:0}])")
    tem = G(pg, "g.pauta.filter(i=>!i.mp).length")
    if tem:
        pg.evaluate("()=>{}")
        vb = pg.locator('button').filter(has_text='Levar a voto')
        if vb.count(): vb.first.click(); pg.wait_for_timeout(300)
        t = pg.locator('[data-toast]').inner_text() if pg.locator('[data-toast]').count() else ''
        ok('Com a presidência da Câmara hostil, o projeto não vai a voto', 'não põe o projeto em votação' in t, t[:160])
    else:
        ok('Com a presidência da Câmara hostil, o projeto não vai a voto (sem item na pauta para testar)', False, G(pg, "g.pauta.map(i=>i.inst)"))
    pg.screenshot(path=OUT + '/pauta_travada.png')
    ok('0 erros de página', not errs, errs[:3])
    falhas = [n for c, n in checks if not c]
    print('RESUMO: %d/%d' % (len(checks) - len(falhas), len(checks)), '| falhas:', falhas)
    b.close()
