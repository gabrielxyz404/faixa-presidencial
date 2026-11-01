# Teste do lote B (motor v4.3): colisões do motor que viram dinheiro.
#  B1 plebiscito/referendo/consulta/debate/audiência/estudo sobre privatizar não vende a estatal;
#  B2 "zerando/sem" PIS/Cofins/CIDE é redução, não aumento;
#  B3 bases absurdas (maconha, floresta por família, botijão, luz zero, custeio, avião) e valor dito no texto;
#  B4 textos com 2-3 medidas listam todas as partes; coordenação "o Bolsa Família e o BPC";
#  e "sair da ONU", estado de defesa contra facção.
# uso: python3 run_sandbox.py motor_lote_b.py <pasta com index.html, fotos.json, logos.json> [porta]
import sys, threading, functools, http.server, json, re
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT = sys.argv[1]; PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8796
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
def click(pg, t):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(500)
# (frase, função de checagem sobre o resumo, descrição)
f = lambda r: r
CASOS = [
    # B1: consulta sobre privatizar não vende nada
    ("Convocar plebiscito sobre a privatização da Petrobras", lambda r: abs(r['once']) < 1 and r['inst'] in ('COM', 'PL', 'ADM', 'DEC'), 'plebiscito: sem receita única'),
    ("Fazer um referendo para decidir se privatiza a Eletrobras", lambda r: abs(r['once']) < 1, 'referendo: sem receita única'),
    ("Abrir consulta pública sobre a venda dos Correios", lambda r: abs(r['once']) < 1, 'consulta pública: sem receita única'),
    ("Realizar audiência pública sobre a privatização do Banco do Brasil", lambda r: abs(r['once']) < 1, 'audiência pública: sem receita única'),
    ("Estudar a privatização da Caixa", lambda r: abs(r['once']) < 1, 'estudo: sem receita única'),
    ("Vender os Correios", lambda r: r['once'] > 0, 'verbo de venda direto continua vendendo'),
    ("Privatizar a Eletrobras", lambda r: r['once'] > 10, 'privatizar continua vendendo'),
    ("acaba com audiencia de custodia q so solta bandido", lambda r: 'sem executar' not in r['topic'], 'audiência de custódia não é consulta'),
    ("Exigir estudo de impacto ambiental antes da licença", lambda r: 'sem executar' not in r['topic'], 'estudo de impacto é exigência, não consulta'),
    # B2: zerar/sem tributo é redução
    ("Baixar o preço da gasolina zerando PIS/Cofins e CIDE", lambda r: r['rev'] < -5 and not re.search(r'aumento do pis', r['topic'], re.I), 'zerando PIS/Cofins reduz receita'),
    ("Baixar o preço do diesel sem PIS/Cofins", lambda r: r['rev'] < -5, 'sem PIS/Cofins reduz receita'),
    ("Zerar a CIDE do diesel", lambda r: r['rev'] < -5, 'zerar a CIDE reduz receita'),
    # B3: bases
    ("Legalizar a maconha para uso recreativo e taxar em 30%", lambda r: 2 <= r['rev'] <= 20, 'maconha: teto de mercado'),
    ("Legalizar o cassino e taxar em 20%", lambda r: 0 <= r['rev'] <= 30, 'cassino: teto de mercado'),
    ("Pagar R$ 500 por mês para cada família que preservar a floresta em pé na Amazônia", lambda r: 1 <= r['cost'] <= 25, 'floresta por família: Amazônia Legal'),
    ("Tabelar o preço do botijão de gás em R$ 80", lambda r: 0 <= r['cost'] <= 30, 'botijão: preço-alvo, não acréscimo'),
    ("Mandar a conta de luz pra zero pra quem ganha até um salário mínimo", lambda r: 2 <= r['cost'] <= 20, 'luz zero: o salário mínimo é o público'),
    ("Instalar painéis solares em 500 mil casas de baixa renda com R$ 5 bilhões", lambda r: 4 <= r['cost'] <= 6, 'valor dito no texto vale mais que o piso por quantidade'),
    ("Em vez de aumentar impostos, cortar 10% do custeio da máquina", lambda r: -30 <= r['cost'] <= -4, 'custeio: base de custeio, não todos os gastos'),
    ("Vender o avião presidencial", lambda r: 0 <= r['once'] <= 2, 'avião presidencial: ativo pequeno'),
    ("Isentar o IR de quem ganha até dois salários mínimos", lambda r: abs(r['rev']) < 1, 'isenção até 2 SM já está na Lei 15.270'),
    # B4: várias medidas
    ("Vamos criar 1 milhão de vagas em creches, dobrar o Pé-de-Meia e isentar de IR quem ganha até R$ 7 mil", lambda r: re.search(r'crech', r['topic'], re.I) and re.search(r'p.-de-meia', r['topic'], re.I) and re.search(r'imposto de renda|\bIR\b', r['topic'], re.I) and -45 <= r['rev'] <= -8, 'três medidas no tópico e IR só acima de 5 mil'),
    ("Aumentar em R$ 50 o Bolsa Família e o BPC", lambda r: re.search(r'bolsa fam', r['topic'], re.I) and re.search(r'bpc', r['topic'], re.I), 'Bolsa Família e BPC'),
    ("Zerar a conta de luz de quem recebe o Bolsa Família", lambda r: not re.search(r'fim do bolsa', r['topic'], re.I) and r['cost'] < 30, 'Bolsa Família como público, não como alvo'),
    # demais erros graves
    ("Tirar o Brasil da ONU", lambda r: re.search(r'onu', r['topic'], re.I) and not re.search(r'oriente', r['topic'], re.I), 'sair da ONU'),
    ("Sair da OMS", lambda r: re.search(r'oms', r['topic'], re.I), 'sair da OMS'),
    ("Decretar estado de defesa em São Paulo para combater o PCC", lambda r: re.search(r'estado de defesa', r['topic'], re.I) and r['cf'] in ('controverso', 'inconstitucional'), 'estado de defesa contra facção é controverso'),
]
res = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    errs = []
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', 'window.__AL=analisaLocal; window.__M=MOTOR;\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='networkidle'); pg.wait_for_timeout(1200)
    for t in ["Presidente eleito", "Assumir o mandato", "3Personalidade", "Negociador", "Técnico", "Avançar"]: click(pg, t)
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count() == 0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(250)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(250)
    click(pg, "Avançar"); click(pg, "Tomar posse"); pg.wait_for_timeout(800)
    pg.evaluate("()=>{const o=__M.analisar; __M.analisar=function(g){window.__g=g; return o.apply(this,arguments)}}")
    pg.locator('#caixa').scroll_into_view_if_needed(); pg.fill('#caixa', 'Acabar com a escala 6x1')
    click(pg, 'Assinar e enviar'); pg.wait_for_timeout(1500)
    out = pg.evaluate("""(PH)=>PH.map(t=>{try{const p=__AL(window.__g,t); return {t, topic:p.topic||'', inst:p.inst, cost:p.cost||0, rev:p.rev||0, once:Math.max(p.once||0,p.extra||0), cf:(p.stf||{}).nivel}}catch(e){return {t, err:String(e)}}})""", [c[0] for c in CASOS])
    b.close()
nf = 0
for (t, chk, desc), r in zip(CASOS, out):
    try: ok = (not r.get('err')) and bool(chk(r))
    except Exception as e: ok = False
    nf += (not ok)
    print(('OK    ' if ok else 'FALHA ') + desc + ' | ' + t[:70] + ('' if ok else ' -> ' + json.dumps({k: r.get(k) for k in ('topic', 'inst', 'cost', 'rev', 'once', 'cf', 'err')}, ensure_ascii=False)[:260]))
print('erros de página:', errs or 'nenhum')
print('RESULTADO: %d/%d' % (len(CASOS) - nf, len(CASOS)))
sys.exit(1 if nf or errs else 0)
