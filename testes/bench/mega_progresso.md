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

## Rodada 5

Entendimento dev: 56,3% -> 57,7% (1211/2100). Efeito no save (mega sim): 61% (ok 471 de 776). cenarios.json: 239/3/6, a única diferença para a base é acelera_obra/custo m24 (ok -> inconclusivo). Benches antigos: dev 160/220, dev2 92/121, cft_dev 89/90, cft_dev2 60/60, zoeira_dev 72/80, zoeira_dev2 48/50, final_dev 123/150, justica_dev 40/40. ui_v39 6/6 e ui_v38 41/0, 0 erros de página (rodados antes das últimas edições de padrão de tamanho); regressao.py sem erros de página na build final.

Mudanças gerais: verbo leve + substantivo de corte; ressalva 'exceto/salvo' tira o que vem depois; teto de proporção (limitar a N% da RCL) não é corte percentual; objetos defesa_gasto, teto_pessoal, fomento_pesquisa, pedagio_br, tarifa_zero_nac, dnit; cobertura ampla de normas em vigor (JN5, ~90 entradas com sujeito tolerante e verbos de criação/proibição, veto por valor, verbo de crescimento ou gratuidade); gírias (p, dnv, d+, naum, c); pergunta retórica com pedido embutido e promessas sem 'vamos' não viram comunicação; fala só como alvo de regra é descartada; propaganda/idade de bets não tira a outorga; limiar em R$ não impede escopo por produto; BPC deixou de ser objeto amplo; programa pequeno sem número fica abaixo de R$ 1 bi; valor explícito em R$ vira dotação (verbos subvencionar, recapitalizar, aportar, injetar, destinar); aporte público não é linha de crédito a 8%; corte amplo de gastos mantém o pacote de economia do catálogo; destino novo de um tributo carimbado não é zerado.

Diagnóstico do sim com custo zero (a pedido): no dev, medidas aprovadas de custo zero mostram D de prim em m12 com média +0,32 (v3.9) e +0,5 (v4), mediana 0 e +0,42; o desvio é pequeno e consistente com o canal macro (confiança/risco -> arrecadação) e não com semente de RNG, mas não foi isolado por experimento controlado.

| Tema | Entende v3.9 | Entende v4 | Δ | Efeito no save v3.9 | Efeito v4 | Δ |
|---|---|---|---|---|---|---|
| agro | 47% | 68% | +22 | 60% | 56% | -4 |
| assistencia_social | 27% | 53% | +27 | 79% | 84% | +5 |
| bets | 42% | 65% | +23 | 62% | 65% | +4 |
| ciencia_tecnologia | 32% | 53% | +22 | 64% | 72% | +8 |
| constituicao | 33% | 57% | +23 | 33% | 33% | +0 |
| corte_gastos | 27% | 48% | +22 | 82% | 100% | +18 |
| cultura_esporte | 28% | 48% | +20 | 62% | 62% | +0 |
| desemprego | 40% | 60% | +20 | 73% | 73% | +0 |
| direitos_humanos | 47% | 62% | +15 | 85% | 85% | +0 |
| dolar | 37% | 58% | +22 | 25% | 50% | +25 |
| economia | 35% | 50% | +15 | 50% | 57% | +7 |
| educacao | 28% | 45% | +17 | 86% | 79% | -7 |
| energia | 27% | 50% | +23 | 51% | 49% | -3 |
| games | 38% | 63% | +25 | 50% | 38% | -12 |
| grandes_empresas | 42% | 52% | +10 | 42% | 45% | +2 |
| ia | 52% | 72% | +20 | 50% | 36% | -14 |
| impostos | 18% | 47% | +28 | 35% | 46% | +11 |
| inflacao | 42% | 55% | +13 | 57% | 57% | +0 |
| infraestrutura | 43% | 65% | +22 | 75% | 75% | +0 |
| justica | 48% | 70% | +22 | 50% | 50% | +0 |
| medias_empresas | 32% | 57% | +25 | 57% | 67% | +10 |
| meio_ambiente | 28% | 58% | +30 | 67% | 64% | -3 |
| micro_empresas | 37% | 58% | +22 | 56% | 59% | +3 |
| moradia | 38% | 57% | +18 | 84% | 81% | -3 |
| previdencia | 33% | 53% | +20 | 60% | 55% | -5 |
| privatizacoes | 32% | 62% | +30 | 100% | 100% | +0 |
| regalias | 35% | 55% | +20 | 46% | 46% | +0 |
| relacoes_exteriores | 18% | 48% | +30 | 44% | 48% | +4 |
| saneamento | 40% | 62% | +22 | 50% | 67% | +17 |
| saude | 52% | 68% | +17 | 82% | 100% | +18 |
| seguranca | 23% | 52% | +28 | 73% | 64% | -9 |
| setor_privado | 38% | 63% | +25 | 67% | 67% | +0 |
| terras_raras | 30% | 67% | +37 | 38% | 38% | +0 |
| trabalhista | 53% | 70% | +17 | 50% | 39% | -11 |
| transporte | 27% | 47% | +20 | 64% | 75% | +11 |
| **TOTAL** | 36% | 58% | +22 | 60% | 61% | +1 |

