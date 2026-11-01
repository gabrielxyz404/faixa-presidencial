# Comércio exterior: transmissão de preços (antes x depois)

Medição: `testes/motor/comex_transmissao.py` (base: `med3.py`), 12 sementes x 18 meses, com a ação e sem ela, mesmo ruído nos dois braços.
Tabela gerada por `testes/motor/comex_transmissao_rel.py antes.json depois.json`. "antes" = `motor-v3.5` (6a1ad16); "depois" = esta branch.
Cada linha é a diferença média entre a partida com a ação e a mesma partida sem ela. Os grupos têm ruído de ±0,3 ponto (as partidas divergem por eventos sorteados), então leia a direção e a ordem de grandeza.

## O que mudou

- Pesos efetivos no IPCA (estimativas POF/IBGE, com derivados): trigo 2,0% x repasse 60% = 1,2%; leite 2,0% x 80% = 1,6%; arroz 0,75% x 100%; remédio 3,2% (igual). A prévia e a coluna "se fechar" usam a mesma conta (agora com o repasse de 0,6 que o motor sempre aplicou).
- Grupos reagem ao preço interno de pão, leite, arroz, carne, remédio, diesel e fertilizantes: só ao que o jogador provocou (preço com o contrato/ato menos o preço sem eles) mais choques de mercado muito grandes. Limiar de 1% contra uma referência que alcança o preço novo em ~5 meses (decaimento) e teto de 0,6 ponto por grupo por mês. Manchete ocasional no feed, nas notícias do Comércio e no balanço.
- Fertilizantes: peso indireto 0,7% (potássio, ureia) e 0,6% (fosfatados) nos alimentos, com defasagem de 6 a 9 meses (buffer de preços), mais custo do agro (grupo agro, `C.mac.agro` e um pouco de PIB).
- Diesel: efeito indireto de 1,2% no frete, defasagem de 1 a 3 meses; caminhoneiros, apps e agro reagem. O mercado de derivados já pesava 5,5% (diesel direto ≈ 0,3%); isso não mudou.
- Remédio: aposentados reagem com coeficiente maior (0,28 contra 0,05 a 0,22 dos demais itens).
- Instrumentos para trigo, leite e arroz (Comprar do produto, seção Abastecimento, 1 ação cada): TEC zero (3, 6 ou 12 meses, revogável), Conab (compra/venda, estoque em meses e toneladas), crédito ao produtor (efeito em 6 a 12 meses) e leilão de importação (1 a cada 6 meses). Prévia = mesma função que aplica (estado temporário + `icFlow` no mês do pico).
- Dano ao produtor: importar barato derruba a produção nacional (`cut`), com limiar de 0,8% e reação maior nos itens básicos; trigo e arroz também derrubam a aprovação do Sul.

## Resultados (mês 12 de cada cenário; tabela completa abaixo)

| cenário | preço interno | termo IPCA comex (pp) antes -> depois | aprovação | grupos principais |
|---|---|---|---|---|
| trigo, contrato típico | -3,7% | -0,015 -> -0,026 | +0,19 | periferia +1,0, aposentados +0,6, agro -1,1 |
| leite | -0,4% | -0,003 -> -0,004 | ≈ 0 | quase nada (contrato pequeno para o mercado) |
| arroz | -0,6% | -0,004 -> -0,003 | ≈ 0 | quase nada |
| eletrônicos | -3,0% | igual | igual | igual |
| diesel (EUA) | +0,1% | +0,004 -> +0,005 | ≈ 0 | ≈ 0 |
| medicamentos | +3,0% | igual | -0,04 -> -0,13 | aposentados -0,06 -> -0,67 |
| potássio, típico | -4,0% | 0 -> -0,014 | +0,04 | agro +0,9 |
| potássio, 4x e 15% abaixo | -14,5% | 0 -> -0,055 (-0,06 nos meses 10 a 14) | +0,10 | agro +2,3 |
| TEC zero arroz (12 meses) | -3,2% | -0,014 | +0,08 | periferia +0,6, agro -1,2, produção -3% |
| Conab vende 0,5 mês | queda que se dissipa | -0,001 | +0,08 | periferia +0,4 |
| leilão arroz | -8% no mês, -0,7% no 12º | -0,003 | -0,12 | agro -1,7, produção -2,5% |
| crédito arroz | -2,3% (só após 6 a 12 meses) | -0,010 | +0,07 | periferia +0,3 |

