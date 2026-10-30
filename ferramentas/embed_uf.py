"""Embute saude_uf.json e areas_uf.json em index.html (entre /*<UFDATA>*/ e /*</UFDATA>*/). Uso: python -I embed_uf.py"""
import json, os, re, sys
W = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work')
H = os.path.join(W, 'index.html')

def carrega(nome, padrao):
    p = os.path.join(W, nome)
    if not os.path.exists(p):
        print('ausente:', nome); return padrao
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)

saude = carrega('saude_uf.json', {'fontes': {}, 'BR': {}, 'UF': {}})
areas = carrega('areas_uf.json', {})

def fontes(d):
    return sorted({(v.get('fonte') or '').strip() for v in d.get('fontes', {}).values() if v.get('fonte')})

def mini(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

com = ['// Dados reais por UF (pesquisa; ver "Fontes e notas" em cada aba do País). Valores no jogo = base real + variação nacional x peso (ver PUF_LIGA).']
com.append('// SAUDE_UF fontes: ' + '; '.join(fontes(saude))[:900])
for k, d in areas.items():
    com.append('// AREAS_UF.' + k + ' fontes: ' + '; '.join(fontes(d))[:600])
bloco = '/*<UFDATA>*/\n' + '\n'.join(com) + '\nconst SAUDE_UF = ' + mini(saude) + ';\nconst AREAS_UF = ' + mini(areas) + ';\n/*</UFDATA>*/'

with open(H, 'r', encoding='utf-8', newline='') as f:
    t = f.read()
nl = '\r\n' if '\r\n' in t[:5000] else '\n'
bloco = bloco.replace('\n', nl)
m = re.search(r'/\*<UFDATA>\*/.*?/\*</UFDATA>\*/', t, re.S)
if not m:
    sys.exit('marcadores nao encontrados')
t = t[:m.start()] + bloco + t[m.end():]
with open(H, 'w', encoding='utf-8', newline='') as f:
    f.write(t)
print('ok', len(bloco), 'bytes; saude UFs:', len(saude.get('UF', {})), 'areas:', list(areas.keys()))
