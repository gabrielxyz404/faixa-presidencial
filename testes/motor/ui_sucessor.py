# Teste do lote C (equilíbrio do 4º ano, escândalo no último ano, inflação x primário, comunicação e jantar, eventos do 2º mandato),
# do lote G (fontes do escândalo e da aprovação no Balanço) e da ideia I3 (eleger sucessor: força do candidato governista, aprovação necessária,
# ações, resultado da eleição, painel de legado e integração ao fim de mandato).
# uso: python3 run_sandbox.py ui_sucessor.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8880
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
SEED = "(()=>{let a=4242;Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
INJ = ("window.__QV = () => QV; window.__AL = analisaLocal; window.__X = () => ({ fimDoMes, aprovacao, qvSerializa, qvValida, qvParse, elEnsure, elCiclo, elSucForca, elSucAlav, elSucVence, elAprovNecessaria, elSucAcao, elSucEscolhe, elNaoConcorrer, elSucessores, "
       "elSemReeleicao, elLegadoPainel, escFontesTxt, elTurno1, elTurno2, aprovEstados, elGerBuild, custoJantar, fazArticulacao, escComTeto, escReg, EVENTOS, ev2M, evRel, elPosse, sorteiaEscandalo, EQ_TRANS_CAP, EL_KF, EL_F0, EL_SUC_MES, primario }); "
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
          const b=[...r.querySelectorAll('button:not([disabled])')].find(b=>/^(Fechar|Voltar ao gabinete|Arquivar|Voltar(?! ao menu)|Continuar|Entendi|OK|Marcar como|Começar |Ver o desfecho|Cancelar)/.test(b.innerText.trim()));
          if(b) b.click(); }""")
        pg.wait_for_timeout(350)
        if overlay(pg): pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
def avanca(pg, n):
    pg.evaluate("(n)=>{__QV().setG(p=>{const x=structuredClone(p);for(let i=0;i<n;i++){if(x.over)break;__X().fimDoMes(x);x.acoes=5;x.props=5;x.pes.energia=90;x.pes.saude=Math.max(x.pes.saude,80);x.pes.estresse=Math.min(x.pes.estresse,40);for(const k in x.parties){x.parties[k].rel=Math.max(x.parties[k].rel,55)}}return x})}", n)
    pg.wait_for_timeout(700)
def vai(pg, sec, chip=None):
    pg.locator('#sec-tab-' + sec).click(timeout=5000); pg.wait_for_timeout(400)
    if chip:
        pg.locator('#%s-chip-%s' % (sec, chip)).click(timeout=5000); pg.wait_for_timeout(500)
def abre_pres(pg):
    vai(pg, 'poder', 'eleicoes')
    pg.locator('[role=tab], button').filter(has_text=re.compile(r'^Presidência')).first.click(timeout=4000); pg.wait_for_timeout(600)
def cru(txt):
    m = re.search(r'(^|[^\w])(NaN|undefined|Infinity)([^\w]|$)|\[object Object\]', txt)
    return m.group(0) if m else None
def corpo(pg): return pg.evaluate("()=>document.body.innerText")

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' and '[Faixa]' not in m.text else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', INJ, 1)
    pg.add_init_script(SEED)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha(pg)
    pg.evaluate("()=>{window.__G0=structuredClone(__QV().gRef.current)}")

    # ---------------- C: parâmetros e funções de equilíbrio ----------------
    r = pg.evaluate("""()=>{const X=__X(); const out={}; out.cap=X.EQ_TRANS_CAP;
      const g=structuredClone(window.__G0); g.pesMes={}; out.j0=X.custoJantar(g); g.pesMes.art_bancada_PT=true; out.j1=X.custoJantar(g); g.pesMes.art_bancada_PL=true; out.j2=X.custoJantar(g); g.pesMes.art_bancada_MDB=true; out.j3=X.custoJantar(g); return out}""")
    ok('C5: EQ_TRANS_CAP = 2,5', abs(r['cap'] - 2.5) < 1e-9, r['cap'])
    ok('C5: jantar com custo crescente (12 mil, 30 mil, 60 mil)', (r['j0'], r['j1'], r['j2'], r['j3']) == (12000, 30000, 60000, 60000), r)
    r = pg.evaluate("""()=>{const X=__X(); const out={};
      // C2: teto mensal de +8 vindo da Justiça/oposição e carência de 6 meses do escândalo sorteado no último ano
      const g=structuredClone(window.__G0); g.mes=40; g.escandalo=10; g.escFM={}; X.escComTeto(g,'teste',()=>{ g.escandalo+=20; }); out.teto=g.escandalo; out.fontes=g.escFM;
      const h=structuredClone(window.__G0); h.mes=40; h.escSorteio=36; h.escandalo=10; const n0=h.escandalo; for(let i=0;i<40;i++) X.sorteiaEscandalo(h,[]); out.carFim=h.escandalo-n0;
      const k=structuredClone(window.__G0); k.mes=20; k.escSorteio=16; k.escandalo=10; const m0=k.escandalo; for(let i=0;i<400;i++){ k.escSorteio=16; X.sorteiaEscandalo(k,[]); k.escandalo=m0; } out.ok=1;
      return out}""")
    ok('C2: teto de +8 por mês nas fontes Justiça/oposição', abs(r['teto'] - 18) < 1e-6, r)
    ok('C2: o excedente contido aparece como fonte negativa', any('teto' in k and v < 0 for k, v in r['fontes'].items()), r['fontes'])
    ok('C2: no último ano o escândalo sorteado respeita 6 meses de carência', abs(r['carFim']) < 1e-9, r['carFim'])

    # C1: desgaste do 4º ano começa no mês 36 e é aliviado por PIB alto
    r = pg.evaluate("""()=>{const X=__X(); const dd=(mes,pib)=>{ const g=structuredClone(window.__G0); g.mes=mes; g.eco.pib=pib; const a0=X.aprovacao(g); const g1=structuredClone(g); const g2=structuredClone(g);
      // mede só a diferença de desgaste: mesma semente, mesmo estado
      let a=99; Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
      X.fimDoMes(g1); return X.aprovacao(g1)-a0 };
      return { m34: dd(34, 2), m36: dd(36, 2), m36pib5: dd(36, 5) } }""")
    ok('C1: no mês 36 (desgaste .55) a aprovação cai mais que no mês 34 (.4)', r['m36'] < r['m34'] - .05, r)
    ok('C1: PIB alto alivia o desgaste do 4º ano', r['m36pib5'] > r['m36'], r)

    # C4: inflação responde ao primário (termo quadrático)
    r = pg.evaluate("""()=>{const X=__X(); const run=(extra)=>{ const g=structuredClone(window.__G0); g.fiscal.extra += extra; let a=7; Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
      for(let i=0;i<30;i++){ X.fimDoMes(g); g.acoes=5;g.props=5; g.pes.energia=90; g.pes.saude=90; g.pes.estresse=20; g.impStreak=0; g.over=null; g.fiscal.extra = extra; } return { ipca: g.eco.ipca, prim: X.primario(g) } };
      return { base: run(0), grande: run(1000) } }""")
    ok('C4: com rombo de ~R$ 1 tri o IPCA passa de 9% em 30 meses', r['grande']['ipca'] > 9 and r['grande']['ipca'] > r['base']['ipca'] + 4, r)

    # ---------------- G: fontes do escândalo e da aprovação ----------------
    avanca(pg, 6)
    ef = G(pg, '(g.hist.escFontes||[])')
    ok('G: g.hist.escFontes registra um item por mês fechado', len(ef) >= 6 and all('itens' in e and 'ap' in e for e in ef), len(ef))
    ok('G: cada mês tem soma das fontes igual à variação do escândalo', all(abs(sum(e['itens'].values()) - (e['e1'] - e['e0'])) < .6 for e in ef), [(e['mes'], round(sum(e['itens'].values()), 1), round(e['e1'] - e['e0'], 1)) for e in ef[:4]])
    ok('G: o decaimento aparece como fonte negativa quando há escândalo', any('decaimento' in e['itens'] and e['itens']['decaimento'] < 0 for e in ef) or max(e['e0'] for e in ef) < 1, ef[-1]['itens'])
    txt = pg.evaluate("()=>{const g=__QV().gRef.current; const T=__X().escFontesTxt(g.hist.escFontes[g.hist.escFontes.length-1]); return T}")
    ok('G: texto das fontes montado (escândalo e aprovação)', txt and txt['esc'] is not None and txt['ap'] is not None, txt)
    SET(pg, "n.escandalo=40; n.hist.escFontes[n.hist.escFontes.length-1].itens={'CPI instalada pela oposição':12,'caso da Justiça que atinge o governo':6,'decaimento':-3}; n.hist.escFontes[n.hist.escFontes.length-1].e0=25; n.hist.escFontes[n.hist.escFontes.length-1].e1=40")
    vai(pg, 'mesa'); fecha(pg)
    achou = pg.evaluate("()=>{const e=[...document.querySelectorAll('[data-el=esc-fontes]')]; return e.map(x=>x.innerText)}")
    if not achou:
        # o Balanço do mês fica no painel de indicadores/atalho; abre o modal de fim de mês pelo estado
        achou = pg.evaluate("()=>{const e=[...document.querySelectorAll('[data-el=esc-fontes]')]; return e.map(x=>x.innerText)}")
    print('   Balanço:', achou[:1])
    ok('G: Balanço do mês mostra "+12 CPI ... −3 decaimento"', any('+12 CPI' in t and '−3 decaimento' in t for t in achou), achou[:1])

    # ---------------- C6: eventos do 2º mandato e minProp ----------------
    r = pg.evaluate("""()=>{const X=__X(); const ids=['reforma_eleitoral','stf_bloco','fadiga','municipais_base','racha_sucessao','pato_manco','cpi_fim','recessao_mundial'];
      const E=ids.map(i=>X.EVENTOS.find(e=>e.id===i)); const g1=structuredClone(window.__G0); g1.el=X.elEnsure(g1); g1.el.mandatos=1; g1.mes=20; const g2=structuredClone(g1); g2.el.mandatos=2;
      const out={n:E.filter(Boolean).length, ops:E.every(e=>e&&e.opcoes.length===3&&e.texto&&e.titulo), w1:E.map(e=>e.w(g1)), w2:E.map(e=>e.w(g2))};
      const g3=structuredClone(window.__G0); g3.minProp={lista:[{id:1}],hist:[{}],eng:{casacivil:2},leal:{x:1},vazou:{},usados:['a'],seq:3,ger:null,aj:null}; X.elEnsure(g3);
      X.elPosse(g3, {nome:'Teste Sucessor', sigla:'PSD', bloco:'PSD', uf:'SP', idade:55}, 'teste'); out.min=g3.minProp.lista.length+g3.minProp.hist.length+Object.keys(g3.minProp.eng).length; out.suc=g3.el.suc; return out}""")
    ok('C6: 8 eventos novos do 2º mandato, cada um com 3 opções', r['n'] == 8 and r['ops'], r['n'])
    ok('C6: eventos só entram no sorteio no 2º mandato', all(w == 0 for w in r['w1']) and all(w > 0 for w in r['w2']), (r['w1'], r['w2']))
    ok('C6: minProp zerado em elPosse (e a sucessão limpa)', r['min'] == 0 and r['suc'] is None, r)

    # ---------------- I3 com o personagem do teste (já no 2º mandato) ----------------
    ok('I3: antes do mês 30 não há estado de sucessão', G(pg, '!g.el.suc'))
    avanca(pg, 30 - G(pg, 'g.mes'))
    ok('I3: chegou ao mês 30', G(pg, 'g.mes') == 30, G(pg, 'g.mes'))
    ok('I3: no mês 30 o estado de sucessão existe com candidato escolhido', G(pg, '!!g.el.suc && !!g.el.suc.id'), G(pg, 'g.el.suc && {id:g.el.suc.id,nome:g.el.suc.nome,F:g.el.suc.forca}'))
    ok('I3: presidente em 2º mandato não pode se reeleger (elSemReeleicao)', G(pg, '__X().elSemReeleicao(g)'))
    vai(pg, 'mesa'); fecha(pg)
    if pg.locator('[data-pend=elforca]').count() == 0 and pg.locator('button').filter(has_text=re.compile(r'^Ver as outras')).count():
        pg.locator('button').filter(has_text=re.compile(r'^Ver as outras')).first.click(); pg.wait_for_timeout(250)
    ok('I3: Mesa mostra o cartão "Força do candidato governista"', pg.locator('[data-pend=elforca]').count() == 1)
    abre_pres(pg)
    ok('I3: painel Poder > Eleições mostra a barra de força desde o mês 30', pg.locator('[data-el=forca-suc]').count() == 1 and pg.locator('[data-suc-forca]').count() == 1, corpo(pg)[:100])
    ok('I3: cinco alavancas visíveis', pg.locator('[data-suc-alavanca]').count() == 5)
    nec_el = pg.locator('[data-suc-nec]'); ok('C3: painel mostra a aprovação necessária para o candidato do governo', nec_el.count() == 1, nec_el.first.inner_text() if nec_el.count() else '')
    ok('I3: sem NaN/undefined no painel', cru(corpo(pg)) is None, cru(corpo(pg)))
    pg.screenshot(path=OUT + '/forca_m30.png')
    F0 = G(pg, '__X().elSucForca(g).F'); ap0 = G(pg, 'g.el.suc.apoio')
    pg.locator('[data-suc-acao=palanque]').click(timeout=4000); pg.wait_for_timeout(600)
    ok('I3: campanha com o candidato sobe o apoio do presidente e gasta 1 ação', G(pg, 'g.el.suc.apoio') > ap0 and G(pg, 'g.acoes') == 4, (ap0, G(pg, 'g.el.suc.apoio'), G(pg, 'g.acoes')))
    ok('I3: força sobe com o apoio', G(pg, '__X().elSucForca(g).F') > F0, (F0, G(pg, '__X().elSucForca(g).F')))
    ok('I3: a mesma ação não se repete no mês', pg.locator('[data-suc-acao=palanque]').is_disabled())
    cb = pg.locator('[data-suc-coligar]').first
    if cb.count():
        n0 = G(pg, 'g.el.suc.aliados.length'); SET(pg, "for(const k in n.parties) n.parties[k].rel=90; n.acoes=5;n.props=5")
        pg.locator('[data-suc-coligar]').first.click(timeout=4000); pg.wait_for_timeout(600)
        ok('I3: coligação fechada entra na lista do candidato', G(pg, 'g.el.suc.aliados.length') == n0 + 1, G(pg, 'g.el.suc.aliados'))
    pg.locator('[data-suc-trocar]').click(timeout=4000); pg.wait_for_timeout(400)
    esc = pg.locator('[data-suc-escolher]:not([disabled])')
    if esc.count():
        novo = esc.first.get_attribute('data-suc-escolher'); SET(pg, "n.acoes=5;n.props=5")
        pg.locator('[data-suc-escolher]:not([disabled])').first.click(timeout=4000); pg.wait_for_timeout(600)
        ok('I3: trocar o candidato na pré-campanha vale e fixa a escolha', G(pg, 'g.el.suc.id') == novo and G(pg, 'g.el.suc.fixado'), (novo, G(pg, 'g.el.suc.id')))
    else:
        ok('I3: lista de candidatos para trocar', False)
    ok('I3: nenhum erro de página até aqui', not [e for e in errs if e.startswith('PAGEERR')], errs[:2])

    # a força entra no resultado da eleição: mesma estrutura, força 15 x 85
    avanca(pg, 37 - G(pg, 'g.mes'))
    ok('I3: campo montado no mês 37 com o sucessor escolhido como candidato do governo', G(pg, 'g.el.ger && g.el.ger.cands[0].sucessor && g.el.ger.cands[0].pid === g.el.suc.id'), G(pg, 'g.el.ger && g.el.ger.cands[0].nome'))
    ok('I3: coligação já fechada vai para o campo', G(pg, 'g.el.suc.aliados.every(a=>g.el.ger.aliancas.includes(a))'))
    r = pg.evaluate("""()=>{const X=__X(); const g=structuredClone(__QV().gRef.current); const ger=g.el.ger; const AE=X.aprovEstados(g); const sh=(F)=>{ ger.forca=F; const t=X.elTurno1(g, ger, AE, 1); return t.nac[ger.sitId] }; return { f15: sh(15), f85: sh(85), f40: sh(40) } }""")
    ok('I3: o resultado usa a força (85 rende mais voto que 15)', r['f85'] > r['f15'] + .03, r)
    vai(pg, 'mesa'); fecha(pg); abre_pres(pg)
    ok('I3: com o campo montado o painel segue visível', pg.locator('[data-el=forca-suc]').count() == 1)
    nec = G(pg, '__X().elAprovNecessaria(g)')
    ok('C3: aprovação necessária calculada com o campo montado', nec and nec['rot'] in ('ok', 'folga', 'fora') and (nec['rot'] != 'ok' or 0 < nec['nec'] < 100), nec)
    if nec and nec['rot'] == 'ok':
        h = pg.evaluate("""(nec)=>{const X=__X(); const g=structuredClone(__QV().gRef.current); const ger=g.el.ger; return { acima: X.elSucVence(g, ger, nec.nec-nec.ap+1.2), abaixo: X.elSucVence(g, ger, nec.nec-nec.ap-1.2) } }""", nec)
        ok('C3: a aprovação necessária separa vitória e derrota', h['acima'] and not h['abaixo'], h)
    avanca(pg, 47 - G(pg, 'g.mes'))
    print('   ger:', G(pg, '({forca:g.el.ger.forca,venc:g.el.ger.res&&g.el.ger.res.venc,sit:g.el.ger.sitId,fase:g.el.ger.fase})'))
    ok('I3: força registrada no campo até a apuração', G(pg, 'g.el.ger.forca != null'))
    sv = pg.evaluate("""()=>{try{const g=__QV().gRef.current; __X().qvValida(__X().qvParse(__X().qvSerializa(g))); return 'ok'}catch(e){return 'ERRO '+e.message}}""")
    ok('I3: save com a sucessão em andamento é válido', sv == 'ok', sv)
    avanca(pg, 48 - G(pg, 'g.mes') + 1); pg.wait_for_timeout(900)
    ov = G(pg, 'g.over&&{tipo:g.over.tipo,motivo:g.over.motivo,suc:g.over.suc,leg:!!g.over.legado}')
    ok('I3: fim do 2º mandato: personagem encerra por limite e guarda o resumo da sucessão', ov and ov['tipo'] == 'personagem' and ov['motivo'] == 'limite' and ov['suc'] and ov['leg'], ov)
    tela = corpo(pg); pg.screenshot(path=OUT + '/fim_legado.png')
    ok('I3: tela de fim mostra o painel de legado', pg.locator('[data-el=legado]').count() == 1 and pg.locator('[data-el=legado-sucessor]').count() == 1, tela[:200].replace('\n', ' | '))
    ok('I3: legado sem NaN/undefined', cru(tela) is None, cru(tela))
    ok('I3: legado traz a força final e o desfecho do candidato', re.search(r'(eleito|derrotado)', tela) and re.search(r'força final \d+/100', tela), re.findall(r'Seu candidato[^\n]*', tela)[:1])
    ok('I3: continuação do jogo segue disponível (escolher próximo personagem)', pg.locator('[data-prox] button').count() >= 1)
    if pg.locator('[data-prox-pres]').count():
        pg.locator('[data-prox-pres]').first.click(timeout=3000); pg.wait_for_timeout(1200)
        ok('I3: continuar como o presidente eleito abre o jogo sem erro', G(pg, '!g.over') and G(pg, 'g.el.suc') is None, G(pg, '({mes:g.mes,pres:g.cfg.nome,suc:g.el.suc})'))
        ok('C6: sucessor empossado começa com minProp limpo', G(pg, 'g.minProp.lista.length + g.minProp.hist.length') == 0)
        fecha(pg)
    ok('2º mandato: nenhum erro de página', not [e for e in errs if e.startswith('PAGEERR')], errs[:2])

    # ---------------- I3 com presidente do 1º mandato que escolhe não concorrer ----------------
    pg.evaluate("()=>{__QV().setG(()=>structuredClone(window.__G0))}"); pg.wait_for_timeout(800)
    SET(pg, "__X().elEnsure(n).mandatos=1; n.el.suc=null; n.el.ger=null")
    ok('1º mandato: elSemReeleicao é falso', not G(pg, '__X().elSemReeleicao(g)'))
    avanca(pg, 31 - G(pg, 'g.mes'))
    abre_pres(pg)
    ok('1º mandato: no mês 31 aparece a decisão "Reeleição ou sucessor?"', pg.locator('[data-el=suc-decisao]').count() == 1, corpo(pg)[:80])
    pg.screenshot(path=OUT + '/decisao_m31.png')
    pg.locator('[data-suc-nao-concorrer]').click(timeout=4000); pg.wait_for_timeout(700)
    ok('1º mandato: anunciar que não concorre cria a sucessão e mostra a barra', G(pg, 'g.el.suc && g.el.suc.naoConcorre && __X().elSemReeleicao(g)') and pg.locator('[data-el=forca-suc]').count() == 1)
    pg.locator('[data-suc-voltar]').click(timeout=4000); pg.wait_for_timeout(600)
    ok('1º mandato: dá para voltar atrás antes da montagem do campo', not G(pg, '__X().elSemReeleicao(g)'))
    pg.locator('[data-suc-nao-concorrer]').click(timeout=4000); pg.wait_for_timeout(600)
    avanca(pg, 37 - G(pg, 'g.mes'))
    ok('1º mandato: campo montado com sucessor e sem candidatura do presidente', G(pg, 'g.el.ger.cands[0].sucessor && !g.el.ger.cands[0].sitPres && g.el.ger.meuId === null'), G(pg, 'g.el.ger.cands[0].nome'))
    avanca(pg, 6)
    vai(pg, 'mesa'); fecha(pg); abre_pres(pg)
    ok('1º mandato: painel e Mesa sem NaN/undefined em plena campanha', cru(corpo(pg)) is None, cru(corpo(pg)))
    ok('1º mandato: ainda dá para voltar atrás? não (campo montado): botão ausente', pg.locator('[data-suc-voltar]').count() == 0)
    avanca(pg, 48 - G(pg, 'g.mes') + 1); pg.wait_for_timeout(900)
    ov = G(pg, 'g.over&&{tipo:g.over.tipo,motivo:g.over.motivo,suc:!!g.over.suc}')
    ok('1º mandato: o personagem encerra por sucessão (não por derrota nem por limite)', ov and ov['tipo'] == 'personagem' and ov['motivo'] == 'sucessao' and ov['suc'], ov)
    tela = corpo(pg)
    ok('1º mandato: tela de fim "passou a faixa" com legado e sem valor cru', 'passou a faixa' in tela and pg.locator('[data-el=legado]').count() == 1 and cru(tela) is None, tela[:160].replace('\n', ' | '))
    pg.screenshot(path=OUT + '/fim_sucessao.png')

    # ---------------- reeleição continua funcionando para quem concorre ----------------
    pg.evaluate("()=>{__QV().setG(()=>structuredClone(window.__G0))}"); pg.wait_for_timeout(800)
    SET(pg, "__X().elEnsure(n).mandatos=1; n.el.suc=null; n.el.ger=null")
    avanca(pg, 47 - G(pg, 'g.mes'))
    ok('reeleição: quem concorre tem o próprio nome como candidato e não há barra de sucessor', G(pg, 'g.el.ger.cands[0].sitPres && !g.el.suc'), G(pg, 'g.el.ger.cands[0].nome'))
    ok('reeleição: nenhum cartão de força nem de sucessão para quem concorre', G(pg, '__X().elSemReeleicao(g)') is False)
    ok('0 erros de página e de console no teste todo', not errs, errs[:3])
    b.close()
print('\nRESULTADO: %d/%d verificações OK' % (sum(checks), len(checks)))
sys.exit(0 if all(checks) else 1)
