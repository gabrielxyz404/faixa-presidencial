# Teste de jogo pela interface: aprova medidas de tipos diferentes, avança meses, abre o painel "Medidas", usa as ações e confere 0 erros.
# uso: python3 run_sandbox.py ui_medidas.py <pasta com index.html> <saida_dir> [porta]
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
PROPS = ["Aumentar o Bolsa Família para R$ 800", "Zerar o IPI de carros elétricos", "Taxar dividendos em 15%", "Regulamentar o trabalho por aplicativo com salário mínimo por hora", "Privatizar os Correios",
         "Criar um programa de creches em tempo integral para 1 milhão de crianças"]
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    start(pg)
    ok = 0
    for i, t in enumerate(PROPS):
        if i == 4:  # acabaram as ações do mês: avança e segue
            encerra(pg)
        try:
            r = propoe(pg, t); ok += 1 if r else 0; print('proposta', i + 1, t[:40], r, flush=True)
        except Exception as e:
            print('ERRO proposta', t[:40], str(e)[:160]); fecha_modais(pg)
    encerra(pg, 3)
    pg.locator('[role=tab]').filter(has_text='Medidas').first.click(timeout=5000); pg.wait_for_timeout(800)
    print('painel após 4 meses:', estado(pg), 'cartões:', pg.locator('.med-card').count())
    encerra_in_panel = lambda n: [ (pg.locator('button').filter(has_text=re.compile(r'^\s*Encerrar m')).first.click(timeout=8000), pg.wait_for_timeout(900), fecha_modais(pg)) for _ in range(n)]
    encerra_in_panel(10)
    print('painel após 14 meses:', 'cartões:', pg.locator('.med-card').count(), '| problemas:', pg.locator('[data-testid=med-probs]').count())
    # ações
    def acao(rot):
        bt = pg.locator('.med-card .med-acoes button:not([disabled])').filter(has_text=re.compile(rot))
        n = bt.count()
        if n: bt.first.click(timeout=4000); pg.wait_for_timeout(700)
        return n
    print('acelerar disponíveis:', acao('Acelerar'))
    print('ajustar disponíveis:', acao('Ajustar|Regulamentar'))
    pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + '/painel_v36.png', full_page=False)
    n_rev = acao('Revogar por decreto'); print('revogar por decreto disponíveis:', n_rev)
    n_prop = pg.locator('.med-card .med-acoes button:not([disabled])').filter(has_text='Propor revogação').count(); print('propor revogação disponíveis:', n_prop)
    if n_prop:
        pg.locator('.med-card .med-acoes button:not([disabled])').filter(has_text='Propor revogação').first.click(timeout=4000); pg.wait_for_timeout(1200)
        print('caixa após propor revogação:', pg.evaluate("()=>document.getElementById('caixa')&&document.getElementById('caixa').value"))
        encerra(pg)  # novo mês, ações renovadas
        print('revogação enviada:', propoe(pg, None))
    # mesa: resumo
    pg.locator('[role=tab]').filter(has_text='Mesa').first.click(timeout=5000); pg.wait_for_timeout(600)
    print('faixa-resumo na mesa:', pg.evaluate("()=>{const e=document.querySelector('[data-resumo-medidas]');return e?e.innerText.replace(/\\n+/g,' | '):null}"))
    print('resumo na mesa (pendência):', pg.evaluate("()=>{const e=document.querySelector('[data-pend=medidas]');return e?e.innerText.replace(/\\n+/g,' | '):null}"))
    try: encerra(pg, 4)
    except Exception as e: print('fim de jogo ou botão ausente:', str(e)[:80])
    pg.locator('[role=tab]').filter(has_text='Medidas').first.click(timeout=5000); pg.wait_for_timeout(600)
    print('painel após ~20 meses: cartões', pg.locator('.med-card').count())
    json.dump(errs, open(OUT + '/errs.json', 'w')); print('ERRS', errs[:8]); b.close()
