# Teste de interface da v3.9: texto informal/mal escrito vira parecer legível; medida condicional ('se o dólar passar de R$ 7, ...') fica "aguardando gatilho" no painel Medidas
# (cartão com o indicador e o limiar), não entra no fiscal e dispara quando o indicador cruza o limiar. Confere 0 erros de página/console.
# uso: python3 run_sandbox.py ui_v39.py <pasta com index.html> <saida_dir> [porta]
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

def parecer_txt(pg, texto):
    fecha_modais(pg)
    pg.locator('#caixa').scroll_into_view_if_needed(); pg.fill('#caixa', texto)
    click(pg, 'Assinar e enviar', 2200)
    return pg.evaluate("()=>{const e=document.querySelector('.modal-wrap');return e?e.innerText:''}")
checks = []
def ok(nome, cond, det=''):
    checks.append(bool(cond)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:200]) if det != '' else ''), flush=True)
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    start(pg)
    # 1) texto informal: o parecer traz o tópico em linguagem normal
    t = parecer_txt(pg, 'bota wifi de graça em todo posto de saúde kkk')
    ok('informal: parecer abre', len(t) > 200, t[:80].replace('\n', ' '))
    ok('informal: não é lido como vago', 'vago' not in t.lower()[:400] and 'wifi' in t.lower(), '')
    fecha_modais(pg)
    # 2) medida condicional: aprova e confere o cartão "aguardando gatilho"
    pg.fill('#caixa', 'Se o dólar passar de R$ 7, zerar o imposto de importação por decreto')
    click(pg, 'Assinar e enviar', 2200)
    t = pg.evaluate("()=>{const e=document.querySelector('.modal-wrap');return e?e.innerText:''}")
    ok('condição: a ementa guarda o texto digitado com o gatilho e o custo é o ESPERADO (valor pleno x chance), não o pleno', 'Se o dólar passar de R$ 7' in t and re.search(r'R\$ 1,\d bi', t) is not None, t[t.find('Ementa'):t.find('Ementa') + 140].replace('\n', ' '))
    btns = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
    for alvo in ['Assinar e publicar no DOU', 'Votar agora']:
        if alvo in btns:
            pg.locator('.modal-wrap button').filter(has_text=alvo).first.click(timeout=4000); pg.wait_for_timeout(1500); break
    for _ in range(6):
        bb = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
        pick = next((x for x in bb if re.match(r'^(Ver resultado|Concluir|Apurar|Aplicar|Fechar|Continuar|Encerrar votação|Pular)', x)), None)
        if not pick: break
        try: pg.locator('.modal-wrap button').filter(has_text=pick).first.click(timeout=3000)
        except Exception: pass
        pg.wait_for_timeout(900)
    fecha_modais(pg)
    print('  botões do parecer:', btns[:8])
    pg.locator('[role=tab]').filter(has_text='Medidas').first.click(timeout=5000); pg.wait_for_timeout(900)
    print('  erros até aqui:', errs[:3]); print('  painel:', pg.evaluate("()=>{const e=document.querySelector('[data-secao-medidas]');return e?e.innerText.slice(0,300).replace(/\\n/g,' | '):'sem painel'}"))
    print('  cartões:', pg.evaluate("()=>[...document.querySelectorAll('.med-card')].map(c=>c.dataset.estado+': '+c.innerText.slice(0,70).replace(/\\n/g,' '))"))
    card = pg.evaluate("()=>{const e=document.querySelector('.med-card[data-estado=aguardando]');return e?e.innerText:''}")
    ok('painel: cartão em estado "aguardando gatilho"', 'aguardando' in card.lower(), card[:100].replace('\n', ' '))
    gat = pg.evaluate("()=>{const e=document.querySelector('[data-testid=med-gatilho]');return e?e.innerText:''}")
    ok('painel: mostra indicador e limiar ("Aguardando: dólar > R$ 7,00")', re.search(r'dólar\s*>\s*R\$\s*7', gat) is not None, gat.replace('\n', ' '))
    pg.screenshot(path=OUT + '/painel_aguardando.png', full_page=False)
    encerra(pg, 1)  # o mês fecha sem erro com a medida aguardando
    json.dump(errs, open(OUT + '/errs.json', 'w')); print('ERRS', errs[:8])
    ok('0 erros de página/console', not errs, errs[:3])
    print('RESUMO: %d/%d' % (sum(checks), len(checks)))
    b.close()
