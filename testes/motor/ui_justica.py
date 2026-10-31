# Teste de interface da aba País > Justiça: custos do CNJ, escândalo forçado aparece na Mesa, bloqueio e avanço, reação ao bloqueio,
# reabrir caso arquivado, save antigo sem g.jus e 0 erros de página/console.
# uso: python3 run_sandbox.py ui_justica.py <pasta com index.html> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8881
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
checks = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:220]) if det != '' else ''), flush=True)
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
        try: pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^(Fechar|Continuar|OK|Entendi|Seguir|Próximo mês|Voltar à Mesa|Arquivar)')).first.click(timeout=1200)
        except Exception: pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
def encerra(pg, n=1):
    for _ in range(n):
        fecha_modais(pg)
        pg.locator('button').filter(has_text=re.compile(r'^\s*Encerrar m')).first.click(timeout=8000); pg.wait_for_timeout(900)
        fecha_modais(pg)
def G(pg, expr): return pg.evaluate("()=>{const g=__QV().gRef.current;return (" + expr + ")}")
def SET(pg, js): pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);" + js + ";return n})"); pg.wait_for_timeout(500)
def secao(pg, nome):
    pg.locator('#sec-tab-' + nome.lower().replace('í', 'i')).click(timeout=6000); pg.wait_for_timeout(500)
