import sys, threading, functools, http.server, json, re
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT=sys.argv[1]; OUT=sys.argv[2]
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8781), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
def click(pg,t):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(600)
def start(pg):
    pg.goto('http://127.0.0.1:8781/index.html', wait_until='networkidle'); pg.wait_for_timeout(1500)
    for t in ["Presidente eleito","Assumir o mandato","3Personalidade","Negociador","Técnico","Avançar"]: click(pg,t)
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count()==0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(300)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(300)
    click(pg,"Avançar"); click(pg,"Tomar posse"); pg.wait_for_timeout(1000)
PROPS = ["Isentar do imposto de renda quem ganha até R$ 6 mil","Acabar com a escala 6x1","Reduzir a jornada para 36 horas semanais","Aumentar a multa do FGTS para 50%","Criar o 14º salário para aposentados","Instituir pena de morte para traficantes","Reduzir a maioridade penal para 16 anos","Fechar o Congresso por 6 meses","Decretar estado de sítio por causa da violência no Rio","Criar imposto sobre grandes fortunas de 2% acima de R$ 50 milhões","Zerar o IPI de carros elétricos","Privatizar a Petrobras","Aumentar o Bolsa Família para R$ 800","Congelar o preço da gasolina","Proibir o aborto em todos os casos","Regulamentar o trabalho por aplicativo com salário mínimo por hora","Dar autonomia total ao Banco Central e mandato fixo","Criar uma estatal de terras raras","Cortar 10% dos salários dos servidores federais","Reduzir a idade mínima de aposentadoria para 60 anos para homens","Mandar a Força Nacional para a Bahia","Taxar dividendos em 15%","Acabar com a reeleição para presidente","Ampliar a licença-paternidade para 60 dias","Cobrar mensalidade nas universidades federais"]
res=[]
def acoes(pg):
    return pg.evaluate("()=>{const m=document.body.innerText.match(/(\\d) de 5 ações/);return m?m[1]:'?'}")
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1440,'height':900})
    start(pg)
    for i,t in enumerate(PROPS):
        try:
            for _ in range(3): pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
            a0=acoes(pg)
            pg.locator('#caixa').scroll_into_view_if_needed(); pg.fill('#caixa',t)
            click(pg,'Assinar e enviar'); pg.wait_for_timeout(2500)
            txt=pg.evaluate("()=>{const e=document.querySelector('.modal-wrap');return e?e.innerText:'NO MODAL: '+document.body.innerText.slice(0,500)}")
            # expand base juridica
            try:
                pg.locator('.modal-wrap').get_by_text(re.compile('Ver base jurídica')).first.click(timeout=1500); pg.wait_for_timeout(300)
                txt=pg.evaluate("()=>document.querySelector('.modal-wrap').innerText")
            except Exception: pass
            btns=pg.evaluate("()=>[...document.querySelectorAll('.modal-wrap button')].map(b=>b.innerText.trim())")
            res.append({'i':i+1,'t':t,'a0':a0,'txt':txt,'btns':btns})
            print(i+1,t,a0,len(txt))
            # desistir
            try: pg.locator('.modal-wrap button').filter(has_text='Desistir').first.click(timeout=2000)
            except Exception: pg.keyboard.press('Escape')
            pg.wait_for_timeout(500)
            res[-1]['a1']=acoes(pg); print('  acoes after',res[-1]['a1'])
        except Exception as e:
            print(i+1,'ERR',str(e)[:200]); res.append({'i':i+1,'t':t,'err':str(e)[:200]})
        json.dump(res,open(OUT+'/raw.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
    b.close()

