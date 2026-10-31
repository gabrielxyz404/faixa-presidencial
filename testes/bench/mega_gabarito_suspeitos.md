# Itens do gabarito de `mega_dev.json` que parecem errados ou inconsistentes

A bateria não foi editada. Cada item abaixo continua contando no placar; a lista serve para quem revisar o gabarito.

## 1. Instrumento `AUT` como única opção em pergunta ou ato interno (6 itens)
`AUT` é a autorização do Congresso (decreto legislativo). Para pergunta de estatística ou lista de siglas não existe instrumento; o esperado seria `COM`/`ADM` ou aceitar qualquer um.
- educacao: "Quantas escolas existem no Brasil?"
- relacoes_exteriores: "Quanto o Brasil exporta por ano?"
- seguranca: "Quantos presos existem no Brasil?"
- justica: "O que é o foro por prerrogativa de função?"
- justica: "STF, TSE, STJ, TST e STM"
- constituicao: "Não precisa de PEC, dá pra cortar privilégios do Congresso só por resolução das Casas" (resolução de cada Casa é ato interno, não autorização do Congresso)

## 2. Norma "já vigente" com faixa fiscal que contradiz a própria nota (4 itens)
O campo `jaVigente` diz que a medida já está em vigor (efeito marginal ~0), mas `custo`/`receita` exigem valor positivo.
- impostos: "Cobrar uma alíquota mínima de 10% de Imposto de Renda sobre rendimentos acima de R$ 600 mil por ano" (Lei 15.270/2025; receita [5, 40])
- impostos: "Criar o Imposto Seletivo sobre carros a combustão e 'bets' de apostas" (LC 214/2025; receita [1, 20])
- impostos: "Criar o cashback de IBS e CBS para famílias do CadÚnico em todos os alimentos e na conta de luz" (LC 214/2025; custo [3, 30])
- previdencia: "Proibir o acúmulo de aposentadoria com pensão, exceto o benefício de maior valor" (EC 103/2019; custo [-30, -1]). A EC 103 já limita o acúmulo; se o pedido é mais duro que a regra vigente, não é `ja_lei`.

## 3. Faixas de custo de itens impossíveis fora de escala (2 itens)
- zoeira: "Dar R$ 10 mil por mês a todos os brasileiros sem aumentar imposto e sem gerar inflação": custo [1000, 3000]. 213 milhões x R$ 120 mil por ano = ~R$ 25 trilhões; a faixa está ~10x abaixo.
- zoeira: "Pagar R$ 100 mil de aposentadoria para cada brasileiro sem aumentar nenhum imposto": custo [10000, 50000]; a conta bruta passa de R$ 250 trilhões.

## 4. Itens `impossivel` com faixa de +-100 mil bi (13 itens)
Nos `impossivel` as faixas de custo, receita e único são [-100000, 100000]: o critério de valor vira sempre verdadeiro e não mede nada. Não é erro de fato, mas esconde se o motor zerou ou inflou o valor.

## 5. Convenções que se contradizem entre baterias do mesmo repositório
- "Elevar o limite de renda do BPC para meio salário mínimo per capita" (mega_dev, cf = só `controverso`) x "Liberar BPC para famílias com renda de até meio salário mínimo por pessoa" (cft_dev, cf = só `ok`).
- "Privatizar a Petrobras" (mega_dev, cf = `controverso`) x "Vender 20% da Petrobras na bolsa" (dev2, cf = `ok`): são ações diferentes, mas o critério não está dito em lugar nenhum.
- Tratados: o corretor conta PL+AUT como `AUT`; em mega_dev os acordos comerciais aceitam `DEC`/`COM`/`PL` e nunca `AUT`, enquanto dev e final_dev aceitam `AUT` ("Sair do Mercosul": só `AUT`/`COM`).

## 6. Expressões `tema` quase sem poder de discriminação
O corretor casa o tópico com a regex única da lista; em vários itens ela é uma alternância de palavras genéricas ("ano", "brasil", "ja", "pra", "tem", "gasto"), então qualquer tópico minimamente relacionado passa. Exemplos: "Quanto o Brasil gasta com a Lei Rouanet por ano?" (`rouanet|gasta|gasto|ano|renuncia`), "Sem fazer nenhuma desapropriação, ampliar a reforma agrária comprando terra..." (`sem fazer|desapropria...`).

Total: 25 itens listados nos números 1 a 4 (6 + 4 + 2 + 13), mais as inconsistências de convenção dos números 5 e 6.

## Rodada 5
- "Acabar com a escala 6x1" e variações (3 itens de trabalhista): o gabarito espera PEC nova, mas o jogo trata a escala 6x1 como já extinta pela EC 141/2026; conflito de premissa entre bateria e jogo.
- Itens com `unico` preenchido para obras pequenas (instalar incubadoras, carregadores) e `unico` nulo para obras equivalentes: critério de capital inconsistente, por isso o motor não modela despesa única de obra.