| Tipo de proposta | v3.9 | v4 |
|---|---|---|
| bem | 39% | 55% |
| ja_lei | 23% | 92% |
| mal | 32% | 57% |
| outro | 28% | 61% |
| teor | 35% | 44% |
| varias | 32% | 39% |
| zoeira | 40% | 73% |

## Rodada 6

Entendimento dev: 57,7% -> 59,2% (1243/2100). Efeito no save: 61% (mega sim, sem mudança relevante). cenarios.json 239/3/6, única diferença para a base: acelera_obra/custo m24 (ok -> inconclusivo). Benches antigos: dev 160/220, dev2 93/121, cft_dev 89/90, cft_dev2 60/60, zoeira_dev 72/80, zoeira_dev2 48/50, final_dev 124/150, justica_dev 40/40. ui_v39 6/6 e ui_v38 41/0 sem erros de página na build final; regressao.py sem erros de página.

Mudanças: (1) recorte nomeado de tributo nunca leva mais de 12% da base (V4_NICHO_RX em contabiliza), beneficiário de tributo (micro/pequenas após IOF/ICMS) deixa de ser objeto, contribuinte facultativo/autônomo do INSS usa 1,5 bi por ponto; (2) obra e compra de equipamento de grande porte (ponte, ferrovia, metrô, porto, aeroporto, hospital, laboratório, satélite, ônibus, transmissão etc.) viram despesa única de 2x o valor anual mais custeio de 40%, ou o valor citado mais custeio de 10%; aporte em fundo com valor explícito é despesa única; privatização de estatal sem valor de mercado informado sempre dá receita única (3 bi, Correios 1 bi); (3) tabela de orçamentos de referência como objetos: FNDCT, defesa agropecuária, DNIT, Embrapa, Funai, ICMBio, Fust, INPE, IBGE, Anvisa; (4) ampliar, contratar ou criar nunca dá custo negativo; defesa e discricionárias deixam de ser objetos de economia; (5) atos administrativos (agência, bolsa de commodities, registro, visto, prazo de pagamento) custam zero ou no máximo R$ 0,4 bi; (6) instrumento: proibir, obrigar, multar, tipificar, taxar, mudar nome e criar órgão ou fundo sobem de ADM/COM para PL, exceto atos do Executivo (decreto, carro oficial, IPI/IOF). Resultado do ajuste de instrumento: +13 itens no dev.

| Tema | Entende v3.9 | Entende v4 | Δ | Efeito no save v3.9 | Efeito v4 | Δ |
|---|---|---|---|---|---|---|
| agro | 47% | 70% | +23 | 60% | 56% | -4 |
| assistencia_social | 27% | 53% | +27 | 79% | 84% | +5 |
| bets | 42% | 65% | +23 | 62% | 65% | +4 |
| ciencia_tecnologia | 32% | 60% | +28 | 64% | 72% | +8 |
| constituicao | 33% | 57% | +23 | 33% | 33% | +0 |
| corte_gastos | 27% | 48% | +22 | 82% | 100% | +18 |
| cultura_esporte | 28% | 48% | +20 | 62% | 62% | +0 |
| desemprego | 40% | 60% | +20 | 73% | 73% | +0 |
| direitos_humanos | 47% | 63% | +17 | 85% | 81% | -4 |
| dolar | 37% | 62% | +25 | 25% | 50% | +25 |
| economia | 35% | 48% | +13 | 50% | 57% | +7 |
| educacao | 28% | 43% | +15 | 86% | 79% | -7 |
| energia | 27% | 52% | +25 | 51% | 46% | -6 |
| games | 38% | 63% | +25 | 50% | 38% | -12 |
| grandes_empresas | 42% | 53% | +12 | 42% | 45% | +2 |
| ia | 52% | 75% | +23 | 50% | 36% | -14 |
| impostos | 18% | 47% | +28 | 35% | 46% | +11 |
| inflacao | 42% | 53% | +12 | 57% | 57% | +0 |
| infraestrutura | 43% | 67% | +23 | 75% | 75% | +0 |
| justica | 48% | 70% | +22 | 50% | 50% | +0 |
| medias_empresas | 32% | 63% | +32 | 57% | 67% | +10 |
| meio_ambiente | 28% | 67% | +38 | 67% | 69% | +3 |
| micro_empresas | 37% | 60% | +23 | 56% | 59% | +3 |
| moradia | 38% | 57% | +18 | 84% | 78% | -5 |
| previdencia | 33% | 53% | +20 | 60% | 57% | -2 |
| privatizacoes | 32% | 62% | +30 | 100% | 100% | +0 |
| regalias | 35% | 55% | +20 | 46% | 46% | +0 |
| relacoes_exteriores | 18% | 50% | +32 | 44% | 48% | +4 |
| saneamento | 40% | 65% | +25 | 50% | 67% | +17 |
| saude | 52% | 68% | +17 | 82% | 100% | +18 |
| seguranca | 23% | 57% | +33 | 73% | 73% | +0 |
| setor_privado | 38% | 68% | +30 | 67% | 67% | +0 |
| terras_raras | 30% | 67% | +37 | 38% | 38% | +0 |
| trabalhista | 53% | 70% | +17 | 50% | 46% | -4 |
| transporte | 27% | 52% | +25 | 64% | 79% | +14 |
| **TOTAL** | 36% | 59% | +24 | 60% | 61% | +2 |

