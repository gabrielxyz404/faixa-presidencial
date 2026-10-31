# Teste de interface de Poder v2 (Congresso, STF, Oposição, Eleições, Figuras): o mesmo desenho da aba Governo.
# Para cada sub-aba: abre, confere a faixa-resumo (5 indicadores) e os cartões; no Congresso coloca uma medida na pauta,
# confere o cartão com as barras de voto e executa Articular e Liberar emendas; em todas confere: sem rolagem horizontal
# em 1440 e 1280, texto mínimo de 12px (fora de detalhes recolhidos) e 0 erros de página/console.
# uso: python3 run_sandbox.py ui_poder.py <pasta com index.html> <saida_dir> [porta]
import sys, threading, functools, http.server, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8896
os.makedirs(OUT, exist_ok=True)
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
        try: pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^(Fechar|Continuar|OK|Entendi|Seguir|Próximo mês|Voltar à Mesa|Arquivar|Cancelar|Voltar)')).first.click(timeout=1200)
        except Exception: pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
def G(pg, expr): return pg.evaluate("()=>{const g=__QV().gRef.current;return (" + expr + ")}")
def encerra(pg):
    fecha_modais(pg)
    pg.locator('button').filter(has_text=re.compile(r'^\s*Encerrar m')).first.click(timeout=8000); pg.wait_for_timeout(900)
    fecha_modais(pg)
def vai_poder(pg, chip):
    pg.locator('#sec-tab-poder').click(timeout=6000); pg.wait_for_timeout(500)
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*' + chip)).first.click(timeout=6000); pg.wait_for_timeout(700)
def sub_el(pg, nome):
    pg.locator('#elp-chip-' + nome).click(timeout=6000); pg.wait_for_timeout(600)
HSCROLL = "()=>document.documentElement.scrollWidth<=innerWidth"
# menor fonte visível na aba (ignora SVG e o interior de <details> fechado)
MINFONT = """()=>{let m=99,quem='';document.querySelectorAll('#poder-pan *').forEach(e=>{if(e.children.length||!e.textContent.trim()||e.closest('svg'))return;
 const d=e.closest('details');if(d&&!d.open&&!e.closest('summary'))return;const cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden')return;
 const f=parseFloat(cs.fontSize);if(f<m){m=f;quem=e.tagName+'.'+e.className+':'+e.textContent.trim().slice(0,30)}});return [m,quem]}"""
