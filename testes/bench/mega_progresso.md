# Progresso do treino do motor para a v4 (bateria mega_dev, 2100 itens, 35 temas)

Pasta de trabalho (fora do repositório): `/tmp/claude-0/-home-user-faixa-presidencial/4e54b5af-4e6e-57af-8b75-cf27fd2fc847/scratchpad/v4w/`
(scripts: `probe4.sh` roda a bateria em 4 partes, `run.sh <tag>` copia o index.html e mede, `benches.sh <pasta> <tag>` roda as 8 baterias antigas,
`dbg.py "frase"...` mostra o que o motor leu, `fail2.py <probe.json> <tema> <de> <ate>` lista erros por tema). O probe (`testes/motor/probe.py`) passou a
exportar também `objs`, `gen`, `calc`, `its`, `nv` (depuração; o corretor ignora).

Linha de base medida no início: mega_dev 749/2100 = 35,7%; dev 65,5; dev2 74,4; cft_dev 98,9; cft_dev2 100; zoeira_dev 80,0; zoeira_dev2 96,0; final_dev 76,7; justica_dev 100.

## Rodada 1 (causas gerais)
- Instrumento: sem urgência declarada, MP vira PL (`V4_URGENTE`, em `escolheInst`). inst 77,1 -> 80,2.
- Consulta: pergunta de informação ("quanto custa...?", "o que é...?") e menção solta (sigla ou nome de área sem verbo) viram ato de comunicação,
  sem despesa/receita, tópico não vago (`v4Consulta`, `A.consulta`).
- Tributo com base nomeada ("imposto de 10% sobre compras dentro de jogos"): a alíquota sai e o que vem depois de "sobre" é o recorte; a conta usa uma base de
  nicho (`V4_NICHO` = R$ 8 bi), não os R$ 2,3 tri dos impostos.
- Normas já em vigor (`JN4`, ~140 entradas por tema, empurradas em `JN37`): `rx` = assunto, `ex` = pedido repete a norma (redundante, custo zero, tópico da
  frase), `nex` = sinal de que vai além do texto vigente. `inst`/`lc`/`pec` por entrada quando a natureza da norma pede ato do CMN, LC ou EC. `v4Cobre` garante que o
  tópico cita o assunto central.
- Placar após a rodada 1: mega_dev 855/2100 = 40,7%; dev 66,4; dev2 76,9; cft 98,9/100; zoeira 80,0/96,0; final_dev 78,0; justica 100.

## Rodada 2 (leitura, impossível, ilegal, tamanhos padrão)
- `GEN_PARAR` não corta mais em ponto de milhar ("1.000 novos CRAS" voltou a ser lido). Verbos que faltavam e molduras de desejo ("quero", "tem que ter", "mais X", "menos X")
  entraram em `GV35` (bloco `// v4`); `mandar` ficou de fora porque trocava o objeto do catálogo (Força Nacional).
- Impossível (`v4Impossivel`, em `absurdoGeral`): resultado ordenado por decreto em prazo curto, restrições que se anulam, valores fora da escala, objetos cósmicos.
  `A.absRes` zera despesa e receita (nada é gasto nem arrecadado); a frase impossível lida não é "vaga". absurdo: 30 falsos negativos -> 6.
- Ilegal por princípio (`Z38_IL.push`, ~20 entradas): confisco sem indenização, perseguição política, favorecimento, tributo confiscatório ou sem fato gerador,
  pena vedada, discriminação, sigilo fiscal, calote, decreto contra lei, mensalidade em escola pública etc. cf 91,1 -> 92,5.
- Destinação ("taxar X para financiar o Bolsa Família"): a despesa de programa que já existe, sem valor novo, não conta (só a receita da fonte).
- Tamanhos sem número no texto: leitura genérica = programa pequeno (R$ 0,6 bi, `V4_GEN_PEQ`) salvo benefício/obra em massa (`V4_MASSA`); objeto do catálogo
  com texto de ação pontual = 15% do pacote padrão (`V4_CAT_PEQ`, piso R$ 0,5 bi).