| Tipo de proposta | v3.9 | v4 |
|---|---|---|
| bem | 39% | 58% |
| ja_lei | 23% | 92% |
| mal | 32% | 58% |
| outro | 28% | 61% |
| teor | 35% | 46% |
| varias | 32% | 42% |
| zoeira | 40% | 74% |

## Rodada 7

Entendimento dev 59,2% (1243/2100), efeito no save 61%. cenarios.json 239/3/6 (única diferença: acelera_obra/custo m24). Benches: dev 160/220, dev2 93/121, cft_dev 89/90, cft_dev2 60/60, zoeira_dev 72/80, zoeira_dev2 48/50, final_dev 124/150, justica_dev 40/40. ui_v39 6/6, ui_v38 41/0, regressao.py sem erros de página.

(A) Norma exata zera o valor marginal de todos os itens principais (exceto quando o texto traz valor explícito de R$ 100 mi ou mais), e as normas amplas do JN5 passam a carregar a exigência de LC (Imposto Seletivo/IBS/CBS, LRF, arcabouço, Kandir, Simples, ICMS de combustíveis/energia) ou de PEC (salário mínimo, imunidade de livros, reforma da Previdência, teto de gastos). Flags de PEC foram retiradas de licença-maternidade, CNJ, ZFM e Defensoria porque três benches esperam PL. (B) Texto com duas a quatro medidas que só rendeu uma leitura genérica é partido em orações com verbo de política (vírgula ou 'e' + infinitivo), cada uma é lida à parte e os itens somam; efeito líquido no dev: neutro, mas o custo de textos como 'fibra óptica, internet subsidiada e Wi-Fi' passa de 1,5 para 4,1 bi. (C) Gancho do banco de normas: V4_NORMAS_DB e v4CarregaNormas() em index.html (entradas [id, rx, ex, txt, flags], entram no fim de JN37, com o mesmo veto de crescimento) e testes/motor/normas_build.js, que lê scratchpad/normas/<tema>.js, roda a autoverificação (amostras/nao), descarta tema/amostras/nao e imprime as linhas compactas para colar. Testado com uma norma fictícia: 'criar' reconhece e vira PLP; 'dobrar' não.

| Tema | Entende v3.9 | Entende v4 | Δ | Efeito no save v3.9 | Efeito v4 | Δ |
|---|---|---|---|---|---|---|
| agro | 47% | 70% | +23 | 60% | 56% | -4 |
| assistencia_social | 27% | 53% | +27 | 79% | 84% | +5 |
| bets | 42% | 65% | +23 | 62% | 65% | +4 |
| ciencia_tecnologia | 32% | 62% | +30 | 64% | 72% | +8 |
| constituicao | 33% | 57% | +23 | 33% | 33% | +0 |
| corte_gastos | 27% | 48% | +22 | 82% | 100% | +18 |
| cultura_esporte | 28% | 48% | +20 | 62% | 62% | +0 |
| desemprego | 40% | 60% | +20 | 73% | 73% | +0 |
| direitos_humanos | 47% | 63% | +17 | 85% | 81% | -4 |
| dolar | 37% | 62% | +25 | 25% | 50% | +25 |
| economia | 35% | 48% | +13 | 50% | 57% | +7 |
| educacao | 28% | 42% | +13 | 86% | 79% | -7 |
| energia | 27% | 52% | +25 | 51% | 46% | -6 |
| games | 38% | 63% | +25 | 50% | 38% | -12 |
| grandes_empresas | 42% | 53% | +12 | 42% | 45% | +2 |
| ia | 52% | 75% | +23 | 50% | 36% | -14 |
| impostos | 18% | 47% | +28 | 35% | 46% | +11 |
| inflacao | 42% | 53% | +12 | 57% | 57% | +0 |
| infraestrutura | 43% | 67% | +23 | 75% | 75% | +0 |
| justica | 48% | 70% | +22 | 50% | 50% | +0 |
| medias_empresas | 32% | 63% | +32 | 57% | 67% | +10 |
| meio_ambiente | 28% | 67% | +38 | 67% | 69% | +3 |
| micro_empresas | 37% | 60% | +23 | 56% | 59% | +3 |
| moradia | 38% | 57% | +18 | 84% | 78% | -5 |
| previdencia | 33% | 52% | +18 | 60% | 55% | -5 |
| privatizacoes | 32% | 62% | +30 | 100% | 100% | +0 |
| regalias | 35% | 55% | +20 | 46% | 46% | +0 |
| relacoes_exteriores | 18% | 50% | +32 | 44% | 48% | +4 |
| saneamento | 40% | 65% | +25 | 50% | 67% | +17 |
| saude | 52% | 68% | +17 | 82% | 100% | +18 |
| seguranca | 23% | 57% | +33 | 73% | 73% | +0 |
| setor_privado | 38% | 68% | +30 | 67% | 83% | +17 |
| terras_raras | 30% | 67% | +37 | 38% | 38% | +0 |
| trabalhista | 53% | 70% | +17 | 50% | 46% | -4 |
| transporte | 27% | 53% | +27 | 64% | 79% | +14 |
| **TOTAL** | 36% | 59% | +24 | 60% | 61% | +2 |

