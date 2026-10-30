# Equivalência do motor entre duas versões (v3.8): 25 propostas, com Math.random semeado, mesmo estado inicial:
# leitura (analisaLocal), placar projetado (projetaVotos), execução (executaProposta) e 6 meses (fimDoMes). Imprime o hash do resultado.
# O v3.8 acrescenta famosos no X (xRegistra); use FAM_OFF=1 para desligar só essa parte e comparar com o v3.7 (devem ser idênticos).
# uso: [FAM_OFF=1] python3 run_sandbox.py eq_motor.py <pasta com index.html> <saida.json> [porta]
import sys, threading, functools, http.server, json, re, os, hashlib
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8881
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
def click(pg, t):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(400)
PROPS = ["Isentar do imposto de renda quem ganha até R$ 6 mil", "Acabar com a escala 6x1", "Reduzir a jornada para 36 horas semanais", "Aumentar a multa do FGTS para 50%", "Criar o 14º salário para aposentados", "Instituir pena de morte para traficantes", "Reduzir a maioridade penal para 16 anos", "Fechar o Congresso por 6 meses", "Decretar estado de sítio por causa da violência no Rio", "Criar imposto sobre grandes fortunas de 2% acima de R$ 50 milhões", "Zerar o IPI de carros elétricos", "Privatizar a Petrobras", "Aumentar o Bolsa Família para R$ 800", "Congelar o preço da gasolina", "Proibir o aborto em todos os casos", "Regulamentar o trabalho por aplicativo com salário mínimo por hora", "Dar autonomia total ao Banco Central e mandato fixo", "Criar uma estatal de terras raras", "Cortar 10% dos salários dos servidores federais", "Reduzir a idade mínima de aposentadoria para 60 anos para homens", "Mandar a Força Nacional para a Bahia", "Taxar dividendos em 15%", "Acabar com a reeleição para presidente", "Ampliar a licença-paternidade para 60 dias", "Cobrar mensalidade nas universidades federais"]
JS = """(args)=>{const [PROPS,off]=args,E=window.__E(),out=[];
  if(off)E.FAMOSOS.splice(0);
  const seed=(n)=>{let a=n;Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}};
  const g0=window.__g0;
  for(let i=0;i<PROPS.length;i++){seed(1000+i);const g=structuredClone(g0);g.seed=777;g.acoes=5;
    try{const p=E.analisaLocal(g,PROPS[i]);const v=E.projetaVotos(g,p);const r=E.executaProposta(g,p,'aprovada');for(let m=0;m<6;m++)E.fimDoMes(g);
      out.push({t:PROPS[i],famlen:E.FAMOSOS.length,fam:(g.x&&g.x.fam?g.x.fam.posts.length:0),topic:p.topic,cost:p.cost,rev:p.rev,cf:p.stf.nivel,totC:v.totC,totS:v.totS,ap:+E.aprovacao(g).toFixed(3),prim:+E.primario(g).toFixed(2),g:Object.keys(g.groups).map(k=>k+':'+g.groups[k].toFixed(2)).join(',')})}
    catch(e){out.push({t:PROPS[i],err:String(e).slice(0,120)})}}
  return out}"""
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', "window.__QV = () => QV; window.__E = () => ({ analisaLocal, projetaVotos, executaProposta, fimDoMes, aprovacao, primario, FAMOSOS: (typeof FAMOSOS !== 'undefined' ? FAMOSOS : []) });\nfunction analisaLegado(g, texto) {", 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    pg.add_init_script("(()=>{let a=424242;Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()")
    pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='networkidle'); pg.wait_for_timeout(1200)
    for t in ["Presidente eleito", "Assumir o mandato", "3Personalidade", "Negociador", "Técnico", "Avançar"]: click(pg, t)
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count() == 0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(200)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(200)
    click(pg, "Avançar"); click(pg, "Tomar posse"); pg.wait_for_timeout(800)
    pg.evaluate("()=>{window.__g0=structuredClone(__QV().gRef.current)}")
    print('estado inicial:', pg.evaluate("()=>{const g=window.__g0;return JSON.stringify({seed:g.seed,mes:g.mes,ap:Object.values(g.groups).reduce((a,b)=>a+b,0).toFixed(3),pib:g.eco.pib,rel:Object.values(g.parties).map(p=>p.rel).reduce((a,b)=>a+b,0).toFixed(3)})}"))
    res = pg.evaluate(JS, [PROPS, bool(os.environ.get('FAM_OFF'))])
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    h = hashlib.sha1(json.dumps(res, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]
    print('propostas:', len(res), '| com erro:', sum(1 for r in res if 'err' in r), '| hash do resultado:', h, '| erros de página:', errs[:3] or 'nenhum')
    b.close()
