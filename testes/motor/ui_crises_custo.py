# I5: cartões de crise com custo e risco explícitos. Cada opção mostra, ANTES da escolha, instrumento, custo fiscal, grupos que ganham e perdem,
# efeito nos indicadores e um rótulo de risco; os números vêm da mesma função que aplica a medida, então o Δ real tem de bater com a prévia.
# uso: python3 run_sandbox.py ui_crises_custo.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8871
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
SEED = "(()=>{let a=4242;Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
INJ = "window.__QV = () => QV; window.__PV = { previaTexto, previaIgnorar, pvMede, pvInerte, EVENTOS, EV }; function analisaLegado(g, texto) {"
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
def SET(pg, js): pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);" + js + ";return n})"); pg.wait_for_timeout(450)
def overlay(pg): return pg.evaluate("()=>[...document.querySelectorAll('.cn,.modal-wrap,.gav-wrap')].some(e=>e.getClientRects().length)")
def fecha(pg):
    for _ in range(8):
        if not overlay(pg): return
        pg.evaluate("""()=>{const L=[...document.querySelectorAll('.cn,.modal-wrap,.gav-wrap')].filter(e=>e.getClientRects().length);const r=L[L.length-1];
          const b=[...r.querySelectorAll('button:not([disabled])')].find(b=>/^(Fechar|Voltar ao gabinete|Arquivar|Voltar(?! ao menu)|Continuar|Entendi|OK|Cancelar)/.test(b.innerText.trim()));
          if(b) b.click(); }""")
        pg.wait_for_timeout(350)
        if overlay(pg): pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
def cru(txt):
    m = re.search(r'(^|[^\w])(NaN|undefined|Infinity)([^\w]|$)|\[object Object\]', txt)
    return m.group(0) if m else None
def aprova(pg):
    """assina ou vota e conclui; devolve o texto do resultado (ou '')"""
    btns = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
    for alvo in ['Assinar e publicar no DOU', 'Assinar mesmo assim', 'Votar agora']:
        if alvo in btns:
            pg.locator('.modal-wrap button').filter(has_text=alvo).first.click(timeout=4000); pg.wait_for_timeout(1500); break
    for _ in range(6):
        b = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
        pick = next((x for x in b if re.match(r'^(Ver resultado|Concluir|Apurar|Aplicar|Continuar|Encerrar votação|Pular)', x)), None)
        if not pick: break
        try: pg.locator('.modal-wrap button').filter(has_text=pick).first.click(timeout=3000)
        except Exception: pass
        pg.wait_for_timeout(900)
    return pg.evaluate("()=>{const e=document.querySelector('.modal-wrap');return e?e.innerText:''}")
