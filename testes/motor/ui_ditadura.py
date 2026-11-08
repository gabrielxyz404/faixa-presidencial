# Ditadura (ficção, selo "simulado"): erosão nas 4 frentes, autogolpe (falho e vitorioso), regime, fins (queda, golpe militar, abertura).
# uso: python3 run_sandbox.py ui_ditadura.py <pasta com index.html> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8862
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
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    pg.on('dialog', lambda d: d.accept())
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__D = () => ({ ditFaz, ditGolpe, ditGolpeChance, ditMensal, ditAbertura, ditFazRegime, analisaLocal, fimDoMes, riscoImpeachment, ditEnsure });\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    SET(pg, "n.acoes=12;n.props=9")
    pg.locator('#sec-tab-poder').click(); pg.wait_for_timeout(500)
    pg.locator('#poder-chip-democracia').click(); pg.wait_for_timeout(700)
    ok('Aba Poder > Democracia com selo "simulado" e as 4 frentes', pg.locator('[data-dit=erosao]').count() == 1 and 'simulado' in pg.locator('[data-dit]').inner_text() and pg.locator('[data-dit-frente]').count() == 4)
    ok('Golpe indisponível com democracia 100', pg.locator('[data-dit-golpe-btn]').is_disabled())
    ok('Midia exige censura antes', pg.locator('[data-dit-faz=midia]').is_disabled())
    pg.screenshot(path=OUT + '/democracia.png', full_page=False)
    for k in ['stf', 'orgaos', 'censura', 'midia', 'perseguir']:
        pg.locator('[data-dit-faz=%s]' % k).click(); pg.wait_for_timeout(350)
    dem = G(pg, 'g.dit.dem')
    ok('Cinco passos derrubam a democracia para 38', dem == 38, dem)
    ok('Passo único fica marcado como feito', pg.locator('[data-dit-faz=stf]').is_disabled())
    feed = G(pg, "g.feed.slice(0,12).filter(f=>f.src==='antag').map(f=>f.txt).join(' | ')")
    ok('Manchetes sem o nome da pessoa real', 'lula' not in feed.lower() and 'GOVERNO' in feed, feed[:200])
    ok('Adiar eleições liberado abaixo de 55', not pg.locator('[data-dit-faz=adiar]').is_disabled())
    m0 = G(pg, 'g.dit.mil'); pg.locator('[data-dit-faz=militares]').click(); pg.wait_for_timeout(350)
    ok('Agradar militares: apoio +12 (repetível)', G(pg, 'g.dit.mil') == m0 + 12 and not pg.locator('[data-dit-faz=militares]').is_disabled())
    ok('Golpe agora disponível', not pg.locator('[data-dit-golpe-btn]').is_disabled())
    pg.locator('[data-dit-golpe]').scroll_into_view_if_needed(); pg.screenshot(path=OUT + '/democracia_erosao.png', full_page=False)
    # desfechos do golpe por lógica (seeds variadas)
    r = pg.evaluate("""()=>{const X=__D();const base=__QV().gRef.current;let win=null,lose=null;
      for(let s=1;s<400&&(!win||!lose);s++){const g=structuredClone(base);g.seed=s;g.acoes=3;const r=X.ditGolpe(g,[]);if(r.venceu&&!win)win=g;if(!r.venceu&&r.ok&&!lose)lose=g;}
      const ri=X.riscoImpeachment(win);const p=X.analisaLocal(win,'Criar imposto sobre grandes fortunas de 2% acima de R$ 50 milhões');
      return {win:!!win,lose:!!lose,regime:win&&win.dit.regime,ri,inst:p.inst,tec:(p.tecnico||'').slice(0,60),
        loseMil:lose&&lose.dit.mil,loseImp:lose&&lose.oposicao&&lose.oposicao.pedidoImp,loseReg:lose&&lose.dit.regime,loseOver:lose&&lose.over,
        winFeed:win&&win.feed[0].txt}}""")
    ok('Golpe vitorioso: regime instalado e impeachment impossível', r['win'] and r['regime'] and r['ri'] == 0, r)
    ok('No regime, PL/PEC vira decreto-lei', r['inst'] == 'DEC' and 'Congresso fechado' in r['tec'], (r['inst'], r['tec']))
    ok('Golpe falho: segue no cargo, militares caem, pedido de impeachment', r['lose'] and not r['loseReg'] and not r['loseOver'] and r['loseImp'] is not None, r)
    # regime ao longo do tempo: eleições suspensas, sanções, fins
    r2 = pg.evaluate("""()=>{const X=__D();const base=structuredClone(__QV().gRef.current);base.dit.regime=true;base.dit.inicio=base.mes;base.dit.dem=8;
      const run=(f,max,rep)=>{const g=structuredClone(base);f(g);const pib0=g.eco.pib;for(let i=0;i<max&&!g.over;i++){if(rep&&g.dit.revolta>=55){g.acoes=3;X.ditFazRegime(g,'policia');}if(rep&&g.dit.mil<50){g.acoes=3;X.ditFazRegime(g,'militares');}X.fimDoMes(g);if(g.over&&g.over.tipo!=='personagem')g.over=null;g.acoes=3;g.props=3;g.pes.saude=95;g.pes.energia=90;}return {over:g.over&&g.over.motivo,mes:g.mes,pib0,pib:g.eco.pib,el:!!(g.el&&g.el.ger)};};
      const queda=run(g=>{for(const k in g.groups)g.groups[k]=8;g.dit.mil=90;},60);
      const mil=run(g=>{g.dit.mil=5;for(const k in g.groups)g.groups[k]=60;},120);
      const longo=run(g=>{g.dit.mil=95;for(const k in g.groups)g.groups[k]=75;},60,true);
      const ab=structuredClone(base);ab.acoes=3;ab.dit.mil=95;const ra=X.ditAbertura(ab);for(let i=0;i<8&&!ab.over;i++){X.fimDoMes(ab);if(ab.over&&ab.over.tipo!=='personagem')ab.over=null;ab.acoes=3;ab.pes.saude=95;}
      return {queda,mil,longo,ab:ab.over&&ab.over.motivo,ra:ra.ok}}""")
    ok('Revolta com aprovação baixa derruba o regime', r2['queda']['over'] == 'dit_queda', r2['queda'])
    ok('Militares insatisfeitos dão golpe militar', r2['mil']['over'] == 'golpe_militar', r2['mil'])
    ok('Regime com repressão e caserna agradada atravessa o fim do mandato sem eleição', r2['longo']['over'] in (None, '') and r2['longo']['mes'] > 48 and not r2['longo']['el'] , r2['longo'])
    ok('Sanções corroem o PIB no regime', r2['longo']['pib'] < r2['longo']['pib0'], r2['longo'])
    ok('Abertura negociada termina em 6 meses com fim próprio', r2['ra'] and r2['ab'] == 'abertura', r2)
    # UI do regime e tela de fim
    SET(pg, "n.dit.regime=true;n.dit.inicio=n.mes;n.dit.dem=8;n.acoes=3")
    ok('Painel do regime com abertura', pg.locator('[data-dit=regime]').count() == 1 and pg.locator('[data-dit-abrir]').count() == 1)
    pg.screenshot(path=OUT + '/regime.png', full_page=False)
    SET(pg, "n.over={tipo:'personagem',motivo:'dit_queda',leg:null,posse:null,venc:null,mes:n.mes}")
    pg.wait_for_timeout(800)
    t = pg.locator('[data-el=fim-personagem]').inner_text() if pg.locator('[data-el=fim-personagem]').count() else ''
    ok('Tela de fim: "Derrubado pelas ruas"', 'DERRUBADO PELAS RUAS' in t.upper() and 'simulado' in t, t[:160])
    pg.screenshot(path=OUT + '/fim_queda.png', full_page=False)
    ok('0 erros de página', not errs, errs[:3])
    falhas = [n for c, n in checks if not c]
    print('RESUMO: %d/%d' % (len(checks) - len(falhas), len(checks)), '| falhas:', falhas)
    b.close()