| Tipo de proposta | v3.9 | v4 |
|---|---|---|
| bem | 39% | 58% |
| ja_lei | 23% | 92% |
| mal | 32% | 58% |
| outro | 28% | 61% |
| teor | 35% | 46% |
| varias | 32% | 43% |
| zoeira | 40% | 74% |

## Rodada 8

Banco externo de normas integrado em V4_NORMAS_DB: 858 normas (869 nos arquivos; 11 ids repetidos entre temas, a primeira ocorrência fica), index.html de 3,12 MB para 3,83 MB (+0,71 MB). Entendimento dev 59,3% (1246/2100), efeito no save 61%. cenarios.json 239/3/6 (única diferença: acelera_obra/custo m24). Benches: dev 161/220, dev2 93/121, cft_dev 89/90, cft_dev2 60/60, zoeira_dev 72/80, zoeira_dev2 48/50, final_dev 126/150, justica_dev 40/40. ui_v39 6/6, ui_v38 41/0, regressao.py sem erros de página. ja_lei no mega_dev: 94/102 antes e depois (o dev já estava coberto pelas rodadas anteriores; o ganho esperado está no holdout).

Auditoria de falsos redundantes (2911 itens: mega_dev e as 8 baterias antigas; 258 com jaVigente): (1) pedido só conta como 'repete a norma' quando não tem número nem R$ e tem no máximo uma palavra de conteúdo fora do trecho casado pelo ex (filtro no carregador); isso baixou os itens sem jaVigente com valor, instrumento ou tópico alterado de 175 para 62. (2) Com o motor real, 94 normas tiveram o ex removido (viram só 'norma relacionada'), pelo critério: o ex alterou custo, receita, receita única, instrumento ou tópico de item cujo gabarito não tem jaVigente (testes/motor/normas_exfalse.js faz a parte offline). Exceção deliberada: mp1394proibe, que mantém o ex porque a MP 1.394/2026 proíbe as bets. (3) Resultado final: 0 itens sem jaVigente com valor ou instrumento alterados, exceto a MP; restam 6 itens com custo diferente por efeito do vocabulário da correção ortográfica (esports, fibra óptica, assentimento prévio); o banco foi retirado da alimentação do vocabulário (flag baixa), o que não eliminou todo o efeito. Prioridade: entradas existentes de JN37 vêm antes (ordenação estável); entrada nova só passa à frente quando é exata e a antiga é só relacionada. Ids já existentes não são recarregados. Flags de instrumento derivadas da citação principal do texto: LC no rótulo => lc (86 normas), EC/CF/Constituição => pec (186), demais PL; os bens de dev com PEC/PLP continuam passando.

Bets e a MP 1.394/2026 (para decisão sua, a economia não foi mexida): o motor continua tratando as bets como atividade legal e tributada (outorga e GGR no catálogo: imposto_bets, bets_proibicao), então propostas de taxar ou aumentar outorga ainda rendem receita (por exemplo 'taxar bets em 30%' dá receita 2,4 bi e 'outorga maior' 6 bi) e o banco só acrescenta a nota 'Norma relacionada' com a MP. 'Proibir as bets' passa a sair como medida já em vigor (custo zero, topic 'já em vigor'). A linha de base de receita das bets no jogo (e as medidas de proibição com receita -8 do catálogo) não foi alterada; seria preciso decidir se a MP deve zerar a arrecadação de bets no cenário inicial e como tratar a conversão pelo Congresso.

