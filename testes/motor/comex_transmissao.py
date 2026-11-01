# Mede a transmissão de preços do Comércio exterior (contratos de compra, TEC zero, Conab, leilão, crédito) para o IPCA, a aprovação e os grupos.
# Compara 18 meses COM a ação e SEM ela (controle), em 6 sementes, com o mesmo ruído nos dois braços (parte de testes/../scratchpad/trigo/med3.py).
# uso: python3 testes/motor/run_sandbox.py testes/motor/comex_transmissao.py <pasta com index.html, fotos.json, logos.json> <saida.json> <porta>
# O mesmo script roda no index.html ANTES e DEPOIS da mudança: ações que ainda não existem aparecem como "na".
import sys, threading, functools, http.server, re, json
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT, PORT = sys.argv[1], sys.argv[2], int(sys.argv[3])
SEEDS = [11, 22, 33, 44, 55, 66, 77, 88, 99, 111, 122, 133]; H = 18
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
def click(pg, t, ms=500):
    pg.locator('button, [role=tab], a, summary, label').filter(has_text=t).first.click(timeout=8000); pg.wait_for_timeout(ms)
INJ = "window.__QV=()=>QV; window.__F=()=>({ensureIC,icContrata,icPrecoPedidoCompra,fimDoMes,aprovacao,IC_IMP,IC_BASE,icFlow,icMkDe,icTick, icTecZero: typeof icTecZero!=='undefined'?icTecZero:null, icConabCompra: typeof icConabCompra!=='undefined'?icConabCompra:null, icConabVende: typeof icConabVende!=='undefined'?icConabVende:null, icCreditoProdutor: typeof icCreditoProdutor!=='undefined'?icCreditoProdutor:null, icLeilaoImport: typeof icLeilaoImport!=='undefined'?icLeilaoImport:null});\nfunction analisaLegado(g, texto) {"
# cada cenário: setup roda no mês 1 (antes do primeiro fimDoMes); hook(g,F,m) roda antes de cada fimDoMes (m = 1..H)
C = lambda k, iso, mult=1, anos=2, desc=1.0: "const q=Math.max(F.IC_IMP['%s'].imp_usd_bi*.5,.05)*%s; const pr=F.icPrecoPedidoCompra(g,'%s','%s',%d,q)*%s; F.icContrata(g,{tipo:'compra',k:'%s',iso:'%s',qtd:q,preco:pr,anos:%d})" % (k, mult, k, iso, anos, desc, k, iso, anos)
NA = "if(!F.%s) return 'na'; "
CEN = [
    ('trigo', 'Contrato trigo (ARG), volume típico, 2 anos', C('trigo', 'ARG'), None),
    ('leite', 'Contrato leite em pó (ARG)', C('leite_po', 'ARG'), None),
    ('arroz', 'Contrato arroz (URY)', C('arroz_imp', 'URY'), None),
    ('eletro', 'Contrato eletrônicos (CHN)', C('eletronicos', 'CHN'), None),
    ('diesel', 'Contrato diesel (EUA)', C('diesel', 'USA'), None),
    ('medic', 'Contrato medicamentos (DEU)', C('medicamentos_imp', 'DEU'), None),
    ('potassio', 'Contrato potássio (CAN), volume típico', C('fert_potassio_imp', 'CAN'), None),
    ('potassio4', 'Contrato grande de potássio (CAN), 4x o volume e 15% abaixo do preço pedido', C('fert_potassio_imp', 'CAN', 4, 2, .85), None),
    ('diesel_caro', 'Diesel: choque de +10% no preço mundial por 6 meses', "g.__choque=['combustiveis',1.10,6]", None),
    ('tec_arroz', 'TEC zero do arroz por 12 meses', NA % 'icTecZero' + "F.icTecZero(g,'arroz',12)", None),
    ('conab_arroz', 'Conab vende arroz (já tinha 1 mês de consumo em estoque; vende 0,5 mês no mês 1)', NA % 'icConabVende' + "F.icConabVende(g,'arroz',.5)", "g.comex.abast=g.comex.abast||{}; g.comex.abast['arroz']={tec:null,conab:1,conabCusto:.47,ch:[],cred:[],leil:null}"),
    ('conab_compra_arroz', 'Conab compra arroz na safra (0,5 mês de consumo no mês 1)', NA % 'icConabCompra' + "F.icConabCompra(g,'arroz',.5)", None),
    ('leilao_arroz', 'Leilão de importação de emergência do arroz', NA % 'icLeilaoImport' + "F.icLeilaoImport(g,'arroz',1)", None),
    ('credito_arroz', 'Crédito ao produtor de arroz (Plano Safra extra)', NA % 'icCreditoProdutor' + "F.icCreditoProdutor(g,'arroz',1)", None),
]
SNAP = """(F,g)=>{ const gr={}; for(const k in g.groups) gr[k]=+g.groups[k].toFixed(3);
  const pd={}, ct={}, es={}; for(const mk in g.comex.fl){ pd[mk]=+g.comex.fl[mk].pdom.toFixed(5); const c=g.comex.cut[mk]||0; if(c>0.0005) ct[mk]=+c.toFixed(4); }
  return {ipca:g.eco.ipca, pib:g.eco.pib, des:g.eco.des, ap:F.aprovacao(g), mac:g.comex.mac.ipca, macAgro:g.comex.mac.agro, gr, rec:g.fiscal.receita, extra:g.fiscal.extra, pd, ct, sal:g.comex.tot.saldoAno}}"""
