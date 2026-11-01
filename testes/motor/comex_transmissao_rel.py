# Tabela antes/depois a partir das saídas de comex_transmissao.py.
# uso: python3 testes/motor/comex_transmissao_rel.py antes.json [depois.json] > tabela.md
import sys, json
MK = {'trigo': 'trigo', 'leite': 'leite_po', 'arroz': 'arroz', 'eletro': 'eletronicos', 'diesel': 'combustiveis', 'medic': 'medicamentos', 'potassio': 'fert_potassio', 'potassio4': 'fert_potassio',
      'diesel_caro': 'combustiveis', 'tec_arroz': 'arroz', 'conab_arroz': 'arroz', 'conab_compra_arroz': 'arroz', 'leilao_arroz': 'arroz', 'credito_arroz': 'arroz'}
GR = ['periferia', 'aposentados', 'agro', 'caminhoneiros']
def load(p): return json.load(open(p))
def media(xs): return sum(xs) / len(xs) if xs else 0
def delta(D, cid, m, f):
    ds = []
    for sd in D['seeds']:
        t = D['res']['trat'][cid].get(str(sd)); c = D['res']['ctrl'][str(sd)]
        if not t or 'serie' not in t or len(t['serie']) <= m or 'err' in t['serie'][m]: continue
        ds.append(f(t['serie'][m]) - f(c['serie'][m]))
    return media(ds)
def linha(D, cid, ms):
    mk = MK[cid]; t0 = D['res']['trat'][cid].get(str(D['seeds'][0]))
    if not t0 or 'serie' not in t0: return None
    out = {}
    for m in ms:
        out[m] = dict(pd=delta(D, cid, m, lambda s: (s['pd'].get(mk, 1) - 1) * 100), ipca=delta(D, cid, m, lambda s: s['ipca']), mac=delta(D, cid, m, lambda s: s['mac']), ap=delta(D, cid, m, lambda s: s['ap']),
                      cut=delta(D, cid, m, lambda s: s['ct'].get(mk, 0) * 100), macagro=delta(D, cid, m, lambda s: s['macAgro']),
                      **{g: delta(D, cid, m, lambda s, g=g: s['gr'][g]) for g in GR})
    return out
def main():
    A = load(sys.argv[1]); B = load(sys.argv[2]) if len(sys.argv) > 2 else None
    MS = [3, 6, 9, 12, 18]
    print('Cada linha é a diferença média (todas as sementes) entre a partida COM a ação e a MESMA partida SEM ela, no mês indicado. pdom = preço interno do mercado (%); IPCA = indicador `eco.ipca` (pp); mac = termo do comércio no IPCA (pp); ap = aprovação geral (pontos).\n')
    for cid, label in A['cen']:
        la = linha(A, cid, MS); lb = linha(B, cid, MS) if B else None
        print('### %s\n' % label)
        print('| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |')
        print('|---|---|---|---|---|---|---|---|---|---|---|---|')
        for m in MS:
            for nome, L in (('antes', la), ('depois', lb)):
                if nome == 'depois' and not B: continue
                if L is None: print('| %d | %s | n/d | | | | | | | | | |' % (m, nome)); continue
                x = L[m]
                print('| %d | %s | %+.2f | %+.4f | %+.4f | %+.3f | %+.3f | %+.3f | %+.3f | %+.3f | %+.2f | %+.4f |' % (m, nome, x['pd'], x['mac'], x['ipca'], x['ap'], x['periferia'], x['aposentados'], x['agro'], x['caminhoneiros'], x['cut'], x['macagro']))
        print()
    if B:  # início do jogo: braço de controle (sem ações) antes x depois, meses 1–12
        print('### Início do jogo (save novo, sem ações): controle antes x depois, meses 1 a 12\n')
        mx = {'ipca': 0, 'ap': 0, 'grupo': 0}; pior = ''
        for sd in A['seeds']:
            ca = A['res']['ctrl'][str(sd)]['serie']; cb = B['res']['ctrl'][str(sd)]['serie']
            for m in range(1, 13):
                mx['ipca'] = max(mx['ipca'], abs(ca[m]['ipca'] - cb[m]['ipca'])); mx['ap'] = max(mx['ap'], abs(ca[m]['ap'] - cb[m]['ap']))
                for g in ca[m]['gr']:
                    d = abs(ca[m]['gr'][g] - cb[m]['gr'][g])
                    if d > mx['grupo']: mx['grupo'] = d; pior = '%s semente %s mês %d' % (g, sd, m)
        print('Maior diferença absoluta em %d sementes x 12 meses: IPCA %.3f pp · aprovação %.3f pontos · grupo %.3f pontos (%s).\n' % (len(A['seeds']), mx['ipca'], mx['ap'], mx['grupo'], pior))
        for m in (3, 6, 12):
            da = media([A['res']['ctrl'][str(sd)]['serie'][m]['ipca'] for sd in A['seeds']]); db = media([B['res']['ctrl'][str(sd)]['serie'][m]['ipca'] for sd in A['seeds']])
            pa = media([A['res']['ctrl'][str(sd)]['serie'][m]['ap'] for sd in A['seeds']]); pb = media([B['res']['ctrl'][str(sd)]['serie'][m]['ap'] for sd in A['seeds']])
            print('- mês %d: IPCA %.3f → %.3f · aprovação %.2f → %.2f' % (m, da, db, pa, pb))
main()