| Tema | Entende v3.9 | Entende v4 | Δ | Efeito no save v3.9 | Efeito v4 | Δ |
|---|---|---|---|---|---|---|
| agro | 47% | 70% | +23 | 60% | 56% | -4 |
| assistencia_social | 27% | 53% | +27 | 79% | 84% | +5 |
| bets | 42% | 65% | +23 | 62% | 65% | +4 |
| ciencia_tecnologia | 32% | 62% | +30 | 64% | 72% | +8 |
| constituicao | 33% | 57% | +23 | 33% | 33% | +0 |
| corte_gastos | 27% | 48% | +22 | 82% | 100% | +18 |
| cultura_esporte | 28% | 48% | +20 | 62% | 54% | -8 |
| desemprego | 40% | 60% | +20 | 73% | 73% | +0 |
| direitos_humanos | 47% | 63% | +17 | 85% | 81% | -4 |
| dolar | 37% | 62% | +25 | 25% | 50% | +25 |
| economia | 35% | 48% | +13 | 50% | 57% | +7 |
| educacao | 28% | 42% | +13 | 86% | 79% | -7 |
| energia | 27% | 52% | +25 | 51% | 46% | -6 |
| games | 38% | 68% | +30 | 50% | 42% | -8 |
| grandes_empresas | 42% | 53% | +12 | 42% | 45% | +2 |
| ia | 52% | 75% | +23 | 50% | 41% | -9 |
| impostos | 18% | 47% | +28 | 35% | 46% | +11 |
| inflacao | 42% | 53% | +12 | 57% | 57% | +0 |
| infraestrutura | 43% | 67% | +23 | 75% | 75% | +0 |
| justica | 48% | 70% | +22 | 50% | 50% | +0 |
| medias_empresas | 32% | 63% | +32 | 57% | 67% | +10 |
| meio_ambiente | 28% | 67% | +38 | 67% | 69% | +3 |
| micro_empresas | 37% | 60% | +23 | 56% | 59% | +3 |
| moradia | 38% | 57% | +18 | 84% | 78% | -5 |
| previdencia | 33% | 52% | +18 | 60% | 55% | -5 |
| privatizacoes | 32% | 62% | +30 | 100% | 100% | +0 |
| regalias | 35% | 55% | +20 | 46% | 46% | +0 |
| relacoes_exteriores | 18% | 50% | +32 | 44% | 48% | +4 |
| saneamento | 40% | 65% | +25 | 50% | 67% | +17 |
| saude | 52% | 68% | +17 | 82% | 100% | +18 |
| seguranca | 23% | 57% | +33 | 73% | 73% | +0 |
| setor_privado | 38% | 68% | +30 | 67% | 83% | +17 |
| terras_raras | 30% | 67% | +37 | 38% | 38% | +0 |
| trabalhista | 53% | 70% | +17 | 50% | 46% | -4 |
| transporte | 27% | 53% | +27 | 64% | 75% | +11 |
| **TOTAL** | 36% | 59% | +24 | 60% | 61% | +2 |

| Tipo de proposta | v3.9 | v4 |
|---|---|---|
| bem | 39% | 58% |
| ja_lei | 23% | 92% |
| mal | 32% | 58% |
| outro | 28% | 61% |
| teor | 35% | 46% |
| varias | 32% | 43% |
| zoeira | 40% | 74% |

## Rodada 9

Entendimento dev 60,0% (1261/2100), efeito no save 63% (era 61%). cenarios.json 239/3/6 (única diferença: acelera_obra/custo m24). Benches: dev 161/220, dev2 92/121, cft_dev 89/90, cft_dev2 60/60, zoeira_dev 72/80, zoeira_dev2 48/50, final_dev 124/150, justica_dev 40/40. ui_v39 6/6, ui_v38 41/0, regressao.py sem erros de página.

Mudanças: (1) obra rodoviária ou ferroviária com quantidade em km vira despesa de capital (4 anos de obra em despesa única mais 10% de custeio no catálogo; no genérico R$ 3 mi/km, 8 para duplicar, 25 para ferrovia, e metrô/VLT/BRT ficam de fora); recuperar custa 10% e pavimentar 30% do custo de duplicar; sem quantidade o dev2 continua sem despesa única. (2) 'manutenção de toda a malha/rede/frota' entra na escala de massa e deixa de ser 0,6 bi. (3) Tributo temporário (até 12 meses) passa a ser receita do exercício em vez de despesa extraordinária: +7 itens no dev, nenhuma perda. (4) A leitura genérica de programa amplo mantém os tributos nomeados (IR, IR PJ, CBS/IBS, IPI, IOF, ICMS) e o escopo por produto vale também para IR; teto de recorte aceita 'R$ 0' do contexto. (5) Público restrito (agricultores familiares, pequenos produtores, comunidades etc.) lê 30% do pacote padrão; adicional por criança/gestante lê 20% do benefício. (6) 'acabar com a fila do BPC/SUS' vira ampliar o atendimento. (7) Carência de crédito não é carência previdenciária. (8) Sinônimos de saneamento e resíduos. (9) Anterioridade: imposto de exportação passa a vigorar sem anterioridade e a CIDE-combustíveis só tem noventena.

