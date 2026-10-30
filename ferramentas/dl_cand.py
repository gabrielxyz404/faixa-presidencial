import sys,os,urllib.request,zipfile
d=sys.argv[1]
for y in (2026,2022):
    out=os.path.join(d,f"cand{y}"); os.makedirs(out,exist_ok=True)
    z=os.path.join(out,"c.zip")
    urllib.request.urlretrieve(f"https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{y}.zip",z)
    zipfile.ZipFile(z).extractall(out)
    print(y,os.listdir(out),os.path.getsize(z))
