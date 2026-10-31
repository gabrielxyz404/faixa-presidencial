# Teste de interface da tela inicial e do assistente (redesenho "inicio-v2"): hero, escolha de modo/dificuldade, abas e filtros,
# fluxo de novo mandato com o stepper, barra fixa, posse, volta ao menu pelo gesto da engrenagem e "Continuar mandato" com o resumo do save.
# Confere também: sem rolagem horizontal em 1440, 1280 e 400 px, texto >= 12 px e 0 erros de página/console.
# uso: python3 run_sandbox.py ui_inicio.py <pasta com index.html, fotos.json e logos.json> <saida_dir> [porta]
import sys, threading, functools, http.server, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8862
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
checks = []
def ok(nome, cond, det=''):
    checks.append(bool(cond)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:200]) if det != '' else ''), flush=True)
def click(pg, t, ms=400):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(ms)
def sem_rolagem_h(pg):
    return pg.evaluate("()=>document.documentElement.scrollWidth<=window.innerWidth+1 && document.body.scrollWidth<=window.innerWidth+1")
def menor_fonte(pg, sel):
    # menor tamanho de fonte (px) entre os elementos com texto visível dentro de sel
    return pg.evaluate("""(sel)=>{let m=99,quem='';const raiz=document.querySelector(sel);if(!raiz)return [0,'sem raiz'];
      const w=document.createTreeWalker(raiz,NodeFilter.SHOW_TEXT);let n;
      while(n=w.nextNode()){if(!n.nodeValue.trim())continue;const e=n.parentElement;if(!e||e.closest('svg,style,script,.sr-only'))continue;const r=e.getBoundingClientRect();if(r.width===0||r.height===0)continue;
        const f=parseFloat(getComputedStyle(e).fontSize);if(f<m){m=f;quem=n.nodeValue.trim().slice(0,40)+' <'+e.className+'>';}}
      return [m,quem];}""", sel)
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='networkidle'); pg.wait_for_timeout(1500)
    # ---- 1) menu sem save: hero ----
    ok('hero: tela inicial montada', pg.locator('[data-tela=inicio]').count() == 1)
    ok('hero: nome do jogo no h1', 'Faixa' in pg.locator('h1').first.inner_text() and 'Presidencial' in pg.locator('h1').first.inner_text(), pg.locator('h1').first.inner_text())
    ok('hero: sem save não há "Continuar mandato", há "Novo mandato"', pg.locator('[data-ini=continuar]').count() == 0 and pg.locator('[data-ini=novo]').count() >= 1)
    ok('modo: 3 cartões (Lua de mel, Brasília, Brasília raiz)', pg.locator('[data-ini-modo]').count() == 3)
    ok('dificuldade: 3 cartões', pg.locator('[data-ini-dif]').count() == 3)
    ok('padrões: Brasília e Realista marcados', pg.locator('[data-ini-modo=brasilia][aria-checked=true]').count() == 1 and pg.locator('[data-ini-dif=realista][aria-checked=true]').count() == 1)
    pg.locator('[data-ini-dif=brutal]').click(); pg.wait_for_timeout(200)
    ok('dificuldade: escolher Brutal marca o cartão', pg.locator('[data-ini-dif=brutal][aria-checked=true]').count() == 1)
    pg.locator('[data-ini-dif=realista]').click(); pg.wait_for_timeout(200)
    abas = pg.locator('[role=tab][id^=ini-tab-]').all_inner_texts()
    ok('abas: criar, eleito, candidatos, políticos, famosos, figuras', len(abas) == 6 and 'Presidente eleito' in abas, abas)
    ok('rodapé: fontes e créditos em details fechado', pg.locator('details[data-ini=creditos]').count() == 1 and pg.evaluate("()=>!document.querySelector('details[data-ini=creditos]').open"))
    ok('rodapé: abre e mostra TSE/Wikipédia', (pg.locator('details[data-ini=creditos] summary').click() or True) and 'Wikipédia' in pg.locator('details[data-ini=creditos]').inner_text())
    pg.locator('details[data-ini=creditos] summary').click()
    for w in (1440, 1280, 400):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.wait_for_timeout(300)
        ok('menu sem rolagem horizontal em %d px' % w, sem_rolagem_h(pg))
    pg.set_viewport_size({'width': 1440, 'height': 900})
    mf = menor_fonte(pg, '[data-tela=inicio]'); ok('menu: texto >= 12 px', mf[0] >= 12, mf)
    pg.screenshot(path=OUT + '/menu_1440.png', full_page=True)
    # ---- 2) abas e filtros ----
    click(pg, 'Candidatos de 2026')
    n0 = pg.locator('[data-ini=candidatos] .ini-card').count()
    ok('candidatos: grade de cartões com foto, logo e botão', n0 >= 3 and pg.locator('[data-ini=candidatos] .ini-card svg[data-foto], [data-ini=candidatos] .ini-card svg[role=img]').count() >= n0 and pg.locator('[data-ini=candidatos] [data-logo]').count() >= 1, n0)
    pg.locator('[data-ini=candidatos] .ini-chipb').filter(has_text='Eleito').first.click(); pg.wait_for_timeout(300)
    ok('candidatos: chip "Eleito" filtra para 1 cartão', pg.locator('[data-ini=candidatos] .ini-card').count() == 1)
    pg.locator('[data-ini=candidatos] .ini-chipb').filter(has_text='Todos').first.click(); pg.wait_for_timeout(200)
    click(pg, 'Políticos')
    ok('políticos: cartões e chips de cargo', pg.locator('[data-ini=politicos] .ini-card').count() > 5 and pg.locator('[data-ini=politicos] .ini-chipb').count() == 4)
    pg.locator('[data-ini=politicos] .ini-chipb').filter(has_text='Governadores').first.click(); pg.wait_for_timeout(300)
    ok('políticos: chip Governadores filtra', 0 < pg.locator('[data-ini=politicos] .ini-card').count() <= 27, pg.locator('[data-ini=politicos] .ini-card').count())
    click(pg, 'Famosos'); ok('famosos: cartões com botão Jogar', pg.locator('[data-ini=famosos] .ini-card button').count() >= 1)
    click(pg, 'Figuras sem mandato'); ok('figuras: painel renderiza', pg.locator('[data-el=figuras]').count() == 1)
    click(pg, 'Criar presidente'); ok('criar: cartão Criar do zero', pg.locator('[data-ini=criar] button').filter(has_text='Criar do zero').count() == 1)
    # ---- 3) novo mandato pelo eleito + stepper ----
    click(pg, 'Presidente eleito'); ok('eleito: destaque com "Assumir o mandato"', pg.locator('[data-ini=eleito] button').filter(has_text='Assumir o mandato').count() == 1)
    click(pg, 'Assumir o mandato', 600)
    ok('wizard: montado', pg.locator('[data-tela=wizard]').count() == 1)
    tabs = pg.locator('.wz-tab').all_inner_texts()
    ok('stepper: 5 etapas numeradas (Presidente, Ideologia, Personalidade, Ministério, Posse)', [re.sub(r'\W+', '', t.replace('●', '')) for t in tabs] and len(tabs) == 5 and tabs[2].replace('\n', '').startswith('3Personalidade'), tabs)
    pr = pg.locator('.wz-prog'); ok('stepper: barra de progresso (passo 2 de 5 ao abrir pelo eleito)', pr.get_attribute('aria-valuenow') == '2' and pr.get_attribute('aria-valuemax') == '5')
    ok('wizard: barra fixa com Voltar e Avançar', pg.locator('.wz-bar button').filter(has_text='Avançar').count() == 1 and pg.locator('.wz-bar button').filter(has_text='Voltar').count() == 1)
    click(pg, '3Personalidade'); ok('stepper: 3Personalidade vai ao passo 3', pg.locator('.wz-prog').get_attribute('aria-valuenow') == '3')
    for t in ["Negociador", "Técnico"]: click(pg, t)
    ok('personalidade: 2 traços marcados', pg.locator('.wz-opt[aria-pressed=true]').count() == 2)
    click(pg, 'Avançar')
    ok('ministério: grade com 9 cartões de pasta', pg.locator('.wz-pasta').count() == 9)
    ok('ministério: Avançar desabilitado até escolher todos', pg.locator('.wz-bar button').filter(has_text='Avançar').first.is_disabled())
    mf = menor_fonte(pg, '[data-tela=wizard]'); ok('wizard passo 4: texto >= 12 px', mf[0] >= 12, mf)
    for w in (1440, 1280, 400):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.wait_for_timeout(300)
        ok('wizard sem rolagem horizontal em %d px' % w, sem_rolagem_h(pg))
        pg.screenshot(path=OUT + '/wizard_min_%d.png' % w)
    pg.set_viewport_size({'width': 1440, 'height': 900})
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count() == 0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(250)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(250)
    ok('ministério: todas as pastas com nome (9/9)', pg.locator('.wz-pasta:not(.vazia)').count() == 9)
    click(pg, 'Avançar'); ok('stepper: passo 5 (Posse)', pg.locator('.wz-prog').get_attribute('aria-valuenow') == '5')
    ok('posse: revisão completa e Tomar posse habilitado', pg.locator('[data-wz=revisao] .b.ok').count() == 5 and pg.locator('.wz-bar button').filter(has_text='Tomar posse').first.is_enabled())
    pg.screenshot(path=OUT + '/wizard_posse_1440.png')
    pos = pg.evaluate("()=>{const r=document.querySelector('.wz-bar').getBoundingClientRect();return [Math.round(r.bottom),window.innerHeight]}")
    ok('wizard: barra fixa colada no rodapé da janela', abs(pos[0] - pos[1]) <= 1, pos)
    click(pg, 'Tomar posse', 1200)
    ok('jogo: Mesa abriu (sem menu)', pg.locator('[data-tela=inicio]').count() == 0 and pg.locator('[data-tela=wizard]').count() == 0)
    # ---- 4) engrenagem > Voltar ao menu > Continuar mandato ----
    for _ in range(4):
        if pg.locator('.modal-wrap').count() == 0: break
        try: pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^(Fechar|Continuar|OK|Entendi|Seguir|Próximo mês|Voltar à Mesa)')).first.click(timeout=1200)
        except Exception: pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
    pg.locator('button[aria-label="Configurações e motor de IA"]').click(timeout=6000); pg.wait_for_timeout(400)
    pg.locator('[data-voltar-menu]').click(timeout=6000); pg.wait_for_timeout(800)
    ok('menu: de volta à tela inicial', pg.locator('[data-tela=inicio]').count() == 1)
    ok('save: botão grande "Continuar mandato"', pg.locator('button[data-ini=continuar]').count() == 1 and 'Continuar mandato' in pg.locator('button[data-ini=continuar]').inner_text())
    card = pg.locator('[data-ini=save]')
    nome = card.locator('[data-ini=save-nome]').inner_text()
    ok('save: resumo com o presidente', len(nome) > 1, nome)
    ok('save: logo do partido', card.locator('[data-logo], svg').count() >= 1)
    ok('save: mês x/48', re.fullmatch(r'\d+/48', card.locator('[data-ini=save-mes]').inner_text().strip()) is not None, card.locator('[data-ini=save-mes]').inner_text())
    ok('save: aprovação em %', re.fullmatch(r'\d+%', card.locator('[data-ini=save-ap]').inner_text().strip()) is not None, card.locator('[data-ini=save-ap]').inner_text())
    ok('save: "Novo mandato" continua disponível', pg.locator('[data-ini=novo]').count() >= 1)
    for w in (1440, 400):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.wait_for_timeout(300)
        ok('menu com save sem rolagem horizontal em %d px' % w, sem_rolagem_h(pg))
        pg.screenshot(path=OUT + '/menu_save_%d.png' % w)
    pg.set_viewport_size({'width': 1440, 'height': 900})
    mf = menor_fonte(pg, '[data-tela=inicio]'); ok('menu com save: texto >= 12 px', mf[0] >= 12, mf)
    pg.locator('button[data-ini=continuar]').click(); pg.wait_for_timeout(1000)
    ok('continuar: retoma o mandato (sai do menu)', pg.locator('[data-tela=inicio]').count() == 0 and pg.locator('button[aria-label="Configurações e motor de IA"]').count() == 1)
    # ---- 5) celular: novo mandato do zero ----
    b.close()
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 400, 'height': 800})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='networkidle'); pg.wait_for_timeout(1200)
    ok('celular: menu sem rolagem horizontal', sem_rolagem_h(pg))
    pg.screenshot(path=OUT + '/menu_400.png', full_page=True)
    click(pg, 'Criar do zero', 600)
    ok('celular: wizard abre pelo "Criar do zero" no passo 1', pg.locator('.wz-prog').get_attribute('aria-valuenow') == '1' and sem_rolagem_h(pg))
    mf = menor_fonte(pg, '[data-tela=wizard]'); ok('celular: wizard texto >= 12 px', mf[0] >= 12, mf)
    pg.screenshot(path=OUT + '/wizard_400.png')
    b.close()
print('ERRS', errs)
ok('0 erros de página/console', not errs, errs[:3])
print('RESUMO: %d/%d' % (sum(checks), len(checks)))
sys.exit(0 if all(checks) and not errs else 1)