Achados sem alteração: (a) BNDESPar (once 110, prim -22 em m12): não é erro de sinal; o motor lança R$ 22 bi/ano de dividendos que a União deixa de receber (dado da fonte, 20% da carteira) contra receita única que só abate a dívida e não entra no resultado primário. Se o rendimento de 20% parecer alto, é o dado DIV_ATIVOS que deve ser revisto. (b) Anterioridade: o calendário já tratava IOF, II e blusinhas como sem anterioridade e IPI com noventena; faltavam exportação e CIDE-combustíveis, corrigidos. (c) Itens em que o gabarito marca 'controverso' para ampliação do BPC (idade, limite de renda) e renda mínima ficam em 'ok' porque cft_dev/dev2 esperam 'ok' para BPC; seria preciso separar por tipo de fonte.

| Tema | Entende v3.9 | Entende v4 | Δ | Efeito no save v3.9 | Efeito v4 | Δ |
|---|---|---|---|---|---|---|
| agro | 47% | 70% | +23 | 60% | 56% | -4 |
| assistencia_social | 27% | 57% | +30 | 79% | 84% | +5 |
| bets | 42% | 65% | +23 | 62% | 65% | +4 |
| ciencia_tecnologia | 32% | 62% | +30 | 64% | 72% | +8 |
| constituicao | 33% | 57% | +23 | 33% | 33% | +0 |
| corte_gastos | 27% | 50% | +23 | 82% | 100% | +18 |
| cultura_esporte | 28% | 48% | +20 | 62% | 54% | -8 |
| desemprego | 40% | 60% | +20 | 73% | 73% | +0 |
| direitos_humanos | 47% | 63% | +17 | 85% | 81% | -4 |
| dolar | 37% | 62% | +25 | 25% | 50% | +25 |
| economia | 35% | 48% | +13 | 50% | 62% | +12 |
| educacao | 28% | 42% | +13 | 86% | 79% | -7 |
| energia | 27% | 57% | +30 | 51% | 63% | +11 |
| games | 38% | 68% | +30 | 50% | 42% | -8 |
| grandes_empresas | 42% | 55% | +13 | 42% | 48% | +5 |
| ia | 52% | 73% | +22 | 50% | 36% | -14 |
| impostos | 18% | 52% | +33 | 35% | 51% | +16 |
| inflacao | 42% | 53% | +12 | 57% | 71% | +14 |
| infraestrutura | 43% | 68% | +25 | 75% | 75% | +0 |
| justica | 48% | 70% | +22 | 50% | 50% | +0 |
| medias_empresas | 32% | 65% | +33 | 57% | 67% | +10 |
| meio_ambiente | 28% | 67% | +38 | 67% | 67% | +0 |
| micro_empresas | 37% | 63% | +27 | 56% | 65% | +9 |
| moradia | 38% | 57% | +18 | 84% | 81% | -3 |
| previdencia | 33% | 52% | +18 | 60% | 52% | -7 |
| privatizacoes | 32% | 62% | +30 | 100% | 100% | +0 |
| regalias | 35% | 55% | +20 | 46% | 46% | +0 |
| relacoes_exteriores | 18% | 50% | +32 | 44% | 48% | +4 |
| saneamento | 40% | 68% | +28 | 50% | 67% | +17 |
| saude | 52% | 70% | +18 | 82% | 100% | +18 |
| seguranca | 23% | 57% | +33 | 73% | 73% | +0 |
| setor_privado | 38% | 67% | +28 | 67% | 83% | +17 |
| terras_raras | 30% | 67% | +37 | 38% | 46% | +8 |
| trabalhista | 53% | 70% | +17 | 50% | 46% | -4 |
| transporte | 27% | 53% | +27 | 64% | 75% | +11 |
| **TOTAL** | 36% | 60% | +24 | 60% | 63% | +3 |

| Tipo de proposta | v3.9 | v4 |
|---|---|---|
| bem | 39% | 59% |
| ja_lei | 23% | 92% |
| mal | 32% | 58% |
| outro | 28% | 61% |
| teor | 35% | 47% |
| varias | 32% | 44% |
| zoeira | 40% | 74% |

## Rodada 10

Treino conjunto em mega_dev (2100) + mega_dev2 (1400). Entendimento: mega_dev 60,8% (1276/2100; v3.9 36%), mega_dev2 52,4% (733/1400; v3.9 37,5%; no início da rodada 51,1%), conjunto 57,4% (2009/3500). Efeito no save: mega_dev_sim 63% (v3.9 60%); mega_dev2_sim 58% (v3.9 58%, sem ganho). cenarios.json 239/3/6 (única diferença: acelera_obra/custo m24). Benches: dev 159/220, dev2 92/121, cft_dev 89/90, cft_dev2 60/60, zoeira_dev 72/80, zoeira_dev2 48/50, final_dev 124/150, justica_dev 40/40. ui_v39 6/6, ui_v38 41/0, regressao.py sem erros de página.

