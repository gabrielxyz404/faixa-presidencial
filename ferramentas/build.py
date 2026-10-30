import sys,os,json,io,zipfile,urllib.request,base64
from PIL import Image
W,D=sys.argv[1],sys.argv[2]
res=json.load(open(D+'/res.json'))
orig=json.load(open(W+'/fotos.orig.json',encoding='utf-8'))
need={}
for k,(y,uf,sq) in res.items(): need.setdefault((y,uf),{})[sq]=k
out={};miss=[]
for (y,uf),m in sorted(need.items()):
    d=f'{D}/fotos{y}'; os.makedirs(d,exist_ok=True); z=f'{d}/{uf}.zip'
    if not os.path.exists(z):
        urllib.request.urlretrieve(f'https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes{y}/fotos/foto_cand{y}_{uf}_div.zip',z)
    zf=zipfile.ZipFile(z)
    idx={}
    for n in zf.namelist():
        b=os.path.basename(n); idx.setdefault(b.rsplit('.',1)[0].upper().removesuffix('_DIV'),n)
    for sq,k in m.items():
        n=idx.get('F'+uf+sq) or idx.get(sq) or next((v for kk,v in idx.items() if kk.endswith(sq)),None)
        if not n: miss.append(k); continue
        im=Image.open(io.BytesIO(zf.read(n))).convert('RGB')
        W0,H0=im.size; t=112/140
        if W0/H0>t: nw=round(H0*t); box=((W0-nw)//2,0,(W0-nw)//2+nw,H0)
        else: nh=round(W0/t); box=(0,(H0-nh)//2,W0,(H0-nh)//2+nh)
        im=im.crop(box).resize((112,140),Image.LANCZOS)
        bf=io.BytesIO(); im.save(bf,'JPEG',quality=82)
        out[k]='data:image/jpeg;base64,'+base64.b64encode(bf.getvalue()).decode()
    print(y,uf,len(m),flush=True)
print('missing',miss)
for k in miss: out[k]=orig['fotos'][k]
fotos={k:out[k] for k in orig['fotos']}
fonte="TSE — Portal de Dados Abertos (fotos de registro de candidatura, 2022 e 2026)"
json.dump({'fonte':fonte,'fotos':fotos},open(W+'/fotos.json','w',encoding='utf-8'),ensure_ascii=False)
bad=0
for k,v in fotos.items():
    if k in miss: continue
    im=Image.open(io.BytesIO(base64.b64decode(v.split(',',1)[1])))
    if im.size!=(112,140) or len(im.getbands())!=3: bad+=1
print('bad',bad,'n',len(fotos),'size',os.path.getsize(W+'/fotos.json'))

