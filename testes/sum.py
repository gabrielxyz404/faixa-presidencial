import json,sys
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(open(sys.argv[1],encoding='utf-8-sig'))
for r in d:
    if 'err' in r: print(r['t'],'ERR',r['err']);continue
    p=json.loads(r['p']) if r['p'].endswith('}') else None
    # reparse failed due truncation: use regex
    import re
    def g(k,pat): 
        m=re.search(pat,r['p']); return m.group(1) if m else '?'
    print('-',r['t']);
    print('   inst',g('i','"inst":"(\w+)"'),'cost',g('c','"cost":(-?[\d.]+)'),'rev',g('r','"rev":(-?[\d.]+)'),'once',g('o','"once":(-?[\d.]+)'),'jur',g('j','"nivel":"(\w+)"'),'pol',g('p','"polaridade":(-?\d)'),'objs',g('o','"objetos":(\[[^\]]*\])'))
    m=re.search(r'"tecnico":"(.{0,330})',r['p']); print('   ',m.group(1) if m else '')