Mecanismos (cada um conferido nos dois conjuntos): (1) medida condicional ('Se/Caso X passar de Y, fazer Z'): o balanço passa a carregar zero até o gatilho disparar (105 de 106 itens condicionais dos dois conjuntos esperam tudo nulo), com o valor pleno guardado em cond.pleno; o parecer na tela continua mostrando o valor esperado (pleno × chance), então o guarda do ui_v39 segue passando; o comparador escrito ('menos de', 'abaixo de') passa a mandar no sentido do gatilho, o que corrigia 'PIB crescer menos de 1%' lido como PIB > 1%. Ganho: +11 no mega_dev e +10 no mega_dev2. (2) Tabela de populações do Brasil para valor por pessoa sem quantidade (nascidos 2,5 mi, formandos 2,2 mi, alunos por nível, aposentados, pensionistas, MEIs, catadores, motoristas de app, professores, agentes comunitários, policiais, servidores etc.), consultada antes da tabela UNIV de universais; 'R$ 2 mil para cada criança nascida' passou de 72 bi para 2,5-2,8 bi. (3) Tributo de exportação com alíquota usa a base nomeada (soja 400, minério 250, petróleo 280, carne 110, milho 60, café 60 etc., R$ bi) em vez da base padrão de 8 bi; 'bens de informática' conta como produto no escopo do imposto de importação. (4) Redistribuir, remanejar e realocar sem aumento do total têm efeito fiscal nulo. (5) Bolsa para categoria pequena (atletas, artistas, cuidadores etc.) limitada a R$ 0,6 bi. (6) Instrumento: regra de sistema eleitoral, quórum de emendas, mandatos e composição dos Poderes sobe para PEC; Simples/MEI, ICMS, IBS/CBS e normas gerais tributárias dão PLP (instDet LC) em pedidos sem decreto; obrigações a distribuidoras e concessionárias ficam com ADM/DEC. (7) cf controverso para legalização de drogas, demarcação de terras indígenas e renda básica universal (nas contagens dos dois conjuntos 5 contra 1, 4 contra 0 e 4 contra 0). (8) Dados: dividendos do BNDESPar passam a R$ 7,7 bi (7% da carteira de R$ 110 bi) e a nota explica que os R$ 22,3 bi do BNDES vêm sobretudo do crédito; vender a carteira perde só os dividendos dela.

Não resolvido: 'ok' esperado como controverso em ampliações do BPC e outros benefícios (47 itens por conjunto), que dependem de regra sobre fonte de custeio e conflitam com cft_dev/dev2; custo alto em programas de bolsa sem público definido (ex.: 'bolsa p morador de rua' 20 bi contra 0,2-3); sim do mega_dev2 sem ganho porque a maior parte das diferenças está em itens pequenos e inconclusivos.

### mega_dev
| Tema | Entende v3.9 | Entende v4 | Δ | Efeito no save v3.9 | Efeito v4 | Δ |
|---|---|---|---|---|---|---|
| agro | 47% | 72% | +25 | 60% | 56% | -4 |
| assistencia_social | 27% | 62% | +35 | 79% | 84% | +5 |
| bets | 42% | 67% | +25 | 62% | 65% | +4 |
| ciencia_tecnologia | 32% | 62% | +30 | 64% | 72% | +8 |
| constituicao | 33% | 57% | +23 | 33% | 33% | +0 |
| corte_gastos | 27% | 52% | +25 | 82% | 100% | +18 |
| cultura_esporte | 28% | 50% | +22 | 62% | 54% | -8 |
| desemprego | 40% | 62% | +22 | 73% | 73% | +0 |
| direitos_humanos | 47% | 63% | +17 | 85% | 81% | -4 |
| dolar | 37% | 62% | +25 | 25% | 50% | +25 |
| economia | 35% | 52% | +17 | 50% | 62% | +12 |
| educacao | 28% | 43% | +15 | 86% | 79% | -7 |
| energia | 27% | 58% | +32 | 51% | 66% | +14 |
| games | 38% | 68% | +30 | 50% | 38% | -12 |
| grandes_empresas | 42% | 55% | +13 | 42% | 45% | +2 |
| ia | 52% | 73% | +22 | 50% | 36% | -14 |
| impostos | 18% | 52% | +33 | 35% | 51% | +16 |
| inflacao | 42% | 53% | +12 | 57% | 71% | +14 |
| infraestrutura | 43% | 70% | +27 | 75% | 75% | +0 |
| justica | 48% | 70% | +22 | 50% | 50% | +0 |
| medias_empresas | 32% | 68% | +37 | 57% | 67% | +10 |
| meio_ambiente | 28% | 67% | +38 | 67% | 67% | +0 |
| micro_empresas | 37% | 65% | +28 | 56% | 65% | +9 |
| moradia | 38% | 57% | +18 | 84% | 81% | -3 |
| previdencia | 33% | 52% | +18 | 60% | 52% | -7 |
| privatizacoes | 32% | 62% | +30 | 100% | 100% | +0 |
| regalias | 35% | 55% | +20 | 46% | 46% | +0 |
| relacoes_exteriores | 18% | 50% | +32 | 44% | 48% | +4 |
| saneamento | 40% | 68% | +28 | 50% | 67% | +17 |
| saude | 52% | 70% | +18 | 82% | 100% | +18 |
| seguranca | 23% | 55% | +32 | 73% | 73% | +0 |
| setor_privado | 38% | 67% | +28 | 67% | 83% | +17 |
| terras_raras | 30% | 67% | +37 | 38% | 46% | +8 |
| trabalhista | 53% | 70% | +17 | 50% | 46% | -4 |
| transporte | 27% | 53% | +27 | 64% | 75% | +11 |
| **TOTAL** | 36% | 61% | +25 | 60% | 63% | +3 |

