# Gera uma versão "mal escrita" de uma bateria (mesmo gabarito, texto estragado como o povo digita).
# uso: python3 ruido.py <bateria.json> <saida.json> [semente]
# Ruídos (determinísticos pela semente): sem acento, abreviações de internet (vc, q, pq, tbm, p/, n),
# erros de digitação (troca, omissão e duplicação de letra), caixa (tudo minúsculo / CAPS), pontuação e espaços.
import json, random, re, sys, unicodedata

ABREV = [(r'\bvocê\b', 'vc'), (r'\bque\b', 'q'), (r'\bporque\b', 'pq'), (r'\bpor que\b', 'pq'), (r'\btambém\b', 'tbm'),
         (r'\bpara\b', 'p/'), (r'\bpra\b', 'p/'), (r'\bnão\b', 'n'), (r'\bmuito\b', 'mto'), (r'\bquando\b', 'qdo'),
         (r'\bcom\b', 'c/'), (r'\bsem\b', 's/'), (r'\bgoverno\b', 'gov'), (r'\bpresidente\b', 'pres'), (r'\bestá\b', 'ta'),
         (r'\bmilhões\b', 'mi'), (r'\bbilhões\b', 'bi'), (r'\breais\b', 'conto')]
VIZ = dict(zip('qwertyuiopasdfghjklzxcvbnm', 'wqrtyuiopsadfghjklzxcvbnmq'))

def sem_acento(s): return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def digita(w, r):
    if len(w) < 5 or not w.isalpha(): return w
    i = r.randrange(1, len(w) - 1); op = r.random()
    if op < .35: return w[:i] + w[i + 1] + w[i] + w[i + 2:]          # troca vizinhas
    if op < .6: return w[:i] + w[i + 1:]                              # omite
    if op < .8: return w[:i] + w[i] + w[i:]                           # duplica
    return w[:i] + VIZ.get(w[i].lower(), w[i]) + w[i + 1:]            # tecla vizinha

def estraga(t, r):
    s = t
    if r.random() < .7: s = sem_acento(s)
    for pat, rep in ABREV:
        if r.random() < .6: s = re.sub(pat, rep, s, flags=re.I) if r.random() < .9 else s
        if r.random() < .6: s = re.sub(sem_acento(pat), rep, s, flags=re.I)
    ws = s.split(' ')
    n = max(1, len(ws) // 6)
    for _ in range(n):
        k = r.randrange(len(ws)); ws[k] = digita(ws[k], r)
    s = ' '.join(ws)
    c = r.random()
    if c < .45: s = s.lower()
    elif c < .55: s = s.upper()
    if r.random() < .5: s = s.rstrip('.') + r.choice(['', '!!', ' kkk', '...', '?', ' pfv'])
    if r.random() < .3: s = re.sub(r',', '', s)
    if r.random() < .2: s = s.replace(' ', '  ', 1)
    return s

def main():
    src, out = sys.argv[1], sys.argv[2]; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 7
    d = json.load(open(src, encoding='utf-8-sig')); res = []
    for i, x in enumerate(d):
        r = random.Random(seed * 100003 + i)
        y = dict(x) if isinstance(x, dict) else {'t': x}
        y['t_original'] = y['t']; y['t'] = estraga(y['t'], r)
        res.append(y)
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(res), 'itens ->', out)

if __name__ == '__main__': main()
