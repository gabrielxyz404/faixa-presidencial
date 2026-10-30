# Bench de propostas do motor

Gabarito para medir o quanto o motor (`analisaLocal` em `index.html`) entende propostas em português livre.
`dev.json` tem 220 propostas (11 por área, 20 áreas). Existe um conjunto reservado (holdout, 100 propostas) fora do repositório.

## Formato de cada item de `dev.json`
`t` (frase), `area`, `tema` (lista de regex em minúsculas sem acento, todas devem casar com o tópico normalizado do motor),
`dir` (aumenta, reduz, cria, extingue, proibe, obriga, regula, libera, transfere, outro), `inst` (aceitos: COM, ADM, DEC, MP, PL, PLP, PEC, AUT),
`custo` / `receita` / `unico` (faixa [min, max] em R$ bi/ano, ou null = |valor| < 1), `jaVigente` (norma que já vale em 2026, ou null),
`cf` (vereditos aceitos: ok, controverso, inconstitucional), `nota` (base jurídica e ordem de grandeza).

Convenções de sinal do motor: `cost` positivo = gasto novo, negativo = economia; `rev` positivo = receita nova, negativo = renúncia (isentar X => receita negativa).
`unico` é comparado ao maior valor absoluto entre `once` e `extra`.

## Critérios (1/0 cada)
- tema: o tópico casa todas as regex e `vago` é falso.
- direção: só pega inversão óbvia (reduz/extingue/proibe com "aumento/ampliação/elevação" no tópico, e aumenta com "redução/corte/fim").
- instrumento: PL+instDet LC conta como PLP; PL+instDet AUT conta como AUT.
- valor: custo, receita e único têm de cair nas faixas (null exige |valor| < 1).
- cf: veredito do STF/AGU do motor está entre os aceitos.
- jaVigente (só nos itens com norma): o tópico, `cfTxt` ou `tecnico` cita o número da norma ou "já em vigor/vigente/instituída/extinta".
- "Totalmente certo": todos os critérios aplicáveis, inclusive jaVigente. O relatório mostra também a taxa só com os 5 critérios.

Faixas são largas (fator 3-5x) para pegar erro de ordem de grandeza e de sinal, não precisão. Quando o fato jurídico era incerto, usou-se jaVigente null.

## Como rodar
```
S=<pasta de trabalho>
python3 testes/motor/run_sandbox.py testes/motor/probe.py $S/cur testes/bench/dev.json $S/bench_dev.json 8801
python3 testes/bench/score.py testes/bench/dev.json $S/bench_dev.json [--json $S/relatorio.json]
```
A saída traz % por critério, % médio, % de itens totalmente certos, totais por área, falsos "já vigente" (informativo) e a lista de itens errados com o motivo.
Não ajuste o motor olhando o holdout; use `dev.json` para desenvolver.

## Bateria `cft_dev.json` (Constituição, trabalho e previdência)
90 propostas (30 de Constituição e organização do Estado, 30 de trabalho/CLT/sindicatos/FGTS, 30 de previdência/servidores/BPC), mesmo formato e corretor. Inclui reformas grandes (capitalização, idade mínima, desvinculação do mínimo,
unicidade sindical, PEC com cláusula pétrea), matérias de lei complementar (CF 7º I, 41 §1º III, 93, 146, 148, 154 I, 192) e normas já vigentes (Lei 12.506/2011, 13.467/2017, 13.429/2017, 14.611/2023, 11.770/2008, LC 150/2015, EC 103/2019 etc.).
O holdout correspondente (45 propostas, 15 por área) fica fora do repositório.
```
python3 testes/motor/run_sandbox.py testes/motor/probe.py $S/cur testes/bench/cft_dev.json $S/cft_dev.json 8841
python3 testes/bench/score.py testes/bench/cft_dev.json $S/cft_dev.json
```
