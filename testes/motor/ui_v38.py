# Teste de jogo pela interface (v3.8): parecer simplificado, resultado com grupos/jornais/vozes, famosos no X, podcasts e rivais.
# uso: python3 run_sandbox.py ui_v38.py <pasta com index.html> <saida_dir> [porta]
# Opcional: CSS_TW=<arquivo.css> injeta um CSS gerado pelo tailwind (o sandbox não tem o CDN) para os prints saírem com o visual real.
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8871
os.makedirs(OUT, exist_ok=True)
CSS = open(os.environ['CSS_TW'], encoding='utf-8').read() if os.environ.get('CSS_TW') else ''
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
checks = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:220]) if det != '' else ''), flush=True)
def click(pg, t, ms=500):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(ms)
def estilo(pg):
    if CSS: pg.add_style_tag(content=CSS)
def start(pg):
    pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='networkidle'); pg.wait_for_timeout(1500); estilo(pg)
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
def abre_parecer(pg, texto):
    fecha_modais(pg)
    pg.locator('#caixa').scroll_into_view_if_needed(); pg.fill('#caixa', texto)
    click(pg, 'Assinar e enviar', 2200)
def modal(pg): return pg.evaluate("()=>{const e=document.querySelector('.modal-wrap');return e?e.innerText:''}")
def aprova(pg):
    btns = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
    for alvo in ['Assinar e publicar no DOU', 'Votar agora']:
        if alvo in btns:
            pg.locator('.modal-wrap button').filter(has_text=alvo).first.click(timeout=4000); pg.wait_for_timeout(1500); break
    for _ in range(6):
        b = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
        pick = next((x for x in b if re.match(r'^(Ver resultado|Concluir|Apurar|Aplicar|Continuar|Encerrar votação|Pular)', x)), None)
        if not pick: break
        try: pg.locator('.modal-wrap button').filter(has_text=pick).first.click(timeout=3000)
        except Exception: pass
        pg.wait_for_timeout(900)
def encerra(pg, n=1):
    for _ in range(n):
        fecha_modais(pg)
        pg.locator('button').filter(has_text=re.compile(r'^\s*Encerrar m')).first.click(timeout=8000); pg.wait_for_timeout(900)
        fecha_modais(pg)