JS = """([cenId, setup, seed, arm, pre])=>{ const F=__F(); const base=__QV().gRef.current; const g=structuredClone(base); g.seed=seed; F.ensureIC(g); g.acoes=9; g.pes.energia=90; if(pre && F.icConabVende) (new Function('g','F',pre))(g,F);
  const snap=%s; let R={};
  if(arm==='trat'){ let r; try{ r=(new Function('g','F', setup+';'))(g,F); }catch(e){ return {err:String(e)} } if(r==='na') return {na:1}; }
  const serie=[snap(F,g)];
  for(let m=0;m<%d;m++){ const st=Math.random; let x=(seed*9301+m*49297)%%233280; Math.random=()=>{x=(x*9301+49297)%%233280; return x/233280};
    try{ if(arm==='trat'&&g.__choque&&m===0){ const [mk,f,n]=g.__choque; g.comex.idx[mk]=g.comex.idx[mk]*f; } F.fimDoMes(g) }catch(e){ serie.push({err:String(e)}); break } finally{ Math.random=st } serie.push(snap(F,g)); }
  return {serie}; }""" % (SNAP, H)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    src = open(ROOT + '/index.html', encoding='utf-8').read().replace('function analisaLegado(g, texto) {', INJ, 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='networkidle'); pg.wait_for_timeout(1500)
    for t in ["Presidente eleito", "Assumir o mandato", "3Personalidade", "Negociador", "Técnico", "Avançar"]: click(pg, t)
    for _ in range(40):
        bt = pg.locator('button').filter(has_text=re.compile(r'^\s*Escolher nome\s*$'))
        if bt.count() == 0: break
        bt.first.click(timeout=5000); pg.wait_for_timeout(250)
        pg.locator('button:not([disabled])').filter(has_text=re.compile(r'^\s*Escolher\s*$')).first.click(timeout=5000); pg.wait_for_timeout(250)
    click(pg, "Avançar"); click(pg, "Tomar posse", 1000)
    res = {'ctrl': {}, 'trat': {}}
    for sd in SEEDS:
        res['ctrl'][sd] = pg.evaluate(JS, ['ctrl', '', sd, 'ctrl', ''])
    for cid, label, setup, pre in CEN:
        res['trat'][cid] = {}
        for sd in SEEDS:
            r = pg.evaluate(JS, [cid, setup, sd, 'trat', pre or ''])
            if isinstance(r, dict) and ('na' in r or 'err' in r) and 'serie' not in r:
                r = {'na': 1} if r.get('na') or "'na'" in str(r) else r
            res['trat'][cid][sd] = r
            if 'na' in r or 'err' in r: break
        print(cid, 'na' if 'na' in r else ('ERR ' + r['err'] if 'err' in r else 'ok'), flush=True)
    json.dump({'res': res, 'errs': errs, 'cen': [(c[0], c[1]) for c in CEN], 'seeds': SEEDS}, open(OUT, 'w'))
    print('errs', errs[:3]); b.close()