## Save novo sem ações

Meses 1 a 12, controle antes x depois (mesma semente): médias em 12 sementes praticamente iguais (ver o fim da tabela). As diferenças individuais maiores vêm de divergência caótica de eventos sorteados (uma pequena mudança no IPCA muda um evento de crise), não de efeito sistemático.

## Equilíbrio (`balance2.py` adaptado: `basicos_baratos` = um contrato barato por mês de um básico, TEC zero 12 meses, Conab, leilão e crédito em todos os básicos; 4 sementes x 48 meses)

| estratégia | versão | aprovação m6 | m12 | m24 | m36 | m48 | média m12–m48 | rodadas encerradas antes do fim | dívida/PIB final |
|---|---|---|---|---|---|---|---|---|---|
| omisso | antes | 51.4 | 46.4 | 37.5 | 30.0 | nan | nan | 4/4 | 95 |
| omisso | depois | 50.6 | 43.2 | 33.5 | 32.8 | nan | nan | 4/4 | 95 |
| moderado | antes | 50.6 | 47.8 | 51.5 | 53.8 | 49.7 | 50.7 | 0/4 | 94 |
| moderado | depois | 49.4 | 52.0 | 51.5 | 53.1 | 49.2 | 51.4 | 0/4 | 96 |
| moderado_forca | antes | 50.2 | 51.8 | 53.5 | 55.8 | 51.0 | 53.0 | 0/4 | 95 |
| moderado_forca | depois | 49.9 | 53.7 | 51.5 | 55.1 | 52.3 | 53.1 | 0/4 | 96 |
| basicos_baratos | antes | 50.8 | 52.6 | 50.0 | 53.8 | 52.4 | 52.2 | 0/4 | 95 |
| basicos_baratos | depois | 51.8 | 54.7 | 48.9 | 51.1 | 50.3 | 51.2 | 0/4 | 97 |
| basicos_e_moderado | antes | 49.8 | 51.1 | 48.7 | 51.5 | 50.2 | 50.4 | 0/4 | 95 |
| basicos_e_moderado | depois | 50.1 | 51.5 | 51.8 | 50.2 | 45.9 | 49.8 | 0/4 | 96 |
| comercio_spam | antes | 50.9 | 53.6 | 48.3 | 52.5 | 49.5 | 51.0 | 0/4 | 96 |
| comercio_spam | depois | 50.9 | 53.7 | 49.4 | 51.6 | 49.2 | 51.0 | 0/4 | 96 |

Leitura: a estratégia que só mexe em comércio fica em torno de 51 a 52 de aprovação, igual ao que já fazia `comercio_spam` e abaixo de `moderado_forca` (53). Misturar com governar bem não ajuda (cansa a equipe). Nenhuma estratégia de comércio passa a dominar.

## Tabela antes/depois completa

Cada linha é a diferença média (todas as sementes) entre a partida COM a ação e a MESMA partida SEM ela, no mês indicado. pdom = preço interno do mercado (%); IPCA = indicador `eco.ipca` (pp); mac = termo do comércio no IPCA (pp); ap = aprovação geral (pontos).

### Contrato trigo (ARG), volume típico, 2 anos

| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | antes | -3.00 | -0.0117 | -0.0030 | +0.001 | +0.002 | +0.002 | +0.001 | +0.002 | +0.00 | +0.0000 |
| 3 | depois | -2.94 | -0.0212 | -0.0054 | +0.156 | +0.755 | +0.417 | -0.335 | +0.003 | +1.48 | +0.0000 |
| 6 | antes | -3.29 | -0.0128 | -0.0053 | +0.003 | +0.005 | +0.005 | +0.002 | +0.006 | +0.00 | +0.0000 |
| 6 | depois | -3.17 | -0.0207 | -0.0088 | +0.176 | +0.888 | +0.489 | -0.600 | +0.007 | +2.29 | +0.0000 |
| 9 | antes | -4.03 | -0.0157 | -0.0073 | +0.003 | +0.005 | -0.009 | -0.002 | -0.007 | +0.00 | +0.0000 |
| 9 | depois | -3.83 | -0.0276 | -0.0125 | +0.183 | +0.943 | +0.540 | -0.873 | +0.013 | +2.89 | +0.0000 |
| 12 | antes | -3.93 | -0.0153 | -0.0091 | +0.007 | +0.011 | +0.000 | -0.001 | +0.002 | +0.00 | +0.0000 |
| 12 | depois | -3.67 | -0.0264 | -0.0156 | +0.191 | +1.021 | +0.571 | -1.134 | +0.018 | +3.34 | +0.0000 |
| 18 | antes | -3.76 | -0.0147 | -0.0112 | +0.015 | +0.022 | +0.015 | -0.000 | +0.015 | +0.00 | +0.0000 |
| 18 | depois | -3.50 | -0.0252 | -0.0178 | +0.134 | +0.811 | +0.454 | -1.643 | +0.028 | +3.74 | +0.0000 |

### Contrato leite em pó (ARG)

| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | antes | -0.46 | -0.0025 | -0.0006 | +0.000 | +0.000 | +0.000 | +0.001 | +0.001 | +0.00 | +0.0000 |
| 3 | depois | -0.43 | -0.0041 | -0.0010 | +0.000 | +0.000 | +0.001 | +0.001 | +0.001 | +0.21 | +0.0000 |
| 6 | antes | -0.49 | -0.0026 | -0.0011 | +0.001 | +0.001 | +0.001 | +0.001 | +0.002 | +0.00 | +0.0000 |
| 6 | depois | -0.40 | -0.0035 | -0.0016 | +0.001 | +0.002 | +0.002 | +0.001 | +0.002 | +0.32 | +0.0000 |
| 9 | antes | -0.48 | -0.0026 | -0.0014 | +0.002 | +0.002 | +0.002 | +0.001 | +0.004 | +0.00 | +0.0000 |
| 9 | depois | -0.39 | -0.0037 | -0.0021 | +0.002 | +0.003 | +0.003 | +0.001 | +0.004 | +0.36 | +0.0000 |
| 12 | antes | -0.49 | -0.0026 | -0.0016 | +0.003 | +0.004 | +0.003 | +0.002 | +0.006 | +0.00 | +0.0000 |
| 12 | depois | -0.41 | -0.0039 | -0.0023 | +0.004 | +0.005 | +0.004 | +0.002 | +0.006 | +0.39 | +0.0000 |
| 18 | antes | -0.46 | -0.0025 | -0.0018 | +0.005 | +0.006 | +0.004 | +0.001 | +0.008 | +0.00 | +0.0000 |
| 18 | depois | -0.37 | -0.0036 | -0.0023 | +0.006 | +0.008 | +0.006 | +0.002 | +0.008 | +0.39 | +0.0000 |

### Contrato arroz (URY)

| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | antes | -0.77 | -0.0034 | -0.0007 | +0.000 | +0.000 | +0.000 | +0.001 | +0.001 | +0.00 | +0.0000 |
| 3 | depois | -0.71 | -0.0032 | -0.0006 | +0.004 | +0.018 | +0.009 | -0.004 | +0.001 | +0.28 | +0.0000 |
| 6 | antes | -0.77 | -0.0035 | -0.0013 | +0.001 | +0.001 | +0.001 | +0.000 | +0.001 | +0.00 | +0.0000 |
| 6 | depois | -0.60 | -0.0023 | -0.0010 | +0.003 | +0.014 | +0.007 | -0.009 | +0.001 | +0.45 | +0.0000 |
| 9 | antes | -0.46 | -0.0021 | -0.0016 | +0.002 | +0.002 | +0.002 | +0.001 | +0.002 | +0.00 | +0.0000 |
| 9 | depois | -0.42 | -0.0019 | -0.0013 | +0.003 | +0.012 | +0.007 | -0.012 | +0.001 | +0.49 | +0.0000 |
| 12 | antes | -0.94 | -0.0042 | -0.0021 | +0.002 | +0.003 | +0.003 | +0.001 | +0.003 | +0.00 | +0.0000 |
| 12 | depois | -0.63 | -0.0029 | -0.0016 | +0.005 | +0.020 | +0.011 | -0.021 | +0.002 | +0.58 | +0.0000 |
| 18 | antes | -0.71 | -0.0032 | -0.0024 | +0.004 | +0.006 | +0.005 | +0.001 | +0.005 | +0.00 | +0.0000 |
| 18 | depois | -0.53 | -0.0024 | -0.0015 | +0.004 | +0.013 | +0.009 | -0.033 | +0.002 | +0.56 | +0.0000 |

### Contrato eletrônicos (CHN)

| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | antes | -2.96 | -0.0195 | -0.0050 | +0.007 | +0.003 | +0.003 | +0.132 | +0.011 | +0.00 | +0.0000 |
| 3 | depois | -2.96 | -0.0195 | -0.0050 | +0.007 | +0.003 | +0.003 | +0.132 | +0.011 | +0.00 | +0.0000 |
| 6 | antes | -2.77 | -0.0183 | -0.0084 | +0.016 | +0.012 | +0.008 | +0.226 | +0.028 | +0.00 | +0.0000 |
| 6 | depois | -2.77 | -0.0167 | -0.0081 | +0.016 | +0.012 | +0.008 | +0.227 | +0.027 | +0.00 | +0.0000 |
| 9 | antes | -2.87 | -0.0189 | -0.0109 | +0.026 | +0.022 | +0.015 | +0.295 | +0.046 | +0.00 | +0.0000 |
| 9 | depois | -2.87 | -0.0189 | -0.0106 | +0.026 | +0.022 | +0.014 | +0.295 | +0.046 | +0.00 | +0.0000 |
| 12 | antes | -3.03 | -0.0200 | +0.0191 | -0.089 | -0.427 | -0.158 | +0.344 | +0.060 | +0.00 | +0.0000 |
| 12 | depois | -3.03 | -0.0200 | +0.0192 | -0.090 | -0.427 | -0.159 | +0.344 | +0.060 | +0.00 | +0.0000 |
| 18 | antes | -2.95 | -0.0195 | -0.0071 | +0.036 | -0.165 | +0.004 | +0.059 | +0.296 | +0.00 | +0.0000 |
| 18 | depois | -2.95 | -0.0195 | -0.0423 | +0.032 | -0.004 | +0.019 | +0.040 | +0.394 | +0.00 | +0.0000 |

### Contrato diesel (EUA)

| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | antes | +0.43 | +0.0143 | +0.0038 | -0.000 | -0.001 | -0.002 | +0.008 | +0.005 | +0.00 | +0.0000 |
| 3 | depois | +0.43 | +0.0169 | +0.0041 | -0.002 | -0.001 | -0.002 | -0.000 | -0.029 | +0.00 | +0.0000 |
| 6 | antes | +0.26 | +0.0087 | +0.0055 | +0.001 | -0.001 | -0.005 | +0.012 | +0.013 | +0.00 | +0.0000 |
| 6 | depois | +0.26 | +0.0137 | +0.0069 | -0.001 | -0.002 | -0.006 | +0.005 | -0.014 | +0.00 | +0.0000 |
| 9 | antes | +0.20 | +0.0065 | +0.0068 | -0.002 | -0.004 | -0.026 | +0.009 | +0.005 | +0.00 | +0.0000 |
| 9 | depois | +0.20 | +0.0089 | +0.0084 | -0.000 | -0.001 | -0.010 | +0.010 | +0.006 | +0.00 | +0.0000 |
| 12 | antes | +0.13 | +0.0042 | +0.0059 | +0.001 | +0.000 | -0.023 | +0.011 | +0.018 | +0.00 | +0.0000 |
| 12 | depois | +0.13 | +0.0053 | +0.0074 | +0.001 | +0.001 | -0.013 | +0.011 | +0.020 | +0.00 | +0.0000 |
| 18 | antes | +0.02 | +0.0006 | +0.0039 | +0.184 | +0.178 | +0.149 | +0.181 | +0.209 | +0.00 | +0.0000 |
| 18 | depois | +0.02 | +0.0011 | -0.0263 | -0.002 | +0.316 | +0.009 | -0.135 | -0.086 | +0.00 | +0.0000 |

### Contrato medicamentos (DEU)

| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | antes | +3.02 | +0.0581 | +0.0146 | -0.004 | -0.006 | -0.008 | +0.003 | -0.004 | +0.00 | +0.0000 |
| 3 | depois | +3.02 | +0.0577 | +0.0145 | -0.167 | -0.376 | -1.031 | +0.002 | -0.004 | +0.00 | +0.0000 |
| 6 | antes | +3.08 | +0.0592 | +0.0249 | -0.013 | -0.017 | -0.024 | +0.004 | -0.012 | +0.00 | +0.0000 |
| 6 | depois | +3.08 | +0.0551 | +0.0243 | -0.178 | -0.390 | -1.059 | +0.004 | -0.012 | +0.00 | +0.0000 |
| 9 | antes | +3.08 | +0.0592 | +0.0328 | -0.024 | -0.031 | -0.043 | +0.006 | -0.021 | +0.00 | +0.0000 |
| 9 | depois | +3.08 | +0.0592 | +0.0318 | -0.152 | -0.319 | -0.844 | +0.006 | -0.021 | +0.00 | +0.0000 |
| 12 | antes | +2.98 | +0.0572 | +0.0361 | -0.036 | -0.046 | -0.063 | +0.007 | -0.031 | +0.00 | +0.0000 |
| 12 | depois | +2.98 | +0.0572 | +0.0354 | -0.131 | -0.262 | -0.665 | +0.006 | -0.030 | +0.00 | +0.0000 |
| 18 | antes | +2.95 | +0.0566 | +0.0393 | -0.060 | -0.072 | -0.097 | +0.008 | -0.049 | +0.00 | +0.0000 |
| 18 | depois | +2.95 | +0.0566 | +0.0418 | -0.112 | -0.196 | -0.438 | +0.008 | -0.049 | +0.00 | +0.0000 |

### Contrato potássio (CAN), volume típico

| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | antes | -3.29 | +0.0000 | -0.0000 | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 | +0.00 | +0.0000 |
| 3 | depois | -3.29 | +0.0000 | -0.0000 | +0.026 | +0.000 | +0.000 | +0.637 | +0.000 | +0.00 | +0.0009 |
| 6 | antes | -2.91 | +0.0000 | -0.0001 | +0.000 | +0.000 | -0.000 | -0.000 | +0.001 | +0.00 | +0.0000 |
| 6 | depois | -2.91 | +0.0000 | +0.0000 | +0.033 | +0.000 | -0.000 | +0.806 | +0.001 | +0.00 | +0.0008 |
| 9 | antes | -4.56 | +0.0000 | -0.0001 | +0.000 | +0.000 | +0.000 | -0.000 | +0.001 | +0.00 | +0.0000 |
| 9 | depois | -4.56 | -0.0110 | -0.0018 | +0.037 | +0.001 | +0.001 | +0.878 | +0.001 | +0.00 | +0.0012 |
| 12 | antes | -4.03 | +0.0000 | -0.0002 | +0.000 | +0.000 | +0.000 | -0.001 | +0.001 | +0.00 | +0.0000 |
| 12 | depois | -4.03 | -0.0142 | -0.0050 | +0.041 | +0.004 | +0.004 | +0.940 | +0.004 | +0.00 | +0.0011 |
| 18 | antes | -5.38 | +0.0000 | -0.0003 | +0.000 | +0.000 | +0.001 | -0.001 | +0.003 | +0.00 | +0.0000 |
| 18 | depois | -5.38 | -0.0188 | -0.0089 | +0.049 | +0.012 | +0.014 | +0.956 | +0.010 | +0.00 | +0.0015 |

### Contrato grande de potássio (CAN), 4x o volume e 15% abaixo do preço pedido

| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | antes | -12.96 | +0.0000 | +0.0028 | -0.001 | -0.001 | -0.002 | +0.008 | -0.021 | +50.00 | +0.0000 |
| 3 | depois | -12.96 | +0.0000 | +0.0029 | +0.068 | -0.001 | -0.001 | +1.457 | -0.021 | +50.00 | +0.0035 |
| 6 | antes | -12.20 | +0.0000 | +0.0068 | -0.004 | -0.004 | -0.006 | +0.019 | -0.054 | +50.00 | +0.0000 |
| 6 | depois | -12.20 | +0.0000 | +0.0071 | +0.096 | -0.004 | -0.005 | +2.162 | -0.054 | +50.00 | +0.0033 |
| 9 | antes | -15.52 | +0.0000 | +0.0108 | -0.007 | -0.009 | -0.011 | +0.030 | -0.087 | +50.00 | +0.0000 |
| 9 | depois | -15.52 | -0.0421 | +0.0043 | +0.101 | -0.006 | -0.009 | +2.340 | -0.085 | +50.00 | +0.0042 |
| 12 | antes | -14.46 | +0.0000 | +0.0139 | -0.012 | -0.015 | -0.019 | +0.040 | -0.115 | +50.00 | +0.0000 |
| 12 | depois | -14.46 | -0.0552 | -0.0042 | +0.100 | -0.002 | -0.005 | +2.276 | -0.107 | +50.00 | +0.0039 |
| 18 | antes | -17.18 | +0.0000 | +0.0148 | -0.025 | -0.028 | -0.036 | +0.052 | -0.157 | +50.00 | +0.0000 |
| 18 | depois | -17.18 | -0.0645 | -0.0156 | +0.094 | +0.012 | +0.011 | +1.948 | -0.134 | +50.00 | +0.0047 |

### Diesel: choque de +10% no preço mundial por 6 meses

| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | antes | +3.87 | +0.1236 | +0.0330 | -0.011 | -0.015 | -0.019 | +0.000 | -0.009 | +0.00 | +0.0000 |
| 3 | depois | +3.87 | +0.1375 | +0.0352 | -0.014 | -0.016 | -0.020 | -0.016 | -0.075 | +0.00 | +0.0000 |
| 6 | antes | +3.04 | +0.0992 | +0.0484 | -0.030 | -0.040 | -0.051 | -0.000 | -0.024 | +0.00 | +0.0000 |
| 6 | depois | +3.04 | +0.1134 | +0.0547 | -0.037 | -0.044 | -0.056 | -0.020 | -0.110 | +0.00 | +0.0000 |
| 9 | antes | +2.38 | +0.0785 | +0.0542 | -0.051 | -0.066 | -0.084 | -0.000 | -0.039 | +0.00 | +0.0000 |
| 9 | depois | +2.38 | +0.0986 | +0.0624 | -0.062 | -0.074 | -0.095 | -0.021 | -0.133 | +0.00 | +0.0000 |
| 12 | antes | +1.88 | +0.0620 | +0.0514 | -0.069 | -0.087 | -0.109 | -0.000 | -0.051 | +0.00 | +0.0000 |
| 12 | depois | +1.88 | +0.0779 | +0.0614 | -0.082 | -0.100 | -0.123 | -0.020 | -0.141 | +0.00 | +0.0000 |
| 18 | antes | +1.17 | +0.0384 | +0.0399 | -0.090 | -0.113 | -0.132 | -0.000 | -0.068 | +0.00 | +0.0000 |
| 18 | depois | +1.17 | +0.0482 | +0.0525 | -0.106 | -0.133 | -0.156 | -0.012 | -0.131 | +0.00 | +0.0000 |

