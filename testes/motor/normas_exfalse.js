// uso: node exfalse.js linhas.js  -> imprime ids cujo ex (com o filtro de resto) casa em itens sem jaVigente
const fs=require('fs');
const fold=(t)=>String(t).normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/\s+/g,' ').trim();
const OK=/^(?:para|sobre|todos|todas|brasil|brasileiro|brasileira|federal|nacional|programa|politica|governo|publico|publica|publicos|publicas|criar|instituir|garantir|oferecer|obrigar|exigir|proibir|estabelecer|implantar|assegurar|nacionais|pessoas|quem|cada|aqui|logo|tambem|voce|porque|pois|ainda|muito|deve|devia|deveria|precisa|precisamos|queremos|quero|estado|estados|municipios|pais)$/;
const NEX=new RegExp(process.argv[3]||'a^');
const lines=fs.readFileSync(process.argv[2],'utf8').split('\n').filter(x=>x.trim().startsWith('['));
const db=lines.map(l=>JSON.parse(l.trim().replace(/,$/,'')));
const items=JSON.parse(fs.readFileSync(process.argv[4],'utf8')); // [{t,vig}]
const bad={};let tp=0;
for(const e of db){
  if(!e[2]) continue;
  const rx=new RegExp(e[1]), ex0=e[2]==='='?rx:new RegExp(e[2]);
  for(const i of items){
    const t=fold(i.t); const m=ex0.exec(t);
    if(!m||/\d|r\$/.test(t)) continue;
    const resto=(t.slice(0,m.index)+' '+t.slice(m.index+m[0].length)).split(/[^a-z]+/).filter(w=>w.length>=5&&!OK.test(w));
    if(resto.length>1) continue;
    if(NEX.test(t)) continue;
    if(i.vig) tp++; else (bad[e[0]]=bad[e[0]]||[]).push(i.t.slice(0,70));
  }
}
console.error('hits em itens vigentes:',tp,' normas com falso exato:',Object.keys(bad).length);
console.log(JSON.stringify(bad));
