# Resume a saída de balance2.py (estratégias jogadas por JS, 48 meses x sementes) em aprovação média por estratégia, antes x depois.
# uso: python3 comex_equilibrio_rel.py antes.json depois.json
import sys, json
def media(xs): return sum(xs) / len(xs) if xs else float('nan')
A = json.load(open(sys.argv[1])); B = json.load(open(sys.argv[2]))
MS = (6, 12, 24, 36, 48)
def tabela(R):
    out = {}
    for r in R:
        o = out.setdefault(r['estrategia'], {'n': 0, 'fim': 0, 'ap': {m: [] for m in MS}, 'saude': {m: [] for m in MS}, 'div': []})
        o['n'] += 1; o['fim'] += (r['fim'] != 'personagem' and r['fim'] != 'sobreviveu')
        for m in MS:
            x = next((s for s in r['serie'] if s['mes'] == m), None)
            if x: o['ap'][m].append(x['ap']); o['saude'][m].append(x['saude'])
        o['div'].append(r['serie'][-1]['div'])
    return out
TA, TB = tabela(A), tabela(B)
print('| estratégia | versão | aprovação m6 | m12 | m24 | m36 | m48 | média m12–m48 | rodadas encerradas antes do fim | dívida/PIB final |')
print('|---|---|---|---|---|---|---|---|---|---|')
for est in TB:
    for nome, T in (('antes', TA), ('depois', TB)):
        if est not in T: continue
        o = T[est]; med = [media(o['ap'][m]) for m in MS]
        print('| %s | %s | %s | %.1f | %d/%d | %.0f |' % (est, nome, ' | '.join('%.1f' % v for v in med), media(med[1:]), o['fim'], o['n'], media(o['div'])))