NUM = r'([+−\-]?\d+(?:[.,]\d+)?)'
def num(s): return float(s.replace('−', '-').replace(',', '.'))
ROT = {'ap': 'Aprovação', 'ipca': 'Inflação', 'pib': 'PIB', 'imp': 'Risco de impeachment', 'cong': 'Relação com o Congresso', 'esc': 'Escândalo'}
MIN = {'ap': .05, 'ipca': .02, 'pib': .02, 'imp': .2, 'cong': .2, 'esc': .2}
TOL = {'ap': .25, 'ipca': .03, 'pib': .03, 'imp': .35, 'cong': .35, 'esc': .35}

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' and 'erro forçado' not in m.text and '[Faixa]' not in m.text else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', INJ, 1)
    pg.add_init_script(SEED)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha(pg)
    pg.evaluate("()=>{window.__g0 = structuredClone(__QV().gRef.current)}")
    CRISES = (os.environ.get('CRISES') or '').split(',') if os.environ.get('CRISES') else ['dolar', 'fuga_capitais', 'pf', 'caminhoneiros', 'enchentes', 'queimadas', 'tr_china_soja', 'greve_receita', 'faccao', 'stf_drogas', 'gasolina']
    cmp_n = 0; cmp_inst = set(); cmp_ids = []; prim = True
    def prepara(cid, fav=False):
        fecha(pg)
        extra = "n.eventoUF='CE';" if cid == 'faccao' else ""
        if fav: extra += "for(const k in n.parties){n.parties[k].rel=88;n.parties[k].relS=88;}"  # base amiga: mais projetos de lei passam e podem ser comparados
        pg.evaluate("(cid)=>{__QV().setG(p=>{const n=structuredClone(__g0);n.evento=cid;n.eventoOk=false;n.eventoIgn=false;n.acoes=5;n.props=5;n.pes.energia=100;" + extra + "return n})}", cid)
        pg.wait_for_timeout(500)
    def abre_crise():
        pg.locator('[data-pend=crise]').first.click(timeout=6000); pg.wait_for_timeout(700)
    for cid in CRISES:
        prepara(cid)
        abre_crise()
        n_op = pg.locator('[data-crise-op]').count()
        ev_n = G(pg, "EV_N") if False else pg.evaluate("(cid)=>__PV.EV(__QV().gRef.current).opcoes.length", cid)
        ok(f'{cid}: {ev_n} opções + "Não agir" com cartão de prévia', n_op == ev_n + 1, n_op)
        txt = pg.evaluate("()=>{const e=document.querySelector('[data-crise-opcoes]');return e?e.innerText:''}")
        ok(f'{cid}: nada de NaN/undefined nos cartões', not cru(txt), cru(txt))
        riscos = pg.evaluate("()=>[...document.querySelectorAll('[data-crise-op]')].map(e=>e.dataset.risco)")
        ok(f'{cid}: todo cartão tem rótulo de risco (baixo/médio/alto)', all(r in ('baixo', 'médio', 'alto') for r in riscos), riscos)
        ok(f'{cid}: cada opção mostra instrumento e custo fiscal', pg.evaluate("()=>[...document.querySelectorAll('[data-crise-op]:not([data-crise-op=ignorar])')].every(e=>e.querySelector('[data-pv-inst]')&&e.querySelector('[data-pv=custo]'))"))
        ok(f'{cid}: o cartão "Não agir" explica o preço de deixar correr', pg.evaluate("()=>!!document.querySelector('[data-crise-op=ignorar]')") and 'não agir' in txt.lower())
        if cid in ('dolar', 'pf', 'enchentes'): pg.screenshot(path=f'{OUT}/crise_{cid}.png')
        fecha(pg)
        # prévia x resultado real, opção a opção
        for i in range(ev_n):
            prepara(cid, True)
            abre_crise()
            prev = pg.evaluate("""(i)=>{const e=document.querySelector('[data-crise-op="'+i+'"]');const o={};
              for(const c of e.querySelectorAll('[data-pv-ind]')) o[c.dataset.pvInd]=c.innerText;
              const inst=e.querySelector('[data-pv-inst]').innerText; const risco=e.dataset.risco; return {o,inst,risco,txt:e.innerText}}""", i)
            ant = pg.evaluate("()=>{const m=__PV.pvMede(__QV().gRef.current);return m}")
            pg.locator(f'[data-crise-op="{i}"] button').first.click(timeout=5000); pg.wait_for_timeout(1800)
            res = aprova(pg)
            dep = pg.evaluate("()=>{const m=__PV.pvMede(__QV().gRef.current);return m}")
            # só compara quando a medida de fato foi aprovada; o Congresso pode derrotar um PL, e a prévia é "se aprovada"
            if not G(pg, "g.log[0] && g.log[0].res === 'aprovada' && g.log.length > __g0.log.length"):
                print('   [dbg] ' + res[:160].replace('\n', ' / ') + ' | log0=' + str(G(pg, 'g.log[0]&&g.log[0].res'))); print('   (sem comparação: ' + cid + ' opção ' + str(i) + ' não foi aprovada; instrumento: ' + prev['inst'] + ')'); fecha(pg); continue
            ruim = []
            for k in ROT:
                real = dep[k] - ant[k]
                if k in prev['o']:
                    m = re.search(NUM + r'\s*(?:p\.p\.)?$', prev['o'][k].strip())
                    pv = num(m.group(1)) if m else None
                    if pv is None or abs(pv - real) > TOL[k]: ruim.append((k, pv, round(real, 3)))
                elif abs(real) >= MIN[k] + TOL[k]: ruim.append((k, 'ausente', round(real, 3)))
            cmp_n += 1; cmp_inst.add(prev['inst'].split(' ·')[0]); cmp_ids.append(f'{cid}#{i}')
            ok(f'{cid} opção {i}: Δ real bate com a prévia ({prev["inst"]})', not ruim, ruim)
            fecha(pg)
    ok('comparou pelo menos 8 opções aprovadas', cmp_n >= 8, cmp_n)
    ok('a comparação cobre mais de um instrumento', len(cmp_inst) >= 2, sorted(cmp_inst))
    print('comparadas:', ', '.join(cmp_ids))

    # a prévia não aplica nada: o jogo real fica idêntico depois de renderizar os cartões
    prepara('dolar')
    antes = pg.evaluate("()=>JSON.stringify(__QV().gRef.current)")
    abre_crise(); pg.wait_for_timeout(600)
    depois = pg.evaluate("()=>JSON.stringify(__QV().gRef.current)")
    ok('abrir o cartão não muda o estado do jogo (a prévia roda em clone)', antes == depois)
    fecha(pg)

    # todas as crises e eventos com escolha têm prévia válida (inclui Fuga de capitais e os eventos de terras raras)
    r = pg.evaluate("""()=>{const g=__QV().gRef.current; const falhas=[]; let n=0;
      for(const e of __PV.EVENTOS){ const ev = e.dyn ? null : e; if(!ev) continue; for(const o of ev.opcoes){ n++; const P=__PV.previaTexto(g,o.t,ev.grav); if(!P.ok || !isFinite(P.d.ap) || !['baixo','médio','alto'].includes(P.risco)) falhas.push(ev.id+':'+o.l);} const I=__PV.previaIgnorar(g,ev); if(!I.ok) falhas.push(ev.id+':ignorar'); }
      return {n,falhas}}""")
    ok('todas as opções de EVENTOS (%d) têm prévia válida' % r['n'], not r['falhas'] and r['n'] >= 60, r['falhas'][:6])
    ok('Fuga de capitais está coberta', pg.evaluate("()=>__PV.EVENTOS.some(e=>e.id==='fuga_capitais')"))

    # opção que não faz nada diz isso em claro
    prepara('stf_drogas'); abre_crise()
    t = pg.evaluate("()=>[...document.querySelectorAll('[data-pv-inerte]')].map(e=>e.innerText)")
    ok('"Silêncio" (STF) avisa que não age de fato', any('Não age de fato' in x for x in t), t)
    pg.screenshot(path=OUT + '/crise_stf_drogas.png'); fecha(pg)
    # Mesa: a crise continua listada em "Precisa de você"
    prepara('fuga_capitais'); pg.screenshot(path=OUT + '/mesa_fuga.png')
    abre_crise(); pg.screenshot(path=OUT + '/crise_fuga_capitais.png'); fecha(pg)

    ok('0 erros de página/console', not errs, errs[:3])
    b.close()
print('\nTOTAL: %d/%d' % (sum(checks), len(checks)), '| ERROS:', len(errs))
sys.exit(0 if all(checks) and not errs else 1)
