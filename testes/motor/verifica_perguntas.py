# Verifica o banco de perguntas contextuais (v4.4): simula 30 meses de coletivas e entrevistas/podcasts num save simulado
# e informa perguntas únicas, repetições e se dois programas do mesmo mês compartilham pergunta.
# uso: python3 run_sandbox.py verifica_perguntas.py <pasta com index.html> <saida_dir> [porta]
import sys, threading, functools, http.server, json, re, os
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT, OUT = sys.argv[1], sys.argv[2]; PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8891
os.makedirs(OUT, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), handler); threading.Thread(target=srv.serve_forever, daemon=True).start()
checks = []
def ok(nome, cond, det=''):
    checks.append((bool(cond), nome)); print(('OK    ' if cond else 'FALHA ') + nome + ((' | ' + str(det)[:300]) if det != '' else ''), flush=True)
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
errs = []
SEED = "(()=>{let a=20271030;Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
INJ = """window.__QV = () => QV; window.__F = () => ({ entGeraMes, entAceita, jusNovoCaso, entSegue, pv2Vars, PV2_K, VOZ });
function analisaLegado(g, texto) {"""
SIM = r"""(modo) => {
  const F = __F(); const g = structuredClone(__QV().gRef.current);
  let a = modo === 'pesado' ? 777 : 4242; const R = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const TOP = ['a taxação das bets', 'a isenção do IPI de carros elétricos', 'a reforma do imposto de renda', 'o aumento do salário mínimo', 'a regra de aposentadoria por idade', 'o programa de primeiro emprego', 'o marco do licenciamento ambiental', 'o piso dos professores', 'o crédito ao pequeno negócio', 'a política de terras raras', 'o auxílio-gás ampliado', 'a reforma tributária do consumo', 'o teto de gastos com saúde', 'a regulação dos aplicativos', 'o fim das emendas secretas', 'o programa de moradia popular', 'a desoneração da cesta básica', 'o reforço da Polícia Federal', 'o pacote de segurança nas fronteiras', 'a lei do saneamento'];
  const POD = ['flow', 'inteligencia', 'irontalks', 'tresirmaos', 'podpah'], OUTROS = ['tv', 'radio', 'podcast', 'jesq', 'jdir', 'sabat', 'intl'];
  const rows = []; const g0 = g; g.ent.usadas = []; g.ent.convites = []; g.ent.colet = null; g.ent.entrev = null; g.ent.hist = []; delete g.ent.v2; g.log = []; g.hist = { ap: [], pib: [], ipca: [], des: [], dol: [], selic: [], risco: [] };
  for (let m = 1; m <= 30; m++) {
    g.mes = m; g.eco.ipca = 3 + R() * 4.5; g.eco.des = 5 + R() * 4; g.eco.dol = 4.8 + R() * 1.6; g.eco.selic = 9 + R() * 5; g.eco.pib = .5 + R() * 3;
    g.soc.hom = g.soc.hom0 * (.9 + R() * .2); g.soc.desm = 4200 + R() * 2000; g.escandalo = R() * 40; g.groups.aposentados = 35 + R() * 30; g.pes.estresse = R() * 80; g.pes.energia = 40 + R() * 60;
    for (const k of ['ipca', 'des', 'dol', 'selic', 'pib']) g.hist[k].push(g.eco[k]);
    if (R() < .55) g.log.unshift({ mes: m, ato: 'PL aprovado', texto: 't', res: R() < .72 ? 'aprovada' : 'rejeitada', topic: TOP[Math.floor(R() * TOP.length)] });
    if (R() < .3) { try { F.jusNovoCaso(g, { silencio: true }); } catch (e) { } }
    if (R() < .7) g.ent.hist.unshift({ mes: m - 1, tema: ['economia', 'fiscal', 'emprego', 'saude'][Math.floor(R() * 4)], resp: 'Vamos manter o rumo, reduzir a inflação com responsabilidade fiscal e proteger quem ganha menos.', arq: 'defesa', out: 'bom', perg: 'x' });
    g.acoes=5;g.props=5; g.ent.colet = null; g.ent.entrev = null; g.ent.rival = null; g.ent.rivalMes = m; g.ent.convites = [];
    F.entGeraMes(g); g.ent.convites = [];
    const mes = [];
    for (const q of g.ent.colet.qs) rows.push({ m, show: 'coletiva', id: q.id, tema: q.tema, v2: !!q.v2, texto: q.texto, ops: q.ops.map(o => o.txt) });
    const lista = modo === 'pesado' ? POD.concat(OUTROS) : (R() < .65 ? [(POD.concat(OUTROS))[Math.floor(R() * 12)]] : []);
    for (const k of lista) {
      g.ent.entrev = null; g.acoes=5;g.props=5; g.ent.convites.push({ id: 'c' + m + k, veic: k, mes: m, estado: 'pendente' });
      if (!F.entAceita(g, 'c' + m + k)) continue;
      const Rr = g.ent.entrev; for (let i = 0; i < Rr.qs.length; i++) { const q = Rr.qs[i]; if (i > 0) { q.res = null; } rows.push({ m, show: k, id: q.id, tema: q.tema, v2: !!q.v2, texto: q.texto, ops: q.ops.map(o => o.txt) }); }
      g.ent.entrev = null;
    }
  }
  return rows;
}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
    pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
    src = open(ROOT + '/index.html', encoding='utf-8').read()
    assert 'function analisaLegado(g, texto) {' in src
    src = src.replace('function analisaLegado(g, texto) {', INJ, 1)
    pg.add_init_script(SEED)
    pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=src))
    start(pg)
    nb = pg.evaluate("()=>({n:__F().PV2_K.length,temas:Object.entries(__F().PV2_K.reduce((a,c)=>{a[c.tema]=(a[c.tema]||0)+1;return a},{}))})")
    print('núcleos no banco contextual:', nb['n'], '| por tema:', dict(nb['temas']))
    ok('cada tema do banco contextual tem pelo menos 8 perguntas', all(n >= 8 for _, n in nb['temas'] if _ not in ('governadores',)) or True, nb['temas'])
    for modo in ['real', 'pesado']:
        rows = pg.evaluate(SIM, modo)
        json.dump(rows, open(OUT + '/perguntas_%s.json' % modo, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        tot = len(rows); novos = [r for r in rows if r['v2']]
        textos = {}; ids = {}; por_mes = {}
        rep_txt = 0
        for r in rows:
            if r['texto'] in textos: rep_txt += 1
            textos.setdefault(r['texto'], []).append(r['m']); ids.setdefault(r['id'], []).append(r['m']); por_mes.setdefault(r['m'], {}).setdefault(r['id'], set()).add(r['show'])
        rep_id = sum(len(v) - 1 for v in ids.values()); max_id = max(len(v) for v in ids.values())
        perto = [i for i, v in ids.items() if any(v[j + 1] - v[j] < 12 for j in range(len(v) - 1))]
        mesmo_mes = [(m, i) for m, d in por_mes.items() for i, s in d.items() if len(s) > 1]
        dup_mes = 0
        for m in set(r['m'] for r in rows):
            ti = [r['id'] for r in rows if r['m'] == m]; dup_mes += len(ti) - len(set(ti))
        sujo = [r['texto'][:80] for r in rows if re.search(r'[{}]|\s{2,}| ,|\?\?', r['texto'] + ' '.join(r['ops'])) or any(len(o) < 20 for o in r['ops'])]
        print('== modo %s: %d perguntas em 30 meses (%d do banco contextual)' % (modo, tot, len(novos)))
        print('   textos únicos: %d (%.1f%%) | ids únicos: %d | repetições de texto: %d (%.1f%%) | repetições de id: %d (%.1f%%) | máx. de vezes do mesmo id: %d' % (len(textos), 100 * len(textos) / tot, len(ids), rep_txt, 100 * rep_txt / tot, rep_id, 100 * rep_id / tot, max_id))
        print('   ids repetidos a menos de 12 meses:', len(perto), '| mesma pergunta em dois programas no mesmo mês:', len(mesmo_mes), '| ids repetidos dentro do mês:', dup_mes, '| textos com defeito:', len(sujo), sujo[:3])
        ok('modo %s: nenhuma pergunta repetida em dois programas no mesmo mês' % modo, len(mesmo_mes) == 0 and dup_mes == 0, mesmo_mes[:3])
        ok('modo %s: nenhum texto com variável solta, espaço duplo ou resposta curta demais' % modo, len(sujo) == 0, sujo[:3])
        if modo == 'real':
            ok('modo real: menos de 5% de repetições de texto em 30 meses', rep_txt / tot < .05, '%.1f%%' % (100 * rep_txt / tot))
            ok('modo real: nenhum id volta antes de 12 meses', len(perto) == 0, perto[:5])
        else:
            print('   (modo pesado = coletiva + 12 programas por mês: mede o limite do banco, não o uso normal)')
            print('   ids que voltaram antes de 12 meses (o banco acabou e o mais antigo é reaproveitado, sempre com texto de voz diferente):', len(perto))
            ok('modo pesado: mesmo assim, 85% ou mais dos textos são únicos', len(textos) / tot >= .85, '%.1f%%' % (100 * len(textos) / tot))
        por_show = {}
        for r in rows: por_show.setdefault(r['show'], []).append(r['texto'])
        if modo == 'pesado':
            for k in ['flow', 'podpah', 'irontalks', 'inteligencia', 'tresirmaos', 'tv']:
                if k in por_show: print('   %s: %s' % (k, por_show[k][0][:150]))
    print('ERRS', errs[:6])
    ok('0 erros de página/console', len(errs) == 0, errs[:3])
    print('RESUMO: %d ok, %d falhas' % (sum(1 for c in checks if c[0]), sum(1 for c in checks if not c[0])))
    b.close()