### TEC zero do arroz por 12 meses

| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | antes | n/d | | | | | | | | | |
| 3 | depois | -3.24 | -0.0146 | -0.0025 | +0.087 | +0.564 | +0.283 | -0.755 | +0.001 | +1.16 | +0.0000 |
| 6 | antes | n/d | | | | | | | | | |
| 6 | depois | -3.22 | -0.0131 | -0.0051 | +0.154 | +0.910 | +0.458 | -0.941 | +0.001 | +2.22 | +0.0000 |
| 9 | antes | n/d | | | | | | | | | |
| 9 | depois | -3.16 | -0.0142 | -0.0072 | +0.118 | +0.753 | +0.382 | -1.052 | +0.001 | +2.77 | +0.0000 |
| 12 | antes | n/d | | | | | | | | | |
| 12 | depois | -3.15 | -0.0142 | -0.0087 | +0.076 | +0.571 | +0.294 | -1.163 | +0.000 | +3.06 | +0.0000 |
| 18 | antes | n/d | | | | | | | | | |
| 18 | depois | +0.09 | +0.0004 | -0.0043 | -0.123 | -0.406 | -0.193 | -1.023 | -0.006 | +1.04 | +0.0000 |

### Conab vende arroz (já tinha 1 mês de consumo em estoque; vende 0,5 mês no mês 1)

| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | antes | n/d | | | | | | | | | |
| 3 | depois | -3.26 | -0.0147 | -0.0051 | +0.216 | +1.039 | +0.718 | -0.838 | +0.002 | +2.17 | +0.0000 |
| 6 | antes | n/d | | | | | | | | | |
| 6 | depois | -1.29 | -0.0053 | -0.0060 | +0.154 | +0.786 | +0.546 | -0.899 | +0.003 | +2.03 | +0.0000 |
| 9 | antes | n/d | | | | | | | | | |
| 9 | depois | -0.51 | -0.0023 | -0.0057 | +0.108 | +0.587 | +0.412 | -0.878 | +0.004 | +1.43 | +0.0000 |
| 12 | antes | n/d | | | | | | | | | |
| 12 | depois | -0.17 | -0.0008 | -0.0051 | +0.077 | +0.443 | +0.314 | -0.793 | +0.005 | +0.90 | +0.0000 |
| 18 | antes | n/d | | | | | | | | | |
| 18 | depois | -0.02 | -0.0001 | -0.0024 | +0.043 | +0.250 | +0.181 | -0.455 | +0.004 | +0.30 | +0.0000 |

### Conab compra arroz na safra (0,5 mês de consumo no mês 1)

| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | antes | n/d | | | | | | | | | |
| 3 | depois | +2.05 | +0.0092 | +0.0033 | -0.120 | -0.663 | -0.357 | +0.570 | -0.001 | +0.00 | +0.0000 |
| 6 | antes | n/d | | | | | | | | | |
| 6 | depois | +0.76 | +0.0031 | +0.0038 | -0.092 | -0.502 | -0.272 | +0.430 | -0.004 | +0.00 | +0.0000 |
| 9 | antes | n/d | | | | | | | | | |
| 9 | depois | +0.28 | +0.0012 | +0.0038 | -0.071 | -0.380 | -0.208 | +0.325 | -0.006 | +0.00 | +0.0000 |
| 12 | antes | n/d | | | | | | | | | |
| 12 | depois | +0.10 | +0.0005 | +0.0037 | -0.056 | -0.289 | -0.160 | +0.246 | -0.008 | +0.00 | +0.0000 |
| 18 | antes | n/d | | | | | | | | | |
| 18 | depois | +0.00 | +0.0000 | +0.0006 | -0.037 | -0.168 | -0.096 | +0.142 | -0.012 | +0.00 | +0.0000 |

### Leilão de importação de emergência do arroz

| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | antes | n/d | | | | | | | | | |
| 3 | depois | -8.21 | -0.0369 | -0.0108 | +0.339 | +1.500 | +1.301 | -1.992 | +0.003 | +5.25 | +0.0000 |
| 6 | antes | n/d | | | | | | | | | |
| 6 | depois | -3.65 | -0.0152 | -0.0121 | +0.251 | +1.223 | +1.032 | -2.192 | +0.003 | +5.17 | +0.0000 |
| 9 | antes | n/d | | | | | | | | | |
| 9 | depois | -1.64 | -0.0074 | -0.0106 | +0.043 | +0.284 | +0.464 | -2.006 | +0.000 | +3.82 | +0.0000 |
| 12 | antes | n/d | | | | | | | | | |
| 12 | depois | -0.66 | -0.0030 | -0.0084 | -0.116 | -0.465 | +0.015 | -1.684 | -0.003 | +2.51 | +0.0000 |
| 18 | antes | n/d | | | | | | | | | |
| 18 | depois | -0.13 | -0.0006 | -0.0038 | -0.252 | -0.739 | -0.263 | -1.721 | -0.092 | +0.92 | +0.0000 |

### Crédito ao produtor de arroz (Plano Safra extra)

| mês | versão | preço interno (%) | termo IPCA comex (pp) | IPCA (pp) | aprovação | periferia | aposentados | agro | caminhoneiros | corte da produção (pp) | C.mac.agro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | antes | n/d | | | | | | | | | |
| 3 | depois | +0.00 | +0.0000 | +0.0001 | +0.029 | +0.000 | +0.000 | +0.678 | +0.000 | +0.00 | +0.0000 |
| 6 | antes | n/d | | | | | | | | | |
| 6 | depois | +0.00 | +0.0000 | +0.0004 | +0.022 | +0.000 | -0.000 | +0.511 | -0.001 | +0.00 | +0.0000 |
| 9 | antes | n/d | | | | | | | | | |
| 9 | depois | -0.65 | -0.0029 | +0.0003 | +0.016 | +0.000 | -0.000 | +0.386 | -0.002 | +0.16 | +0.0000 |
| 12 | antes | n/d | | | | | | | | | |
| 12 | depois | -2.28 | -0.0103 | -0.0014 | +0.065 | +0.274 | +0.136 | +0.171 | -0.002 | +1.01 | +0.0000 |
| 18 | antes | n/d | | | | | | | | | |
| 18 | depois | -2.33 | -0.0105 | -0.0038 | +0.045 | +0.271 | +0.137 | -0.330 | -0.005 | +2.09 | +0.0000 |

### Início do jogo (save novo, sem ações): controle antes x depois, meses 1 a 12

Maior diferença absoluta em 12 sementes x 12 meses: IPCA 0.360 pp · aprovação 2.139 pontos · grupo 7.709 pontos (agro semente 66 mês 12).

- mês 3: IPCA 4.379 → 4.380 · aprovação 52.66 → 52.69
- mês 6: IPCA 4.238 → 4.240 · aprovação 50.92 → 50.94
- mês 12: IPCA 4.206 → 4.224 · aprovação 45.23 → 44.89
