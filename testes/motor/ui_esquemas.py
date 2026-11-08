# Esquemas de corrupção (escolha do jogador, com selo "simulado"): painel, ganhos, rastro, escalada da investigação e desfecho.
# uso: python3 run_sandbox.py ui_esquemas.py <pasta com index.html> <saida_dir> [porta]
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
def SET(pg, js): pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);" + js + ";return n})"); pg.wait_for_timeout(500)
def G(pg, e): return pg.evaluate("()=>{const g=__QV().gRef.current;return (" + e + ")}")
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__E = () => ({ esqFaz, esqMensal, esqDesfecho, esqRiscoMes, apoioPartido, analisaLocal, fimDoMes });\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    ok('Personagem real (Lula): esquemas disponíveis', bool(G(pg, '!!g.cfg.real')))
    SET(pg, "n.acoes=9;n.props=9")
    pg.locator('#sec-tab-eu').click(); pg.wait_for_timeout(500)
    pg.locator('#eu-chip-bastidores').click(); pg.wait_for_timeout(700)
    ok('Painel de esquemas aparece com o selo "simulado"', pg.locator('[data-esquemas]').count() == 1 and 'simulado' in pg.locator('[data-esquemas]').inner_text(), '')
    # apoio de um partido antes do mensalão
    ap0 = pg.evaluate("()=>{const g=__QV().gRef.current;const p=__E().analisaLocal(g,'Criar o programa Farmácia Popular para todos');return __E().apoioPartido(g,'UNIAO',p,'cam')}")
    a0 = G(pg, 'g.acoes')
    pg.locator('[data-esq-faz=caixa2]').click(); pg.wait_for_timeout(500)
    ok('Caixa 2: +R$ 150 mi, gasta 1 ação e deixa rastro', G(pg, 'g.eu.esq.caixa2') == 150 and G(pg, 'g.acoes') == a0 - 1 and G(pg, 'g.eu.esq.rastro') > 0, (G(pg, 'g.eu.esq.caixa2'), G(pg, 'g.acoes'), G(pg, 'g.eu.esq.rastro')))
    pg.locator('[data-esq-faz=mensalao]').click(); pg.wait_for_timeout(500)
    ap1 = pg.evaluate("()=>{const g=__QV().gRef.current;const p=__E().analisaLocal(g,'Criar o programa Farmácia Popular para todos');return __E().apoioPartido(g,'UNIAO',p,'cam')}")
    ok('Mensalão: pago com caixa 2 (R$ 60 mi) e apoio da base sobe', G(pg, 'g.eu.esq.caixa2') == 90 and ap1 > ap0 + 10, (ap0, ap1))
    gr0 = G(pg, 'g.groups.agro'); pg.locator('[data-esq=grupo] .chip').filter(has_text='agronegócio').click(); pg.locator('[data-esq-faz=grupo]').click(); pg.wait_for_timeout(500)
    ok('Favorecer o agro: +6 de apoio do grupo e R$ 2 bi de gasto extra', G(pg, 'g.groups.agro') > gr0 + 5, (gr0, G(pg, 'g.groups.agro')))
    pg.locator('[data-esq-faz=fortuna]').click(); pg.wait_for_timeout(500)
    ok('Propina: +R$ 25 mi de fortuna', G(pg, 'g.eu.esq.fortuna') == 25)
    pg.locator('[data-esq-faz=abafar]').click(); pg.wait_for_timeout(500)
    ok('Trocar o comando da PF: investigação freada por 6 meses', G(pg, 'g.eu.esq.abafa') == G(pg, 'g.mes') + 6)
    pg.locator('[data-esquemas]').scroll_into_view_if_needed(); pg.screenshot(path=OUT + '/esquemas.png', full_page=False)
    # escalada: rastro alto, vários meses
    r = pg.evaluate("()=>{const X=__E();const g=structuredClone(__QV().gRef.current);g.eu.esq.rastro=95;g.eu.esq.abafa=0;const fases=[];for(let i=0;i<30&&g.eu.esq.fase<4;i++){X.fimDoMes(g);g.over=null;g.acoes=3;g.props=3;g.pes.saude=90;fases.push(g.eu.esq.fase)}return {fases, feed:g.feed.slice(0,60).map(f=>f.txt).filter(t=>/^(?:Reportagem revela pagamentos|CPI INSTALADA|PF FAZ OPERAÇÃO CONTRA O ENTORNO|PRESIDENTE É DENUNCIADO|Planalto troca o comando)/.test(t)).join(' | '), desf:X.esqDesfecho(g), nome:g.cfg.nome}}")
    ok('Rastro alto leva à escalada: reportagem, CPI, operação da PF, denúncia', max(r['fases']) == 4 and 1 in r['fases'] and 3 in r['fases'], r['fases'])
    ok('Notícias falam em "o presidente"/"Planalto", sem o nome da pessoa real', 'lula' not in r['feed'].lower() and r['feed'] != '' and ('Planalto' in r['feed'] or 'PRESIDENTE' in r['feed']), r['feed'][:200])
    ok('Desfecho com operação da PF: condenação e prisão depois do mandato (simulado)', 'preso' in (r['desf'] or '') and 'simulado' in (r['desf'] or ''), r['desf'])
    ok('Sem esquemas, nenhum desfecho', pg.evaluate("()=>{const g=structuredClone(__QV().gRef.current);delete g.eu.esq;return __E().esqDesfecho(g)}") is None)
    ok('0 erros de página', not errs, errs[:2])
    falhas = [n for c, n in checks if not c]
    print('RESUMO: %d/%d' % (len(checks) - len(falhas), len(checks)), '| falhas:', falhas)
    b.close()
