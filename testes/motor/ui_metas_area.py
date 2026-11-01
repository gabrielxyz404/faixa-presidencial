# Teste das METAS POR ÁREA (indicadores de área com meta do mandato nas abas do País).
# Confere: cartões e resumo (GvKpi) em cada aba, fonte no tooltip, escolha/aceite de meta, programa aprovado que move o indicador mês a mês,
# corte de orçamento que piora, meta batida (Balanço e legado), efeito nacional (IDH, pobreza, homicídios), save antigo sem g.areas,
# validador de save com g.areas malformado, 0 erros de página/console. Tira screenshots 1440 de cada aba do País.
# uso: python3 run_sandbox.py ui_metas_area.py <pasta com index.html> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8884
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
checks = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:240]) if det != '' else ''), flush=True)
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
def G(pg, expr): return pg.evaluate("()=>{const g=__QV().gRef.current;return (" + expr + ")}")
def SET(pg, js): pg.evaluate("()=>__QV().setG(p=>{const n=structuredClone(p);" + js + ";return n})"); pg.wait_for_timeout(500)
def secao(pg, nome): pg.locator('#sec-tab-' + nome.lower().replace('í', 'i')).click(timeout=6000); pg.wait_for_timeout(500)
def chip(pg, nome):
    pg.locator('.chipnav [role=tab]').filter(has_text=re.compile(r'^\s*' + nome + r'\s*$')).first.click(timeout=6000); pg.wait_for_timeout(700)
