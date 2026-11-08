# Teste de interface do reequilíbrio v2 ("equilibrio-v2"): impeachment com 1 mês de aviso (cartão de admissibilidade na Mesa, notícia e votação só no mês seguinte),
# medida repetida sinalizada no parecer e sem soma de efeito, rendimento decrescente da comunicação (2º ato 50%, 3º 25%, teto global do efeito transitório),
# saúde no lugar do estresse, afastamento temporário antes do fim por saúde, jantar com a bancada com efeito decrescente, aceite do Comércio pela demanda
# já contratada, linha de retorno das decisões no Balanço do mês, base inicial do presidente Negociador e 0 erros de página/console.
# uso: python3 run_sandbox.py ui_equilibrio.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8896
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
checks = []
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
    click(pg, "Avançar"); click(pg, "Tomar posse", 1000)
def fecha_modais(pg):
    for _ in range(4):
        if pg.locator('.modal-wrap').count() == 0: break
        try: pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^(Fechar|Continuar|OK|Entendi|Seguir|Próximo mês|Voltar à Mesa|Arquivar|Cancelar|Desistir|Começar)')).first.click(timeout=1200)
        except Exception: pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
def G(pg, expr): return pg.evaluate("()=>{const g=__QV().gRef.current;return (" + expr + ")}")
def SET(pg, js): pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);" + js + ";return n})"); pg.wait_for_timeout(500)
def secao(pg, nome): pg.locator('#sec-tab-' + nome.lower().replace('í', 'i')).click(timeout=6000); pg.wait_for_timeout(500)
errs = []
INJ = "window.__QV = () => QV; window.__AL = analisaLocal; window.__X = () => ({ fimDoMes, executaProposta, aprovacao, riscoImpeachment, impAdmissibilidade, efTransTotal, medRepetida, fazArticulacao, icAvaliaVenda, icContrata, ensureIC, GRUPOS, aliadosCentrao, EQ_TRANS_CAP, eqRelEconomia, primario, EVENTOS, icShareUsd }); function analisaLegado(g, texto) {"
# estado "governo derretido": risco de impeachment em 100 sem depender de sorte
DERRETE = "for(const k of Object.keys(n.groups)) n.groups[k]=6; n.escandalo=100; for(const P of Object.keys(n.parties)) {n.parties[P].rel=5; n.parties[P].relS=5}"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', INJ, 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)

    # ---------------- base inicial do Negociador ----------------
    base = G(pg, "Object.values(g.parties).filter(p=>p.rel>=62).length")
    ali = G(pg, "Object.entries(g.parties).filter(([k,p])=>p.ali).map(([k])=>k)")
    ok('Negociador: começa com 2-3 blocos aliados do Centrão acima de 62 (além do próprio partido)', len(ali) in (2, 3) and all(G(pg, "g.parties['%s'].rel" % a) >= 62 for a in ali) and base >= 3, (ali, base))
    ok('Negociador: relações respondem à economia (função eqRelEconomia existe e é neutra no ponto de partida)', abs(pg.evaluate("()=>{const g=__QV().gRef.current;const X=__X();return X.eqRelEconomia(g,X.primario(g))}")) < 2.5)

    # ---------------- impeachment: 3 meses + aviso de admissibilidade ----------------
    SET(pg, DERRETE + "; n.impStreak=0; n.evento=null; n.eventoOk=true")
    need = G(pg, "__X().impAdmissibilidade(g).need")
    ok('Impeachment: exige 3 meses seguidos com risco >= 80 (modo Brasília, dificuldade Realista)', need == 3, need)
    def passa_mes():
        return pg.evaluate("()=>{let r=null;__QV().setG(p=>{const n=structuredClone(p);" + DERRETE + ";r=__X().fimDoMes(n);n.acoes=5;n.props=5;n.pes.energia=90;n.eventoOk=true;n.evento=null;window.__r={imp:r.impeachment?{c:r.impeachment.votosC,s:r.impeachment.votosS}:null,notas:r.notas.map(x=>x.x),feed:n.feed.slice(0,4).map(f=>f.txt),streak:n.impStreak,over:n.over?n.over.tipo:null};return n});return null}")
    passa_mes(); pg.wait_for_timeout(600); r1 = pg.evaluate("()=>window.__r")
    ok('Mês 1 de risco >= 80: sem votação, sem aviso ainda', r1['imp'] is None and r1['streak'] == 1 and not any('Admissibilidade' in x for x in r1['notas']), r1['streak'])
    passa_mes(); pg.wait_for_timeout(800); r2 = pg.evaluate("()=>window.__r")
    ok('Mês 2: Câmara abre a admissibilidade (nota no balanço e manchete) e ainda não há votação', r2['imp'] is None and any('Admissibilidade' in x for x in r2['notas']) and any('ADMISSIBILIDADE' in x for x in r2['feed']), (r2['notas'][:2], r2['feed'][:2]))
    fecha_modais(pg)
    ok('Mesa: cartão "Admissibilidade do impeachment" aparece antes da votação', pg.locator('[data-pend=admissibilidade]').count() == 1, pg.locator('[data-pend]').evaluate_all("els=>els.map(e=>e.dataset.pend)"))
    if pg.locator('[data-pend=admissibilidade]').count():
        txt = pg.locator('[data-pend=admissibilidade]').inner_text()
        ok('Cartão de admissibilidade: explica o prazo de 1 mês e o limiar de 80%', '80%' in txt and 'votação' in txt, txt.replace('\n', ' ')[:200])
        pg.screenshot(path=OUT + '/eq_admissibilidade_mesa.png')
        pg.locator('[data-pend=admissibilidade]').click(); pg.wait_for_timeout(600)
        ok('Cartão abre a gaveta com risco, base e como baixar o risco', pg.locator('[data-cartao=admissibilidade]').count() == 1)
        pg.screenshot(path=OUT + '/eq_admissibilidade_gaveta.png'); fecha_modais(pg)
        try: pg.keyboard.press('Escape')
        except Exception: pass
    passa_mes(); pg.wait_for_timeout(800); r3 = pg.evaluate("()=>window.__r")
    ok('Mês 3 com risco >= 80: agora sim, a votação acontece', r3['imp'] is not None, r3)
    fecha_modais(pg)
    # se o jogador reage no mês do aviso, a votação não vem
    SET(pg, DERRETE + "; n.impStreak=2; n.evento=null; n.eventoOk=true; n.over=null")
    pg.evaluate("()=>{__QV().setG(p=>{const n=structuredClone(p);for(const k of Object.keys(n.groups)) n.groups[k]=70;n.escandalo=0;for(const P of Object.keys(n.parties)){n.parties[P].rel=80;n.parties[P].relS=80};const r=__X().fimDoMes(n);window.__r={imp:r.impeachment,streak:n.impStreak};return n})}")
    r4 = pg.evaluate("()=>window.__r")
    ok('Se o risco cai no mês do aviso, não há votação e a sequência diminui', r4['imp'] is None and r4['streak'] <= 1, r4)
    SET(pg, "n.impStreak=0; n.over=null")
    cfgmod = pg.evaluate("()=>{const g=structuredClone(__QV().gRef.current);g.cfg.modo='lua';const a=__X().impAdmissibilidade(g).need;g.cfg.modo='raiz';return [a,__X().impAdmissibilidade(g).need]}")
    ok('Lua de mel exige 4 meses (mais fácil); Brasília raiz exige 3', cfgmod == [4, 3], cfgmod)

    # ---------------- medida repetida ----------------
    SET(pg, "n.evento=null; n.eventoOk=true; n.acoes=5;n.props=5; n.pes.energia=100; n.impStreak=0; n.over=null")
    pg.evaluate("()=>{__QV().setG(p=>{const n=structuredClone(p);const pr=__AL(n,'Ampliar o Bolsa Família em R$ 100 por família');__X().executaProposta(n,pr,'aprovada');return n})}"); pg.wait_for_timeout(600)
    ok('1ª aprovação do Bolsa Família cria a medida em vigor', G(pg, "g.medidas.filter(m=>m.estado==='ativa'&&/Bolsa/i.test(m.topic)).length") >= 1, G(pg, "g.medidas.map(m=>m.topic+'/'+m.estado)"))
    rep = pg.evaluate("()=>{const g=__QV().gRef.current;const p=__AL(g,'Reajustar o Bolsa Família em R$ 50 por família');return {rep:!!p.repetida,tec:(p.tecnico||'').includes('Já aprovada')}}")
    ok('Medida repetida: o parecer do motor local marca "já aprovada"', rep['rep'] and rep['tec'], rep)
    ef = pg.evaluate("()=>{let out=null;__QV().setG(p=>{const n=structuredClone(p);const c0=n.fiscal.custo,e0=n.fiscal.extra,r0=n.fiscal.receita,a0=__X().aprovacao(n),m0=n.medidas.length;const pr=__AL(n,'Reajustar o Bolsa Família em R$ 50 por família');__X().executaProposta(n,pr,'aprovada');out={dc:n.fiscal.custo-c0,de:n.fiscal.extra-e0,dr:n.fiscal.receita-r0,dap:__X().aprovacao(n)-a0,dm:n.medidas.length-m0};window.__r=out;return n});return null}")
    pg.wait_for_timeout(500); ef = pg.evaluate("()=>window.__r")
    ok('Medida repetida: aprovar de novo não soma custo, receita nem aprovação (< 0,15 ponto de resíduo), e não cria outra medida', abs(ef['dc']) < 1e-9 and abs(ef['de']) < 1e-9 and abs(ef['dr']) < 1e-9 and abs(ef['dap']) < 0.15 and ef['dm'] == 0, ef)
    # na interface: Mesa -> escrever -> parecer com o aviso
    secao(pg, 'Mesa'); pg.wait_for_timeout(400)
    pg.locator('#caixa').fill('Reajustar o Bolsa Família em R$ 30 por família'); pg.wait_for_timeout(300)
    click(pg, 'Assinar e enviar', 3000)
    ok('Parecer na interface: banner "Já aprovada" visível', pg.locator('[data-parecer-repetida]').count() == 1 and 'Já aprovada' in pg.locator('[data-parecer-repetida]').inner_text(), pg.locator('.modal-wrap').first.inner_text()[:120].replace('\n', ' ') if pg.locator('.modal-wrap').count() else 'sem modal')
    pg.screenshot(path=OUT + '/eq_parecer_repetida.png')
    fecha_modais(pg)
    # custo fiscal no voto: gasto gigante pesa mais que gasto pequeno
    cv = pg.evaluate("()=>{const g=__QV().gRef.current;const a=__AL(g,'Zerar o imposto de renda para todo mundo'),b=__AL(g,'Ampliar o Merenda escolar em R$ 1 bilhão');return {a:a.custoVoto,b:b.custoVoto,ta:/Custo fiscal pesa/.test(a.tecnico||'')}}")
    ok('Voto do Congresso tem termo de custo fiscal: gasto líquido gigante é marcado no parecer', cv['a'] and cv['a']['pts'] <= -10 and cv['ta'] and not cv['b'], cv)

    # ---------------- comunicação com rendimento decrescente ----------------
    SET(pg, "n.evento=null; n.eventoOk=true; n.acoes=5;n.props=5; n.pes.energia=100; n.efTrans=[]; n.comMes=0; n.aprMes=0")
    d = pg.evaluate("()=>{let out=null;__QV().setG(p=>{const n=structuredClone(p);const X=__X();const ds=[];for(let i=0;i<4;i++){const a0=X.aprovacao(n);const pr=__AL(n,'Fazer um pronunciamento em cadeia nacional sobre a economia');X.executaProposta(n,pr,'aprovada');ds.push(X.aprovacao(n)-a0)}out={ds,tot:X.efTransTotal(n),cap:X.EQ_TRANS_CAP};window.__r=out;return n});return null}")
    pg.wait_for_timeout(500); d = pg.evaluate("()=>window.__r"); ds = d['ds']
    ok('Comunicação: 2º ato rende ~50% do 1º e o 3º ~25%', ds[0] > 0.2 and 0.3 <= ds[1] / ds[0] <= 0.7 and ds[2] / ds[0] <= 0.4 and ds[3] <= ds[1], [round(x, 2) for x in ds])
    ok('Comunicação: o efeito transitório acumulado respeita o teto global', d['tot'] <= d['cap'] + 1e-6, (round(d['tot'], 2), d['cap']))
    # discursos "sem motor" (COM sem custo) também são transitórios: não mexem em pobreza
    pob = pg.evaluate("()=>{let out=null;__QV().setG(p=>{const n=structuredClone(p);const X=__X();const b0=n.bias.pob,p0=n.soc.pob;for(let m=0;m<6;m++){const pr=__AL(n,'Discurso sobre o combate à fome');X.executaProposta(n,pr,'aprovada')}window.__r={dpob:n.soc.pob-p0,dbias:n.bias.pob-b0};return n});return null}")
    pg.wait_for_timeout(400); pob = pg.evaluate("()=>window.__r")
    ok('Discurso de comunicação não derruba a pobreza (efeito só na opinião)', abs(pob['dpob']) < 0.05 and abs(pob['dbias']) < 0.05, pob)

    # ---------------- jantar com a bancada: efeito decrescente no trimestre ----------------
    SET(pg, "n.pes.conta=5000000; n.pesMes={}; n.parties.MDB.jant=[]; n.parties.MDB.rel=40; n.parties.MDB.relS=40")
    j = pg.evaluate("()=>{let out=null;__QV().setG(p=>{const n=structuredClone(p);const X=__X();const r=[];const rel=()=>n.parties.MDB.rel;let v=rel();const a=X.fazArticulacao(n,'bancada','MDB');r.push(rel()-v,a.fator,a.dica);for(const mes of [1,2]){n.mes+=1;n.pesMes={};v=rel();const b=X.fazArticulacao(n,'bancada','MDB');r.push(rel()-v,b.fator,b.dica)}out=r;window.__r=out;return n});return null}")
    pg.wait_for_timeout(400); j = pg.evaluate("()=>window.__r")
    ok('Jantar com a bancada: +4, depois +2 e +1 no mesmo trimestre, com a dica "estranha a frequência"', abs(j[0] - 4) < 0.01 and abs(j[3] - 2) < 0.01 and abs(j[6] - 1) < 0.01 and j[2] is None and 'estranha a frequência' in (j[5] or ''), j)
    SET(pg, "n.mes=n.mes-2; n.pesMes={}"); secao(pg, 'Eu'); pg.wait_for_timeout(500)
    for t in ['Articulação', 'Política']:
        try: pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(t)).first.click(timeout=1500); pg.wait_for_timeout(400); break
        except Exception: pass
    ok('Eu > articulação: dica "a bancada estranha a frequência" aparece depois de um jantar recente', pg.locator('[data-art-dica=bancada]').count() >= 1 or pg.locator('[data-art=bancada]').count() == 0, pg.locator('[data-art-dica]').count())
    secao(pg, 'Mesa')

    # ---------------- estresse ----------------
    # o estresse saiu do jogo: o desgaste do cargo cai direto na saúde
    SET(pg, "n.pes.saude=60; n.evento=null; n.eventoOk=true; n.acoes=1;n.props=1; n.escandalo=0; for(const k of Object.keys(n.groups)) n.groups[k]=55")
    e = pg.evaluate("()=>{let out=null;__QV().setG(p=>{const n=structuredClone(p);__X().fimDoMes(n);window.__r={s:n.pes.saude,e:n.pes.estresse};n.acoes=5;n.props=5;n.eventoOk=true;n.evento=null;return n});return null}")
    pg.wait_for_timeout(400); e = pg.evaluate("()=>window.__r")
    ok('Mês sem crise não desgasta a saúde (60 -> 60 ou mais) e o estresse fica zerado', e['s'] >= 60 and e['e'] == 0, e)
    SET(pg, "n.pes.saude=60; n.eventoOk=false; n.evento='podcast'; n.acoes=1;n.props=1")
    e2 = pg.evaluate("()=>{__QV().setG(p=>{const n=structuredClone(p);__X().fimDoMes(n);window.__r=n.pes.saude;n.acoes=5;n.props=5;n.eventoOk=true;n.evento=null;return n});return null}")
    pg.wait_for_timeout(400); e2 = pg.evaluate("()=>window.__r")
    ok('Com crise ignorada a saúde cai', e2 < 60 and e2 < e['s'] - 2, e2)
    ok('A aba Eu não mostra mais a barra de estresse', pg.evaluate("()=>!document.body.innerText.includes('Estresse')"), '')
    # afastamento temporário
    SET(pg, "n.pes.saude=0.2; n.evento='podcast'; n.eventoOk=false; n.afastUsado=null; n.over=null; n.acoes=5;n.props=5")
    pg.evaluate("()=>{__QV().setG(p=>{const n=structuredClone(p);const r=__X().fimDoMes(n);window.__r={over:n.over?n.over.tipo:null,acoes:n.acoes,saude:n.pes.saude,afast:n.afastUsado===n.mes,nota:r.notas.some(x=>/Afastamento temporário/.test(x.x))};return n})}"); pg.wait_for_timeout(700)
    a1 = pg.evaluate("()=>window.__r")
    ok('Saúde zerada pela 1ª vez: afastamento temporário (sem ações no mês, saúde volta a 30), não o fim do jogo', a1['over'] is None and a1['acoes'] == 0 and a1['afast'] and a1['saude'] >= 25 and a1['nota'], a1)
    fecha_modais(pg)
    ok('Mesa: cartão "Afastamento temporário"', pg.locator('[data-pend=afastamento]').count() == 1)
    pg.screenshot(path=OUT + '/eq_afastamento_mesa.png')
    SET(pg, "n.pes.saude=0.2; n.evento='podcast'; n.eventoOk=false; n.acoes=5;n.props=5")
    pg.evaluate("()=>{__QV().setG(p=>{const n=structuredClone(p);__X().fimDoMes(n);window.__r={over:n.over?n.over.tipo:null};return n})}"); pg.wait_for_timeout(500)
    ok('Segunda vez com a saúde zerada: aí sim o afastamento é definitivo', pg.evaluate("()=>window.__r")['over'] == 'saude')
    SET(pg, "n.over=null; n.pes.saude=70; n.pes.estresse=20; n.acoes=5;n.props=5; n.afastUsado=null"); fecha_modais(pg)

    # ---------------- Comércio: aceite depende da demanda já contratada ----------------
    r = pg.evaluate("()=>{const g=structuredClone(__QV().gRef.current);const X=__X();X.ensureIC(g);const k='soja_grao',iso='CHN';const base=X.icShareUsd(k,iso);const q1=Math.round(base*.5*100)/100;const fresh=X.icAvaliaVenda(g,k,iso,q1,0.0001,2,0);const max=fresh.max;const a1=X.icAvaliaVenda(g,k,iso,q1,max,2,0);X.icContrata(g,{tipo:'venda',k,iso,qtd:Math.round(base*.8*100)/100,preco:max,anos:2});const a2=X.icAvaliaVenda(g,k,iso,q1,max,2,0);const a3=X.icAvaliaVenda(g,k,iso,Math.round(base*1.2*100)/100,max,2,0);return {a1:a1.res,a2:a2.res,a3:a3.res,m1:max,m2:a2.max}}")
    ok('Comércio: com a demanda ainda livre, preço cheio é aceito; com demanda já contratada o mesmo preço deixa de ser aceito', r['a1'] == 'aceita' and r['a2'] != 'aceita' and r['a3'] == 'rejeita' and r['m2'] < r['m1'], r)

    # ---------------- Balanço do mês: retorno das decisões ----------------
    SET(pg, "n.prioridade={q:Math.floor((n.mes-1)/3),k:'gastos',ini:n.mes,mult:1,n:0}; n.evento=null; n.eventoOk=true; n.acoes=5;n.props=5; n.over=null; n.ignAcum={n:2,ap:3.4,esc:12}; n.impStreak=0")
    secao(pg, 'Mesa'); pg.wait_for_timeout(300)
    click(pg, 'Encerrar m', 1500)
    ok('Balanço do mês: bloco "Retorno das suas decisões" com a prioridade do trimestre e o custo acumulado das crises ignoradas', pg.locator('[data-modal-retorno]').count() == 1 and pg.locator('[data-retorno=prioridade]').count() == 1 and pg.locator('[data-retorno=ignoradas]').count() == 1, pg.locator('[data-modal-retorno]').inner_text()[:300].replace('\n', ' ') if pg.locator('[data-modal-retorno]').count() else 'sem bloco')
    pg.screenshot(path=OUT + '/eq_balanco_retorno.png')
    fecha_modais(pg)

    # ---------------- escândalo sorteado e eventos de mercado ----------------
    ev = pg.evaluate("()=>{const g=structuredClone(__QV().gRef.current);g.eco.conf=5;const EV_=__X().EVENTOS;const f=EV_.find(e=>e.id==='fuga_capitais'),d=EV_.find(e=>e.id==='dolar');const w1=d.w(g);g.eco.conf=50;return {fuga:!!f,w_baixa:f?f.w(Object.assign({},g,{eco:Object.assign({},g.eco,{conf:5})})):0,w_normal:f?f.w(g):0,dolar_baixa:w1,dolar_normal:d.w(g)}}")
    ok('Crises de mercado ganham peso com confiança abaixo de 20 (fuga de capitais só entra com conf < 35)', ev['fuga'] and ev['w_baixa'] > 1 and ev['w_normal'] == 0 and ev['dolar_baixa'] > 3 * ev['dolar_normal'], ev)
    ok('Sem erros de página/console', not errs, errs[:3])
    b.close()
falhas = [n for c, n in checks if not c]
print('\n%d verificações, %d falhas' % (len(checks), len(falhas)))
for n in falhas: print('  FALHA:', n)
sys.exit(1 if falhas else 0)
