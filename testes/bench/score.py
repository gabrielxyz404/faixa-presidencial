#!/usr/bin/env python3
# Corretor do bench de propostas. uso: python3 score.py <gabarito.json> <saida_probe.json> [--json relatorio.json]
import sys, json, re, unicodedata, collections

def norm(s):
    s = unicodedata.normalize('NFD', str(s or '').lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')

AUM = re.compile(r'aument|ampliac|elevac|majorac|alta d')
RED = re.compile(r'reduc|corte|diminui|queda|isenc|fim d|extinc|baixa')
VIG = re.compile(r'ja em vigor|ja vigente|ja instituid|ja extint')
CRIT = ['tema', 'dir', 'inst', 'valor', 'cf']

def inst_of(r):
    i, d = r.get('inst'), r.get('instDet')
    if i == 'PL' and d == 'LC': return 'PLP'
    if i == 'PL' and d == 'AUT': return 'AUT'
    return i

def val_ok(faixa, v):
    v = float(v or 0)
    if faixa is None: return abs(v) < 1
    return faixa[0] <= v <= faixa[1]

def score_item(g, r):
    """devolve (dict criterio->0/1, lista de motivos, vig 0/1/None)"""
    s, why = {}, []
    if r is None or r.get('err'):
        return {c: 0 for c in CRIT + (['absurdo'] if g.get('absurdo_esperado') else [])}, ['sem resposta do motor' + (': ' + str(r.get('err')) if r else '')], (0 if g.get('jaVigente') else None)
    topic = norm(r.get('topic'))
    ok = bool(topic) and not r.get('vago') and all(re.search(rx, topic) for rx in g.get('tema', []))
    s['tema'] = int(ok)
    if not ok:
        why.append('tema: "%s"%s não casa %s' % (r.get('topic'), ' [vago]' if r.get('vago') else '', g.get('tema')))
    d = g.get('dir'); dok = 1
    if d in ('reduz', 'extingue', 'proibe') and AUM.search(topic) and not RED.search(topic): dok = 0
    if d == 'aumenta' and RED.search(topic) and not AUM.search(topic): dok = 0
    s['dir'] = dok
    if not dok: why.append('direção: esperado %s, tópico "%s"' % (d, r.get('topic')))
    mi = inst_of(r); s['inst'] = int(mi in g.get('inst', []))
    if not s['inst']: why.append('instrumento: motor %s, aceitos %s' % (mi, g.get('inst')))
    once = max([r.get('once') or 0, r.get('extra') or 0], key=abs)
    vp = []
    for nome, fx, v in (('custo', g.get('custo'), r.get('cost')), ('receita', g.get('receita'), r.get('rev')), ('unico', g.get('unico'), once)):
        if not val_ok(fx, v): vp.append('%s motor %s esperado %s' % (nome, v, fx if fx is not None else '~0'))
    s['valor'] = int(not vp)
    if vp: why.append('valor: ' + '; '.join(vp))
    s['cf'] = int(r.get('cf') in g.get('cf', ['ok']))
    if not s['cf']: why.append('cf: motor %s, aceitos %s' % (r.get('cf'), g.get('cf')))
    if g.get('absurdo_esperado'):  # item impossível: o motor deve marcar como absurda
        s['absurdo'] = int(bool(r.get('absurdo')))
        if not s['absurdo']: why.append('absurdo: impossível, mas o motor NÃO marcou como absurda')
    elif g.get('zoeira') == 'legal':  # bizarra mas permitida: não pode ser tratada como piada
        s['nao_absurdo'] = int(not r.get('absurdo'))
        if not s['nao_absurdo']: why.append('nao_absurdo: proposta legal marcada como absurda/piada')
    blob = norm(' '.join(str(r.get(k) or '') for k in ('topic', 'cfTxt', 'tecnico')))
    vig = None
    if g.get('jaVigente'):
        m = re.search(r'\d+\.?\d*/\d{4}', g['jaVigente'])
        vig = int(bool(VIG.search(blob)) or (m and m.group(0) in blob))
        if not vig: why.append('jaVigente: não reconheceu %s' % g['jaVigente'])
    return s, why, vig

def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    jout = None
    if '--json' in sys.argv:
        i = sys.argv.index('--json'); jout = sys.argv[i + 1]; a = [x for x in a if x != jout]
    gab = json.load(open(a[0], encoding='utf-8-sig')); out = json.load(open(a[1], encoding='utf-8-sig'))
    byt = {x['t']: x for x in out if isinstance(x, dict) and 't' in x}
    tot = collections.Counter(); n = 0; an = 0; fpa = []; fna = []; full = 0; full5 = 0; vn = vs = 0; fp = []
    area = collections.defaultdict(lambda: [0, 0, 0.0]); errs = []; pct_sum = 0.0
    for g in gab:
        r = byt.get(g['t']); s, why, vig = score_item(g, r); n += 1
        crit = list(s.values()) + ([vig] if vig is not None else [])
        for c in CRIT: tot[c] += s[c]
        if 'absurdo' in s: an += 1; tot['absurdo'] += s['absurdo']; (fna.append(g['t']) if not s['absurdo'] else None)
        if s.get('nao_absurdo') == 0 and r and not r.get('err'): fpa.append(g['t'])
        if vig is not None: vn += 1; vs += vig
        elif r and not r.get('err') and VIG.search(norm(' '.join(str(r.get(k) or '') for k in ('topic', 'cfTxt', 'tecnico')))):
            fp.append(g['t'])
        p = sum(crit) / len(crit); pct_sum += p; ok = all(crit); full += ok; full5 += all(s.values())
        ar = area[g.get('area', '?')]; ar[0] += 1; ar[1] += ok; ar[2] += p
        if not ok: errs.append((g.get('area'), g['t'], why))
    print('Itens: %d  (sem resposta: %d)' % (n, sum(1 for g in gab if g['t'] not in byt)))
    for c in CRIT: print('  %-8s %5.1f%%' % (c, 100 * tot[c] / n))
    if vn: print('  %-8s %5.1f%%  (%d itens)' % ('jaVigente', 100 * vs / vn, vn))
    if an: print('  %-8s %5.1f%%  (%d itens impossíveis marcados como absurda; falsos negativos: %d)' % ('absurdo', 100 * tot['absurdo'] / an, an, len(fna)))
    nl = sum(1 for g in gab if g.get('zoeira') == 'legal')
    if nl: print('Falsos positivos de absurdo (legal marcado como absurda): %d/%d' % (len(fpa), nl)); [print('   - ' + t) for t in fpa]
    print('Média por item: %.1f%%   Totalmente certos: %d/%d = %.1f%%' % (100 * pct_sum / n, full, n, 100 * full / n))
    print('Certos nos 5 critérios (ignorando jaVigente): %d/%d = %.1f%%' % (full5, n, 100 * full5 / n))
    print('Falso "já vigente" (gabarito null, motor alega): %d' % len(fp))
    print('\nPor área (itens | totalmente certos | média):')
    for k, (c, f, ps) in sorted(area.items()): print('  %-34s %3d | %3d (%4.0f%%) | %4.0f%%' % (k, c, f, 100 * f / c, 100 * ps / c))
    print('\nItens errados (%d):' % len(errs))
    for ar, t, why in errs:
        print('- [%s] %s' % (ar, t))
        for w in why: print('     ' + w)
    if jout:
        json.dump({'n': n, 'criterios': {c: tot[c] / n for c in CRIT}, 'jaVigente': (vs / vn if vn else None), 'media': pct_sum / n,
                   'totalmente_certos': full / n, 'certos_5_criterios': full5 / n, 'falso_ja_vigente': fp, 'absurdo': (tot['absurdo'] / an if an else None), 'falsos_positivos_absurdo': fpa, 'falsos_negativos_absurdo': fna,
                   'areas': {k: {'n': c, 'certos': f, 'media': ps / c} for k, (c, f, ps) in area.items()},
                   'erros': [{'area': a_, 't': t, 'motivos': w} for a_, t, w in errs]}, open(jout, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
main()