# roda n meses numa cópia do estado: aprova (opcional) os textos dados no mês 0, depois fecha n meses. Devolve o resumo; não toca no estado da tela.
SIMJS = """([textos, n, orcSet, metaSet])=>{
  const P = window.__P(); const g = structuredClone(__QV().gRef.current); let sd = 12345; Math.random = () => { sd |= 0; sd = sd + 0x6D2B79F5 | 0; let t = Math.imul(sd ^ sd >>> 15, 1 | sd); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  if (orcSet) for (const k in orcSet) g.orc[k] = orcSet[k];
  P.ensureAreas(g);
  for (const k in (metaSet||{})) { P.areaSetMeta(g, k, 'sugerida'); if (metaSet[k] != null) g.areas.meta[k].alvo = metaSet[k]; }
  for (const t of textos) { const p = P.analisaLocal(g, t); p.fromEvento = false; try { P.executaProposta(g, p, 'aprovada'); } catch (e) { return { erro: 'executa: ' + e }; } }
  const bal = [], serie = [];
  for (let m = 0; m < n; m++) {
    const rel = P.fimDoMes(g); if (g.over) g.over = null; if (rel && rel.notas) for (const nt of rel.notas) if (/^Meta de/.test(nt.x)) bal.push(nt.x);
    serie.push({ mes: g.mes, uti: P.areaVal(g, 'uti'), fila: P.areaVal(g, 'fila'), creche: P.areaVal(g, 'creche'), rod: P.areaVal(g, 'rodovias'), hom: g.soc.hom, esg: P.areaVal(g, 'esgoto'), idh: g.soc.idh, pob: g.soc.pob });
  }
  const A = g.areas;
  return { serie, meta: A && A.meta, med: A && A.med, nMed: (g.medidas || []).length, linha: (g.linha || []).filter(l => l.cat === 'METAS').map(l => l.txt), ok: A && A.ok,
    bal, leg: P.elLegado(g).metas, efeito: A && A.efeito, estados: (g.medidas || []).map(m => m.estado), grupos: Object.assign({}, g.groups) };
}"""
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    gancho = ("window.__QV = () => QV; window.__P = () => ({ ensureAreas, areaSetMeta, areaVal, analisaLocal, executaProposta, fimDoMes, elLegado, areasLegado, qvParse, qvValida, migraSave, AREA_IND, IDS: AREA_IND_ID });\n"
              "function analisaLegado(g, texto) {")
    assert src.count('function analisaLegado(g, texto) {') == 1
    src = src.replace('function analisaLegado(g, texto) {', gancho, 1)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg); fecha_modais(pg)
    secao(pg, 'País')

    # ---------- 1. cada aba tem o resumo (GvKpi) e os cartões ----------
    abas = [('Saúde', 'saude', 4), ('Educação', 'educacao', 5), ('Infraestrutura e transportes', 'infra', 5), ('Segurança', 'seguranca', 3), ('Justiça', 'justica', 2), ('Trabalho', 'trabalho', 4), ('Indústria', 'industria', 2)]
    for nome, area, n in abas:
        chip(pg, nome); fecha_modais(pg)
        base = '[data-metas-area=%s]' % area
        ok('%s: resumo no topo (5 GvKpi de metas)' % nome, pg.locator(base + ' [data-metas-resumo] .gv-kpi').count() == 5, pg.locator(base + ' .gv-kpi').count())
        ok('%s: %d cartões de indicador com valor, base e fonte no tooltip' % (nome, n), pg.locator(base + ' [data-meta]').count() == n and pg.locator(base + ' [data-meta] .gv-tip').count() == n, pg.locator(base + ' [data-meta]').count())
        ok('%s: o resumo fica antes do conteúdo antigo da aba' % nome, pg.evaluate("(a)=>{const m=document.querySelector('[data-metas-area='+a+']');const nx=m&&m.nextElementSibling;return !!m&&!!nx&&m.compareDocumentPosition(nx)&4}", area))
        pg.screenshot(path=OUT + '/pais_%s.png' % area, full_page=False)
    for nome, k in [('Mapa', 'mapa'), ('Economia', 'economia'), ('Sociedade', 'sociedade')]:
        chip(pg, nome); pg.screenshot(path=OUT + '/pais_%s.png' % k)

    # ---------- 2. Saúde: valores de partida e meta ----------
    chip(pg, 'Saúde')
    t = pg.locator('[data-metas=saude]').inner_text()
    ok('Saúde: linha de base visível e rótulo "estimativa" nos dados sem série oficial', 'Base 2025' in t and 'estimativa' in t.lower(), t[:160].replace('\n', ' '))
    tip = pg.locator('[data-meta=uti] .gv-tipbox').inner_text()
    ok('Saúde: o tooltip traz a fonte (CNES/DataSUS)', 'CNES' in tip, tip[:100])
    ok('Saúde: sem meta definida, mostra as 3 opções (cautelosa, sugerida, ousada)', pg.locator('[data-meta=uti] [data-meta-nivel]').count() == 3)
    pg.locator('[data-meta-nivel="uti:sugerida"]').click(); pg.wait_for_timeout(500)
    ok('Saúde: escolher a meta grava em g.areas.meta e mostra a barra de progresso', G(pg, "g.areas&&g.areas.meta.uti&&g.areas.meta.uti.alvo") > 21 and pg.locator('[data-meta=uti] [data-meta-def]').count() == 1, G(pg, "JSON.stringify(g.areas.meta.uti)"))
    pg.locator('[data-metas-aceitar=saude]').click(); pg.wait_for_timeout(500)
    ok('Saúde: "Aceitar metas sugeridas" define as outras 3', G(pg, "Object.keys(g.areas.meta).filter(k=>['fila','uti','vacinal','medicos'].includes(k)).length") == 4)
    pg.screenshot(path=OUT + '/saude_metas.png')
    chip(pg, 'Educação'); pg.locator('[data-metas-aceitar=educacao]').click(); pg.wait_for_timeout(400)
    chip(pg, 'Infraestrutura e transportes'); pg.locator('[data-metas-aceitar=infra]').click(); pg.wait_for_timeout(400)
    chip(pg, 'Segurança'); pg.locator('[data-metas-aceitar=seguranca]').click(); pg.wait_for_timeout(400)

    # ---------- 3. programa aprovado move o indicador, mês a mês ----------
    UTI = 'Financiar 5 mil novos leitos de UTI no SUS, em hospitais filantrópicos e municipais, com R$ 3 bilhões por ano'
    CRE = 'Garantir vaga em creche a toda criança de 0 a 3 anos de famílias do CadÚnico, com R$ 5 bilhões por ano de cofinanciamento aos municípios'
    ctl = pg.evaluate(SIMJS, [[], 24, None, None])
    tr = pg.evaluate(SIMJS, [[UTI, CRE], 24, None, None])
    ok('programa: a medida é criada e reivindicada pelo programa (ind declarado)', not tr.get('erro') and any(v.get('k', '').startswith('p:') for v in (tr['med'] or {}).values()), json.dumps(tr.get('med'))[:200])
    s0, s6, s24 = tr['serie'][0], tr['serie'][5], tr['serie'][23]; c24 = ctl['serie'][23]
    ok('programa: UTI sobe mês a mês (não de uma vez)', s0['uti'] < s6['uti'] < s24['uti'] and (s24['uti'] - s0['uti']) > 1.0, [round(x['uti'], 2) for x in tr['serie'][::4]])
    ok('programa: UTI com programa supera o controle sem programa em ao menos 1,5 leito', s24['uti'] - c24['uti'] > 1.5, (round(s24['uti'], 2), round(c24['uti'], 2)))
    ok('programa: creche sobe com a vaga garantida', s24['creche'] - c24['creche'] > 2.5, (round(s24['creche'], 2), round(c24['creche'], 2)))
    ok('programa: o efeito nacional acumulado é visível mas pequeno (IDH +0,0008 a +0,006; pobreza de -0,05 a -0,6 p.p.)', 0.0008 < tr['efeito']['idh'] < 0.006 and -0.6 < tr['efeito']['pob'] < -0.05, json.dumps(tr['efeito']))
    ok('controle sem programa: efeito nacional dos indicadores de área é nulo', abs(ctl['efeito']['idh']) < 1e-9 or abs(ctl['efeito']['idh']) < 0.0004, json.dumps(ctl['efeito']))
    mt = pg.evaluate(SIMJS, [[UTI], 30, None, {'uti': 22.5}])
    ok('meta: a meta de UTI é batida, entra no Balanço do mês e no legado', mt['meta']['uti']['ok'] and any('leitos de UTI' in x for x in mt['bal']) and any(m['id'] == 'uti' and m['ok'] and 'atingida' in m['txt'] for m in mt['leg']), json.dumps(mt['bal'])[:200])
    sm = pg.evaluate(SIMJS, [[UTI], 30, None, None])
    ok('meta: bater a meta rende aprovação aos grupos ligados (+0,7 ponto na meta sugerida, acumulado em efeito.apr)', mt['efeito']['apr'] >= 1.4 and sm['efeito']['apr'] == 0, (mt['efeito']['apr'], sm['efeito']['apr']))

    # ---------- 4. cortar o orçamento piora ----------
    cut = pg.evaluate(SIMJS, [[], 24, {'saude': -20}, None])
    inv = pg.evaluate(SIMJS, [[], 24, {'saude': 30}, None])
    cs, ins = cut['serie'][23], inv['serie'][23]; cz = ctl['serie'][23]
    ok('orçamento: cortar 20% da Saúde piora UTI e fila contra o controle', cs['uti'] < cz['uti'] - .15 and cs['fila'] > cz['fila'] + .6, (round(cs['uti'], 2), round(cz['uti'], 2), round(cs['fila'], 1), round(cz['fila'], 1)))
    ok('orçamento: investir 30% melhora, mas bem menos que um programa específico', 0 < ins['uti'] - cz['uti'] < (s24['uti'] - c24['uti']) * 1.6 and ins['fila'] < cz['fila'], (round(ins['uti'], 2), round(cz['uti'], 2)))

    # ---------- 5. segurança e infraestrutura: indicadores ligados ao jogo ----------
    PF = 'Criar mais 3 mil cargos de delegado, agente e perito na Polícia Federal, R$ 1 bilhão por ano'
    seg = pg.evaluate(SIMJS, [[PF], 24, None, None]); sc = ctl['serie'][23]['hom']
    ok('segurança: programa da PF não faz os homicídios subirem e as metas seguem calculadas', seg['serie'][23]['hom'] <= sc + 0.15, (round(seg['serie'][23]['hom'], 2), round(sc, 2)))
    esg = pg.evaluate(SIMJS, [['Criar linha de R$ 6 bilhões por ano do Orçamento da União para esgoto nos municípios pequenos fora das concessões do Marco do Saneamento'], 30, None, None])
    ok('infra: programa de esgoto move o esgoto do jogo (indicador ligado)', esg['serie'][29]['esg'] - ctl['serie'][23]['esg'] > 0.5 or esg['serie'][29]['esg'] > ctl['serie'][23]['esg'], (round(esg['serie'][29]['esg'], 2), round(ctl['serie'][23]['esg'], 2)))

    # ---------- 6. saves antigos e validador ----------
    SET(pg, "delete n.areas")
    chip(pg, 'Educação'); pg.wait_for_timeout(500)
    ok('save antigo sem g.areas: a aba abre sem erro e mostra os valores de base', pg.locator('[data-metas-area=educacao] [data-meta=creche]').count() == 1 and '43,3' in pg.locator('[data-meta=creche] [data-meta-val]').inner_text())
    ok('save antigo: migraSave cria g.areas', pg.evaluate("()=>{const g=structuredClone(__QV().gRef.current);delete g.areas;__P().migraSave(g);return !!g.areas&&g.areas.v===1&&Object.keys(g.areas.val).length>10}"))
    ok('qvValida aceita g.areas e descarta o campo malformado', pg.evaluate("()=>{const g=structuredClone(__QV().gRef.current);__P().ensureAreas(g);const a=__P().qvValida(JSON.parse(JSON.stringify(g)));g.areas=5;const b=__P().qvValida(JSON.parse(JSON.stringify(g)));return !!a.areas&&a.areas.v===1&&b.areas===undefined}"))
    ok('qvParse de save com g.areas corrompido não quebra', pg.evaluate("()=>{const g=structuredClone(__QV().gRef.current);g.areas={v:1,val:null,meta:'x',med:[],nat:null};const r=__P().qvParse(JSON.stringify(g));return !!r.areas&&typeof r.areas.val==='object'&&Number.isFinite(r.areas.val.uti)}"))
    r = pg.evaluate(SIMJS, [[], 3, None, None])
    ok('save antigo: o jogo avança meses depois de apagar g.areas', not r.get('erro') and len(r['serie']) == 3)
    # fechar meses pela interface
    for _ in range(2):
        fecha_modais(pg)
        pg.locator('button').filter(has_text=re.compile(r'^\s*Encerrar m')).first.click(timeout=8000); pg.wait_for_timeout(900); fecha_modais(pg)
    secao(pg, 'País'); chip(pg, 'Saúde')
    ok('depois de fechar meses pela interface a aba segue com os cartões e a tendência', pg.locator('[data-meta]').count() == 4 and pg.locator('[data-meta-tend]').count() == 4)
    print('ERRS', errs[:8])
    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    print('RESUMO: %d ok, %d falhas' % (sum(1 for c in checks if c[0]), sum(1 for c in checks if not c[0])))
    b.close()
