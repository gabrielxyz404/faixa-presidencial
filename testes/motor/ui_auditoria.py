# Auditoria v92: quórum, lei já em vigor, chip de corte, assinar crise direto, aviso de pendências, Bastidores, comunicado fora de Medidas.
# uso: python3 run_sandbox.py ui_auditoria.py <pasta com index.html> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8863
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
    pg.on('dialog', lambda d: d.accept())
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__A = () => ({ quorum, analisaLocal, executaProposta, medidasDe, pendenciasMesa });\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    q = pg.evaluate("()=>{const X=__A();return [X.quorum('PL'),X.quorum('PL','LC'),X.quorum('PEC'),X.quorum('MP')]}")
    ok('Quórum: PL e MP por maioria dos presentes (236/38); lei complementar 257/41; PEC 308/49', q[0] == {'c': 236, 's': 38} and q[1] == {'c': 257, 's': 41} and q[2] == {'c': 308, 's': 49} and q[3] == q[0], q)
    r = pg.evaluate("()=>{const X=__A();const g=structuredClone(__QV().gRef.current);const n0=X.medidasDe(g).length;const p=X.analisaLocal(g,'Fazer um pronunciamento em rede nacional pedindo calma');X.executaProposta(g,p,'aprovada');return {inst:p.inst,n0,n1:X.medidasDe(g).length}}")
    ok('Comunicado puro não vira "medida em vigor"', r['inst'] == 'COM' and r['n1'] == r['n0'], r)
    SET(pg, "n.acoes=9;n.props=9")
    # lei já em vigor
    pg.locator('#caixa').scroll_into_view_if_needed(); pg.fill('#caixa', 'Isentar do imposto de renda quem ganha até 5 mil reais')
    pg.locator('button').filter(has_text='Assinar e enviar').first.click(); pg.wait_for_timeout(2000)
    ok('Lei já em vigor: aviso "Isso já é lei" no parecer', pg.locator('[data-ja-vigente]').count() == 1)
    pg.screenshot(path=OUT + '/ja_vigente.png')
    pg.locator('[data-ja-vigente-com]').click(); pg.wait_for_timeout(600)
    btns = pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
    ok('"Divulgar sem votação" troca para comunicado (assinar no DOU, sem voto)', 'Assinar e publicar no DOU' in btns and 'Votar agora' not in btns, btns[:6])
    fecha_modais(pg)
    # crise: chip de corte e assinar direto
    SET(pg, "n.acoes=9")
    pg.locator('#sec-tab-mesa').click() if pg.locator('#sec-tab-mesa').count() else None; pg.wait_for_timeout(400)
    ab = pg.locator('button').filter(has_text=re.compile(r'^\s*Responder'))
    if ab.count(): ab.first.click(); pg.wait_for_timeout(1200)
    nd = pg.locator('[data-crise-direto]').count()
    ok('Gaveta da crise oferece "Assinar" direto nas opções sem Congresso', nd >= 1, nd)
    cortes = pg.evaluate("()=>[...document.querySelectorAll('[data-pv-custo]')].map(e=>[e.dataset.pvCusto,e.innerText])")
    ok('Chip de custo respeita o sinal (corte não aparece como gasto)', all((c[0] == '-1') == c[1].startswith('corte') for c in cortes), cortes)
    pg.screenshot(path=OUT + '/crise_gaveta.png')
    if nd:
        a0 = G(pg, 'g.acoes'); l0 = G(pg, 'g.log.length')
        pg.locator('[data-crise-direto]').first.click(); pg.wait_for_timeout(1500)
        res = pg.locator('.modal-wrap').inner_text() if pg.locator('.modal-wrap').count() else ''
        ok('Assinar direto: abre o resultado já publicado e gasta 1 ação', G(pg, 'g.acoes') == a0 - 1 and ('Publicada' in res or 'PUBLICADA' in res.upper()), (a0, G(pg, 'g.acoes'), res[:120]))
        fecha_modais(pg)
    # pendências urgentes no botão
    SET(pg, "n.eventoOk=false")
    u = pg.evaluate("()=>{const b=document.querySelector('[data-enc-urg]');return b?[b.dataset.encUrg,b.title]:null}")
    ok('Botão Encerrar mês mostra pendências urgentes', u is not None, u)
    # Bastidores coerente
    pg.locator('#sec-tab-eu').click(); pg.wait_for_timeout(600)
    t = pg.locator('[data-gv=eu-resumo]').inner_text() if pg.locator('[data-gv=eu-resumo]').count() else ''
    ok('Resumo do Eu não diz mais "indisponível" para Bastidores', 'indisponível' not in t and 'só com personagem fictício' not in t, t[:200])
    pg.locator('#sec-tab-mesa').click(); pg.wait_for_timeout(500)
    ok('Aviso de último mandato na Mesa (personagem em 2º mandato)', pg.locator('[data-aviso-ultimo]').count() == 1)
    ok('0 erros de página', not errs, errs[:3])
    falhas = [n for c, n in checks if not c]
    print('RESUMO: %d/%d' % (len(checks) - len(falhas), len(checks)), '| falhas:', falhas)
    b.close()