def chip(pg, nome):
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*' + nome + r'\s*$')).first.click(timeout=6000); pg.wait_for_timeout(500)
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__J = () => ({ PARTIDOS, jusNovoCaso, jusPrende, jusAcao, jusMensal, ensureJus, migraSave, jusProbQuebra, riscoImpeachment });\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg)
    fecha_modais(pg)
    # 1) aba Justiça
    secao(pg, 'País'); chip(pg, 'Justiça')
    t = pg.locator('[data-pais=justica]').inner_text()
    ok('aba País > Justiça abre', pg.locator('[data-pais=justica]').count() == 1)
    ok('custos do CNJ: total, pessoal, verbas e por habitante', 'R$ 164,6 bi' in t and 'R$ 148,5 bi' in t and 'R$ 9,8 bi' in t and '771,48' in t)
    ok('tabela por ramo com 6 ramos', pg.locator('[data-jus-ramos] tbody tr').count() == 6)
    ok('arquivo histórico com 7 casos e fontes com link', pg.locator('[data-hist]').count() == 7 and pg.locator('[data-hist] a[href^=https]').count() >= 14)
    ok('Fontes e notas no fim da aba', pg.locator('[data-fontes=justica]').count() == 1)
    ok('sem casos no começo (estado preguiçoso)', pg.locator('[data-caso]').count() == 0 and 'Nenhum caso aberto' in t)
    pg.screenshot(path=OUT + '/justica_vazia.png', full_page=True)
    # 2) força um escândalo que atinge o governo e confere na Mesa
    SET(pg, "__J().jusNovoCaso(n,{gov:true})")
    secao(pg, 'Mesa')
    ok('o escândalo aparece como cartão na Mesa', pg.locator('[data-pend=justica]').count() == 1, pg.locator('[data-pend=justica]').first.inner_text()[:120].replace('\n', ' ') if pg.locator('[data-pend=justica]').count() else '')
    ok('escândalo subiu', G(pg, "g.escandalo") > 0)
    pg.locator('[data-pend=justica] .pend-ab').first.click(timeout=5000); pg.wait_for_timeout(600)
    ok('a gaveta mostra o caso com ações de bloqueio e avanço', pg.locator('[data-mesa-justica] [data-jus-acao=sigilo]').count() == 1 and pg.locator('[data-mesa-justica] [data-jus-acao=acelerar]').count() == 1)
    pg.screenshot(path=OUT + '/justica_mesa.png')
    # 3) bloqueio pela gaveta: trocar o diretor-geral da PF
    a0 = G(pg, "g.acoes")
    pg.locator('[data-mesa-justica] [data-jus-acao=trocar_dg]').first.click(timeout=5000); pg.wait_for_timeout(700)
    ok('bloqueio gasta 1 ação', G(pg, "g.acoes") == a0 - 1, (a0, G(pg, "g.acoes")))
    ok('bloqueio registrado (trava, rastro e resultado)', G(pg, "g.jus.casos[0].trava>g.mes && g.jus.casos[0].rastro===1 && !!g.jus.ult && g.jus.ult.k==='trocar_dg'"), G(pg, "g.jus.ult&&g.jus.ult.res"))
    ok('o caso saiu da Mesa depois da decisão', pg.locator('[data-pend=justica]').count() == 0)
    fecha_modais(pg)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    # 4) avançar em outro caso pela aba País
    SET(pg, "__J().jusNovoCaso(n,{gov:false})")
    secao(pg, 'País'); chip(pg, 'Justiça')
    ok('dois casos listados', pg.locator('[data-pais=justica] [data-caso]').count() == 2)
    ok('um caso por mês: botão do caso já usado desabilitado', pg.locator('[data-caso=j1] [data-jus-acao=sigilo]').first.is_disabled())
    r0 = G(pg, "g.jus.casos[1].prova")
    pg.locator('[data-caso=j2] [data-jus-acao=forca_tarefa]').first.click(timeout=5000); pg.wait_for_timeout(700)
    ok('força-tarefa: mais prova e órgãos somados', G(pg, "g.jus.casos[1].forca===true && g.jus.casos[1].prova>" + str(r0) + " && g.jus.casos[1].orgaos.includes('MPF') && g.jus.casos[1].orgaos.includes('CGU')"), G(pg, "g.jus.casos[1].orgaos.join()"))
    ok('resultado da ação exibido na aba', pg.locator('[data-jus=resultado]').count() == 1)
    pg.screenshot(path=OUT + '/justica_casos.png', full_page=True)
    # 5) reação ao bloqueio (sorteio forçado): escândalo, STF e risco de impeachment sobem
    r = pg.evaluate("()=>{const g=structuredClone(__QV().gRef.current);const J=__J();for(const k in g.groups)g.groups[k]=30;g.escandalo=20;const i0=J.riscoImpeachment(g),s0=g.stf,e0=g.escandalo;const o=Math.random;Math.random=()=>0;J.jusNovoCaso(g,{gov:true});const c=g.jus.casos[g.jus.casos.length-1];g.acoes=5;const R=J.jusAcao(g,c.id,'sigilo');Math.random=o;return {ok:R.ok,back:g.jus.ult.back,stf:g.stf-s0,esc:g.escandalo-e0,imp:J.riscoImpeachment(g)-i0,res:g.jus.ult.res}}")
    ok('bloqueio com reação sobe escândalo, STF e risco de impeachment', r['ok'] and r['back'] and r['stf'] > 0 and r['esc'] > 0 and r['imp'] > 0, r)
    # 6) arquivar e reabrir
    SET(pg, "const c=n.jus.casos[1];c.fase='arquivado';c.ult=0;n.acoes=5")
    ok('caso arquivado oferece reabrir', pg.locator('[data-caso=j2] [data-jus-acao=reabrir]').count() == 1 and not pg.locator('[data-caso=j2] [data-jus-acao=reabrir]').first.is_disabled())
    pg.locator('[data-caso=j2] [data-jus-acao=reabrir]').first.click(timeout=5000); pg.wait_for_timeout(600)
    ok('reabrir volta ao inquérito', G(pg, "g.jus.casos[1].fase==='inquérito' && g.jus.casos[1].reab===1"))
    # 7) save antigo sem g.jus
    SET(pg, "delete n.jus")
    t = pg.locator('[data-pais=justica]').inner_text()
    ok('save antigo (sem g.jus) renderiza a aba sem erro', 'Nenhum caso aberto' in t and 'R$ 164,6 bi' in t)
    m = pg.evaluate("()=>{const g=structuredClone(__QV().gRef.current);delete g.jus;__J().migraSave(g);return !!g.jus && Array.isArray(g.jus.casos) && g.jus.seq===0}")
    ok('migraSave cria g.jus com padrões', m)
    # 8) fecha meses: a lógica mensal roda sem erro
    encerra(pg, 4)
    ok('g.jus existe depois de fechar meses (criação preguiçosa)', G(pg, "!!g.jus && Array.isArray(g.jus.casos)"))
    n = pg.evaluate("()=>{const g=structuredClone(__QV().gRef.current);const J=__J();J.ensureJus(g);g.escandalo=60;g.jus.casos=[];let k=0;for(let i=0;i<48;i++){g.mes=2+i;g.jus.ultQuebra=0;const nt=[];const e0=g.jus.casos.length;J.jusMensal(g,nt);k+=g.jus.casos.length-e0;if(g.jus.casos.filter(c=>c.fase!=='arquivado').length>=4)break}return k}")
    ok('com escândalo alto novos casos estouram sozinhos', n >= 1, n)
    alvos = pg.evaluate("()=>{const g=structuredClone(__QV().gRef.current);const J=__J();J.ensureJus(g);g.jus.casos=[];for(let i=0;i<30;i++){g.mes=3+i;J.jusNovoCaso(g)}return [...new Set(g.jus.casos.map(c=>c.alvo))]}")
    uf = re.compile(r'\b(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b')
    ok('alvos fictícios genéricos (sem pessoa real nem estado)', len(alvos) >= 5 and not any(uf.search(a) for a in alvos), alvos)
    # 9) prisão de parlamentar: o suplente aparece como linha extra e nenhum nome real some da lista
    SET(pg, "n.jus.casos=[];n.jus.suplentes=[];n.jus.reacoes=[];n.acoes=5")
    secao(pg, 'poder')
    pg.select_option('#parl-casa', 'sen'); pg.select_option('#parl-bloco', 'PL'); pg.wait_for_timeout(500)
    NOMES = "()=>Array.from(document.querySelectorAll('span.font-medium.truncate[title]')).map(e=>e.getAttribute('title'))"
    antes = pg.evaluate(NOMES); cont0 = pg.locator('[data-parl-contagem]').inner_text()
    ok('lista de parlamentares do PL no Senado tem nomes reais', len(antes) >= 3 and pg.locator('[data-suplente]').count() == 0, (len(antes), cont0))
    SET(pg, "const J=__J();J.ensureJus(n);const c=J.jusNovoCaso(n,{alvoT:'um senador do PL'});c.fase='ação penal';J.jusPrende(n,c,[])")
    depois = pg.evaluate(NOMES)
    ok('nenhum nome real some da lista depois da prisão', sorted(antes) == sorted(depois), (len(antes), len(depois)))
    sup = pg.locator('[data-suplente=PL]')
    ok('aparece a linha "Suplente do PL" sem nome nem estado', sup.count() == 1 and 'Suplente do PL' in sup.inner_text() and 'preso na Operação' in sup.inner_text() and not uf.search(sup.inner_text().split('Sem nome')[0]), sup.first.inner_text().replace('\n', ' ')[:200] if sup.count() else '')
    cont1 = pg.locator('[data-parl-contagem]').inner_text()
    ok('cabeçalho "N cadeiras · 1 ocupada por suplente"', cont1 == '%d cadeiras · 1 ocupada por suplente' % len(antes), cont1)
    ok('o plenário continua com 81 cadeiras (partidos somam)', pg.evaluate("()=>__J().PARTIDOS.reduce((a,p)=>a+p.sen,0)") == 81 and G(pg, "g.jus.suplentes.length") == 1)
    pg.locator('button[aria-pressed]').filter(has_text='Senado').first.click(timeout=5000); pg.wait_for_timeout(400)
    ok('linha do partido na articulação política (Senado)', pg.locator('[data-cadeira-suplente=PL]').count() == 1, pg.locator('[data-cadeira-suplente=PL]').first.inner_text() if pg.locator('[data-cadeira-suplente=PL]').count() else '')
    ok('efeitos da prisão: escândalo subiu e suplente persistido no save', G(pg, "g.escandalo>0 && g.jus.suplentes[0].p==='PL' && g.jus.suplentes[0].casa==='sen' && !('nome' in g.jus.suplentes[0])"))
    # governadores nunca presos: nenhum alvo com cargo de governador
    ok('nenhum alvo é governador', pg.evaluate("()=>true") and all('governador' not in a for a in alvos), alvos[:2])
    # reações de políticos reais no X
    secao(pg, 'x'); pg.wait_for_timeout(600)
    pol = pg.locator('[data-post=pol]').filter(has_text=re.compile(r'Operação|CPI|PF|instituições|processo'))
    ok('há reação de político real no X', pol.count() >= 1, pol.count())
    ok('a reação traz o selo "simulado"', pol.count() >= 1 and pol.first.locator('.chip', has_text='simulado').count() == 1)
    lid = pg.locator('[data-post=lider]').filter(has_text='Operação')
    ok('conta com @ existente (oposição) posta sobre a operação', lid.count() >= 1 and '@OposicaoNaCamara' in lid.first.inner_text())
    txts = G(pg, "g.jus.reacoes.map(r=>r.txt)")
    ok('falas só institucionais: sem acusação nem o alvo do caso', len(txts) >= 1 and not any(re.search(r'senador do PL|corrup|crimin|ladr|roub|propina|vida privada|preso', t, re.I) for t in txts), txts[:2])
    SET(pg, "n.jus.reacoes.forEach(r=>0)")
    # pelo mensal: caso parlamentar com prova alta chega à prisão sozinho
    pr = pg.evaluate("()=>{const g=structuredClone(__QV().gRef.current);const J=__J();J.ensureJus(g);g.jus.suplentes=[];g.jus.casos=[];g.mes=10;const c=J.jusNovoCaso(g,{alvoT:'deputados do PT'});c.fase='ação penal';c.prova=95;c.pend=false;let m=0;for(let i=0;i<40&&c.fase!=='prisão';i++){g.mes=11+i;c.faseMes=g.mes-5;J.jusMensal(g,[]);m=i}return {fase:c.fase,mes:m,sup:g.jus.suplentes.length}}")
    ok('no mensal, caso de parlamentar com prova forte chega à prisão e cria suplente', pr['fase'] == 'prisão' and pr['sup'] == 1, pr)
    # save antigo com g.jus sem os campos novos
    SET(pg, "delete n.jus.suplentes;delete n.jus.reacoes;delete n.jus.cpiMes")
    secao(pg, 'poder'); pg.wait_for_timeout(300)
    ok('save antigo sem suplentes/reacoes renderiza o Congresso', pg.locator('#parl-bloco').count() == 1)
    m2 = pg.evaluate("()=>{const g=structuredClone(__QV().gRef.current);const J=__J();g.jus={ver:1,seq:2,casos:[]};J.ensureJus(g);return Array.isArray(g.jus.suplentes)&&Array.isArray(g.jus.reacoes)}")
    ok('ensureJus completa campos novos de saves da fase 1', m2)
    print('ERRS', errs[:8])
    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    print('RESUMO: %d ok, %d falhas' % (sum(1 for c in checks if c[0]), sum(1 for c in checks if not c[0])))
    b.close()
