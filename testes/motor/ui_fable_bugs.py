# Teste das correções da revisão independente (B1, B2, B4, B5, B6, B7, B8, B9, C1-C3), da fronteira de erro e do jogo depois de 2034
# (reeleição forçada em 2030, segundo mandato até o mês 96, fim do personagem, continuação como outro personagem, saves e rótulos de mês).
# uso: python3 run_sandbox.py ui_fable_bugs.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8870
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
SEED = "(()=>{let a=777;Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
INJ = ("window.__QV = () => QV; window.__AL = analisaLocal; window.__X = () => ({ fimDoMes, aprovacao, qvSerializa, qvValida, qvParse, elEnsure, elCiclo, elO, elDiscurso, medResumo, escolheEventoNovo, riscoImpeachment, elEscolheProximo, elSucessores }); "
       "function analisaLegado(g, texto) {")
checks = []; errs = []; logs_console = []
def ok(nome, cond, det=''):
    checks.append(bool(cond)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:260]) if det != '' else ''), flush=True)
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
    """fimDoMes via JS n vezes, mantendo o personagem vivo (ações, energia, saúde, escândalo, base)"""
    pg.evaluate("(n)=>{__QV().setG(p=>{const x=structuredClone(p);for(let i=0;i<n;i++){if(x.over)break;__X().fimDoMes(x);x.acoes=5;x.pes.energia=90;x.pes.saude=Math.max(x.pes.saude,80);x.pes.estresse=Math.min(x.pes.estresse,40);x.escandalo=Math.min(x.escandalo,10);for(const k in x.parties){x.parties[k].rel=Math.max(x.parties[k].rel,55)}}return x})}", n)
    pg.wait_for_timeout(700)
def vai(pg, sec, chip=None):
    pg.locator('#sec-tab-' + sec).click(timeout=5000); pg.wait_for_timeout(400)
    if chip:
        pg.locator('#%s-chip-%s' % (sec, chip)).click(timeout=5000); pg.wait_for_timeout(500)
def barra(pg): return pg.evaluate("()=>{const e=document.querySelector('[data-vital-v=mes]');return e?e.innerText:null}")
def cru(txt):
    m = re.search(r'(^|[^\w])(NaN|undefined|Infinity)([^\w]|$)|\[object Object\]', txt)
    return m.group(0) if m else None
def corpo(pg): return pg.evaluate("()=>document.body.innerText")
def fecha_modais(pg):
    for _ in range(4):
        if pg.locator('.modal-wrap').count() == 0: break
        try: pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^(Fechar|Continuar|OK|Entendi|Seguir|Próximo mês|Voltar à Mesa)')).first.click(timeout=1200)
        except Exception: pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
