# Quadro por tema: entendimento (gabarito x probe) e efeito no save (sim) para duas versões.
# uso: python3 quadro.py <gabarito.json> <probeA.json> <probeB.json> [<simA.json> <simB.json>] [--md saida.md]
import sys, json, collections
sys.path.insert(0, '/home/user/faixa-presidencial/testes/bench'); import score
a = [x for x in sys.argv[1:] if not x.startswith('--')]
md = None
if '--md' in sys.argv: md = sys.argv[sys.argv.index('--md') + 1]; a.remove(md)
gab = json.load(open(a[0], encoding='utf-8'))
def ent(fp):
    rs = json.load(open(fp, encoding='utf-8')); T = collections.defaultdict(lambda: [0, 0]); TT = collections.defaultdict(lambda: [0, 0])
    for g, r in zip(gab, rs):
        s, why, vig = score.score_item(g, r); ok = all(s.values()) and vig != 0
        for k in (g['area'], '*'): T[k][0] += ok; T[k][1] += 1
        TT[g.get('tipo')][0] += ok; TT[g.get('tipo')][1] += 1
    return T, TT
def sim(fp):
    d = json.load(open(fp, encoding='utf-8')); T = collections.defaultdict(lambda: [0, 0])
    for c in d['cenarios']:
        area = c['descricao'].split(':')[0]
        for r in c['resultados']:
            if r['veredito'] == 'info': continue
            for k in (area, '*'): T[k][0] += r['veredito'] == 'ok'; T[k][1] += 1
    return T
EA, TA = ent(a[1]); EB, TB = ent(a[2])
SA = sim(a[3]) if len(a) > 4 else None; SB = sim(a[4]) if len(a) > 4 else None
p = lambda t: (100.0 * t[0] / t[1]) if t[1] else float('nan')
L = ['| Tema | Entende v3.9 | Entende v4 | Δ | Efeito no save v3.9 | Efeito v4 | Δ |', '|---|---|---|---|---|---|---|']
for k in sorted(EA, key=lambda k: (k == '*', k)):
    row = [('**TOTAL**' if k == '*' else k), '%.0f%%' % p(EA[k]), '%.0f%%' % p(EB[k]), '%+.0f' % (p(EB[k]) - p(EA[k]))]
    if SA: row += ['%.0f%%' % p(SA[k]), '%.0f%%' % p(SB[k]), '%+.0f' % (p(SB[k]) - p(SA[k]))]
    else: row += ['-', '-', '-']
    L.append('| ' + ' | '.join(row) + ' |')
L += ['', '| Tipo de proposta | v3.9 | v4 |', '|---|---|---|'] + ['| %s | %.0f%% | %.0f%% |' % (k, p(TA[k]), p(TB[k])) for k in sorted(TA)]
out = '\n'.join(L); print(out)
if md: open(md, 'w', encoding='utf-8').write(out + '\n')