| Tipo de proposta | v3.9 | v4 |
|---|---|---|
| bem | 39% | 59% |
| ja_lei | 23% | 92% |
| mal | 32% | 59% |
| outro | 28% | 62% |
| teor | 35% | 52% |
| varias | 32% | 44% |
| zoeira | 40% | 74% |

### mega_dev2
| Tema | Entende v3.9 | Entende v4 | Δ | Efeito no save v3.9 | Efeito v4 | Δ |
|---|---|---|---|---|---|---|
| agro | 30% | 48% | +18 | 45% | 41% | -3 |
| assistencia_social | 40% | 48% | +8 | 80% | 80% | +0 |
| bets | 38% | 60% | +22 | 46% | 46% | +0 |
| ciencia_tecnologia | 35% | 40% | +5 | 70% | 60% | -10 |
| constituicao | 55% | 68% | +12 | 100% | 100% | +0 |
| corte_gastos | 35% | 50% | +15 | 71% | 76% | +6 |
| cultura_esporte | 45% | 68% | +22 | 40% | 50% | +10 |
| desemprego | 40% | 52% | +12 | 60% | 67% | +7 |
| direitos_humanos | 35% | 48% | +12 | 88% | 62% | -25 |
| dolar | 42% | 65% | +22 | 50% | 38% | -12 |
| economia | 38% | 65% | +28 | 51% | 51% | +0 |
| educacao | 38% | 42% | +5 | 86% | 71% | -14 |
| energia | 28% | 38% | +10 | 50% | 42% | -8 |
| games | 35% | 52% | +18 | 47% | 47% | +0 |
| grandes_empresas | 28% | 30% | +2 | 37% | 40% | +3 |
| ia | 58% | 62% | +5 | 44% | 38% | -6 |
| impostos | 22% | 32% | +10 | 35% | 35% | +0 |
| inflacao | 20% | 45% | +25 | 88% | 100% | +12 |
| infraestrutura | 45% | 52% | +8 | 86% | 86% | +0 |
| justica | 42% | 55% | +12 | 80% | 60% | -20 |
| medias_empresas | 30% | 45% | +15 | 73% | 73% | +0 |
| meio_ambiente | 42% | 68% | +25 | 59% | 64% | +5 |
| micro_empresas | 35% | 62% | +28 | 65% | 73% | +8 |
| moradia | 40% | 48% | +8 | 80% | 64% | -16 |
| previdencia | 45% | 55% | +10 | 50% | 58% | +8 |
| privatizacoes | 38% | 65% | +28 | 50% | 50% | +0 |
| regalias | 30% | 40% | +10 | 45% | 45% | +0 |
| relacoes_exteriores | 32% | 45% | +12 | 58% | 58% | +0 |
| saneamento | 35% | 52% | +18 | 79% | 71% | -7 |
| saude | 45% | 65% | +20 | 100% | 100% | +0 |
| seguranca | 20% | 40% | +20 | 62% | 77% | +15 |
| setor_privado | 62% | 78% | +15 | 33% | 33% | +0 |
| terras_raras | 28% | 38% | +10 | 20% | 33% | +13 |
| trabalhista | 58% | 70% | +12 | 74% | 70% | -4 |
| transporte | 25% | 42% | +18 | 20% | 30% | +10 |
| **TOTAL** | 38% | 52% | +15 | 58% | 58% | -0 |

| Tipo de proposta | v3.9 | v4 |
|---|---|---|
| bem | 44% | 53% |
| ja_lei | 25% | 60% |
| mal | 29% | 44% |
| outro | 27% | 63% |
| teor | 31% | 51% |
| varias | 34% | 49% |
| zoeira | 47% | 58% |