def on_console(m):
    if m.type == 'error':
        logs_console.append(m.text)
        if 'erro forçado' not in m.text and '[Faixa]' not in m.text: errs.append('CONSOLE ' + m.text[:300])

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', on_console)
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', INJ, 1)
    pg.add_init_script(SEED)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha(pg)
    SET(pg, "__X().elEnsure(n).mandatos=1")  # o Lula do teste já tem 2 mandatos; aqui o presidente ainda pode se reeleger

    # ---------- B5: emendas e pesquisa devolvidas ao retirar a proposta ----------
    e0 = G(pg, 'g.fiscal.extra')
    pg.fill('#caixa', 'Reforma administrativa com fim da estabilidade para novos servidores'); click(pg, 'Assinar e enviar', 2200)
    em = pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^Emendas p/'))
    n_em = em.count()
    for i in range(3):  # a lista de indecisos encolhe a cada emenda: reconta a cada volta
        if not em.count(): break
        try: em.first.click(timeout=2000)
        except Exception: break
        pg.wait_for_timeout(300)
    pq = pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^Fazer pesquisa popular'))
    if pq.count(): pq.first.click(timeout=2000); pg.wait_for_timeout(500)
    e1 = G(pg, 'g.fiscal.extra')
    ok('B5: emendas/pesquisa cobram na hora (pré-condição)', e1 > e0, (e0, e1, n_em))
    pg.locator('.modal-wrap button').filter(has_text='Retirar proposta').first.click(timeout=3000); pg.wait_for_timeout(600)
    e2 = G(pg, 'g.fiscal.extra')
    ok('B5: retirar a proposta devolve emendas e pesquisa', abs(e2 - e0) < 1e-6, (e0, e1, e2))
    fecha(pg)

    # ---------- B7: medida consolidada conta como em vigor ----------
    pg.fill('#caixa', 'Zerar o IPI de carros elétricos'); click(pg, 'Assinar e enviar', 2200)
    btns = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
    alvo = next((x for x in ['Assinar e publicar no DOU', 'Votar agora'] if x in btns), None)
    if alvo: pg.locator('.modal-wrap button').filter(has_text=alvo).first.click(timeout=4000); pg.wait_for_timeout(1500)
    for _ in range(6):
        bb = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
        pick = next((x for x in bb if re.match(r'^(Ver resultado|Concluir|Apurar|Aplicar|Fechar|Continuar|Encerrar votação|Pular)', x)), None)
        if not pick: break
        try: pg.locator('.modal-wrap button').filter(has_text=pick).first.click(timeout=3000)
        except Exception: pass
        pg.wait_for_timeout(900)
    fecha_modais(pg)
    nmed = G(pg, '(g.medidas||[]).length')
    if nmed:
        SET(pg, "n.medidas[0].estado='consolidada'")
        r = G(pg, '__X().medResumo(g)')
        ok('B7: medResumo conta a consolidada em vigor', r and r['n'] >= 1, r)
        vai(pg, 'medidas'); pg.wait_for_timeout(500)
        txt = pg.evaluate("()=>document.querySelector('[data-secao-medidas]').innerText")
        m = re.search(r'EM VIGOR\s*\n?\s*(\d+)', txt, re.I)
        ok('B7: painel Medidas mostra "Em vigor" >= 1 com decreto consolidado', m and int(m.group(1)) >= 1, txt[:120].replace('\n', ' | '))
        vai(pg, 'mesa')
    else:
        ok('B7: medida criada para o teste', False, 'nenhuma medida')

    # ---------- B6: concordância "500 mil crianças" ----------
    top = pg.evaluate("()=>window.__AL(__QV().gRef.current,'Criar escola em tempo integral para 500 mil crianças').topic")
    ok('B6: tópico sem "mil de crianças"', not re.search(r'mil de ', top), top)

    # ---------- fronteira de erro: uma tela quebrada não derruba o jogo ----------
    pg.evaluate("()=>{window.__faixaErro='pais'}")
    pg.locator('#sec-tab-pais').click(timeout=5000); pg.wait_for_timeout(700)
    ok('Erro: cartão "Algo deu errado nesta tela" aparece', pg.locator('[data-erro-tela=pais]').count() == 1, corpo(pg)[:80])
    ok('Erro: barra superior e navegação seguem vivas', pg.locator('[data-vitais]').count() == 1 and pg.locator('#sec-tab-mesa').count() == 1)
    ok('Erro: o erro foi registrado no console', any('erro forçado' in t or '[Faixa]' in t for t in logs_console), logs_console[:1])
    pg.evaluate("()=>{window.__faixaErro=null}")
    pg.locator('[data-erro-tela=pais] button').click(timeout=3000); pg.wait_for_timeout(700)
    ok('Erro: "Voltar" leva à Mesa e o jogo continua', G(pg, "g.ui.sec") == 'mesa' and pg.locator('[data-erro-tela]').count() == 0)
    pg.evaluate("()=>{window.__faixaErro='gaveta'}")
    abriu = False
    for sel in ['[data-pend] button']:
        if pg.locator(sel).count():
            pg.locator(sel).first.click(timeout=3000); pg.wait_for_timeout(700); abriu = True; break
    if abriu and pg.locator('.gav-wrap').count():
        ok('Erro: falha dentro da gaveta fica contida no painel', pg.locator('.gav-wrap [data-erro-tela=gaveta]').count() == 1 and pg.locator('[data-vitais]').count() == 1)
    pg.evaluate("()=>{window.__faixaErro=null}"); fecha(pg)

    # ---------- B8: toast acima da gaveta ----------
    z = pg.evaluate("()=>{const t=document.createElement('div');t.className='toast';document.body.appendChild(t);const z=parseInt(getComputedStyle(t).zIndex);t.remove();return z}")
    ok('B8 (lote D): toast fica abaixo das gavetas (z-index < 55) e nunca as cobre; entra por fila só sem gaveta/modal aberto', z < 55, z)

    # ---------- C1/C2: selos discretos ----------
    pg.evaluate("()=>{const s=document.createElement('span');s.className='selo-sim';s.textContent='simulado';s.id='tst-selo';document.body.appendChild(s)}")
    css = pg.evaluate("()=>{const c=getComputedStyle(document.getElementById('tst-selo'));return {fs:c.fontSize,op:c.opacity,bd:c.borderTopWidth,bg:c.backgroundColor,tt:c.textTransform}}")
    ok('C1: selo discreto (12px, opacidade 0,5, sem borda, sem fundo, minúsculo)', css['fs'] == '12px' and abs(float(css['op']) - .5) < .01 and css['bd'] == '0px' and css['bg'] == 'rgba(0, 0, 0, 0)' and css['tt'] == 'lowercase', css)
    pg.evaluate("()=>document.getElementById('tst-selo').remove()")
    vai(pg, 'poder', 'governo')
    ok('C2: nota "traços simulados" na Esplanada', pg.locator('[data-traco-sim]').count() == 1 and pg.locator('[data-traco-sim]').get_attribute('title'))
    ok('C2: ministros sem selo em todo cartão', pg.locator('[data-min-linha] .selo-sim').count() == 0)

    # ---------- B4/B2 em mês > 48 (estado forçado) ----------
    st = pg.evaluate("""()=>{const g=structuredClone(__QV().gRef.current); g.mes=49; __X().escolheEventoNovo(g); const r={ev:g.evento}; for(const m of [50,96,97]){g.mes=m; try{__X().qvValida(g); r['v'+m]='ok'}catch(e){r['v'+m]=e.message}} return r}""")
    ok('B4: crise do mês sorteada depois do mês 48', st['ev'] is not None, st)
    ok('B2: qvValida aceita meses 50, 96 e 97', st['v50'] == st['v96'] == st['v97'] == 'ok', st)

    # ---------- B9: aviso de Congresso na prévia de investimento da Indústria ----------
    SET(pg, "n.ui.sec='pais';n.ui.chip=n.ui.chip||{};n.ui.chip.pais='industria';n.acoes=5;n.pes.energia=90")
    cards = pg.locator('[data-ind-prod]')
    if cards.count():
        cards.first.click(timeout=3000); pg.wait_for_timeout(600)
        previa = pg.locator('[data-ind-previa]').inner_text() if pg.locator('[data-ind-previa]').count() else ''
        aviso = pg.locator('[data-ind-aviso-congresso]')
        ok('B9: prévia diz que precisa do Congresso e mostra a previsão de voto', 'precisa do congresso' in previa.lower() and aviso.count() == 1 and 'Previsão de voto' in aviso.inner_text(), previa[:200])
    else:
        ok('B9: cartões da Indústria presentes', False)
    vai(pg, 'mesa')

    # =====================================================================================================
    # B1 e eleição de 2030, reeleição forçada e o segundo mandato até 2034
    # =====================================================================================================
    avanca(pg, 45 - G(pg, 'g.mes') + 1)
    ok('chegou ao mês 46', G(pg, 'g.mes') == 46, G(pg, 'g.mes'))
    r = pg.evaluate("""()=>{const g=__QV().gRef.current; const ger=g.el.ger; try{ const t=__X().elDiscurso(g, ger, Object.assign({}, ger.res||{}, {venc:undefined, fin:[ger.cands[0].id, ger.cands[1].id]})); return 'ok: '+t.slice(0,80) }catch(e){ return 'ERRO '+e.message } }""")
    ok('B1: elDiscurso sem vencedor (2º turno) não lança', r.startswith('ok'), r)
    vai(pg, 'mesa')
    if pg.locator('[data-pend=elapurg]').count() == 0 and pg.locator('button').filter(has_text=re.compile(r'^Ver as outras')).count():
        pg.locator('button').filter(has_text=re.compile(r'^Ver as outras')).first.click(); pg.wait_for_timeout(250)
    card = pg.locator('[data-pend=elapurg]').first
    ok('B1: pendência "Noite da apuração" existe no mês 46', card.count() == 1)
    if card.count():
        bt = card.locator('button').filter(has_text=re.compile(r'^\s*Abrir'))
        (bt if bt.count() else card).first.click(timeout=3000); pg.wait_for_timeout(900)
        disc = pg.locator('[data-el=discurso]').inner_text() if pg.locator('[data-el=discurso]').count() else ''
        ok('B1: apuração abre sem tela preta e mostra o discurso/2º turno', pg.locator('[data-vitais]').count() == 1 and disc != '', disc[:120])
        pg.screenshot(path=OUT + '/b1_apuracao.png')
        ok('B1: nenhum erro de página até aqui', not [e for e in errs if e.startswith('PAGEERR')], errs[:2])
        fecha(pg)
    avanca(pg, 48 - G(pg, 'g.mes'))
    print('   antes do último mês do 1º mandato:', G(pg, '({fase:g.el.ger&&g.el.ger.fase, venc:g.el.ger&&g.el.ger.res&&g.el.ger.res.venc, sit:g.el.ger&&g.el.ger.sitId, mand:g.el.mandatos})'))
    SET(pg, "const ger=n.el.ger; if(ger&&ger.res){ger.res.venc=ger.sitId;}")
    avanca(pg, 1)
    ok('2030: reeleição vale, segundo mandato começa (mês 49)', G(pg, 'g.mes') == 49 and G(pg, 'g.el.mandatos') == 2 and not G(pg, 'g.over'), G(pg, '({mes:g.mes,mand:g.el.mandatos,over:g.over&&g.over.tipo})'))
    vai(pg, 'mesa'); fecha(pg)
    ok('B4: barra no mês 49 diz "mês 1 do 2º mandato"', (barra(pg) or '').strip() == 'mês 1 do 2º mandato', barra(pg))
    ok('B4: crise do mês existe no mês 49', G(pg, 'g.evento') is not None, G(pg, 'g.evento'))
    pg.screenshot(path=OUT + '/mes49.png')

    evs = 0; nulos = []
    for alvo in [60, 72, 84, 95]:
        while G(pg, 'g.mes') < alvo:
            avanca(pg, 1)
            if G(pg, 'g.over'): break
            if G(pg, 'g.evento'): evs += 1
            else: nulos.append(G(pg, 'g.mes'))
        if G(pg, 'g.over'): break
        vai(pg, 'mesa'); fecha(pg)
        bl = barra(pg); m = G(pg, 'g.mes')
        ok('mês %d: barra "mês %d do 2º mandato"' % (m, m - 48), (bl or '').strip() == 'mês %d do 2º mandato' % (m - 48), bl)
        ok('mês %d: sem NaN/undefined na Mesa' % m, cru(corpo(pg)) is None, cru(corpo(pg)))
        sv = pg.evaluate("""()=>{try{const g=__QV().gRef.current; const o=__X().qvParse(__X().qvSerializa(g)); __X().qvValida(o); return 'ok'}catch(e){return 'ERRO '+e.message}}""")
        ok('mês %d: save serializa, lê e valida' % m, sv == 'ok', sv)
    ok('2º mandato: crises continuam sendo sorteadas', evs >= 30 and len(nulos) <= 3, (evs, nulos[:5]))
    for sec, chip in [('poder', 'eleicoes'), ('poder', 'congresso'), ('pais', 'economia'), ('eu', None)]:
        try:
            vai(pg, sec, chip); fecha(pg)
            ok('mês %d: %s/%s sem valor cru' % (G(pg, 'g.mes'), sec, chip), cru(corpo(pg)) is None, cru(corpo(pg)))
        except Exception as e:
            ok('abrir %s/%s' % (sec, chip), False, str(e)[:80])
    vai(pg, 'poder', 'eleicoes'); pg.screenshot(path=OUT + '/eleicoes_2034.png')
    print('   ger 2034:', G(pg, '(g.el.ger&&{c:g.el.ger.c,fase:g.el.ger.fase,sit:g.el.ger.sitId,cands:g.el.ger.cands.map(c=>c.nome+"/"+c.sigla+(c.sitPres?"*":"")).slice(0,8),venc:g.el.ger.res&&g.el.ger.res.venc})'))
    avanca(pg, 96 - G(pg, 'g.mes'))
    print('   mês', G(pg, 'g.mes'), 'barra', barra(pg), 'over', G(pg, 'g.over&&g.over.tipo'))
    for t in ['elsuc', 'elpesq', 'eldeb', 'elcamp', 'elapurg']:
        vai(pg, 'mesa')
        if pg.locator('[data-pend=%s]' % t).count() == 0 and pg.locator('button').filter(has_text=re.compile(r'^Ver as outras')).count():
            pg.locator('button').filter(has_text=re.compile(r'^Ver as outras')).first.click(); pg.wait_for_timeout(250)
        c = pg.locator('[data-pend=%s]' % t).first
        if c.count():
            bt = c.locator('button').filter(has_text=re.compile(r'^\s*Abrir'))
            try:
                (bt if bt.count() else c).first.click(timeout=3000); pg.wait_for_timeout(700)
                ok('2034: pendência %s abre sem tela preta nem valor cru' % t, pg.locator('[data-vitais]').count() == 1 and cru(corpo(pg)) is None, cru(corpo(pg)))
                fecha(pg)
            except Exception as e: ok('2034: abrir %s' % t, False, str(e)[:80])
    print('   antes do último mês: mes', G(pg, 'g.mes'), 'mand', G(pg, 'g.el.mandatos'), 'venc', G(pg, 'g.el.ger&&g.el.ger.res&&g.el.ger.res.venc'), 'fase', G(pg, 'g.el.ger&&g.el.ger.fase'))
    avanca(pg, 1); pg.wait_for_timeout(800)
    ov = G(pg, 'g.over&&{tipo:g.over.tipo,motivo:g.over.motivo,venc:g.over.venc,posse:g.over.posse&&g.over.posse.nome}')
    print('   fim do 2º mandato: mes', G(pg, 'g.mes'), 'over', ov)
    ok('2034: o personagem encerra por limite de mandatos (sem reeleição e sem crash)', G(pg, 'g.mes') == 97 and ov and ov['tipo'] == 'personagem', ov)
    ok('2034: nenhum erro de página', not [e for e in errs if e.startswith('PAGEERR')], errs[:2])
    pg.wait_for_timeout(500); pg.screenshot(path=OUT + '/fim_2034.png')
    tela = corpo(pg)
    ok('2034: tela de fim sem NaN/undefined', cru(tela) is None, (cru(tela), tela[:300].replace('\n', ' | ')))
    print('   tela de fim:', tela[:700].replace('\n', ' | '))
    print('   botões:', pg.evaluate("()=>[...document.querySelectorAll('button')].map(b=>b.innerText.trim()).filter(Boolean).slice(0,30)"))
    sv = pg.evaluate("""()=>{try{const g=__QV().gRef.current; __X().qvValida(__X().qvParse(__X().qvSerializa(g))); return 'ok'}catch(e){return 'ERRO '+e.message}}""")
    ok('2034: save do estado final (mês 97) é válido', sv == 'ok', sv)
    pg.evaluate("()=>{window.__fim=structuredClone(__QV().gRef.current)}")
    prox = pg.locator('[data-prox] button'); npx = prox.count()
    print('   opções de continuação:', npx, pg.locator('[data-prox-pres]').count())
    if pg.locator('[data-prox-pres]').count():
        pg.locator('[data-prox-pres]').first.click(timeout=3000); pg.wait_for_timeout(1200)
    elif npx:
        prox.first.click(timeout=3000); pg.wait_for_timeout(1200)
    cont = G(pg, '!g.over')
    ok('2034: dá para continuar como outro personagem', cont, G(pg, '({mes:g.mes,pj:g.el.pj&&g.el.pj.nome,pres:g.cfg.nome,mand:g.el.mandatos})'))
    if cont:
        fecha(pg)
        print('   depois de continuar:', G(pg, '({mes:g.mes,pj:g.el.pj&&g.el.pj.nome,pres:g.cfg.nome,mand:g.el.mandatos,evento:g.evento})'), 'barra', barra(pg))
        bl = barra(pg) or ''
        ok('depois de 2034: rótulo do mês sem "97/48" nem "49/48"', not re.search(r'(\d+) / 48', bl) or int(re.search(r'(\d+) / 48', bl).group(1)) <= 48, bl)
        ok('depois de 2034: Mesa sem NaN/undefined', cru(corpo(pg)) is None, cru(corpo(pg)))
        pg.screenshot(path=OUT + '/pos2034_mesa.png')
        avanca(pg, 3)
        ok('depois de 2034: o mês corre (97 -> 100) sem crash', G(pg, 'g.mes') >= 99 and cru(corpo(pg)) is None, (G(pg, 'g.mes'), G(pg, 'g.evento')))
        sv = pg.evaluate("""()=>{try{const g=__QV().gRef.current; __X().qvValida(__X().qvParse(__X().qvSerializa(g))); return 'ok'}catch(e){return 'ERRO '+e.message}}""")
        ok('depois de 2034: save válido', sv == 'ok', sv)
        for sec, chip in [('poder', 'eleicoes'), ('poder', 'congresso'), ('pais', 'economia'), ('mundo', None), ('eu', None), ('x', None), ('medidas', None)]:
            try:
                vai(pg, sec, chip); fecha(pg)
                ok('depois de 2034: %s/%s abre sem valor cru nem tela preta' % (sec, chip), cru(corpo(pg)) is None and pg.locator('[data-vitais]').count() == 1, cru(corpo(pg)))
            except Exception as e:
                ok('depois de 2034: abrir %s/%s' % (sec, chip), False, str(e)[:80])
    # ---- ramo 2: volta ao fim de 2034 e continua como outro personagem (modo leve, sem ser o presidente) ----
    pg.evaluate("()=>{__QV().setG(()=>structuredClone(window.__fim))}"); pg.wait_for_timeout(800)
    outros = pg.locator('[data-prox] button').filter(has_text=re.compile(r'^Continuar como (?!Ratinho)'))
    print('   ramo 2: opções de personagem:', outros.count(), 'tela:', corpo(pg)[:80].replace('\n', ' | '))
    if outros.count():
        nome = outros.first.inner_text().strip()
        outros.first.click(timeout=3000); pg.wait_for_timeout(1200); fecha(pg)
        pj = G(pg, 'g.el.pj&&g.el.pj.nome')
        print('   ramo 2:', nome, '->', G(pg, '({mes:g.mes,pj:g.el.pj&&g.el.pj.nome,pres:g.cfg.nome,over:g.over&&g.over.tipo})'), 'barra', barra(pg))
        ok('2034/ramo 2: continua como %s em modo leve' % nome, G(pg, '!g.over') and pj, pj)
        ok('2034/ramo 2: Mesa sem NaN/undefined e com a barra viva', cru(corpo(pg)) is None and pg.locator('[data-vitais]').count() == 1, cru(corpo(pg)))
        avanca(pg, 6)
        ok('2034/ramo 2: seis meses correm sem crash (97 -> 103)', G(pg, 'g.mes') >= 102 and not G(pg, 'g.over'), (G(pg, 'g.mes'), G(pg, 'g.over&&g.over.tipo')))
        for sec, chip in [('mesa', None), ('poder', 'eleicoes'), ('poder', 'governo'), ('pais', 'economia'), ('eu', None)]:
            try:
                vai(pg, sec, chip); fecha(pg)
                ok('2034/ramo 2: %s/%s abre sem valor cru nem tela preta' % (sec, chip), cru(corpo(pg)) is None and pg.locator('[data-vitais]').count() == 1, cru(corpo(pg)))
            except Exception as e:
                ok('2034/ramo 2: abrir %s/%s' % (sec, chip), False, str(e)[:80])
    ok('0 erros de página e de console no teste todo', not errs, errs[:3])
    b.close()
print('\nRESULTADO: %d/%d verificações OK' % (sum(checks), len(checks)))
sys.exit(0 if all(checks) else 1)