- Instrumento: ADM vira PL para programa com despesa nova que não é ato interno (`V4_EXEC`); política externa genérica = ADM.
- Tributos: `reonerar` é aumento; escopo por produto também para CBS/IBS e ICMS; recorte nomeado ("sobre compras dentro de jogos").
- Placar após a rodada 2: mega_dev 1031/2100 = 49,1%; dev 69,5; dev2 76,0; cft 98,9/100; zoeira 86,2/96,0; final_dev 78,7; justica 100.

## Rodada 3 (tópico completo, desejo livre, constituição, exterior, tributos)
- `v4Completa`: o tópico traz também o assunto que o objeto do catálogo deixou de fora (só da oração principal; só quando faltam 2+ termos ou metade). tema 89,9 -> 97,0.
- Leitura livre de desejo ou ordem solta (sem verbo que o catálogo conheça, 4+ palavras, sem retórica): vira item genérico (G se há gasto, R se é norma; venda se o verbo
  é privatizar/vender) em vez de "vago". Perguntas e menção solta curta continuam consulta (sem custo).
- Constituição (`V37_NORMAS.push`): suplente, artigo da CF, tramitação urgente, referendo, datas de eleição, prazo ao Congresso, número de deputados (LC), federalizar polícia,
  bipartidarismo, competência tributária. Política externa genérica = ADM/DEC; `abertura_comercial` = DEC; objeto novo `reintegra`.
- Tributos: `v4Tributos` (isenção dada/ampliada reduz o tributo; deduções e tabela do IR; alíquota-alvo da CBS/IBS; parte administrativa da reforma sem custo), limiar
  ("acima de R$ 50 milhões" não é o valor do tributo), "de R$ 200 para R$ 300" vira um valor com referência, PIS/Cofins da gasolina deixa de virar fonte.
- Sim: o texto do tópico entra na escolha dos famosos que comentam (xFamosos), então mudar o tópico muda os comentários e pode deslocar cenários no limite do
  limiar (acelera_obra, bf_pl); o tópico só é completado quando faltam termos de verdade.
- Placar após a rodada 3: mega_dev 1118/2100 = 53,2%; dev 71,4; dev2 76,0; cft 98,9/100; zoeira 91,2/96,0; final_dev 82,0; justica 100.

## Rodada 4 (CF, tributos, exterior, ministros)
- `CF35.push`: 20 gatilhos de controvérsia constitucional (privatizar Correios/nuclear/EBC, IPTU pela União, BPC, ordem ao Banco Central, cota de exportação, nacionalidade,
  reconhecimento facial, tribunal de exceção, imposto em dólar, RPPS, pensão de filhas, auxílio a categoria etc.). cf 92,6 -> 94,0. BPC "meio salário mínimo" e venda
  parcial da Petrobras ficaram de fora porque cft_dev e dev2 esperam `ok`.
- Política externa (`V4_EXTERIOR`): ADM, sem tributo, salário nem lei. Tributo de estado ou município sem dizer que o ente local age = PL com LC.
- `v4Tributos` também retira "saúde e educação" como gasto quando só qualificam o tributo ("ISS de serviços de saúde e educação").
- Objetos novos: `discricionarias`, `reintegra`; `imposto_exportacao` com base de R$ 200 bi; `contingenciamento` deixou de ser receita única (é economia de despesa).
- Ministros: o validador `minValida` compara o instrumento de cada ideia com o do modelo (MIN_BANCO); a regra ADM->PL ignora textos de "ministério/portaria/ato" e
  `abertura_comercial` volta a ADM com "portaria". Modelos válidos: 70 (v3.9) -> 73.
- Sim: o número de chamadas a analisar (ANALISE_SEQ) entra no id da proposta, e o id semeia votos e famosos; mexer na leitura desloca cenários no limiar
  (acelera_obra m24 'sobe', bf_pl m24 'persiste'). Último resultado de cenarios.json: 239 ok / 3 falha / 6 inconclusivo (base 240/3/5).
- Placar após a rodada 4: mega_dev 1162/2100 = 55,3%; dev 71,8; dev2 76,0; cft 98,9/100; zoeira 90,0/96,0; final_dev 82,0; justica 100.

