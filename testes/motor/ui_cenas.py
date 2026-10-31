# Teste das cenas de imprensa em tela cheia (quebra-queixo, coletiva, entrevista/podcast): v4.x
# uso: python3 run_sandbox.py ui_cenas.py <pasta com index.html> <saida_dir> [porta]
# Para prints com o visual real: a pasta pode ser uma cópia com tw.css e fontes (veja SHOTS=1).
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8881
os.makedirs(OUT, exist_ok=True)
SHOTS = bool(os.environ.get('SHOTS'))
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
checks = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:240]) if det != '' else ''), flush=True)
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
def pend(pg, tipo):
    # a Mesa mostra só as 4 mais urgentes; abre as outras quando o cartão não está visível
    if pg.locator('[data-pend=%s]' % tipo).count() == 0:
        bt = pg.locator('button').filter(has_text=re.compile(r'^Ver as outras'))
        if bt.count(): bt.first.click(); pg.wait_for_timeout(300)
    return pg.locator('[data-pend=%s]' % tipo).first
def G(pg, expr): return pg.evaluate("()=>{const g=__QV().gRef.current;return (" + expr + ")}")
def SET(pg, js): pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);" + js + ";return n})"); pg.wait_for_timeout(400)
errs = []
SEED = "(()=>{let a=" + os.environ.get("SEED_N", "20271030") + ";Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
POD = ['flow', 'inteligencia', 'irontalks', 'tresirmaos', 'podpah']
def cobre(pg):
    return pg.evaluate("()=>{const e=document.querySelector('.cn');if(!e)return null;const r=e.getBoundingClientRect();const s=getComputedStyle(e);return {x:r.x,y:r.y,w:r.width,h:r.height,vw:innerWidth,vh:innerHeight,pos:s.position}}")
def cobre_ok(pg):
    c = cobre(pg)
    return bool(c) and c['pos'] == 'fixed' and abs(c['x']) < 1 and abs(c['y']) < 1 and abs(c['w'] - c['vw']) < 2 and abs(c['h'] - c['vh']) < 2, c
def minfonte(pg):
    return pg.evaluate("()=>{let m=99,q=null;document.querySelectorAll('.cn *').forEach(e=>{if(!e.childNodes.length)return;const t=[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());if(!t)return;const r=e.getBoundingClientRect();if(!r.width||!r.height)return;const f=parseFloat(getComputedStyle(e).fontSize);if(f<m){m=f;q=e.textContent.trim().slice(0,30)}});return [m,q]}")