SEED = "(()=>{let a=" + os.environ.get("SEED_N", "20271030") + ";Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV;\nfunction analisaLegado(g, texto) {', 1)
    pg.add_init_script(SEED)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    # uma medida de lei vai à pauta do Congresso, para haver cartão de pauta
    pg.locator('#caixa').scroll_into_view_if_needed(); pg.fill('#caixa', 'criar programa de creches com 5 bilhões'); click(pg, 'Assinar e enviar', 2500)
    try: pg.locator('.modal-wrap button').filter(has_text='Enviar e tramitar').first.click(timeout=4000); pg.wait_for_timeout(1200)
    except Exception as e: print('sem botão Enviar e tramitar', str(e)[:100])
    fecha_modais(pg); encerra(pg)

    def aba(nome, chip, kpis, cartoes, rot):
        vai_poder(pg, chip)
        ok(nome + ': faixa-resumo com 5 indicadores', pg.locator('[data-pd=resumo] [data-gv-kpi]').count() == 5, pg.evaluate("()=>[...document.querySelectorAll('[data-pd=resumo] [data-gv-kpi]')].map(e=>e.getAttribute('data-gv-kpi'))"))
        for k in kpis:
            ok(nome + ': indicador ' + k, pg.locator('[data-pd=resumo] [data-gv-kpi=%s]' % k).count() == 1)
        sel, mn = cartoes
        ok(nome + ': ' + rot, pg.locator(sel).count() >= mn, (pg.locator(sel).count(), mn))
        ok(nome + ': seções com "?" de dica', pg.locator('[data-pd-sec] [data-gv-tip], [data-pd=resumo]').count() >= 1)
        ok(nome + ': sem rolagem horizontal em 1440', pg.evaluate(HSCROLL))
        mf = pg.evaluate(MINFONT); ok(nome + ': texto mínimo de 12px', mf[0] >= 12, mf)

    # ---------- Congresso ----------
    aba('Congresso', 'Congresso', ['camara', 'senado', 'pauta', 'ultvoto', 'relacao'], ('[data-partido]', 10), 'um cartão por bancada (>=10)')
    k = pg.evaluate("()=>Object.fromEntries([...document.querySelectorAll('[data-gv-kpi]')].map(e=>[e.getAttribute('data-gv-kpi'),e.innerText.replace(/\\n/g,' | ')]))")
    ok('Congresso: base da Câmara mostra x/513 e do Senado y/81', '/513' in k['camara'] and '/81' in k['senado'], (k['camara'], k['senado']))
    ok('Congresso: itens na pauta batem com o jogo', ('| %d |' % G(pg, 'g.pauta.length')) in k['pauta'], k['pauta'])
    ok('Congresso: hemiciclo, alternância Câmara/Senado e pauta preservados', pg.locator('svg[role=img]').count() >= 1 and pg.locator('button[aria-pressed]').filter(has_text='Senado').count() == 1 and pg.locator('[data-pauta]').count() == 1)
    it = pg.locator('[data-pauta-item]')
    ok('Congresso: item da pauta em cartão com barras de voto Câmara e Senado', it.count() >= 1 and it.first.locator('[role=meter]').count() == 2, it.count())
    ok('Congresso: ações Levar a voto (principal) e Articular', it.first.locator('button').filter(has_text='Levar a voto').count() == 1 and it.first.locator('button').filter(has_text='Articular').count() == 1)
    ok('Congresso: detalhes recolhidos por padrão', pg.locator('[data-pauta-item] details[open]').count() == 0)
    # ação 1: liberar emendas a uma bancada (custa caixa, sobe a relação)
    ex0 = G(pg, 'g.fiscal.extra')
    pg.locator('[data-partido] button').filter(has_text='Emendas').first.click(timeout=5000); pg.wait_for_timeout(500)
    ok('Congresso: Emendas aumenta o custo extra do ano', G(pg, 'g.fiscal.extra') > ex0, (ex0, G(pg, 'g.fiscal.extra')))
    # ação 2: Articular na pauta (gaveta com 1 conversa) e continuar tramitando
    ac0 = G(pg, 'g.acoes')
    it.first.locator('button').filter(has_text='Articular').click(timeout=5000); pg.wait_for_timeout(600)
    ok('Congresso: Articular abre a gaveta de articulação', pg.locator('.gav').count() >= 1)
    pg.locator('.gav select').first.select_option(index=1); pg.wait_for_timeout(300)
    pg.locator('.gav button').filter(has_text='Continuar tramitando').click(timeout=5000); pg.wait_for_timeout(700)
    ok('Congresso: Articular gasta 1 ação política', G(pg, 'g.acoes') == ac0 - 1, (ac0, G(pg, 'g.acoes')))
    # alternar para o Senado troca os cartões de bancada
    pg.locator('button[aria-pressed]').filter(has_text='Senado').click(); pg.wait_for_timeout(500)
    ok('Congresso: Senado mostra ações próprias (Pauta/Agência)', pg.locator('[data-partido] button').filter(has_text='Agência').count() >= 1)
    pg.locator('button[aria-pressed]').filter(has_text='Câmara').click(); pg.wait_for_timeout(300)
    ok('Congresso: lista de parlamentares e filtros preservados', pg.locator('#parl-busca').count() == 1 and pg.locator('#parl-bloco').count() == 1 and pg.locator('[data-parl-contagem]').count() == 1)
    pg.screenshot(path=OUT + '/poder_congresso_1440.png', full_page=True)
    pg.set_viewport_size({'width': 1280, 'height': 800}); pg.wait_for_timeout(500)
    ok('Congresso: sem rolagem horizontal em 1280', pg.evaluate(HSCROLL), pg.evaluate("()=>document.documentElement.scrollWidth"))
    pg.set_viewport_size({'width': 1440, 'height': 900})

    # ---------- STF ----------
    aba('STF', 'STF', ['tensao', 'vagas', 'ministros', 'derrubadas', 'aposentadoria'], ('[data-stf-min]', 9), 'um cartão por ministro em exercício')
    nv = G(pg, '(g.stfCadeiras||[]).filter(c=>c.vaga).length')
    ok('STF: cartão de vaga com Indicar ministro(a)', pg.locator('[data-stf-vaga]').count() == nv and (nv == 0 or pg.locator('[data-stf-vaga] button').filter(has_text='Indicar ministro').count() == nv), nv)
    ok('STF: fluxo da indicação em 3 cartões', pg.locator('[data-stf-fluxo] .pd-step').count() == 3)
    ok('STF: perfil e dossiê recolhidos', pg.locator('[data-stf-min] details[open]').count() == 0)
    if nv:
        pg.locator('[data-stf-vaga] button').filter(has_text='Indicar ministro').first.click(timeout=5000); pg.wait_for_timeout(700)
        ok('STF: Indicar abre a gaveta de indicação', pg.locator('.gav').count() >= 1)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(400); fecha_modais(pg)
    ok('STF: sem rolagem em 1280', (pg.set_viewport_size({'width': 1280, 'height': 800}), pg.wait_for_timeout(400), pg.evaluate(HSCROLL))[2]); pg.set_viewport_size({'width': 1440, 'height': 900})

    # ---------- Oposição ----------
    aba('Oposição', 'Oposi', ['lider', 'forca', 'impeachment', 'cpi', 'intencao'], ('[data-ameaca]', 2), 'ameaças em cartões (impeachment e metas)')
    ok('Oposição: líder e equilíbrio dos Poderes preservados', pg.locator('[data-oposicao]').count() == 1 and pg.locator('[data-poderes]').count() == 1 and pg.locator('[data-poder-aresta]').count() == 3)
    pg.locator('[data-ameaca=impeachment] button').filter(has_text='Congresso').click(timeout=5000); pg.wait_for_timeout(700)
    ok('Oposição: ação leva ao Congresso', pg.locator('[data-pd=congresso]').count() == 1)

    # ---------- Eleições ----------
    aba('Eleições', 'Elei', ['marco', 'personagem', 'mandato', 'aprovacao', 'pesquisa'], ('[data-pd-sec]', 3), 'visão geral em blocos (calendário, personagem, Congresso)')
    for sub, sel, mn, rot in [('mun', '[data-el=mun-vazio], [data-cidade]', 1, 'municipais (vazio ou cidades)'), ('pres', '[data-el=pres-vazio], [data-candidato]', 1, 'presidência (vazio ou candidatos)'),
                              ('aliados', '[data-pessoa]', 10, 'aliados em cartões (>=10)'), ('din', '[data-el=dinastia] li', 1, 'linha do tempo em cartões')]:
        sub_el(pg, sub); ok('Eleições/' + sub + ': ' + rot, pg.locator(sel).count() >= mn, pg.locator(sel).count())
        ok('Eleições/' + sub + ': faixa-resumo mantida', pg.locator('[data-pd=resumo] [data-gv-kpi]').count() == 5)
        mf = pg.evaluate(MINFONT); ok('Eleições/' + sub + ': texto mínimo de 12px', mf[0] >= 12, mf)
        ok('Eleições/' + sub + ': sem rolagem horizontal em 1440', pg.evaluate(HSCROLL))
    sub_el(pg, 'aliados')
    ac0 = G(pg, 'g.acoes'); pg.locator('[data-pessoa] [data-aliado=palco]').first.click(timeout=5000); pg.wait_for_timeout(500)
    ok('Eleições/aliados: Palco gasta 1 ação', G(pg, 'g.acoes') == ac0 - 1, (ac0, G(pg, 'g.acoes')))
    sub_el(pg, 'visao')

    # ---------- Figuras ----------
    aba('Figuras', 'Figuras', ['total', 'sem-mandato', 'estaduais', 'prefeitos', 'elegiveis'], ('[data-figura]', 10), 'figuras em grade de cartões (>=10)')
    n0 = pg.locator('[data-figura]').count(); pg.locator('input[aria-label="Buscar figura"]').fill('Haddad'); pg.wait_for_timeout(400)
    ok('Figuras: busca filtra os cartões', 1 <= pg.locator('[data-figura]').count() < n0, (n0, pg.locator('[data-figura]').count()))

    # ---------- layout em 1280 em todas ----------
    for chip, nm in [('Congresso', 'congresso'), ('STF', 'stf'), ('Oposi', 'oposicao'), ('Elei', 'eleicoes'), ('Figuras', 'figuras')]:
        vai_poder(pg, chip); pg.set_viewport_size({'width': 1280, 'height': 800}); pg.wait_for_timeout(500)
        ok('sem rolagem horizontal em 1280: ' + nm, pg.evaluate(HSCROLL), pg.evaluate("()=>document.documentElement.scrollWidth"))
        pg.screenshot(path=OUT + '/poder_%s_1280.png' % nm, full_page=True); pg.set_viewport_size({'width': 1440, 'height': 900})
    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    b.close()
falhas = [n for c, n in checks if not c]
print('\nRESULTADO: %d/%d ok' % (len(checks) - len(falhas), len(checks)), '| falhas:', falhas)
sys.exit(1 if falhas else 0)