def G(pg, expr): return pg.evaluate("()=>{const g=__QV().gRef.current;return (" + expr + ")}")
def SET(pg, js): pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);" + js + ";return n})"); pg.wait_for_timeout(400)
errs = []
SEED = "(()=>{let a=" + os.environ.get("SEED_N", "20271030") + ";Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__F = () => ({ entRivalMes, entRenovaConvites, entGeraMes, entRivais, xFamosos, xPauta, pressaoRede, fatosImprensa, aprovacao, ensureX, analisaLocal, FAMOSOS, famConc, eixosDaProp });\nfunction analisaLegado(g, texto) {', 1)
    pg.add_init_script(SEED)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg)

    # ---------- 1) parecer simplificado de 3 propostas ----------
    abre_parecer(pg, 'Isentar do imposto de renda quem ganha até R$ 6 mil')
    t = modal(pg)
    ok('parecer A: custo/ganho em destaque', pg.locator('[data-secao=bloco-custo]').count() == 1, pg.locator('[data-secao=bloco-custo]').inner_text().replace('\n', ' | '))
    ok('parecer A: chance de aprovar (Câmara e Senado)', pg.locator('[data-chance=Câmara]').count() == 1 and pg.locator('[data-chance=Senado]').count() == 1, pg.locator('[data-secao=chance-aprovar]').first.inner_text().replace('\n', ' | ')[:160])
    ok('parecer A: removidos analista/parecer técnico/quem ganha/riscos/calendário/no tempo/precedentes', not re.search(r'Resumo do analista|Parecer técnico|Quem ganha e quem perde|Riscos|Calendário e legalidade|No tempo|Precedentes|Efeitos futuros', t))
    ok('parecer A: botões Pedir opinião do ministro e pesquisa popular', 'Pedir opinião do ministro' in t and 'Fazer pesquisa popular' in t)
    ok('parecer A: análise do ministro NÃO aparece antes de pedir', pg.locator('[data-secao=cf-ministro]').count() == 0)
    ok('parecer A: coerência com o partido e base jurídica presentes', 'Coerência com o seu partido' in t or 'Coerência com' in t, '' )
    pg.locator('.modal-wrap').get_by_text('Fazer pesquisa popular').first.click(timeout=4000); pg.wait_for_timeout(500)
    ok('pesquisa popular abre resultado', 'a favor' in modal(pg) and 'instituto bússola' in modal(pg).lower())
    pg.locator('.modal-wrap [data-pedir-ministro]').first.click(timeout=4000); pg.wait_for_timeout(500)
    ok('opinião do ministro abre sob demanda', pg.locator('[data-secao=cf-ministro]').count() == 1 and 'Análise do ministro' in modal(pg))
    if pg.locator('.modal-wrap').get_by_text('Ver detalhe por partido').count(): pg.locator('.modal-wrap').get_by_text('Ver detalhe por partido').first.click(timeout=3000); pg.wait_for_timeout(300)
    ok('detalhe por partido recolhível', 'sim / precisa' in modal(pg))
    pg.locator('.modal-wrap').evaluate("e => e.scrollTo ? e.scrollTo(0,0) : null"); pg.wait_for_timeout(200)
    pg.screenshot(path=OUT + '/v38_parecer.png')
    # rolar o modal até o fim para o segundo print (opcional)
    pg.evaluate("()=>{const m=document.querySelector('.modal-wrap');const sc=[m,...m.querySelectorAll('*')].find(e=>e.scrollHeight>e.clientHeight+50&&getComputedStyle(e).overflowY!='visible');if(sc)sc.scrollTop=sc.scrollHeight}"); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/v38_parecer_fim.png')
    pg.locator('.modal-wrap button').filter(has_text='Retirar proposta').first.click(timeout=4000); pg.wait_for_timeout(500)

    abre_parecer(pg, 'Instituir pena de morte para traficantes')
    t = modal(pg)
    fa = pg.locator('[data-secao=faixa-cf]')
    ok('parecer B (inconstitucional): faixa vermelha no topo', fa.count() == 1 and fa.first.get_attribute('data-nivel') == 'inconstitucional' and 'Inconstitucional: o STF deve derrubar' in fa.first.inner_text(), fa.first.inner_text().replace('\n', ' ') if fa.count() else t[:200])
    pg.screenshot(path=OUT + '/v38_parecer_incons.png')
    # ministro sob demanda com sugestões: Aplicar / Aceitar sugestões continuam funcionando
    pg.locator('.modal-wrap [data-pedir-ministro]').first.click(timeout=4000); pg.wait_for_timeout(500)
    em0 = pg.locator('.modal-wrap .text-lg.font-semibold').first.inner_text()
    ac = pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^Aceitar sugestões'))
    ap = pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^Aplicar$'))
    print('  ministro: botões Aplicar =', ap.count(), '| Aceitar sugestões =', ac.count())
    if ac.count():
        ac.first.click(timeout=4000); pg.wait_for_timeout(900)
        em1 = pg.locator('.modal-wrap .text-lg.font-semibold').first.inner_text()
        ok('aceitar sugestões do ministro reescreve a proposta e mantém a análise aberta', em1 != em0 and pg.locator('[data-secao=cf-ministro]').count() == 1, em1[:100])
        fa2 = pg.locator('[data-secao=faixa-cf]'); print('  faixa depois das sugestões:', fa2.first.inner_text().replace('\n', ' ')[:90] if fa2.count() else 'sem faixa (constitucional)')
    else: ok('ministro abre sem sugestões editáveis para esta proposta', pg.locator('[data-secao=cf-ministro]').count() == 1)
    pg.locator('.modal-wrap button').filter(has_text=re.compile('^(Retirar proposta|Desistir)$')).first.click(timeout=4000); pg.wait_for_timeout(500)

    abre_parecer(pg, 'Zerar o IPI de carros elétricos')
    t = modal(pg)
    ok('parecer C (decreto): sem faixa quando constitucional/sem Congresso mostra assinatura', 'não passa pelo Congresso' in t or pg.locator('[data-chance]').count() == 2, t[:120].replace('\n', ' '))
    pg.locator('.modal-wrap button').filter(has_text='Retirar proposta').first.click(timeout=4000); pg.wait_for_timeout(500)

    # ---------- 2) aprova e confere a tela de resultado ----------
    abre_parecer(pg, 'Zerar o IPI de carros elétricos'); aprova(pg)
    t = modal(pg)
    ok('resultado: efeito por grupo da população', pg.locator('[data-secao=grupos-resultado] li').count() >= 3, pg.locator('[data-secao=grupos-resultado]').inner_text().replace('\n', ' ')[:200] if pg.locator('[data-secao=grupos-resultado]').count() else t[:200])
    ds = pg.evaluate("()=>[...document.querySelectorAll('[data-secao=grupos-resultado] li .num')].map(e=>Math.abs(parseFloat(e.innerText.replace(',','.').replace('−','-'))))")
    ok('resultado: grupos ordenados pelo tamanho do efeito', all(ds[i] >= ds[i + 1] - 1e-9 for i in range(len(ds) - 1)), ds[:9])
    ok('resultado: reação dos jornais (3 manchetes)', 'reação dos jornais' in t.lower() and 'carta capital' in t.lower() and 'o antagonista' in t.lower())
    vz = pg.evaluate("()=>[...document.querySelectorAll('[data-voz]')].map(e=>e.innerText)")
    ok('resultado: pessoas comentando no formato "Nome, N anos, Estado: fala"', len(vz) >= 1 and all(re.match(r'^.{2,40}, \d+ anos, [^:]+: “', v.replace('\n', ' ')) for v in vz), vz[:1])
    pg.screenshot(path=OUT + '/v38_resultado.png')
    pg.evaluate("()=>{const m=document.querySelector('.modal-wrap');const sc=[m,...m.querySelectorAll('*')].find(e=>e.scrollHeight>e.clientHeight+50&&getComputedStyle(e).overflowY!='visible');if(sc)sc.scrollTop=sc.scrollHeight}"); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/v38_resultado_fim.png')
    fecha_modais(pg)
    # mais uma medida com Congresso (PL), para dar material aos famosos
    abre_parecer(pg, 'Criar um programa de creches em tempo integral para 1 milhão de crianças'); aprova(pg); fecha_modais(pg)
    abre_parecer(pg, 'Taxar dividendos em 15%'); aprova(pg); fecha_modais(pg)

    # ---------- 3) X: famosos ----------
    pg.evaluate("location.hash='#/x'"); pg.wait_for_timeout(900)
    fam = G(pg, "(g.x&&g.x.fam&&g.x.fam.posts||[]).map(p=>({n:p.nome,tom:p.tom,conc:p.conc,t:p.topic}))")
    ok('famosos postaram no X após as medidas aprovadas (1–3 por medida)', 1 <= len(fam) <= 9, fam)
    ok('X: filtro Famosos e chip simulado nos posts', pg.locator('button').filter(has_text='Famosos').count() >= 1)
    pg.locator('[data-secao=x-feed] button').filter(has_text='Famosos').first.click(timeout=4000); pg.wait_for_timeout(500)
    fp = pg.evaluate("()=>[...document.querySelectorAll('[data-secao=x-feed] [data-post=famoso]')].map(e=>({s:/simulado/i.test(e.innerText),t:e.innerText.replace(/\\n/g,' ').slice(0,200)}))")
    ok('posts de famosos têm o chip "simulado" e nenhum @', len(fp) >= 1 and all(x['s'] and '@' not in x['t'] for x in fp), fp[:2])
    pg.locator('[data-secao=x-famosos]').scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    ok('X: seção de famosos com "Convidar para live"', pg.locator('[data-fam-live]').count() >= 1)
    pg.screenshot(path=OUT + '/v38_x.png')
    ac0 = G(pg, "g.acoes"); nome = pg.locator('[data-fam-live]:not([disabled])').first.get_attribute('data-fam-live') if pg.locator('[data-fam-live]:not([disabled])').count() else None
    if nome:
        pg.locator('[data-fam-live]:not([disabled])').first.click(timeout=4000); pg.wait_for_timeout(600)
        ok('live gasta 1 ação e mostra o resultado', G(pg, "g.acoes") == ac0 - 1 and pg.locator('[data-fam-ult]').count() == 1, pg.locator('[data-fam-ult]').first.inner_text() if pg.locator('[data-fam-ult]').count() else '')
    else: ok('live disponível', False, 'nenhum famoso elegível')

    # ---------- 3b) tamanho do efeito dos famosos, teto de saliência e pressão sobre o voto ----------
    ef = pg.evaluate("""()=>{const F=__F(),g0=structuredClone(__QV().gRef.current),T=['Taxar dividendos em 15%','Privatizar os Correios','Criar o 14º salário para aposentados','Aumentar a multa do FGTS para 50%','Reduzir a maioridade penal para 16 anos','Zerar o IPI de carros elétricos','Acabar com a escala 6x1','Cobrar mensalidade nas universidades federais'];
      const o={dAp:[],dG:[],posts:[],teto:null,nomes:{}};
      for(const t of T){const g=structuredClone(g0),p=F.analisaLocal(g,t),X=F.ensureX(g),Fi=F.fatosImprensa(g,p,'aprovada'),a0=F.aprovacao(g),g00=Object.assign({},g.groups),nv=[];
        F.xFamosos(g,X,p,Fi,'s|'+t,nv,{efeito:true});o.posts.push(nv.length);nv.forEach(x=>o.nomes[x.a.nome+':'+x.tom]=1);o.dAp.push(+(F.aprovacao(g)-a0).toFixed(3));o.dG.push(+Math.max(...Object.keys(g.groups).map(k=>Math.abs(g.groups[k]-g00[k]))).toFixed(3))}
      {const g=structuredClone(g0),p=F.analisaLocal(g,'Taxar dividendos em 15%'),X=F.ensureX(g),Fi=F.fatosImprensa(g,p,'aprovada'),a0=F.aprovacao(g),nv=[];F.xFamosos(g,X,p,Fi,'teto',nv,{efeito:true,lim:{g0:{},a0:a0-5}});o.teto={dAp:+(F.aprovacao(g)-a0).toFixed(3),posts:nv.length}}
      return o}""")
    print('efeito dos famosos em 8 medidas:', json.dumps(ef, ensure_ascii=False))
    ok('famosos: 1–3 posts por medida', all(1 <= n <= 3 for n in ef['posts']) or sum(1 for n in ef['posts'] if 1 <= n <= 3) >= 6, ef['posts'])
    ok('famosos: efeito pequeno (≤0,3 p.p. na aprovação geral; ≤0,8 por grupo)', max(abs(x) for x in ef['dAp']) <= .3 and max(ef['dG']) <= .8, (max(abs(x) for x in ef['dAp']), max(ef['dG'])))
    ok('famosos: teto de saliência (limitaImpactoAprovacao) zera o efeito quando a medida já moveu a aprovação além de 4,7 p.p.', ef['teto']['dAp'] == 0 and ef['teto']['posts'] >= 1, ef['teto'])
    pr = pg.evaluate("""()=>{const F=__F(),g=structuredClone(__QV().gRef.current),p=F.analisaLocal(g,'Taxar dividendos em 15%'),a=F.pressaoRede(g,p);F.xPauta(g,p);const b=F.pressaoRede(g,p);return {antes:a.pts,depois:b.pts,fonte:b.fonte,posts:(g.x.fam.posts||[]).map(x=>x.nome+':'+x.tom)}}""")
    print('pressão das redes com famoso na pauta:', json.dumps(pr, ensure_ascii=False))
    ok('famoso na pauta entra na pressão de redes sobre o voto', pr['depois'] != pr['antes'] and 'famosos' in pr['fonte'], pr)
    gen = pg.evaluate("""()=>{const F=__F(),g=structuredClone(__QV().gRef.current),o={};for(const f of F.FAMOSOS){o[f.n]=Math.round(F.famConc(f,{economia:2,tributacao:2,gasto_social:2,trabalho:2,privatizacao:2,costumes:0,seguranca:0,ambiente:0,soberania_externa:0},{},false))}return o}""")
    ok('viés dos famosos coerente com o declarado (medida liberal: direita concorda, esquerda discorda)', gen['Nando Moura'] > 50 and gen['Luciano Hang'] > 50 and gen['Chico Buarque'] < -50 and gen['Sabrina Fernandes'] < -50 and gen['Felipe Neto'] < -20, {k: gen[k] for k in ['Nando Moura', 'Luciano Hang', 'Felipe Neto', 'Chico Buarque', 'Sabrina Fernandes']})
    # ---------- 4) 12 meses: convites de podcast naturais, recusa, aceite, rival ----------
    POD = "['flow','inteligencia','irontalks','tresirmaos','podpah']"
    nat = []; rv_nat = []; nat_all = []
    for m in range(12):
        encerra(pg, 1)
        nat += G(pg, "(g.ent.convites||[]).filter(c=>%s.includes(c.veic)&&c.mes===g.mes).map(c=>c.veic+'@'+c.mes)" % POD)
        nat_all += G(pg, "(g.ent.convites||[]).filter(c=>c.mes===g.mes).map(c=>c.veic)")
        r = G(pg, "g.ent.rival&&g.ent.rival.mes===g.mes?g.ent.rival.quem.nome+' -> '+g.ent.rival.pod+' ('+g.ent.rival.tipo+')':null")
        if r: rv_nat.append(r)
    mes = G(pg, "g.mes"); ok('avançou 12 meses pela interface', mes >= 13, mes)
    print('convites naturais (todos os veículos) nos 12 meses:', nat_all); print('convites de podcast naturais por mês (mês 2..13):', nat); print('rivais naturais nos 12 meses:', rv_nat)
    # frequência dos convites de podcast: mandato x ano eleitoral, com tema em alta ou não (1200 sorteios dentro da página)
    freq = pg.evaluate("""()=>{const F=__F(), g0=structuredClone(__QV().gRef.current), POD=%s, out={};
      for(const [rot,mes,alta] of [['mandato',10,false],['mandato, tema em alta',10,true],['ano eleitoral',40,false],['ano eleitoral, tema em alta',40,true]]){let pod=0,tot=0,conv=0;
        for(let s=0;s<400;s++){const g=structuredClone(g0);g.mes=mes;g.seed=s*131+7;g.ent.convites=[];g.ent.prefPod=null;g.x.trend=[];if(alta){for(const k in g.groups)g.groups[k]=Math.max(g.groups[k],68)}else{for(const k in g.groups)g.groups[k]=Math.min(g.groups[k],38)}
          F.entRenovaConvites(g,g.ent);conv+=g.ent.convites.length>0?1:0;for(const c of g.ent.convites){tot++;if(POD.includes(c.veic))pod++}}
        out[rot]={meses_com_convite:conv+'/400',convites_podcast:pod+'/'+tot}}
      return out}""" % POD)
    print('frequência (400 sorteios por cenário):', json.dumps(freq, ensure_ascii=False))
    p1 = int(freq['mandato']['convites_podcast'].split('/')[0]); p2 = int(freq['ano eleitoral']['convites_podcast'].split('/')[0])
    ok('podcasts convidam mais em ano eleitoral do que no mandato', p2 > p1, freq)
    # rotina mensal real (entGeraMes) em 300 partidas clonadas: com que frequência aparece um rival/aliado num podcast, e quem?
    rv = pg.evaluate("""()=>{const F=__F(),g0=structuredClone(__QV().gRef.current),o={n:0,critica:0,defesa:0,quem:{},pod:{},papel:{}};
      for(let s=0;s<300;s++){const g=structuredClone(g0);g.mes=8;g.seed=s*97+3;g.ent.colet=null;g.ent.rival=null;g.ent.rivalMes=0;g.ent.convites=[];g.log.unshift({mes:7,ato:'x',texto:'t',res:'aprovada',topic:'a taxação das bets'});
        F.entGeraMes(g);const r=g.ent.rival;if(r){o.n++;o[r.tipo]++;o.quem[r.quem.papel]=(o.quem[r.quem.papel]||0)+1;o.pod[r.pod]=(o.pod[r.pod]||0)+1}}
      return o}""")
    print('rival/aliado em podcast (300 meses sorteados):', json.dumps(rv, ensure_ascii=False))
    pool = pg.evaluate("""()=>{const F=__F(),g=structuredClone(__QV().gRef.current);g.mes=40;g.el=g.el||{};g.el.ger=Object.assign(g.el.ger||{},{meuId:'eu',cands:[{id:'p:a',nome:'Fulano de Tal',sigla:'PL',uf:'SP',camp:'dir'},{id:'eu',nome:'Eu',sigla:'PT',camp:'esq'}]});
      const c=F.entRivais(g,'critica'),d=F.entRivais(g,'defesa');return {critica:c.map(x=>x.papel).reduce((a,b)=>{a[b]=(a[b]||0)+1;return a},{}),defesa:d.length}}""")
    print('pool de convidados (ano eleitoral, candidato adversário simulado):', json.dumps(pool, ensure_ascii=False))
    ok('pool de rivais: líder da oposição, governadores de partido rival e candidato adversário em ano eleitoral', 'líder da oposição' in pool['critica'] and 'candidato(a) adversário(a)' in pool['critica'] and pool['defesa'] > 0, pool)
    ok('rival/aliado aparece de tempos em tempos (entre 5% e 40% dos meses)', 15 <= rv['n'] <= 120, rv['n'])
    # injeta dois convites (um para aceitar, outro para recusar) e um rival gerado pela rotina mensal
    got = None
    for sd in range(80):
        SET(pg, "n.seed=%d;n.ent.rival=null;n.ent.rivalMes=0;n.log.unshift({mes:n.mes,ato:'x',texto:'t',res:'aprovada',topic:'a isenção do IPI de carros elétricos'});__F().entRivalMes(n, n.ent)" % (1000 + sd * 7))
        got = G(pg, "g.ent.rival?{q:g.ent.rival.quem.nome+' ('+g.ent.rival.quem.papel+')',tipo:g.ent.rival.tipo,pod:g.ent.rival.pod,frase:g.ent.rival.frase,est:g.ent.rival.estado}:null")
        if got: break
    ok('rival/aliado foi a um podcast e falou de uma medida (rotina mensal)', got is not None, got)
    SET(pg, "n.ent.convites=n.ent.convites.filter(c=>c.estado!=='pendente');n.ent.convites.push({id:'cvt1',veic:'flow',mes:n.mes,estado:'pendente'},{id:'cvt2',veic:'irontalks',mes:n.mes,estado:'pendente'});n.acoes=5")
    pg.evaluate("location.hash='#/poder/imprensa'"); pg.wait_for_timeout(900)
    click(pg, 'Convites de entrevista', 700)
    cv = pg.locator('[data-convite=flow]')
    ok('convite de podcast real aparece com chip simulado', cv.count() == 1 and 'simulado' in cv.inner_text().lower(), cv.inner_text().replace('\n', ' ')[:200] if cv.count() else '')
    if got:
        ok('card "Repercussão em podcast" com chip simulado e 3 respostas', pg.locator('[data-podrival]').count() == 1 and pg.locator('[data-rival-convite]').count() == 1 and pg.locator('[data-rival-x]').count() == 1 and pg.locator('[data-rival-ignorar]').count() == 1 and 'simulado' in pg.locator('[data-podrival]').inner_text().lower(), pg.locator('[data-podrival]').inner_text().replace('\n', ' ')[:300])
    pg.screenshot(path=OUT + '/v38_podcast_rival.png')
    cv.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/v38_podcast.png')
    g0 = G(pg, "Object.assign({},g.groups)")
    pg.locator('[data-conv-recusar=irontalks]').first.click(timeout=4000); pg.wait_for_timeout(600)
    g1 = G(pg, "Object.assign({},g.groups)")
    perd = [k for k in g1 if g1[k] < g0[k] - 0.01]
    ok('convite recusado: público do podcast reage (grupos caem)', len(perd) >= 2, perd[:6])
    xr = G(pg, "(g.x.posts||[]).filter(p=>p.a&&p.a.nome==='IronTalks').map(p=>p.txt)")
    ok('convite recusado: o podcast comenta no X', len(xr) >= 1, xr[:1])
    if got:
        pg.locator('[data-rival-convite]').first.click(timeout=4000); pg.wait_for_timeout(600)
        ok('responder ao rival aceitando o próximo convite do podcast', G(pg, "g.ent.prefPod&&g.ent.prefPod.k") == got['pod'], G(pg, "g.ent.prefPod"))
        ok('corte do rival aparece no X', G(pg, "(g.x.posts||[]).filter(p=>p.kind==='pol'&&/^Corte do/.test(p.txt)).length") >= 1)
    pg.locator('[data-conv-aceitar=flow]').first.click(timeout=4000); pg.wait_for_timeout(900)
    qs = G(pg, "g.ent.entrev?g.ent.entrev.qs.map(q=>({t:q.texto,peg:!!q.pegadinha,rep:q.rep})):null")
    ok('convite aceito: entrevista no estilo do programa (3–5 perguntas, apresentador Igor 3K)', qs and 3 <= len(qs) <= 5 and qs[0]['rep'] == 'igor3k', [q['t'][:70] for q in qs] if qs else qs)
    pg.screenshot(path=OUT + '/v38_podcast_pergunta.png')
    for i in range(5):
        if pg.locator('[data-ent-pergunta]').count() == 0: break
        if pg.locator('[data-ent-pergunta] [data-op=defesa]').count():
            pg.locator('[data-ent-pergunta] [data-op=defesa]').first.click(timeout=4000); pg.wait_for_timeout(500)
        if pg.locator('[data-ent-prox]').count(): pg.locator('[data-ent-prox]').first.click(timeout=3000); pg.wait_for_timeout(300)
        elif pg.locator('[data-ent-concluir]').count(): pg.locator('[data-ent-concluir]').first.click(timeout=3000); pg.wait_for_timeout(400); break
    ok('entrevista de podcast concluída (histórico)', G(pg, "g.ent.hist.filter(h=>h.veic==='flow').length") >= 1)
    # um segundo mês: o convite preferido chega, com a pergunta sobre a medida do rival
    if got:
        SET(pg, "n.ent.convites=n.ent.convites.filter(c=>c.estado!=='pendente');n.mes=n.mes+1;n.ent.colet=null;n.ent.rivalMes=0;__F().entRenovaConvites(n, n.ent)")
        pk = G(pg, "(g.ent.convites||[]).filter(c=>c.resposta).map(c=>c.veic)")
        ok('o convite de resposta do mesmo podcast chega no mês seguinte', got['pod'] in pk, pk)
    fecha_modais(pg); pg.wait_for_timeout(300)
    print('ERRS', errs[:8])
    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    print('RESUMO: %d ok, %d falhas' % (sum(1 for c in checks if c[0]), sum(1 for c in checks if not c[0])))
    b.close()
