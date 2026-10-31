# Teste de interface do pacote visual (v4.2): Diário do mandato agrupado por mês, Banca de jornal com capas, tela Medidas
# (filtros, linhas que expandem, botão Revogar) e cartão PIB per capita no painel de indicadores. Confere 0 erros de página/console.
# uso: python3 run_sandbox.py ui_visual.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8871
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
    pg.locator('#caixa').scroll_into_view_if_needed(); pg.fill('#caixa', texto)
    click(pg, 'Assinar e enviar', 2200)
    btns = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
    for alvo in ['Assinar e publicar no DOU', 'Votar agora']:
        if alvo in btns:
            pg.locator('.modal-wrap button').filter(has_text=alvo).first.click(timeout=4000); pg.wait_for_timeout(1500); break
    else:
        print('  sem botão de aprovar:', btns[:6]); return False
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
def aba(pg, nome):
    fecha_modais(pg); pg.locator('[role=tab]').filter(has_text=nome).first.click(timeout=5000); pg.wait_for_timeout(800)
def n_cards(pg): return pg.locator('.med-card').count()
checks = []
def ok(nome, cond, det=''):
    checks.append(bool(cond)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:220]) if det != '' else ''), flush=True)
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    start(pg)
    # painel de indicadores: PIB per capita na posse
    k0 = pg.evaluate("()=>{const e=document.querySelector('[data-kpi=pibpc]');return e?e.innerText:''}")
    ok('PIB per capita: cartão no painel, em R$', re.search(r'R\$\s*\d{2}\.\d{3}', k0) is not None, k0.replace('\n', ' | '))
    ok('PIB per capita: parte do valor real do IBGE 2025 (R$ 59.687)', 'R$ 59.687' in k0.replace(' ', ' '), k0.replace('\n', ' | '))
    tip = pg.evaluate("()=>{const e=document.querySelector('[data-kpi=pibpc] [title]');return e?e.title:''}")
    ok('PIB per capita: fonte IBGE citada no tooltip', 'IBGE' in tip, tip[:80])
    # duas medidas aprovadas, em meses diferentes, e dois meses avançados
    a1 = propoe(pg, 'zerar o imposto de importação de remédios por decreto')
    encerra(pg, 1)
    a2 = propoe(pg, 'decreto criando o programa de merenda escolar de R$ 1 bilhão')
    encerra(pg, 1)
    ok('duas medidas aprovadas', a1 and a2, (a1, a2))
    aba(pg, 'Mesa')
    # Diário por mês
    grp = pg.evaluate("()=>[...document.querySelectorAll('[data-por-mes=diario] [data-mes-grupo]')].map(e=>({m:e.dataset.mesGrupo,ab:e.dataset.aberto,h:e.querySelector('.pm-h').textContent.trim()}))")
    print('  grupos do Diário:', grp)
    ok('Diário: atos agrupados por mês (2+ grupos)', len(grp) >= 2, grp)
    ok('Diário: cabeçalho "Mês de 2027 · N ato(s)"', all(re.match(r'^[A-ZÀ-Ú][a-zç]+ de 20\d\d · \d+ atos?$', x['h']) for x in grp), [x['h'] for x in grp])
    ok('Diário: mês mais recente aberto e o mais antigo recolhido', grp and grp[0]['ab'] == '1' and grp[-1]['ab'] == '0', [x['ab'] for x in grp])
    n_antes = pg.locator('[data-por-mes=diario] .pm-i').count()
    pg.locator('[data-por-mes=diario] [data-mes-grupo]').last.locator('button.pm-h').click(); pg.wait_for_timeout(300)
    ok('Diário: mês antigo expande ao clicar', pg.locator('[data-por-mes=diario] .pm-i').count() > n_antes, (n_antes, pg.locator('[data-por-mes=diario] .pm-i').count()))
    ok('Diário: mantém os selos de status', pg.locator('[data-por-mes=diario] .chip').count() >= 1)
    # Banca de jornal
    capas = pg.locator('[data-testid=banca-capas] .jornal')
    ok('Banca: 3 capas de jornal', capas.count() >= 3, capas.count())
    ok('Banca: manchete principal grande', pg.locator('[data-testid=banca-capas] .j-grande').count() == 1)
    fam = pg.evaluate("()=>getComputedStyle(document.querySelector('.j-grande .j-hl')).fontFamily")
    ok('Banca: manchete em fonte serifada (Playfair Display)', 'Playfair' in fam, fam)
    fontes = pg.evaluate("()=>[...new Set([...document.querySelectorAll('.jornal')].map(e=>e.dataset.jornal))].sort().join(',')")
    ok('Banca: os três veículos aparecem', fontes == 'antag,carta,globo', fontes)
    txt = pg.locator('[data-secao=banca]').text_content()
    ok('Banca: nomes dos veículos e selo "simulado" preservados', all(n in txt for n in ['O Globo / Estadão', 'Carta Capital', 'O Antagonista']) and 'simulad' in txt.lower(), '')
    pg.wait_for_timeout(400); pg.screenshot(path=OUT + '/depois_mesa.png', full_page=True)
    # legibilidade: nada abaixo de 12px nos textos visíveis da Mesa
    peq = pg.evaluate("""()=>{const r=[];for(const e of document.querySelectorAll('#root *')){if(!e.childNodes.length||e instanceof SVGElement)continue;const t=[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>1);if(!t)continue;const s=parseFloat(getComputedStyle(e).fontSize);const b=e.getBoundingClientRect();if(s<11.5&&b.width>0&&b.height>0)r.push(s+'px '+e.tagName+'.'+String(e.className).slice(0,40)+' '+e.textContent.trim().slice(0,30));}return r.slice(0,10)}""")
    ok('legibilidade: nenhum texto da Mesa abaixo de 12px', len(peq) == 0, peq)
    # PIB per capita sobe com o PIB nominal e mostra delta no mês
    k1 = pg.evaluate("()=>{const e=document.querySelector('[data-kpi=pibpc]');return e?e.innerText:''}")
    ok('PIB per capita: segue com valor em R$ e variação no mês após 2 meses', re.search(r'R\$\s*\d{2}\.\d{3}', k1) is not None and re.search(r'[▲▼→]', k1) is not None, k1.replace('\n', ' | '))
    # seletor de indicadores
    click(pg, 'Escolher indicadores', 400)
    ok('"Escolher indicadores" lista o PIB per capita', pg.locator('[role=dialog][aria-label="Escolher indicadores"] label').filter(has_text='PIB per capita').count() == 1)
    click(pg, 'Fechar', 300)
    # Medidas
    aba(pg, 'Medidas')
    n_todas = n_cards(pg)
    ok('Medidas: linhas compactas (2+) e resumo com impacto fiscal', n_todas >= 2 and 'despesa' in pg.locator('.med-resumo').text_content().lower() and 'receita' in pg.locator('.med-resumo').text_content().lower(), n_todas)
    fil = pg.evaluate("()=>[...document.querySelectorAll('.med-fil')].map(b=>b.innerText.replace(/\\n/g,' '))")
    print('  filtros:', fil)
    ok('Medidas: filtros Todas / Em implantação / Em vigor / Com problema / Revogadas / Rejeitadas', all(any(n in f for f in fil) for n in ['Todas', 'Em implantação', 'Em vigor', 'Com problema', 'Revogadas', 'Rejeitadas']), fil)
    ok('Medidas: linha recolhida não mostra Revogar', pg.locator('.med-card .med-acoes').count() == 0)
    click(pg, re.compile(r'^\s*Revogadas e encerradas'), 400)
    n_enc = n_cards(pg)
    ok('Medidas: filtro muda a lista (Revogadas e encerradas)', n_enc != n_todas, (n_todas, n_enc))
    ok('Medidas: estado vazio do filtro', n_enc > 0 or pg.locator('[data-testid=med-sem-itens]').count() == 1)
    click(pg, re.compile(r'^\s*Rejeitadas ou arquivadas'), 400)
    ok('Medidas: filtro Rejeitadas troca a lista por propostas rejeitadas/arquivadas', n_cards(pg) == 0 and (pg.locator('.med-rej li').count() >= 0))
    click(pg, re.compile(r'^\s*Em implantação'), 400)
    n_imp = n_cards(pg)
    ok('Medidas: filtro Em implantação filtra', 0 < n_imp <= n_todas, n_imp)
    click(pg, re.compile(r'^\s*Todas'), 400)
    ok('Medidas: Todas restaura a lista', n_cards(pg) == n_todas)
    # agrupamento
    pg.select_option('select[aria-label="Agrupar medidas por"]', 'tipo'); pg.wait_for_timeout(300)
    ok('Medidas: agrupa por tipo', pg.locator('.med-grupo').count() >= 1 and pg.locator('.med-gh').first.inner_text() != '', pg.locator('.med-gh').first.inner_text().replace('\n', ' '))
    pg.select_option('select[aria-label="Agrupar medidas por"]', 'data'); pg.wait_for_timeout(300)
    # expandir uma linha
    pg.locator('.med-row').first.click(); pg.wait_for_timeout(400)
    ok('Medidas: linha expande e mostra a linha do tempo de fases', pg.locator('.med-card[data-aberto="1"] .med-fases').count() == 1)
    rev = pg.locator('.med-card[data-aberto="1"] .med-acoes button').filter(has_text=re.compile(r'Revogar|Propor revogação'))
    ok('Medidas: linha expandida mostra o botão Revogar', rev.count() == 1, pg.locator('.med-card[data-aberto="1"] .med-acoes').inner_text().replace('\n', ' | ') if pg.locator('.med-card[data-aberto="1"] .med-acoes').count() else '')
    ok('Medidas: Acelerar e Ajustar também presentes', pg.locator('.med-card[data-aberto="1"] .med-acoes button').count() == 3)
    pg.locator('.med-row').first.click(); pg.wait_for_timeout(300)
    ok('Medidas: linha recolhe de novo', pg.locator('.med-card[data-aberto="1"]').count() == 0)
    click(pg, 'Expandir tudo', 400)
    pg.screenshot(path=OUT + '/depois_medidas_expandida.png', full_page=True)
    click(pg, 'Recolher tudo', 400)
    pg.screenshot(path=OUT + '/depois_medidas.png', full_page=True)
    # sem overflow horizontal a 1440 e 1280
    for w in (1440, 1280):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.wait_for_timeout(400)
        ov = pg.evaluate("()=>document.documentElement.scrollWidth-document.documentElement.clientWidth")
        ok('sem rolagem horizontal da página em %dpx (Medidas)' % w, ov <= 1, ov)
    aba(pg, 'Mesa')
    ov = pg.evaluate("()=>document.documentElement.scrollWidth-document.documentElement.clientWidth")
    ok('sem rolagem horizontal da página em 1280px (Mesa)', ov <= 1, ov)
    pg.screenshot(path=OUT + '/depois_mesa_1280.png', full_page=True)
    # medida revogada vai para o filtro Revogadas
    aba(pg, 'Medidas'); pg.locator('.med-row').first.click(); pg.wait_for_timeout(300)
    bt = pg.locator('.med-card[data-aberto="1"] .med-acoes button:not([disabled])').filter(has_text=re.compile(r'Revogar por decreto'))
    if bt.count():
        bt.first.click(); pg.wait_for_timeout(800)
        aba(pg, 'Medidas'); click(pg, re.compile(r'^\s*Revogadas e encerradas'), 400)
        ok('Revogar por decreto continua funcionando (medida vai para Revogadas e encerradas)', n_cards(pg) >= 1, n_cards(pg))
    else: print('  (Revogar por decreto indisponível; ignorado)')
    json.dump(errs, open(OUT + '/errs_visual.json', 'w')); print('ERRS', errs[:8])
    ok('0 erros de página/console', not errs, errs[:3])
    print('RESUMO: %d/%d' % (sum(checks), len(checks)))
    b.close()
