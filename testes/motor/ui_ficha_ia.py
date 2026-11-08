# Motor 5, etapa 4: no modo Claude integrado, a IA devolve só a ficha e as regras do jogo calculam o parecer (Claude simulado com uma ficha pronta).
# uso: python3 run_sandbox.py ui_ficha_ia.py <pasta com index.html> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8861
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
    pg.locator('#caixa').scroll_into_view_if_needed()
    if texto: pg.fill('#caixa', texto)
    click(pg, 'Assinar e enviar', 2200)
    if SHOT:
        AV.append(pg.locator('[data-parecer-corte-linear]').count())
        pg.screenshot(path=OUT + '/' + SHOT[0] + '.png'); SHOT.clear()
    btns = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
    for alvo in ['Assinar e publicar no DOU', 'Votar agora']:
        if alvo in btns:
            pg.locator('.modal-wrap button').filter(has_text=alvo).first.click(timeout=4000); pg.wait_for_timeout(1500); break
    else:
        print('  sem botão de aprovar:', btns[:6]); return False
    # votação ao vivo: tenta concluir
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
def estado(pg):
    return pg.evaluate("()=>{const e=document.querySelector('[data-secao-medidas]');return e?e.innerText.length:-1}")


checks = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:300]) if det != '' else ''), flush=True)
FICHA = {"medidas": [{"texto_canonico": "Zerar o IPI e o imposto de importação de consoles de videogame", "acao": "isentar", "objeto": "IPI e imposto de importação de consoles", "publico": "", "publico_n": None, "quantia_rs": None, "periodicidade": None, "duracao_meses": None, "instrumento_dito": None}],
         "pergunta": False, "ironia": False, "condicao": None, "resumo": "Zera os tributos federais sobre consoles.", "vozes": [{"nome": "Kauã", "papel": "gamer", "emoji": "🎮", "fala": "Agora sim, PS5 no preço de PS2."}], "manchetes": {"globo": "Governo zera IPI de consoles", "carta": "Videogame mais barato", "antagonista": "Planalto troca imposto por voto gamer"}}
INIT = "window.__prompts=[];window.claude={use:async()=>({json:async(p,o)=>{window.__prompts.push(String(p));await new Promise(r=>setTimeout(r,1500));return %s;}})};" % json.dumps(FICHA, ensure_ascii=False)
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    pg.add_init_script(INIT)
    start(pg); fecha_modais(pg)
    pg.locator('button[aria-label*="onfigura"], button[title*="onfigura"]').first.click(timeout=6000); pg.wait_for_timeout(600)
    pg.locator('.modal-wrap button').filter(has_text='Claude integrado · rápido').first.click(timeout=6000); pg.wait_for_timeout(300)
    pg.locator('.modal-wrap button[aria-label="Fechar"]').first.click(timeout=4000); pg.wait_for_timeout(500)
    pg.locator('#caixa').scroll_into_view_if_needed(); pg.fill('#caixa', 'zera o imposto dos videogame q ta caro dms'); click(pg, 'Assinar e enviar', 300)
    ok('Enquanto a IA pensa, o parecer do motor local já está aberto com o aviso "refinando"', pg.locator('.modal-wrap [data-refinando]').count() == 1, '')
    pg.screenshot(path=OUT + '/refinando.png'); pg.wait_for_timeout(2500)
    txt = pg.locator('.modal-wrap').first.inner_text()
    pr = pg.evaluate("()=>window.__prompts")
    ok('O jogo manda o prompt da ficha (não pede números à IA)', pr and 'FICHA de leitura' in pr[0] and 'custo_anual_bi' not in pr[0], (pr[0][:120] if pr else pr))
    ok('A ementa mostra o texto do jogador', 'zera o imposto dos videogame' in txt, txt[:200])
    ok('O valor sai das regras do jogo (consoles: menos de R$ 3 bi), não da IA', ('R$ 0,8 bi' in txt) or ('R$ 0,4 bi' in txt) or ('R$ 1' in txt and 'bi' in txt), txt[txt.find('ANUAL'):txt.find('ANUAL') + 60] if 'ANUAL' in txt else txt[:300])
    ok('O parecer abre na hora e depois é refinado pela IA (aviso "Leitura refinada")', pg.locator('[data-refinado]').count() == 1 and pg.locator('[data-refinando]').count() == 0, '')
    ok('O cabeçalho diz que a leitura é da IA e as contas do motor', 'leitura da IA, contas do motor 5' in txt, txt[:300])
    pg.screenshot(path=OUT + '/ficha_ia.png')
    print('erros:', errs[:3])
    falhas = [n for c, n in checks if not c]
    print('RESUMO: %d/%d' % (len(checks) - len(falhas), len(checks)), '| falhas:', falhas)
    b.close()
