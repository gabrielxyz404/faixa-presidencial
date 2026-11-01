# Varre todos os botões/cartões de programa do jogo (abas do País, Segurança, Trabalho, Mundo, Comércio exterior), lê cada texto com o motor
# local (analisaLocal, só leitura) e grava a tabela testes/motor/programas_probe.md (aba, botão, texto, tema lido, custo, instrumento, situação).
# uso: python3 run_sandbox.py programas_probe.py <pasta com index.html> <saida.md> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8897
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
        try: pg.locator('.modal-wrap button').filter(has_text=re.compile(r'^(Fechar|Continuar|OK|Entendi|Seguir|Próximo mês|Voltar à Mesa|Arquivar|Cancelar|Voltar)')).first.click(timeout=1200)
        except Exception: pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
def secao(pg, nome): pg.locator('#sec-tab-' + nome.lower().replace('í', 'i')).click(timeout=6000); pg.wait_for_timeout(500)
def chip(pg, nome): pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*' + nome + r'\s*$')).first.click(timeout=6000); pg.wait_for_timeout(600)

# situação de cada programa (decisão desta revisão). Chave: (aba, botão). 'ok' = já era novo; 'trocado' = o original já existia em 2026 e foi trocado por medida nova;
# 'ajustado' = a medida já era nova, mas o texto foi reescrito para o motor ler tema, custo e instrumento certos.
SIT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programas_situacao.json'), encoding='utf-8')) if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programas_situacao.json')) else {}

LEIA = """(PH)=>PH.map(r=>{try{const g=__QV().gRef.current; const p=__AL(g,r.t); const A=p._A||{}; const nv=A.normaVigente||{};
  return Object.assign({}, r, {topic:p.topic, inst:p.inst, cost:p.cost, rev:p.rev, once:p.once, pasta:p.pastaNome, nvx:!!nv.exato, jv:!!A.jaVigente||(A.items||[]).some(i=>i.jaVigente), red:!!A.redundante, vago:!!(p.qualidade||{}).vago, absurdo:!!p.absurdo,
    its:((A.items||[]).map(i=>i.o.id+(i.jaVigente?'!jv':'')).slice(0,5)), nv:nv.id||null, instD:p.instDetalhe||null})}catch(e){return Object.assign({}, r, {err:String(e)})}})"""