## Rodada final (v4 fechado)

Entendimento dev: 36% (v3.9) -> 56% (v4). Efeito no save (mega sim): 60% -> 60% (ok 462->465 de 776). cenarios.json: 239 ok / 3 falha / 6 inconclusivo (base 240/3/5; diferenca = acelera_obra m24, ruido caotico). Benches antigos todos >= linha de base; ui_v39/ui_v38 sem erros de pagina; regressao.py sem erros de pagina.

| Tema | Entende v3.9 | Entende v4 | Δ | Efeito no save v3.9 | Efeito v4 | Δ |
|---|---|---|---|---|---|---|
| agro | 47% | 67% | +20 | 60% | 56% | -4 |
| assistencia_social | 27% | 52% | +25 | 79% | 82% | +3 |
| bets | 42% | 60% | +18 | 62% | 65% | +4 |
| ciencia_tecnologia | 32% | 45% | +13 | 64% | 64% | +0 |
| constituicao | 33% | 57% | +23 | 33% | 33% | +0 |
| corte_gastos | 27% | 40% | +13 | 82% | 88% | +6 |
| cultura_esporte | 28% | 43% | +15 | 62% | 62% | +0 |
| desemprego | 40% | 62% | +22 | 73% | 73% | +0 |
| direitos_humanos | 47% | 60% | +13 | 85% | 85% | +0 |
| dolar | 37% | 58% | +22 | 25% | 50% | +25 |
| economia | 35% | 48% | +13 | 50% | 57% | +7 |
| educacao | 28% | 47% | +18 | 86% | 79% | -7 |
| energia | 27% | 50% | +23 | 51% | 49% | -3 |
| games | 38% | 63% | +25 | 50% | 38% | -12 |
| grandes_empresas | 42% | 52% | +10 | 42% | 45% | +2 |
| ia | 52% | 70% | +18 | 50% | 36% | -14 |
| impostos | 18% | 45% | +27 | 35% | 49% | +14 |
| inflacao | 42% | 55% | +13 | 57% | 57% | +0 |
| infraestrutura | 43% | 63% | +20 | 75% | 75% | +0 |
| justica | 48% | 70% | +22 | 50% | 50% | +0 |
| medias_empresas | 32% | 57% | +25 | 57% | 67% | +10 |
| meio_ambiente | 28% | 57% | +28 | 67% | 64% | -3 |
| micro_empresas | 37% | 57% | +20 | 56% | 56% | +0 |
| moradia | 38% | 57% | +18 | 84% | 81% | -3 |
| previdencia | 33% | 52% | +18 | 60% | 55% | -5 |
| privatizacoes | 32% | 62% | +30 | 100% | 100% | +0 |
| regalias | 35% | 55% | +20 | 46% | 38% | -8 |
| relacoes_exteriores | 18% | 50% | +32 | 44% | 48% | +4 |
| saneamento | 40% | 62% | +22 | 50% | 67% | +17 |
| saude | 52% | 68% | +17 | 82% | 100% | +18 |
| seguranca | 23% | 52% | +28 | 73% | 64% | -9 |
| setor_privado | 38% | 63% | +25 | 67% | 67% | +0 |
| terras_raras | 30% | 65% | +35 | 38% | 38% | +0 |
| trabalhista | 53% | 68% | +15 | 50% | 39% | -11 |
| transporte | 27% | 40% | +13 | 64% | 75% | +11 |
| **TOTAL** | 36% | 56% | +21 | 60% | 60% | +0 |

| Tipo de proposta | v3.9 | v4 |
|---|---|---|
| bem | 39% | 54% |
| ja_lei | 23% | 92% |
| mal | 32% | 55% |
| outro | 28% | 60% |
| teor | 35% | 46% |
| varias | 32% | 37% |
| zoeira | 40% | 73% |

Abaixo de 50% ao parar: ciencia_tecnologia 45, corte_gastos 40, cultura_esporte 43, economia 48, educacao 47, impostos 45, transporte 40.
