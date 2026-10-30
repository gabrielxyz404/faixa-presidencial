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

## Bateria `zoeira_dev.json` (propostas bizarras / de zoeira)
80 propostas informais (gírias, "kkk", emoji) como as de um vídeo de youtuber jogando: 36 `legal`, 24 `ilegal`, 20 `impossivel`. Mesmo formato e corretor, mais dois campos:
- `zoeira`: `legal` (bizarra mas permitida: deve ser processada normalmente e NÃO marcada como absurda, ex. Dia Nacional do Meme, mascote, hino por PL, feriado por lei, ministério por lei/MP), `ilegal` (fere lei ou CF, ex. promoção pessoal art. 37 §1º, capital por decreto art. 18 §1º, religião art. 5º VI; o motor deve apontar o veredito `cf`), `impossivel` (física ou fiscalmente impossível, ou resultado por decreto: o motor deve continuar marcando como absurda).
- `absurdo_esperado`: true só para `impossivel`. Nesses itens o corretor soma o critério `absurdo` (o campo `absurdo` do probe tem de ser verdadeiro). Nos itens `legal` soma `nao_absurdo` (o campo tem de ser falso). O relatório mostra os falsos positivos (legal marcado como absurda) e falsos negativos (impossível não marcada). Nos impossíveis as faixas de valor e instrumento são largas de propósito; o que vale é `absurdo`.
O probe passou a exportar `absurdo` e `generica`. O holdout correspondente (40 propostas: 18/12/10) fica fora do repositório.
```
python3 testes/motor/run_sandbox.py testes/motor/probe.py $S/cur testes/bench/zoeira_dev.json $S/zoeira_dev.json 8881
python3 testes/bench/score.py testes/bench/zoeira_dev.json $S/zoeira_dev.json
```

## Bateria `cft_dev2.json` (v3.7)
60 propostas novas (20 de Constituição, 20 de trabalho, 20 de previdência), escritas antes de mexer no motor da v3.7 e congeladas, no mesmo formato e com o mesmo corretor de `cft_dev.json`.
Serve para medir generalização: o motor da v3.7 foi desenvolvido olhando `cft_dev.json`, e `cft_dev2.json` só entrou depois para conferir o que não foi decorado.
```
python3 testes/motor/run_sandbox.py testes/motor/probe.py $S/cur testes/bench/cft_dev2.json $S/cft_dev2.json 8842
python3 testes/bench/score.py testes/bench/cft_dev2.json $S/cft_dev2.json
```

## Bateria `zoeira_dev2.json` (v3.8)
50 propostas novas de zoeira (22 `legal`, 15 `ilegal`, 13 `impossivel`), escritas e congeladas antes de mexer no motor da v3.8, no mesmo formato e com o mesmo corretor de `zoeira_dev.json`.
Placar antes da v3.8 (motor v3.7): 26,0% totalmente certos, `absurdo` 3/13, 1 falso positivo de absurdo. A v3.8 passou a ler o conteúdo (kkk, emoji e gíria deixaram de ser gatilho de absurdo).
```
python3 testes/motor/run_sandbox.py testes/motor/probe.py $S/cur testes/bench/zoeira_dev2.json $S/zoeira_dev2.json 8883
python3 testes/bench/score.py testes/bench/zoeira_dev2.json $S/zoeira_dev2.json
```

## Bateria `final_dev.json` (teste final, v3.8)
150 propostas novas escritas para o teste final do motor, no mesmo formato e com o mesmo corretor, mais o campo `tipo` (e `teor` / `zoeira`) para separar o placar:
- `bem` (40, duas por área), `mal` (30, digitadas como no celular: sem acento, abreviação, CAPS, gíria, frase corrida), `zoeira` (22: 9 legais, 7 ilegais, 6 impossíveis),
  `teor` (22: negação, condição, ironia/retórica, finalidade fonte+destino, público e região, prazo e valor; campo `teor`), `varias` (21: várias medidas no mesmo texto; o `tema` avalia a medida
  principal, a primeira e maior, e o custo/receita devem somar as partes) e `ja_lei` (15: norma já em vigor, com `jaVigente`).
- Convenções do gabarito: em `condicao` o efeito imediato esperado é ~0 (o gatilho não disparou); em `ja_lei` aceita-se `COM` como instrumento e custo a partir de 0 (a norma já vale); em obras o `unico`
  aceita 0 quando há `custo` (o motor pode contar como custo anual ou gasto único); as regex de `tema` toleram plural (`concess` pega `concessões`).
- Nos `impossivel`, o corretor exige `absurdo`, mas o campo `tema` falha quando o motor marca a frase como `vago` (convenção herdada de `zoeira_dev.json`).
```
python3 testes/motor/run_sandbox.py testes/motor/probe.py $S/cur testes/bench/final_dev.json $S/final_dev.json 8951
python3 testes/bench/score.py testes/bench/final_dev.json $S/final_dev.json
```
O holdout correspondente (150 propostas, mesma composição) fica fora do repositório.
