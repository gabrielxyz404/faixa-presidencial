import sys,os,json,csv,unicodedata,re,difflib
W,D=sys.argv[1],sys.argv[2]
def N(s): 
    s=unicodedata.normalize('NFKD',s); s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'\s+',' ',s).strip().upper()
keys=list(json.load(open(W+'/fotos.orig.json',encoding='utf-8'))['fotos'])
def load(y):
    rows=[]
    for f in os.listdir(f'{D}/cand{y}'):
        if f.endswith('.csv') and not f.endswith('BRASIL.csv') and not f.endswith('_BR.csv') or f.endswith('_BR.csv'):
            with open(f'{D}/cand{y}/{f}',encoding='latin-1',newline='') as fh:
                rows+=list(csv.DictReader(fh,delimiter=';',quotechar='"'))
    return rows
R={y:load(y) for y in (2026,2022)}
print({y:len(r) for y,r in R.items()})
cmap={'deputado':('6',2026),'senador':('5',2026),'senador2022':('5',2022),'governador':('3',2026),'presidente':('1',2026),'vice':('2',2026)}
res={};fuzzy=[];unm=[]
for k in keys:
    uf,cargo,nome=k.split('|',2)
    cd,y=cmap[cargo]
    c=[r for r in R[y] if r['SG_UF']==uf and r['CD_CARGO']==cd]
    if cargo=='senador2022': pass
    def pick(cs):
        e=[r for r in cs if 'ELEITO' in r['DS_SIT_TOT_TURNO'].upper() and 'NÃO' not in r['DS_SIT_TOT_TURNO'].upper() and 'NAO' not in N(r['DS_SIT_TOT_TURNO'])]
        return (e or cs)[0]
    m=[r for r in c if N(r['NM_URNA_CANDIDATO'])==N(nome)]
    if m: res[k]=(y,uf,pick(m)['SQ_CANDIDATO']); continue
    names=[N(r['NM_URNA_CANDIDATO']) for r in c]
    cl=difflib.get_close_matches(N(nome),names,n=1,cutoff=0.8)
    if cl:
        r=pick([r for r in c if N(r['NM_URNA_CANDIDATO'])==cl[0]]); res[k]=(y,uf,r['SQ_CANDIDATO']); fuzzy.append((k,r['NM_URNA_CANDIDATO'],r['DS_SIT_TOT_TURNO']))
    else: unm.append(k)
print(len(res),'unmatched',unm,'fuzzy',fuzzy)
json.dump(res,open(W+'/../tse_dl/res.json','w'))
