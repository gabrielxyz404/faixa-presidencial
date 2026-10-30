# Regressão do motor: 25 propostas pela interface (batch3) + frases pelo probe, comparadas com as linhas de base.
# uso: python3 regressao.py <pasta com index.html> <saida> [frases.json base_probe.json ...pares]
#   pasta precisa ter fotos.json e logos.json (link simbólico serve). Porta: 8781 (batch3) e 8791+ (probe).
import sys, os, json, re, subprocess
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..', 'regressao')
ROOT, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
pares = sys.argv[3:]
run = lambda *a: subprocess.run([sys.executable, os.path.join(H, 'run_sandbox.py'), *a], capture_output=True, text=True)
r = run(os.path.join(R, 'batch3.py'), ROOT, OUT)
errs = json.load(open(os.path.join(OUT, 'errs.json'))) if os.path.exists(os.path.join(OUT, 'errs.json')) else ['batch3 falhou: ' + r.stderr[-400:]]
def norm(t): return [re.sub(r'[\d,.+−-]+', '#', l) for l in (t or '').splitlines() if not re.search(r'Emendas p/|sim / precisa|Faltam votos|\d+/\d+.*\d+/\d+', l)]
base = json.load(open(os.path.join(R, 'raw_depois.json'))); novo = json.load(open(os.path.join(OUT, 'raw.json')))
mud = [x['i'] for x, y in zip(base, novo) if norm(x.get('txt')) != norm(y.get('txt'))]
print('25 propostas: mudaram', mud or 'nenhuma', '| erros de página/console:', errs or 'nenhum')
K = ['topic', 'inst', 'instDet', 'cost', 'rev', 'once', 'cf']
for n in range(0, len(pares), 2):
    fr, bp = pares[n], pares[n + 1]; out = os.path.join(OUT, 'probe_' + os.path.basename(fr))
    rr = run(os.path.join(H, 'probe.py'), ROOT, fr, out, str(8791 + n))
    print(os.path.basename(fr), ':', [l for l in rr.stdout.splitlines() if 'GET /' not in l][-1:] )
    if not os.path.exists(bp): print('  (sem linha de base em', bp, ')'); continue
    a = {x['t']: x for x in json.load(open(bp))}; b = json.load(open(out))
    for y in b:
        x = a.get(y['t'])
        if x is None: continue
        d = {k: (x.get(k), y.get(k)) for k in K if x.get(k) != y.get(k)}
        if d: print('  MUDOU:', y['t'], '|', '; '.join('%s: %s -> %s' % (k, v[0], v[1]) for k, v in d.items()))