COLETA = """()=>{const P=__PROGS(); const g=__QV().gRef.current; const R=[];
  const add=(aba,l,t,extra)=>R.push(Object.assign({aba,l,t},extra||{}));
  for(const a of P.SAU_PROG){add('Saúde',a.l,a.t); if(a.p2)add('Saúde',a.l+' (próximo passo: '+a.p2.l+')',a.p2.t)}
  for(const a of P.EDU_PROG){add('Educação',a.l,a.t); if(a.p2)add('Educação',a.l+' (próximo passo: '+a.p2.l+')',a.p2.t)}
  for(const G of P.INFRA_GRUPOS) for(const a of G.itens){add('Infraestrutura e transportes',a.l,a.t); if(a.p2)add('Infraestrutura e transportes',a.l+' (próximo passo: '+a.p2.l+')',a.p2.t)}
  for(const a of P.JUS_GOV){add('Justiça',a.l,a.t); if(a.p2)add('Justiça',a.l+' (próximo passo: '+a.p2.l+')',a.p2.t)}
  for(const L of P.TB_LEV){let vs=[]; try{vs=L.vals(g)||[]}catch(e){}; for(const x of vs){let t=''; try{t=L.texto(g,x.v)}catch(e){continue}; add('Trabalho',L.nome+': '+x.rot,t)}}
  for(const x of P.IC_TLC) add('Mundo · Comércio exterior','Tratado '+x.bloco,x.t);
  // ideias dos ministros (Poder, Governo): cada modelo é montado 4 vezes (sorteios diferentes) e validado como o jogo valida
  for(const pk of Object.keys(P.MIN_BANCO)){ const pe=P.minPessoa(g,pk); for(const tpl of P.MIN_BANCO[pk]){ let ok=0, txt=null;
    for(let sal=0; sal<4; sal++){ try{ const m=P.minMonta(g,pk,tpl,pe,'alta',String(sal),false); const v=P.minValida(g,pk,tpl,m,'alta'); if(v.ok) ok++; if(txt==null) txt=m.texto }catch(e){} }
    if(txt!=null) add('Poder · Governo (ideias dos ministros)', pk+': '+tpl.k, txt, {minOk: ok}) } }
  return R}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    errs = []
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    src = src.replace('function analisaLegado(g, texto) {', 'window.__QV = () => QV; window.__AL = analisaLocal; window.__PROGS = () => ({ SAU_PROG, EDU_PROG, INFRA_GRUPOS, JUS_GOV, TB_LEV, IC_TLC, MIN_BANCO, minPessoa, minMonta, minValida });\nfunction analisaLegado(g, texto) {', 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg); secao(pg, 'País')
    rows = pg.evaluate(COLETA)
    # botões que só existem na tela: Segurança (nacionais; operações já são atos pontuais por UF) e agenda externa do Mundo
    chip(pg, 'Segurança')
    for e in pg.evaluate("()=>[...document.querySelectorAll('[data-pais=seguranca] button[data-prog], [data-pais=seguranca] [data-prog]')].map(b=>({l:b.querySelector('.mx-act-h span:nth-child(2)').innerText.trim(), t:b.querySelector('.mx-txt').innerText.trim()}))"):
        rows.append({'aba': 'Segurança', 'l': e['l'], 't': e['t']})
    secao(pg, 'Mundo'); pg.wait_for_timeout(600)
    for e in pg.evaluate("()=>[...document.querySelectorAll('[data-secao-mundo=agenda] .mx-card')].map(c=>({l:c.querySelector('.mx-t').innerText.trim(), t:c.querySelector('.mx-txt').innerText.trim()}))"):
        rows.append({'aba': 'Mundo · Panorama', 'l': e['l'], 't': e['t']})
    res = pg.evaluate(LEIA, rows)
    b.close()
def md(s): return str(s).replace('|', '/').replace('\n', ' ')
def custo(r):
    if r.get('err'): return 'erro'
    c, rv = r.get('cost') or 0, r.get('rev') or 0
    if rv: return 'renúncia R$ %s bi/ano' % ('%.1f' % abs(rv)).replace('.', ',')
    if c: return ('R$ %s bi' % ('%.1f' % abs(c)).replace('.', ',')) + ('' if r.get('once') else '/ano') if c > 0 else 'economia R$ %s bi' % ('%.1f' % abs(c)).replace('.', ',')
    return 'sem custo'
linhas = ['# Programas lidos pelo motor', '',
          'Gerado por `testes/motor/programas_probe.py` (analisaLocal, só leitura). Situação: **ok** = já era medida nova; **trocado** = o original já existia em 2026 (lei, decreto, emenda ou programa em vigor) e foi trocado por medida nova, concreta e quantificada; **ajustado** = a medida era nova, mas o texto foi reescrito até o motor ler tema, custo e instrumento certos.', '',
          'Escopo: cartões das abas Saúde, Educação, Infraestrutura e transportes, Justiça e Segurança (com o "próximo passo" de cada um), alavancas de Trabalho (todas as opções que o estado do jogo oferece), tratados de Comércio exterior, agenda do Mundo e o banco de ideias dos ministros (Poder, Governo; cada modelo é montado 4 vezes e validado como o jogo valida). Ficam de fora os textos montados a partir de escolhas do jogador (Indústria: produto, ação e valor; Orçamento por área; tratados negociados) e as respostas a crises e protestos.', '',
          '"Custo" é o que o motor lê (inclui a base do objeto lido, por isso pode passar do valor pedido no texto). "Tema lido" é o texto de `topic` que o motor mostra no parecer.', '',
          '| Aba | Botão | Texto | Tema lido | Custo | Instrumento | Situação |', '|---|---|---|---|---|---|---|']
n_ruim = 0; n_min = 0
for r in res:
    chave = r['l'].split(': ')[0] if r['aba'] == 'Trabalho' else r['l'].split(' (próximo passo')[0]
    sit = SIT.get(r['aba'] + '|' + chave, 'ok')
    if r.get('minOk') is not None:
        sit = SIT.get(r['aba'] + '|' + r['l'], 'ok') + (' [válida em %d de 4 sorteios]' % r['minOk'])
        if r['minOk'] < 4: n_min += 1
    flag = ''
    if r.get('err') or r.get('nvx') or r.get('jv') or r.get('red') or r.get('vago') or r.get('absurdo'): flag = ' **ALERTA** ' + ','.join(k for k in ('nvx', 'jv', 'red', 'vago', 'absurdo', 'err') if r.get(k)); n_ruim += 1
    linhas.append('| %s | %s | %s | %s | %s | %s | %s%s |' % (md(r['aba']), md(r['l']), md(r['t']), md(r.get('topic') or '-'), md(custo(r)), md(r.get('inst') or '-'), md(sit), flag))
open(OUT, 'w', encoding='utf-8').write('\n'.join(linhas) + '\n')
print('%d linhas, %d com alerta, %d ideias de ministro que falham em algum sorteio, erros de página: %s' % (len(res), n_ruim, n_min, errs[:3]))
