#!/usr/bin/env python3
# Resume (e compara) saídas de sim.py.  uso: python3 relatorio.py <saida.json> [<outra_saida.json>]
# Com um arquivo: tabela cenário x indicador x mês (esperado -> veredito). Com dois: mostra só o que mudou de veredito.
import sys, json
def carrega(f):
    d = json.load(open(f, encoding='utf-8')); m = {}
    for c in d['cenarios']:
        for r in c['resultados']: m[(c['id'], r['ind'], r['mes'])] = r
    return d, m
SIM = {'ok': 'ok', 'falha': 'FALHA', 'inconclusivo': 'inconcl.', 'info': 'info'}
d1, m1 = carrega(sys.argv[1])
if len(sys.argv) < 3:
    print('versão %s  reps=%d  totais=%s  tempo=%ss' % (d1['versao']['sha1'], d1['repeticoes'], d1['totais'], d1['segundos']))
    for c in d1['cenarios']:
        print('\n%s  %s\n  %s' % (c['id'], c['resumo'], c['descricao']))
        for l in c['acoes_executadas']: print('  ação: %s' % {k: l.get(k) for k in ('mes', 'tipo', 'inst', 'res', 'topic', 'cost', 'rev', 'once', 'erro') if l.get(k) is not None})
        for r in c['resultados']:
            print('  %-14s m%-2d esperado %-8s -> %-8s trat %9.3f ctrl %9.3f  dif %s' % (r['ind'], r['mes'], r['esperado'], SIM[r['veredito']], r.get('media_trat', 0), r.get('media_ctrl', 0), r.get('D')))
else:
    d2, m2 = carrega(sys.argv[2])
    print('A: %s %s   B: %s %s' % (d1['versao']['sha1'], d1['totais'], d2['versao']['sha1'], d2['totais']))
    for k in sorted(set(m1) | set(m2)):
        a, b = m1.get(k), m2.get(k)
        va, vb = a and a['veredito'], b and b['veredito']
        if va != vb: print('%-18s %-14s m%-2d esperado %-8s  A=%-8s B=%-8s  difA=%s difB=%s' % (k[0], k[1], k[2], (a or b)['esperado'], SIM.get(va, '-'), SIM.get(vb, '-'), a and a.get('D'), b and b.get('D')))