def fecha_cena(pg):
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
def shot(pg, nome):
    pg.wait_for_timeout(1000); pg.screenshot(path=OUT + '/' + nome + '.png')
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    assert 'function analisaLegado(g, texto) {' in src
    INJ = """window.__QV = () => QV; window.__F = () => ({ entGeraMes, entRenovaConvites, qqNovo: (n, i) => ({ mes: n.mes, id: QQ[(i || 0) % QQ.length].id, respondida: false, tom: null, out: null, v: { ipca: '5,2', des: '8,1', ap: '41', dol: '5,40', prim: '-R$ 12 bi', restam: '30', grupo: 'Caminhoneiros', cidade: 'em Goiânia', motivo: 'o preço do diesel', pm: '2 mil', org: '8 mil', gk: 'caminhoneiros', crise: 'a crise', promessa: 'a promessa de campanha' } }) }); function analisaLegado(g, texto) {"""
    src = src.replace('function analisaLegado(g, texto) {', INJ, 1)
    pg.add_init_script(SEED)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)

    # ---------- 1) quebra-queixo ----------
    # o jogo atual gera a coletiva (ent) no lugar do quebra-queixo legado; aqui o qq é injetado para testar a cena (mesmos dados de geraQQ)
    SET(pg, "n.qq=__F().qqNovo(n,0)")
    ok('há um quebra-queixo pendente na Mesa', pend(pg, 'qq').count() == 1)
    pend(pg, 'qq').click(timeout=5000); pg.wait_for_timeout(900)
    ok('quebra-queixo abre a cena em tela cheia (cobre o viewport)', cobre_ok(pg)[0], cobre(pg))
    ok('não é mais a gaveta lateral', pg.locator('.gav').count() == 0)
    ok('cena de coletiva: SVG com vários microfones e bandeirinhas', pg.locator('.cn-bg svg .cn-mic').count() >= 12 and pg.locator('.cn-bg svg text').count() >= 6, pg.locator('.cn-bg svg .cn-mic').count())
    bal = pg.locator('.cn-bal')
    ok('balão de quadrinhos com a pergunta, nome e veículo', bal.count() == 1 and len(bal.inner_text()) > 30, bal.inner_text().replace('\n', ' | ')[:120])
    bs = pg.evaluate("()=>{const e=document.querySelector('.cn-bal');const s=getComputedStyle(e);const a=getComputedStyle(e,'::before'),c=getComputedStyle(e,'::after');return {bg:s.backgroundColor,bw:s.borderTopWidth,bc:s.borderTopColor,tail:a.content+c.content}}")
    ok('balão: fundo branco, contorno preto grosso e cauda', bs['bg'] == 'rgb(255, 255, 255)' and float(bs['bw'].replace('px', '')) >= 4 and bs['bc'] == 'rgb(0, 0, 0)' and '""' in bs['tail'], bs)
    ok('3 opções grandes de resposta + "mais opções" para a quarta', pg.locator('.cn-ops .cn-op').count() == 3 and pg.locator('[data-cena-mais]').count() == 1)
    ok('campo de resposta livre com botão enviar (desabilitado vazio)', pg.locator('[data-qq-livre]').count() == 1 and pg.locator('[data-qq-enviar]').is_disabled())
    f = minfonte(pg); ok('texto mínimo de 12px na cena', f[0] >= 12, f)
    ok('selo "simulado" ausente no quebra-queixo com repórter fictício', pg.locator('.cn .selo-sim').count() == 0)
    if SHOTS: shot(pg, 'cena_quebraqueixo')
    pg.locator('[data-cena-mais]').click(); pg.wait_for_timeout(200)
    ok('"mais opções" revela a quarta postura (desconversar)', pg.locator('[data-op=desc]').count() == 1)
    ap0 = G(pg, "Math.round(Object.values(g.groups).reduce((a,b)=>a+b,0))")
    pg.locator('.cn-ops .cn-op').first.click(timeout=4000); pg.wait_for_timeout(500)
    ok('quebra-queixo respondido: lógica do jogo aplicada (qq.respondida, tom e resultado)', G(pg, "g.qq.respondida===true&&g.qq.tom==='tec'&&!!g.qq.out"), G(pg, "[g.qq.tom,g.qq.out]"))
    ok('a cena fica aberta mostrando a reação e um botão Fechar', pg.locator('.cn').count() == 1 and pg.locator('[data-cena-fechar]').count() == 1 and len(pg.locator('.cn-res').inner_text()) > 20, pg.locator('.cn-res').inner_text().replace('\n', ' ')[:120])
    # Esc fecha
    fecha_cena(pg)
    ok('Esc fecha a cena do quebra-queixo', pg.locator('.cn').count() == 0)
    # texto livre no quebra-queixo (novo mês de teste): usa o leitor de texto livre da coletiva
    SET(pg, "n.qq=__F().qqNovo(n,1)")
    pend(pg, 'qq').click(timeout=5000); pg.wait_for_timeout(700)
    pg.fill('[data-qq-livre]', 'Os números mostram o caminho: vamos manter o rumo e prestar contas de tudo.'); pg.wait_for_timeout(150)
    ok('texto livre habilita o botão enviar', not pg.locator('[data-qq-enviar]').is_disabled())
    pg.locator('[data-qq-enviar]').click(timeout=4000); pg.wait_for_timeout(500)
    ok('quebra-queixo respondido por texto livre', G(pg, "g.qq.respondida===true&&['tec','emo','iro','desc'].includes(g.qq.tom)"), G(pg, "g.qq.tom"))
    fecha_cena(pg)

    # ---------- 2) coletiva ----------
    if not G(pg, "!!(g.ent&&g.ent.colet&&!g.ent.colet.fim)"): SET(pg, "n.ent.colet=null;__F().entGeraMes(n)")
    ok('há uma coletiva pendente', pend(pg, 'entcol').count() == 1, G(pg, "g.ent.colet&&g.ent.colet.qs.length"))
    total = G(pg, "g.ent.colet.qs.length")
    pend(pg, 'entcol').click(timeout=5000); pg.wait_for_timeout(900)
    ok('coletiva abre a cena em tela cheia', cobre_ok(pg)[0], cobre(pg))
    ok('indicador de progresso (1 de N)', pg.locator('.cn-prog li').count() == total and '1 de %d' % total in pg.locator('.cn-prog-n').inner_text(), pg.locator('.cn-prog-n').inner_text())
    ok('coletiva: balão + 3 opções + livre', pg.locator('.cn-bal').count() == 1 and pg.locator('.cn-ops .cn-op').count() == 3 and pg.locator('[data-ent-livre]').count() == 1 and pg.locator('[data-ent-enviar]').count() == 1)
    ok('pergunta traz o gancho de teste data-ent-pergunta e data-op=defesa', pg.locator('[data-ent-pergunta] [data-op=defesa]').count() == 1)
    pg.locator('[data-cena-mais]').click(); pg.wait_for_timeout(150)
    ok('quarta postura (pivotar) continua disponível em "mais opções"', pg.locator('[data-op=pivo]').count() == 1)
    pg.locator('[data-cena-mais]').click(); pg.wait_for_timeout(100)
    if SHOTS: shot(pg, 'cena_coletiva')
    for i in range(total):
        op = ['defesa', 'ajuste', 'ataque'][i % 3]
        pg.locator('[data-ent-pergunta] [data-op=%s]' % op).first.click(timeout=4000); pg.wait_for_timeout(500)
        ok('coletiva %d/%d: reação do repórter mostrada (balão de réplica + resultado)' % (i + 1, total), pg.locator('[data-ent-res]').count() == 1 and pg.locator('.cn-bal[data-reacao="1"]').count() == 1 and G(pg, "g.ent.colet.qs.filter(q=>q.res).length") == i + 1, pg.locator('.cn-bal-q').inner_text()[:80])
        if i < total - 1:
            pg.locator('[data-ent-prox]').first.click(timeout=3000); pg.wait_for_timeout(500)
        else:
            ok('última resposta: botão encerrar a coletiva', pg.locator('[data-ent-concluir]').count() == 1)
            pg.locator('[data-ent-concluir]').first.click(timeout=3000); pg.wait_for_timeout(500)
    ok('coletiva encerrada (lógica: fim=true, feitas+1)', G(pg, "g.ent.colet.fim===true") and pg.locator('[data-cena-fim]').count() == 1, pg.locator('[data-cena-fim]').inner_text()[:100] if pg.locator('[data-cena-fim]').count() else '')
    fecha_cena(pg)
    ok('Esc fecha a cena da coletiva', pg.locator('.cn').count() == 0)

    # ---------- 3) podcast: convite → aceite → pergunta com texto livre ----------
    SET(pg, "n.ent.entrev=null;n.ent.convites=n.ent.convites.filter(c=>c.estado!=='pendente');n.ent.convites.push({id:'cvtA',veic:'flow',mes:n.mes,estado:'pendente'});n.acoes=5;n.pes.energia=90")
    ok('convite de podcast aparece na Mesa', pend(pg, 'entconv').count() >= 1)
    pend(pg, 'entconv').click(timeout=5000); pg.wait_for_timeout(900)
    ok('convite abre a cena do podcast em tela cheia', cobre_ok(pg)[0] and pg.locator('[data-cena-tipo="podcast:flow"]').count() == 1, cobre(pg))
    ok('convite: lista de convites com selo simulado e aceitar/recusar', pg.locator('[data-convite=flow]').count() == 1 and 'simulado' in pg.locator('[data-convite=flow]').inner_text().lower() and pg.locator('[data-conv-aceitar=flow]').count() == 1 and pg.locator('[data-conv-recusar=flow]').count() == 1)
    pg.locator('[data-conv-aceitar=flow]').click(timeout=4000); pg.wait_for_timeout(900)
    ok('aceite inicia a entrevista (lógica: entrev criada, 1 ação)', G(pg, "!!g.ent.entrev&&g.ent.entrev.veic==='flow'") and G(pg, "g.acoes") == 4)
    sc = pg.evaluate("()=>{const s=document.querySelector('.cn-bg svg');return {txt:s.textContent,hosts:s.querySelectorAll('.cn-fala').length,svg:!!s}}")
    ok('cena do podcast: estúdio SVG com letreiro do programa em texto simples', 'Flow' in sc['txt'] and 'PODCAST' in sc['txt'], sc['txt'][:80])
    ok('cena do podcast: apresentador desenhado e rótulo com o nome', sc['hosts'] >= 1 and 'Igor 3K' in sc['txt'])
    ok('legenda "personagem ilustrado" e selo simulado discreto', 'personagem ilustrado' in pg.locator('.cn-top').inner_text() and pg.locator('.cn-top .selo-sim').count() == 1)
    ok('podcast: balão, 3 opções, livre', pg.locator('.cn-bal').count() == 1 and pg.locator('.cn-ops .cn-op').count() == 3 and pg.locator('[data-ent-livre]').count() == 1)
    f = minfonte(pg); ok('podcast: texto mínimo de 12px', f[0] >= 12, f)
    if SHOTS: shot(pg, 'cena_podcast_flow')
    pg.fill('[data-ent-livre]', 'Vamos reduzir a inflação com responsabilidade fiscal e proteger quem ganha menos. Prometo prestar contas.'); pg.wait_for_timeout(150)
    pg.locator('[data-ent-enviar]').click(timeout=4000); pg.wait_for_timeout(600)
    ok('resposta livre no podcast passa pelo motor (via=livre)', G(pg, "g.ent.entrev.qs[0].res&&g.ent.entrev.qs[0].res.via==='livre'") and pg.locator('[data-ent-res]').count() == 1, G(pg, "g.ent.entrev.qs[0].res&&g.ent.entrev.qs[0].res.op"))
    for i in range(6):
        if pg.locator('[data-ent-prox]').count(): pg.locator('[data-ent-prox]').first.click(timeout=3000); pg.wait_for_timeout(400)
        if pg.locator('[data-ent-pergunta] [data-op=defesa]').count(): pg.locator('[data-ent-pergunta] [data-op=defesa]').first.click(timeout=3000); pg.wait_for_timeout(400)
        if pg.locator('[data-ent-concluir]').count(): pg.locator('[data-ent-concluir]').first.click(timeout=3000); pg.wait_for_timeout(500); break
    ok('entrevista de podcast concluída (histórico)', G(pg, "g.ent.hist.filter(h=>h.veic==='flow').length") >= 1 and G(pg, "g.ent.entrev===null"))
    ok('fim da entrevista mostra o resumo', pg.locator('[data-cena-fim]').count() == 1)
    fecha_cena(pg)
    ok('Esc fecha a cena do podcast', pg.locator('.cn').count() == 0)

    # ---------- 4) uma cena diferente por podcast (+ estúdios simples) ----------
    vistos = {}
    for k in POD + ['podcast', 'tv', 'radio', 'jesq', 'jdir', 'sabat', 'intl']:
        SET(pg, "n.ent.entrev=null;n.ent.convites=n.ent.convites.filter(c=>c.estado!=='pendente');n.ent.convites.push({id:'cv_%s',veic:'%s',mes:n.mes,estado:'pendente'});n.acoes=5;n.pes.energia=90" % (k, k))
        pend(pg, 'entconv').click(timeout=5000); pg.wait_for_timeout(600)
        pg.locator('[data-conv-aceitar=%s]' % k).click(timeout=4000); pg.wait_for_timeout(700)
        vistos[k] = pg.evaluate("()=>{const s=document.querySelector('.cn-bg svg');return {len:s.innerHTML.length,sig:s.innerHTML.replace(/[0-9.\\-]+/g,'').length,tipo:document.querySelector('.cn').dataset.cenaTipo,full:s.textContent}}")
        if SHOTS and (k in POD or k in ('tv', 'radio')): shot(pg, 'cena_%s' % ('podcast_' + k if k in POD else 'estudio_' + k))
        fecha_cena(pg)
        SET(pg, "n.ent.entrev=null")
    ok('cada podcast tem uma cena diferente (5 assinaturas distintas)', len({vistos[k]['sig'] for k in POD}) == 5 and len({vistos[k]['tipo'] for k in POD}) == 5, {k: vistos[k]['tipo'] for k in POD})
    LET = {'flow': 'Flow', 'inteligencia': 'INTELIGÊNCIA', 'irontalks': 'TALKS', 'tresirmaos': '3 IRMÃOS', 'podpah': 'PODPAH'}
    ok('letreiro de cada programa em texto simples na cena', all(LET[k] in vistos[k]['full'] for k in POD), {k: LET[k] in vistos[k]['full'] for k in POD})
    ok('veículos não-podcast usam estúdio simples (TV, rádio, jornal)', all(vistos[k]['tipo'].startswith('estudio:') for k in ['tv', 'radio', 'jesq', 'jdir', 'sabat', 'intl']) and vistos['podcast']['tipo'] == 'podcast:generico', {k: vistos[k]['tipo'] for k in vistos})

    # ---------- 4b) histórico de respostas na aba Imprensa ----------
    pg.evaluate("location.hash='#/poder/imprensa'"); pg.wait_for_timeout(1000)
    ok('histórico: seção com resumo no topo', pg.locator('[data-ent-hist]').count() == 1 and pg.locator('[data-hist-resumo]').count() == 1, pg.locator('[data-hist-resumo]').inner_text().replace('\n', ' ')[:200] if pg.locator('[data-hist-resumo]').count() else '')
    nrows = pg.locator('[data-hist-row]').count()
    ok('histórico: uma linha por resposta, agrupadas por mês', nrows >= 5 and pg.locator('[data-hist-mes]').count() >= 1, nrows)
    ok('histórico: filtros Todas / Podcasts / TV e rádio / Coletivas', pg.locator('[data-hist-filtro]').count() == 4)
    pg.locator('[data-hist-filtro=pod]').click(); pg.wait_for_timeout(200)
    npod = pg.locator('[data-hist-row]').count(); ok('histórico: filtro Podcasts só mostra podcasts', npod >= 1 and pg.locator('[data-hist-row]:not([data-hist-row=pod])').count() == 0, npod)
    pg.locator('[data-hist-filtro=col]').click(); pg.wait_for_timeout(200)
    ok('histórico: filtro Coletivas só mostra coletivas', pg.locator('[data-hist-row]').count() >= 1 and pg.locator('[data-hist-row]:not([data-hist-row=col])').count() == 0)
    pg.locator('[data-hist-filtro=todas]').click(); pg.wait_for_timeout(200)
    pg.locator('[data-hist-row] .hs-row').first.click(); pg.wait_for_timeout(200)
    ok('histórico: clicar na linha abre pergunta completa, resposta e reação', pg.locator('[data-hist-det]').count() == 1 and 'Você' in pg.locator('[data-hist-det]').inner_text(), pg.locator('[data-hist-det]').inner_text().replace('\n', ' ')[:160])
    mf = pg.evaluate("()=>{let m=99,q=null;document.querySelectorAll('[data-ent-hist] *').forEach(e=>{const t=[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());if(!t)return;const r=e.getBoundingClientRect();if(!r.width)return;const f=parseFloat(getComputedStyle(e).fontSize);if(f<m){m=f;q=e.textContent.trim().slice(0,30)}});return [m,q]}")
    ok('histórico: texto mínimo de 12px', mf[0] >= 12, mf)
    if SHOTS:
        pg.locator('[data-ent-hist]').scroll_into_view_if_needed(); pg.wait_for_timeout(300); pg.screenshot(path=OUT + '/imprensa_historico.png')
    pg.evaluate("location.hash='#/mesa'"); pg.wait_for_timeout(800)

    # ---------- 5) 1280x720, foco preso e reduced-motion ----------
    pg.set_viewport_size({'width': 1280, 'height': 720})
    SET(pg, "n.qq=__F().qqNovo(n,1)")
    pend(pg, 'qq').click(timeout=5000); pg.wait_for_timeout(900)
    ok('1280x720: cena cobre o viewport', cobre_ok(pg)[0], cobre(pg))
    low = pg.evaluate("()=>{const l=document.querySelector('.cn-low').getBoundingClientRect(),b=document.querySelector('.cn-bal').getBoundingClientRect();return {lowTop:l.top,balBottom:b.bottom+52,h:innerHeight,ops:document.querySelector('.cn-ops').getBoundingClientRect().bottom}}")
    ok('1280x720: balão e respostas cabem sem sobreposição', low['balBottom'] <= low['lowTop'] + 40 and low['ops'] <= low['h'], low)
    f = minfonte(pg); ok('1280x720: texto mínimo de 12px', f[0] >= 12, f)
    if SHOTS: shot(pg, 'cena_quebraqueixo_1280')
    for _ in range(14): pg.keyboard.press('Tab')
    ok('foco preso dentro da cena (Tab não escapa)', pg.evaluate("()=>document.querySelector('.cn').contains(document.activeElement)"))
    fecha_cena(pg)
    pg.emulate_media(reduced_motion='reduce')
    pend(pg, 'qq').click(timeout=5000); pg.wait_for_timeout(500)
    an = pg.evaluate("()=>[getComputedStyle(document.querySelector('.cn')).animationName,getComputedStyle(document.querySelector('.cn-bal')).animationName,getComputedStyle(document.querySelector('.cn-mic')).animationName]")
    ok('prefers-reduced-motion desliga as animações da cena', all(x == 'none' for x in an), an)
    pg.locator('.cn-x').click(timeout=3000); pg.wait_for_timeout(300)
    ok('botão X fecha a cena', pg.locator('.cn').count() == 0)
    fecha_modais(pg)
    print('ERRS', errs[:8])
    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    print('RESUMO: %d ok, %d falhas' % (sum(1 for c in checks if c[0]), sum(1 for c in checks if not c[0])))
    b.close()
