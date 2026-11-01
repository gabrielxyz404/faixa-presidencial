# Teste dos programas prontos das abas do País (e das alavancas de Trabalho e tratados de Comércio exterior): nenhum texto pode ser lido pelo motor como "já em vigor" (norma exata, item jaVigente, redundante),
# vago ou absurdo; os que gastam têm custo positivo; e, depois de aprovar um programa, o cartão dele vira "Em vigor" (com fase e link para Medidas).
# uso: python3 run_sandbox.py ui_programas_novos.py <pasta com index.html> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8895
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
        try: pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^(Fechar|Continuar|OK|Entendi|Seguir|Próximo mês|Voltar à Mesa|Arquivar|Cancelar|Voltar)')).first.click(timeout=1200)
        except Exception: pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
def G(pg, expr): return pg.evaluate("()=>{const g=__QV().gRef.current;return (" + expr + ")}")
def secao(pg, nome): pg.locator('#sec-tab-' + nome.lower().replace('í', 'i')).click(timeout=6000); pg.wait_for_timeout(500)
def chip(pg, nome):
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*' + nome + r'\s*$')).first.click(timeout=6000); pg.wait_for_timeout(600)
AREAS = [('Saúde', 'saude'), ('Educação', 'educacao'), ('Infraestrutura e transportes', 'infraestrutura'), ('Justiça', 'justica'), ('Segurança', 'seguranca')]
LEIA = """(PH)=>PH.map(t=>{try{const p=__AL(__QV().gRef.current,t); const A=p._A||{}; const nv=A.normaVigente||{};
  return {t, topic:p.topic, inst:p.inst, cost:p.cost, rev:p.rev, nvx:!!nv.exato, jv:!!A.jaVigente||(A.items||[]).some(i=>i.jaVigente), red:!!A.redundante, vago:!!(p.qualidade||{}).vago, absurdo:!!p.absurdo}}catch(e){return {t,err:String(e)}}})"""
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__AL = analisaLocal; window.__MC = medidaCria; window.__PROGS = () => ({ SAU_PROG, EDU_PROG, INFRA_GRUPOS, JUS_GOV, TB_LEV, IC_TLC, psVigor });\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg); secao(pg, 'País')

    # 1) todos os textos dos cartões (lidos da tela) e os próximos passos (p2, lidos dos dados) passam pelo motor
    textos = []
    for nome, dp in AREAS:
        chip(pg, nome)
        L = pg.evaluate("(dp)=>[...document.querySelectorAll('[data-pais=%s] button[data-prog] .mx-txt')].map(e=>e.innerText.trim())" % dp, dp)
        ok('%s: cartões de programa na tela' % nome, len(L) >= 6, len(L))
        textos += [(nome, t) for t in L]
    P = pg.evaluate("()=>{const P=__PROGS(); const todos=[].concat(P.SAU_PROG, P.EDU_PROG, ...P.INFRA_GRUPOS.map(G=>G.itens), P.JUS_GOV); return todos.filter(a=>a.p2).map(a=>a.p2.t)}")
    textos += [('próximo passo', t) for t in P]
    ok('há próximos passos (p2) cadastrados', len(P) >= 8, len(P))
    res = pg.evaluate(LEIA, [t for _, t in textos])
    ruins = []
    for (nome, t), r in zip(textos, res):
        if 'err' in r: ruins.append((nome, t[:60], r['err'])); continue
        if r['nvx'] or r['jv'] or r['red'] or r['vago'] or r['absurdo']: ruins.append((nome, t[:60], {k: r[k] for k in ('nvx', 'jv', 'red', 'vago', 'absurdo')}))
        gasta = re.search(r'R\$ [\d.,]+ (bilh|milh)', t) and not re.search(r'(?i)^(cortar|reduzir)', t)
        if gasta and not (r['cost'] or 0) > 0 and not (r.get('rev') or 0) < 0 and 'penduricalhos' not in t.lower() and 'verbas indenizat' not in t.lower(): ruins.append((nome, t[:60], 'sem custo positivo: %s' % r['cost']))
    ok('nenhum dos %d textos é lido como já em vigor, redundante, vago ou absurdo (e os que gastam têm custo > 0)' % len(textos), not ruins, ruins[:4])

    # 2) cartão "Em vigor": aprova um programa pela interface e confere o cartão
    chip(pg, 'Educação')
    alvo = pg.locator('[data-pais=educacao] button[data-prog]').filter(has_text='Pé-de-Meia').first
    ok('Educação: cartão "Pé-de-Meia no fundamental II" é um botão de proposta', alvo.count() == 1 and 'fundamental' in alvo.inner_text().lower())
    txt_prog = alvo.locator('.mx-txt').inner_text()
    # aprovação: o parecer abre pelo clique (a Câmara de teste não tem votos), então a medida nasce pelo mesmo caminho da aprovação (medidaCria sobre a proposta do motor)
    alvo.click(timeout=6000); pg.wait_for_timeout(1800)
    ok('o clique no programa abre o parecer da Casa Civil', pg.locator('.modal-wrap').count() >= 1)
    fecha_modais(pg)
    pg.evaluate("(t)=>__QV().setG(p=>{const n=structuredClone(p); const prop=__AL(n,t); __MC(n,prop,1,'Lei'); return n})", txt_prog); pg.wait_for_timeout(700)
    nmed = G(pg, "(g.medidas||[]).length")
    ok('o programa aprovado virou medida no save', nmed >= 1, G(pg, "(g.medidas||[]).map(m=>m.estado+': '+m.topic)"))
    secao(pg, 'País'); chip(pg, 'Educação'); pg.wait_for_timeout(500)
    card = pg.locator('[data-pais=educacao] [data-prog-vigor]')
    ok('Educação: o cartão do programa aprovado mostra "Em vigor" (não é mais botão de propor)', card.count() == 1 and 'Em vigor' in card.first.inner_text(), card.first.inner_text()[:140] if card.count() else 'sem cartão')
    ok('cartão "Em vigor": pílula da fase e link para Medidas', card.count() == 1 and card.first.locator('[data-prog-fase]').count() == 1 and card.first.locator('a[href="#medidas"]').count() == 1)
    ok('Educação: os outros 9 programas continuam como botões de propor', pg.locator('[data-pais=educacao] button[data-prog]').count() == 9, pg.locator('[data-pais=educacao] button[data-prog]').count())
    ok('cartão "Em vigor" oferece o próximo passo (Ampliar mais)', card.count() == 1 and card.first.locator('[data-prog-prox]').count() == 1)
    pg.screenshot(path=OUT + '/educacao_em_vigor.png', full_page=True)
    if card.count() == 1:
        card.first.locator('a[href="#medidas"]').click(timeout=4000); pg.wait_for_timeout(900)
        ok('o link leva à seção Medidas', pg.locator('[data-secao-medidas]').count() >= 1 or '#medidas' in pg.url, pg.url[-30:])
    # 3) outras áreas não são afetadas por essa medida
    secao(pg, 'País'); chip(pg, 'Saúde')
    ok('Saúde: 6 botões de proposta intactos', pg.locator('[data-pais=saude] button[data-prog]').count() == 6 and pg.locator('[data-pais=saude] [data-prog-vigor]').count() == 0)


    # 4) alavancas de Trabalho e tratados de Comércio exterior: também não podem ser lidos como norma já em vigor nem absurdos
    TB = pg.evaluate("""()=>{const P=__PROGS(); const g=__QV().gRef.current; const R=[]; for(const L of P.TB_LEV){let vs=[]; try{vs=L.vals(g)||[]}catch(e){} for(const x of vs){try{R.push({t:L.texto(g,x.v)})}catch(e){}}} for(const x of P.IC_TLC) R.push({t:x.t}); return R}""")
    resTb = pg.evaluate(LEIA, [r['t'] for r in TB])
    ruinsTb = [(r['t'][:60], {k: r[k] for k in ('nvx', 'jv', 'red', 'vago', 'absurdo')}) for r in resTb if 'err' in r or r['nvx'] or r['jv'] or r['red'] or r['vago'] or r['absurdo']]
    ok('as %d alavancas de Trabalho e tratados de Comércio exterior não são lidos como em vigor, redundantes, vagos ou absurdos' % len(resTb), len(resTb) >= 25 and not ruinsTb, ruinsTb[:4])

    # 5) nenhum cartão propõe algo idêntico a medida já ativa: aprova um programa em cada área e confere, em toda a aba, que só ele virou "Em vigor"
    IDENT = """()=>{const P=__PROGS(); const g=__QV().gRef.current;
      const todos=[].concat(P.SAU_PROG.map(a=>['saude',a]), P.EDU_PROG.map(a=>['educacao',a]), ...P.INFRA_GRUPOS.map(G=>G.itens.map(a=>['infraestrutura',a])), P.JUS_GOV.map(a=>['justica',a]));
      const vivas=(g.medidas||[]).filter(m=>['ativa','suspensa','aguardando','consolidada'].includes(m.estado));
      const out=[]; for(const [aba,a] of todos){ const p=__AL(g,a.t); const ids=(p.objs||[]).filter(o=>o.sg&&!/^gen_/.test(o.id)).map(o=>o.id); const pol=p.entendimento?p.entendimento.polaridade:0;
        const m=vivas.find(m=>m.topic===p.topic||(pol&&ids.length&&m.pol===pol&&(m.objIds||[]).length&&ids.every(i=>m.objIds.includes(i))));
        out.push({aba,l:a.l,ident:m?m.id:null,vigor:!!P.psVigor(g,a)})} return out}"""
    aprovar = [('educacao', 'Mais vagas de ensino técnico'), ('saude', 'Mais 5 mil leitos de UTI'), ('infraestrutura', 'Novo PAC 2027-2030'), ('justica', 'Mais 1.500 auditores na CGU')]
    for dp, rot in aprovar:
        nome = [n for n, d in AREAS if d == dp][0]
        secao(pg, 'País'); chip(pg, nome)
        t = pg.evaluate("(r)=>{const P=__PROGS(); const todos=[].concat(P.SAU_PROG, P.EDU_PROG, ...P.INFRA_GRUPOS.map(G=>G.itens), P.JUS_GOV); const a=todos.find(x=>x.l===r); return a?a.t:null}", rot)
        ok('%s: programa "%s" existe' % (nome, rot), t is not None)
        if t: pg.evaluate("(t)=>__QV().setG(p=>{const n=structuredClone(p); const prop=__AL(n,t); __MC(n,prop,1,'Lei'); return n})", t); pg.wait_for_timeout(500)
    iden = pg.evaluate(IDENT)
    vig = [r for r in iden if r['vigor']]
    ok('os 4 programas aprovados (e só eles) são lidos como em vigor (Educação já tinha o Pé-de-Meia)', len(vig) >= 4 and all(r['ident'] for r in vig), [(r['aba'], r['l']) for r in vig])
    falso = [(r['aba'], r['l']) for r in iden if r['ident'] and not r['vigor']]
    ok('nenhum programa idêntico a medida ativa continua como botão de propor', not falso, falso[:4])
    sobra = [(r['aba'], r['l']) for r in iden if r['vigor'] and not r['ident']]
    ok('nenhum cartão "Em vigor" sem medida correspondente (sem falso positivo)', not sobra, sobra[:4])
    for nome, dp in AREAS[:4]:
        if dp == 'seguranca': continue
        secao(pg, 'País'); chip(pg, nome)
        nv = pg.locator('[data-pais=%s] [data-prog-vigor]' % dp).count(); nb = pg.locator('[data-pais=%s] button[data-prog]' % dp).count()
        esperado = sum(1 for r in vig if r['aba'] == dp)
        ok('%s: %d cartões "Em vigor" na tela, batendo com a leitura (%d), e os demais continuam botões (%d)' % (nome, nv, esperado, nb), nv == esperado and nb > 0, (nv, esperado, nb))

    # 6) a noção de "em vigor" é a do motor: suspensa e consolidada contam; revogada devolve o botão
    chip(pg, 'Educação')
    mid = G(pg, "(g.medidas||[]).find(m=>/ensino medio|cursos tecnicos|tecnic/i.test(m.topic||''))?.id || (g.medidas||[])[0].id")
    for est, espera in (('consolidada', True), ('suspensa', True), ('revogada', False), ('ativa', True)):
        pg.evaluate("([id,e])=>__QV().setG(p=>{const n=structuredClone(p); n.medidas.find(m=>m.id===id).estado=e; return n})", [mid, est]); pg.wait_for_timeout(500)
        secao(pg, 'País'); chip(pg, 'Educação')
        n = pg.locator('[data-pais=educacao] [data-prog-vigor=%s]' % mid).count()
        ok('medida %s: cartão %s' % (est, '"Em vigor"' if espera else 'volta a ser botão de propor'), (n == 1) == espera, n)

    print('ERRS', errs[:8])
    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    print('RESUMO: %d ok, %d falhas' % (sum(1 for c in checks if c[0]), sum(1 for c in checks if not c[0])))
    b.close()
