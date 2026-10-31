// uso: node testes/motor/normas_build.js <pasta com <tema>.js> [--teste] > linhas.js
// Lê module.exports=[{id,tema,rx,ex,txt,amostras,nao}], descarta tema/amostras/nao e imprime uma linha compacta por norma,
// no formato de V4_NORMAS_DB em index.html: [id, rx, ex, txt, flags]. Com --teste só roda a autoverificação (amostras casam, nao não casam).
const fs = require('fs'), path = require('path');
const dir = process.argv[2], teste = process.argv.includes('--teste');
const fold = (t) => String(t).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/\s+/g, ' ').trim();
const src = (r) => r instanceof RegExp ? r.source : String(r);
let ids = new Set(), erros = 0, n = 0;
for (const f of fs.readdirSync(dir).filter(x => x.endsWith('.js')).sort()) {
  const arr = require(path.resolve(dir, f));
  for (const e of arr) {
    n++;
    if (ids.has(e.id)) { console.error('id repetido: ' + e.id); erros++; continue; } ids.add(e.id);
    const rx = new RegExp(src(e.rx)), ex = e.ex === 'rx' || e.ex === '=' ? rx : (e.ex ? new RegExp(src(e.ex)) : null);
    for (const t of (e.amostras || [])) { const s = fold(t); if (!(ex ? ex.test(s) : rx.test(s))) { console.error(`[${e.id}] amostra não casa: ${t}`); erros++; } }
    for (const t of (e.nao || [])) { const s = fold(t); if (ex ? ex.test(s) : rx.test(s)) { console.error(`[${e.id}] 'nao' casou: ${t}`); erros++; } }
    if (!teste) {
      const fl = [e.lc ? 'lc' : '', e.pec ? 'pec' : '', e.inst === 'ADM' ? 'adm' : '', e.inst === 'DEC' ? 'dec' : ''].filter(Boolean).join(' ');
      const exs = e.ex === 'rx' || e.ex === '=' || (e.ex && src(e.ex) === src(e.rx)) ? '=' : (e.ex ? src(e.ex) : '');
      console.log('  ' + JSON.stringify([e.id, src(e.rx), exs, e.txt, fl]) + ',');
    }
  }
}
console.error(`${n} normas, ${erros} problemas`);
process.exit(erros ? 1 : 0);
