# Efeitos das ações da aba País: antes e depois dos lotes A e E

Branch `lote-ae` (a partir de `motor-v3.5`, commit ea0bd47). Relatório de origem: 2ª revisão do Fable, seção C e lotes A e E da seção H.

## Método

Igual ao do avaliador (`pais_probe.py` + `sim2.py` = `testes/sim/sim.py` com as ações `indu`, `conv` e `orc`; 248 cenários da aba País): cada ação é aplicada no mês 0 (tratamento) e comparada a uma partida igual sem ela (controle), com a mesma semente e os mesmos eventos aleatórios; 8 repetições pareadas; Δ = média(tratamento − controle) em 3, 6, 12 e 24 meses. Um Δ só conta como efeito se |Δ| > max(materialidade, 2,3 erros-padrão); abaixo disso aparece com `~` nas tabelas. Veredito (script `pais_relatorio.py` do avaliador): **ok** = fiscal certo e indicador social (IDH, pobreza, homicídios, desmatamento) na direção certa; **misto** = social certo e outro indicador (confiança, inflação, desmatamento) errado; **só fiscal** / **nulo** = só o custo entra / nada entra; **INVERTIDO** = social na direção errada. "Antes" = ea0bd47; "depois" = este commit. As mesmas ações dos dois lados; só mudou o texto onde o texto mudou (Todo o MEC, Todo o Trabalho, Energia e AFRMM).

Complementos feitos nesta rodada: (i) os 8 casos que sobraram como INVERTIDO com 8 repetições foram refeitos com 24 repetições; (ii) uma segunda leitura do veredito inclui desemprego e PIB entre os indicadores que contam (a regra do avaliador só conta IDH, pobreza, homicídios e desmatamento, o que deixa Trabalho e Ferrovias "só fiscal" mesmo quando o desemprego e o PIB mexem); (iii) `testes/motor/ui_pais_efeitos.py` (22 checagens) trava os sinais no código.

## Resumo por grupo (antes → depois)

| grupo | n | ok | misto | só fiscal | nulo | fiscal ausente | INVERTIDO | DUPLICOU |
|---|---|---|---|---|---|---|---|---|
| dup | 4 | 4 → 4 | · | · | · | · | · | · |
| ind | 44 | 32 → 29 | 12 → 6 | 0 → 9 | · | · | · | · |
| orc_cont | 22 | 0 → 20 | · | 1 → 1 | · | · | 21 → 1 | · |
| orc_cut | 32 | 19 → 27 | · | 6 → 4 | · | · | 7 → 1 | · |
| orc_inv | 31 | 25 → 29 | 2 → 1 | 4 → 1 | · | · | · | · |
| programa | 64 | 50 → 56 | 6 → 1 | 4 → 3 | 3 → 4 | · | · | · |
| slider | 6 | 6 → 6 | · | · | · | · | · | · |
| **total** | 203 | **136 → 171** | **20 → 8** | **15 → 18** | **3 → 4** | **0 → 0** | **28 → 2** | **0 → 0** |
| total com desemprego e PIB contando (2ª leitura) | 203 | 136 → 174 | 20 → 11 | 15 → 14 | 3 → 2 | 0 → 0 | 28 → 2 | 0 → 0 |

(Programas inclui os "próximos passos"; Trabalho (34 alavancas) e Conversas (12) ficam fora da contagem porque não têm gabarito de sinal; ver as seções próprias. O total depois tem 1 ação a mais: o AFRMM virou programa + próximo passo.)

## Os itens do lote, medidos (Δ pareado contra o controle; `~` = dentro do ruído)

### A1. Contingenciar e bloquear verba piora a área (antes: melhorava)

Causa: "contingenciar" casava o objeto `contingenciamento` (economia) e o objeto da área herdava o sinal de ampliação. Agora a leitura normaliza "contingenciar/bloquear R$ X do orçamento de Y" para corte por decreto (`v4Leve`), só com valor ou "orçamento/verba" logo depois (não pega "bloquear o Telegram"). Os 22 textos `orc_cont` do painel ficam com despesa −5, polaridade negativa e efeito social ≤ 0 (checado em `ui_pais_efeitos.py`). Vale para o "Contingenciar" do painel e para o texto livre da Mesa. O painel passa a dizer que contingenciar tem o efeito do corte (a dotação congelada é liberável depois), em vez de "segura só parte".

| ação | antes (idh m12 / pob m24 / conf m12) | depois |
|---|---|---|
| saude · ateno_bsica | idh +0.001 / pob -0.03 / conf +1.63 (INVERTIDO) | idh -0.003 / pob +0.01~ / conf +0.64 (ok) |
| infra · saneamento | idh +0.001 / pob -0.07 / conf +1.32 (INVERTIDO) | idh -0.002 / pob +0.03~ / conf +0.55 (ok) |
| trabalho · seguro_desemprego | idh -0.001 / pob -0.21 / conf +1.39 (INVERTIDO) | idh -0.000~ / pob +0.39 / conf -0.83 (ok) |
| sociedade · cozinha_solidria | idh -0.001 / pob -0.20 / conf +1.49 (INVERTIDO) | idh -0.000~ / pob +0.53 / conf +0.80 (ok) |
| educacao · creches | idh +0.001 / pob -0.04 / conf +1.59 (INVERTIDO) | idh -0.003 / pob +0.01~ / conf +0.62 (ok) |
| seguranca · presdios | idh -0.001 / pob -0.03~ / conf +1.24 (INVERTIDO) | idh -0.000~ / pob +0.01~ / conf +0.40~ (ok) |

### A2. Cortar a Segurança não reduz homicídios (antes: reduzia)

`segPrevia` agora inverte o sinal quando a despesa é negativa (corte e contingenciamento de polícia, plano e presídios): mortes violentas sobem, controle do crime organizado cai, sem efeito em letalidade nem em presos. Investir continua reduzindo.

| ação | hom m12 antes → depois | hom m24 antes → depois |
|---|---|---|
| seg orc_inv_toda_a_segurana_pb | -0.41 → -0.41 | -0.34 → -0.34 |
| seg orc_cut_toda_a_segurana_pb | -0.39 → +0.40 | -0.33 → +0.32 |
| seg orc_cut_polcia_federal | -0.39 → +0.40 | -0.33 → +0.32 |
| seg orc_cut_prf | -0.38 → +0.39 | -0.31 → +0.31 |
| seg orc_cut_fora_nacional | -0.39 → +0.40 | -0.32 → +0.32 |
| seg orc_cut_presdios | -0.55 → +0.59 | -0.44 → +0.46 |
| seg orc_cont_polcia_federal | -0.39 → +0.39 | -0.33 → +0.31 |
| just orc_cut_polcia_federal | -0.39 → +0.40 | -0.33 → +0.32 |

### A3. Crédito do BNDES na Indústria deixou de ser exploit

Causa real (não era só `icResolve`): os objetos `bndes_credito` e `credito_subsidiado` tinham a categoria `programa_social`, e a tabela de efeitos futuros por categoria agendava "Cadastro Único mostra queda da pobreza" (−1,2 p.p., 6 meses depois) para qualquer crédito; textos de minério e chips ainda agendavam o evento de "mineração e petróleo" (+284 km²). Agora: os dois objetos não têm categoria, o crédito a produto não agenda eventos por categoria, não leva efeito social direto e leva só 25% do impulso macro (PIB, desemprego, preços) do mesmo valor investido; o efeito produtivo vem de `icResolve`/`icTick`. O custo lido continua sendo a equalização de juros (10% do valor: R$ 5 bi de crédito = R$ 0,5 bi de despesa) e o cartão da Indústria agora explica isso. Em 12 meses o crédito de R$ 5 bi reduz a pobreza menos que o investimento direto dos mesmos R$ 5 bi em 8 dos 9 produtos (a exceção é o etanol, marginal: o texto também casa o objeto de biocombustíveis, e o crédito lê despesa de R$ 1,6 bi); em 24 meses, em todos. Na soma dos 9 produtos o efeito em 12 meses cai de −9,64 p.p. para o valor abaixo.

| produto | pob m12 crédito: antes → depois | pob m12 investir (depois) | pob m24 crédito: antes → depois | pob m24 investir (depois) | custo lido do crédito (m24) |
|---|---|---|---|---|---|
| caf_solvel | -1.06 → -0.02~ | -0.05 | -0.78 → -0.03~ | -0.10 | +0.6 |
| couros_e_peles | -1.06 → -0.02~ | -0.03 | -0.78 → -0.03~ | -0.03~ | +0.6 |
| etanol | -1.08 → -0.05 | -0.04 | -0.92 → -0.09 | -0.22 | +1.6 |
| farelo_de_soja | -1.07 → -0.03~ | -0.06 | -0.78 → -0.03~ | -0.10 | +0.7 |
| minrio_de_ferro | -1.11 → -0.02~ | -0.02~ | -1.01 → -0.03~ | -0.04 | +1.3 |
| ouro | -1.06 → -0.02~ | -0.04 | -0.78 → -0.03~ | -0.03 | +0.6 |
| petrleo_bruto | -1.06 → -0.02~ | -0.04 | -0.78 → -0.03~ | -0.18 | +0.6 |
| semicondutores_chips | -1.10 → -0.02~ | -0.03 | -0.87 → -0.03~ | -0.20 | +0.7 |
| soja_em_gro | -1.07 → -0.03~ | -0.07 | -0.79 → -0.04 | -0.11 | +0.7 |

Soma de pob m12 dos produtos com crédito: antes -9.64, depois -0.20; investindo R$ 5 bi: -0.39.

### A4. Operações de Segurança agora mexem em homicídios; "Força Nacional para <UF>" não toca desmatamento

Duas causas. (1) "Enviar a Força Nacional para Pernambuco/Rio de Janeiro" caía na leitura genérica (o nome do estado contava como assunto não coberto pelo objeto `plano_seguranca`), ganhava a categoria `desenvolvimento` (+284 km² de desmatamento e −3 com a UE, por evento agendado) ou `ambiente` (Rio de Janeiro). O nome do estado deixa de contar como assunto e a leitura genérica deixou de herdar a categoria "desenvolvimento" (também as de "administração geral" e "turismo", que davam o mesmo desmatamento a textos como "mais 1.500 auditores na CGU"). (2) `segPrevia` ganha o canal de câmeras corporais (menos mortes por intervenção policial), o de prevenção social (Centros de Juventude) e intensidade 2x para operação concentrada em até 3 estados; o efeito nacional sai da média por UF ponderada pela população (`segMedia`), então um estado grande pesa mais.

| ação | hom m12 antes → depois | hom m24 antes → depois | desmatamento m12 antes → depois | veredito antes → depois |
|---|---|---|---|---|
| Centros de Juventude nas periferias | -0.00~ → -0.16 | -0.00~ → -0.13 | +0~ → +0~ | só fiscal → ok |
| Decretar GLO em Pernambuco | -0.07~ → -0.14 | -0.05~ → -0.11 | +0~ → +0~ | nulo → ok |
| Enviar a Força Nacional para Pernambuco | -0.06~ → -0.10 | -0.06~ → -0.09~ | +284 → +0~ | misto → ok |
| Mais 100 mil câmeras corporais | +0.01~ → -0.12 | +0.01~ → -0.09~ | +0~ → +0~ | só fiscal → ok |
| Operação integrada PF + inteligência contra Pr | -0.12 → -0.23 | -0.10~ → -0.19 | +0~ → +0~ | ok → ok |
| Transferir lideranças de Pernambuco para presí | -0.09~ → -0.18 | -0.07~ → -0.14 | +0~ → +0~ | só fiscal → ok |

### E1. Qualificação, Sine e Trabalho reduzem o desemprego

`primeiro_emprego` (qualificação) ganhou `lab` −0,012 (antes −0,003), o Sine entra no mesmo objeto (sinônimo) e a leitura genérica de trabalho herda `lab` −0,01. "Todo o Trabalho" passou a falar de qualificação e intermediação de mão de obra do MTE (antes caía em "gastos do governo", sem canal). Cortar faz o inverso (desemprego sobe).

| ação | des m12 antes → depois | des m24 antes → depois | pob m12 antes → depois | veredito antes → depois (2ª leitura) |
|---|---|---|---|---|
| orc_inv_qualificao | -0.03 → -0.09 | +0.05~ → -0.04 | -0.02~ → -0.05 | só fiscal → ok (ok) |
| orc_inv_intermediao_sine | -0.04~ → -0.06 | -0.01~ → +0.03~ | -0.02~ → -0.04 | só fiscal → ok (ok) |
| orc_inv_todo_o_trabalho | -0.04~ → -0.09 | -0.01~ → -0.04 | -0.02~ → -0.05 | só fiscal → ok (ok) |
| orc_cut_qualificao | -0.00~ → +0.04 | -0.01~ → +0.04~ | +0.01~ → +0.02~ | INVERTIDO → só fiscal (ok) |
| orc_cut_intermediao_sine | +0.02~ → +0.04 | +0.00~ → +0.04~ | +0.01~ → +0.03~ | só fiscal → só fiscal (ok) |
| orc_cut_todo_o_trabalho | -0.02~ → +0.04 | +0.01~ → +0.03~ | -0.01~ → +0.02~ | só fiscal → só fiscal (ok) |

### E2. Ferrovias dão PIB

`ferrovias`: multiplicador do gasto 1,6 → 2,4 e maturação 24 → 16 meses (obra ferroviária é a de maior efeito sobre a logística de carga). Cortar tira PIB e emprego.

| ação | pib m12 antes → depois | pib m24 antes → depois | des m24 antes → depois | pob m24 antes → depois | veredito antes → depois |
|---|---|---|---|---|---|
| orc_inv_ferrovias | +0.04~ → +0.05~ | -0.02~ → +0.06 | -0.02~ → -0.14 | -0.03~ → -0.13 | só fiscal → ok |
| orc_cut_ferrovias | +0.00~ → -0.01~ | -0.06~ → -0.07~ | +0.05 → +0.07 | +0.04 → +0.07 | ok → ok |
| orc_cont_ferrovias | +0.06~ → -0.01~ | +0.05~ → -0.07~ | -0.03~ → +0.07 | -0.04~ → +0.07 | só fiscal → ok |

### E3. AFRMM

O motor lia "criar linha de crédito de R$ 3 bilhões" e perdia a renúncia (custo R$ 0,3 bi, nenhum efeito fiscal da desoneração). Textos com duas medidas ainda perdem a primeira (é o lote de motor, não este). Por isso o programa foi dividido em dois passos que o motor lê direito: **Desonerar pela metade o AFRMM (adicional de frete) da cabotagem, com renúncia de R$ 1,5 bilhão por ano** (receita −1,5) e, como próximo passo, **Ampliar em R$ 3 bilhões a linha de crédito subsidiado para navios de cabotagem, financiada pelo AFRMM** (despesa +0,3, a equalização). Fiscal presente nos dois; sem o falso efeito de −1 p.p. de pobreza que o crédito dava.

| passo | receita m24 | custo m24 | pob m24 | veredito |
|---|---|---|---|---|
| antes: texto único | +0.0~ | +0.3 | -0.73 | ok |
| depois: desonerar | -1.5 | +0.2~ | -0.03 | ok |
| depois: crédito (próximo passo) | +0.0~ | +0.3 | +0.00~ | só fiscal |

### E4. Conversa com o governador

A cobrança deixou de ser binária (relação >= 60): a chance de surtir efeito é (relação − 30) / 55, de 5% a 95% (relação 30: 5%; 50: 36%; 60: 55%; 80: 91%), sorteada de forma determinística por semente, estado, tema e mês. O cartão mostra a chance com a relação atual, o que o apoio rende (% ao mês no indicador do estado e por quantos meses) e que o pacto custa o dobro e rende 1,6 vez o apoio, por mais tempo. Em 40 sorteios: 5 cobranças com efeito com relação 20, 13 com 50 e 34 com 80 (`ui_pais_efeitos.py`). O efeito continua sendo no indicador do estado, não no nacional.

## Tabela por ação

Δcusto = R$ bi/ano no mês 24. "2ª leitura" conta também desemprego e PIB.

| área | grupo | ação | Δcusto m24 antes → depois | antes | depois | depois (2ª leitura) | indicadores antes | indicadores depois |
|---|---|---|---|---|---|---|---|---|
| saude | programa | Carreira médica do SUS | +10.5 → +10.5 | ok | ok | misto | idh@12+0.002 idh@24+0.002 pib@24-0.06 ipca@24+0.05 conf@12-2.30 | idh@12+0.002 idh@24+0.002 pib@24-0.06 ipca@24+0.05 conf@12-2.30 |
| saude | programa | Canetas de obesidade no SUS | +3.2 → +3.2 | ok | ok | = | idh@12+0.002 idh@24+0.002 conf@12-0.38 conf@24-0.50 | idh@12+0.002 idh@24+0.002 conf@12-0.38 conf@24-0.50 |
| saude | programa | Mais 5 mil leitos de UTI | +3.1 → +3.1 | ok | ok | = | idh@12+0.002 idh@24+0.002 conf@12-0.35 conf@24-0.49 | idh@12+0.002 idh@24+0.002 conf@12-0.35 conf@24-0.49 |
| educacao | programa | Mais 1 milhão de vagas em tempo integral | +3.1 → +3.1 | ok | ok | = | idh@12+0.002 idh@24+0.006 conf@12-0.34 conf@24-0.49 | idh@12+0.002 idh@24+0.006 conf@12-0.34 conf@24-0.49 |
| educacao | programa | Adicional para professores de periferia | +3.3 → +3.3 | ok | ok | = | idh@12+0.002 idh@24+0.002 conf@12-0.37 conf@24-0.51 | idh@12+0.002 idh@24+0.002 conf@12-0.37 conf@24-0.51 |
| educacao | programa_p2 | Notebooks para o ensino médio > Mais 2 milhõ | +2.1 → +2.1 | ok | ok | = | idh@12+0.002 idh@24+0.002 conf@24-0.33 | idh@12+0.002 idh@24+0.002 conf@24-0.33 |
| educacao | programa_p2 | Passe livre estudantil > Passe livre também  | +1.1 → +1.1 | ok | ok | = | pob@12-0.29 pob@24-0.21 | pob@12-0.29 pob@24-0.21 |
| infraestrutura | programa | Mais Minha Casa Minha Vida | +16.3 → +16.3 | ok | ok | = | idh@24+0.001 pob@12-0.49 pob@24-0.55 pib@12+0.15 pib@24+0.04 | idh@24+0.001 pob@12-0.49 pob@24-0.55 pib@12+0.15 pib@24+0.04 |
| infraestrutura | programa_p2 | Energia solar para famílias de baixa renda > | +5.4 → +5.4 | ok | ok | = | pob@24-0.16 pib@24+0.06 des@24-0.16 ipca@24+0.06 conf@12-0.62 | pob@24-0.16 pib@24+0.06 des@24-0.16 ipca@24+0.06 conf@12-0.62 |
| infraestrutura | programa_p2 | Duplicar trechos de BRs > Mais 2 mil km dupl | +7.3 → +7.3 | ok | ok | = | pob@12-0.04 pob@24-0.11 des@12-0.07 des@24-0.12 ipca@24+0.06 | pob@12-0.04 pob@24-0.11 des@12-0.07 des@24-0.12 ipca@24+0.06 |
| infraestrutura | programa | 3 mil radares nas BRs | +1.1 → +1.1 | ok | ok | = | pob@24-0.05 pib@24+0.03 des@24-0.06 | pob@24-0.05 pib@24+0.03 des@24-0.06 |
| infraestrutura | programa | Cabotagem: AFRMM pela metade | +0.3 → +0.0 | ok | ok | = | idh@24+0.001 pob@12-1.02 pob@24-0.73 | pob@24-0.03 pib@12+0.04 des@24-0.03 |
| justica | programa | Autonomia da PF (PEC) | +0.5 → +0.5 | ok | ok | = | hom@12-0.40 hom@24-0.34 | hom@12-0.40 hom@24-0.34 |
| justica | programa | Mais 1.500 auditores na CGU | +0.7 → +0.4 | misto | **só fiscal** | = | pob@12-0.03 pob@24-0.08 pib@12+0.08 des@12-0.04 desm@12+284.08 | — |
| justica | programa | Fundo contra as facções | +1.0 → +1.0 | ok | ok | = | hom@12-0.88 hom@24-0.72 conf@12-1.04 conf@24-0.91 | hom@12-0.88 hom@24-0.72 conf@12-1.03 conf@24-0.91 |
| orc_educacao | orc_cut | Educação básica | -4.9 → -5.0 | ok (piora social) | ok (piora social) | = | idh@12-0.001 idh@24-0.002 conf@12+0.42 conf@24+0.60 | idh@12-0.002 idh@24-0.002 conf@12+0.53 conf@24+0.63 |
| orc_educacao | orc_inv | Creches | +5.4 → +5.6 | ok | ok | = | idh@12+0.003 idh@24+0.006 ipca@24+0.03 conf@12-0.71 conf@24-1.07 | idh@12+0.003 idh@24+0.006 ipca@24+0.03 conf@12-0.71 conf@24-1.09 |
| orc_educacao | orc_cut | Merenda escolar | -5.0 → -5.0 | ok (piora social) | ok (piora social) | = | idh@12-0.002 idh@24-0.002 conf@12+0.62 conf@24+0.61 | idh@12-0.002 idh@24-0.002 conf@12+0.62 conf@24+0.58 |
| orc_saude | orc_inv | Atenção básica | +5.4 → +5.1 | ok | ok | = | idh@12+0.006 idh@24+0.006 conf@12-0.49 | idh@12+0.006 idh@24+0.006 conf@12-0.48 |
| orc_saude | orc_cut | Hospitais federais | -5.0 → -5.0 | ok (piora social) | ok (piora social) | = | idh@12-0.003 idh@24-0.003 conf@12+0.60 conf@24+0.58 | idh@12-0.003 idh@24-0.003 conf@12+0.60 conf@24+0.58 |
| orc_saude | orc_cont | Remédios | -4.3 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12+0.001 idh@24+0.001 pob@24-0.04 conf@12+1.65 conf@24+1.23 | idh@12-0.001 idh@24-0.001 conf@12+0.63 conf@24+0.59 |
| orc_seguranca | orc_inv | Toda a Segurança Pública | +5.4 → +5.2 | ok | ok | = | hom@12-0.41 hom@24-0.34 pib@24-0.03 ipca@24+0.03 conf@12-0.74 | hom@12-0.41 hom@24-0.34 ipca@24+0.03 conf@12-0.70 conf@24-1.05 |
| orc_seguranca | orc_cont | Polícia Federal | -4.3 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12-0.001 pob@24-0.04 hom@12-0.39 hom@24-0.33 conf@12+1.65 | hom@12+0.39 hom@24+0.31 conf@12+0.88 |
| orc_seguranca | orc_inv | Força Nacional | +5.4 → +5.5 | ok | ok | = | hom@12-0.41 hom@24-0.34 conf@12-1.12 conf@24-1.64 | hom@12-0.41 hom@24-0.35 conf@12-0.88 |
| orc_seguranca | orc_cut | Presídios | -5.0 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | hom@12-0.55 hom@24-0.44 | hom@12+0.59 hom@24+0.46 |
| orc_infra | orc_inv | Rodovias | +5.8 → +5.8 | ok | ok | = | pob@24-0.10 des@24-0.11 conf@12-0.93 conf@24-1.62 | pob@24-0.10 des@24-0.11 conf@12-0.97 conf@24-1.69 |
| orc_infra | orc_cut | Ferrovias | -5.1 → -5.2 | ok (piora social) | ok (piora social) | = | pob@24+0.04 des@24+0.05 | pob@24+0.07 des@24+0.07 |
| orc_infra | orc_cont | Saneamento | -3.3 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12+0.001 idh@24+0.001 pob@24-0.07 pib@24+0.06 des@24-0.08 | idh@12-0.002 idh@24-0.002 des@24+0.03 conf@12+0.55 conf@24+0.55 |
| orc_infra | orc_inv | Habitação | +5.6 → +5.5 | ok | ok | = | idh@24+0.001 pob@12-0.45 pob@24-0.44 pib@12+0.11 des@12-0.25 | idh@24+0.001 pob@12-0.45 pob@24-0.44 pib@12+0.12 des@12-0.25 |
| orc_trabalho | orc_cut | Todo o Trabalho | -5.0 → -5.2 | só fiscal | só fiscal | ok (piora social) | conf@12+0.71 conf@24+0.66 | des@12+0.04 conf@12-0.67 |
| orc_trabalho | orc_inv | Seguro-desemprego | +5.2 → +5.4 | ok | ok | = | pob@12-0.46 pob@24-0.28 des@12-0.03 | pob@12-0.48 pob@24-0.35 conf@12-0.58 |
| orc_trabalho | orc_cut | Intermediação (Sine) | -5.0 → -5.2 | só fiscal | só fiscal | ok (piora social) | conf@12+0.72 conf@24+0.79 | des@12+0.04 conf@12-0.62 |
| orc_sociedade | orc_cut | Bolsa Família | -5.1 → -5.2 | ok (piora social) | ok (piora social) | = | pob@12+0.44 pob@24+0.33 conf@12+0.67 conf@24+0.63 | pob@12+0.43 pob@24+0.33 conf@12+0.67 conf@24+0.64 |
| orc_sociedade | orc_inv | Cozinha Solidária | +5.4 → +5.3 | ok | ok | = | idh@24+0.001 pob@12-0.80 pob@24-0.58 conf@12-0.58 | idh@24+0.001 pob@12-0.80 pob@24-0.58 conf@12-0.57 |
| orc_justica | orc_cut | Polícia Federal | -5.0 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | hom@12-0.39 hom@24-0.33 | hom@12+0.40 hom@24+0.32 |
| orc_justica | orc_cont | CGU | -4.6 → -5.3 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12-0.001 pob@12-0.04 pob@24-0.11 pib@12+0.13 des@12-0.05 | pob@12+0.03 pib@12-0.07 conf@12-2.54 conf@24-1.17 |
| industria | ind_inv | Soja em grão | +5.7 → +5.7 | misto | misto | = | idh@24+0.001 pob@12-0.07 pob@24-0.11 pib@12+0.12 des@12-0.08 | idh@24+0.001 pob@12-0.07 pob@24-0.11 pib@12+0.12 des@12-0.08 |
| industria | ind_inv | Farelo de soja | +5.6 → +5.8 | misto | misto | = | pob@12-0.07 pob@24-0.10 pib@12+0.10 des@12-0.07 des@24-0.08 | pob@12-0.06 pob@24-0.10 pib@12+0.10 des@12-0.07 des@24-0.08 |
| industria | ind_inv | Café solúvel | +5.6 → +5.7 | misto | misto | = | pob@12-0.05 pob@24-0.10 pib@12+0.09 des@12-0.06 des@24-0.08 | pob@12-0.05 pob@24-0.10 pib@12+0.09 des@12-0.06 des@24-0.08 |
| industria | ind_inv | Couros e peles | +5.7 → +5.5 | misto | **ok** | = | pob@12-0.07 pob@24-0.15 pib@12+0.15 des@12-0.12 des@24-0.13 | pob@12-0.03 ipca@24+0.04 conf@12-0.71 conf@24-1.03 |
| industria | ind_inv | Etanol | +5.5 → +5.6 | ok | ok | = | pob@12-0.05 pob@24-0.21 pib@12+0.07 pib@24+0.09 des@12-0.08 | pob@12-0.04 pob@24-0.22 pib@12+0.07 pib@24+0.09 des@12-0.08 |
| industria | ind_inv | Petróleo bruto | +5.2 → +5.5 | ok | ok | = | pob@12-0.03 pob@24-0.18 pib@24+0.09 des@24-0.18 ipca@24+0.06 | pob@12-0.04 pob@24-0.18 pib@12+0.06 pib@24+0.08 des@24-0.18 |
| industria | ind_inv | Minério de ferro | +5.6 → +5.4 | misto | **ok** | = | pob@12-0.07 pob@24-0.11 pib@12+0.13 des@12-0.09 des@24-0.09 | pob@24-0.04 conf@12-1.03 conf@24-1.58 |
| industria | ind_inv | Ouro | +6.0 → +5.2 | misto | misto | = | pob@12-0.07 pob@24-0.11 pib@12+0.13 des@12-0.09 des@24-0.09 | pob@12-0.04 pob@24-0.03 ipca@24+0.04 desm@24+24.74 conf@12-0.72 |
| industria | ind_inv | Semicondutores / chips | +5.7 → +5.8 | ok | ok | = | idh@24+0.004 pob@12-0.04 pob@24-0.20 pib@24+0.11 des@24-0.22 | idh@24+0.004 pob@12-0.03 pob@24-0.20 pib@24+0.11 des@24-0.22 |
| industria | ind_inv | Fertilizante potássico (KCl) | +5.7 → +5.7 | misto | misto | = | pob@12-0.05 pob@24-0.09 pib@12+0.09 des@12-0.06 des@24-0.08 | pob@12-0.05 pob@24-0.09 pib@12+0.09 des@12-0.06 des@24-0.08 |
| industria | ind_inv | Fertilizantes nitrogenados (ureia, amônia) | +5.7 → +5.6 | misto | misto | = | pob@12-0.05 pob@24-0.10 pib@12+0.09 des@12-0.06 des@24-0.08 | pob@12-0.05 pob@24-0.10 pib@12+0.09 des@12-0.06 des@24-0.08 |
| seguranca | programa | Enviar a Força Nacional para Pernambuco | +0.9 → +0.8 | misto | **ok** | = | pob@12-0.03 pob@24-0.08 pib@12+0.08 des@12-0.04 desm@12+284.08 | hom@12-0.10 |
| seguranca | programa | Mais 100 mil câmeras corporais | +0.7 → +0.7 | só fiscal | **ok** | = | — | hom@12-0.12 |
| infraestrutura | dup | Novo PAC 2027-2030 | +0.0 → +0.0 | ok: repetida não soma | ok: repetida não soma | = | pob@24-0.08 | pob@12+0.06 pib@12-0.06 des@12+0.08 ipca@12-0.06 |
| orc_slider | slider | slider segurança +20% (~R$ 4,4 bi) | +0.0 → +0.0 | ok | ok | = | hom@12-0.44 hom@24-0.57 conf@12-0.33 conf@24-0.46 | hom@12-0.44 hom@24-0.57 conf@12-0.33 conf@24-0.46 |
| conv_seg | conv_apoio | Crime organizado e facções · apoio | +0.0 → +0.0 | extra 0; sem efeito nacional (só indicador do estado) | extra 0; sem efeito nacional (só indicador do estado) | = | — | — |
| conv_sau | conv_cobrar | Filas de cirurgias e consultas · cobrar | +0.0 → +0.0 | extra 0; sem efeito nacional (só indicador do estado) | extra 0; sem efeito nacional (só indicador do estado) | = | — | — |
| conv_edu | conv_plano | Alfabetização e anos iniciais · plano | +0.0 → +0.0 | extra +0.6; sem efeito nacional (só indicador do estado) | extra +0.6; sem efeito nacional (só indicador do estado) | = | — | — |
| saude | programa_p2 | Carreira médica do SUS > Mais R$ 2 bi na car | +2.1 → +2.1 | ok | ok | = | idh@12+0.002 idh@24+0.002 conf@24-0.33 | idh@12+0.002 idh@24+0.002 conf@24-0.33 |
| saude | programa_p2 | Canetas de obesidade no SUS > Mais R$ 2 bi e | +2.1 → +2.1 | ok | ok | = | idh@12+0.002 idh@24+0.002 conf@24-0.33 | idh@12+0.002 idh@24+0.002 conf@24-0.33 |
| saude | programa_p2 | Mais 5 mil leitos de UTI > Mais 5 mil leitos | +3.1 → +3.1 | ok | ok | = | idh@12+0.002 idh@24+0.002 conf@12-0.34 conf@24-0.49 | idh@12+0.002 idh@24+0.002 conf@12-0.34 conf@24-0.49 |
| educacao | programa_p2 | Mais 1 milhão de vagas em tempo integral > M | +0.8 → +0.8 | ok | ok | = | idh@12+0.002 idh@24+0.004 | idh@12+0.002 idh@24+0.004 |
| educacao | programa_p2 | Adicional para professores de periferia > Ad | +1.1 → +1.1 | ok | ok | = | idh@12+0.001 idh@24+0.001 | idh@12+0.001 idh@24+0.001 |
| educacao | programa | Vagas em licenciaturas e saúde | +3.1 → +3.1 | ok | ok | = | idh@12+0.002 idh@24+0.002 conf@12-0.36 conf@24-0.49 | idh@12+0.002 idh@24+0.002 conf@12-0.36 conf@24-0.49 |
| educacao | programa | Mais vagas de ensino técnico | +2.1 → +2.1 | ok | ok | = | pob@12-0.44 pob@24-0.27 | pob@12-0.44 pob@24-0.27 |
| infraestrutura | programa_p2 | Mais Minha Casa Minha Vida > Mais 500 mil mo | +8.8 → +8.8 | ok | ok | = | idh@24+0.001 pob@12-0.46 pob@24-0.47 pib@12+0.14 pib@24+0.04 | idh@24+0.001 pob@12-0.46 pob@24-0.47 pib@12+0.14 pib@24+0.04 |
| infraestrutura | programa | Transmissão para o Nordeste | +6.4 → +6.4 | ok | ok | = | pob@24-0.24 pib@12+0.07 pib@24+0.15 des@24-0.26 ipca@24+0.06 | pob@24-0.24 pib@12+0.07 pib@24+0.15 des@24-0.26 ipca@24+0.06 |
| infraestrutura | programa | Manutenção das BRs (DNIT) | +6.8 → +6.8 | ok | ok | = | pob@24-0.16 pib@24+0.07 des@24-0.18 conf@12-1.09 conf@24-1.59 | pob@24-0.16 pib@24+0.07 des@24-0.18 conf@12-1.09 conf@24-1.59 |
| infraestrutura | programa | Ferrovia Centro-Oeste (FICO) | +7.2 → +7.2 | ok | ok | = | pob@12-0.03 pob@24-0.03 ipca@24+0.05 conf@12-0.68 conf@24-1.45 | pob@12-0.04 pob@24-0.13 pib@12+0.06 pib@24+0.06 des@12-0.08 |
| infraestrutura | programa | Bolsa-sucata para caminhões | +2.2 → +2.2 | ok | ok | = | pob@24-0.08 pib@24+0.05 des@24-0.09 | pob@24-0.08 pib@24+0.05 des@24-0.09 |
| justica | programa | PGR com mandato único (PEC) | +0.0 → +0.0 | nulo | nulo | ok | pib@12+0.05 conf@12+2.01 conf@24+1.08 | pib@12+0.05 conf@12+2.01 conf@24+1.08 | lote Justiça: **ok (efeito próprio)** |
| justica | programa | Balcão único da leniência | +0.0 → +0.0 | misto | **nulo** | = | pob@24-0.06 pib@12+0.06 des@12-0.03 desm@12+248.57 desm@24+186.12 | — | lote Justiça: **ok (efeito próprio)** |
| orc_educacao | orc_inv | Todo o MEC | +6.0 → +5.3 | ok | ok | = | idh@12+0.002 idh@24+0.004 ipca@24+0.03 conf@12-0.68 conf@24-1.10 | idh@12+0.001 idh@24+0.004 conf@12-1.03 conf@24-1.62 |
| orc_educacao | orc_inv | Universidades e IFs | +5.5 → +5.4 | ok | ok | = | idh@12+0.001 idh@24+0.004 ipca@24+0.03 conf@12-0.66 conf@24-1.07 | idh@12+0.002 idh@24+0.004 ipca@24+0.03 conf@12-0.72 conf@24-1.08 |
| orc_educacao | orc_cut | Creches | -5.0 → -5.0 | ok (piora social) | ok (piora social) | = | idh@12-0.003 idh@24-0.003 conf@12+0.63 conf@24+0.61 | idh@12-0.003 idh@24-0.003 conf@12+0.61 conf@24+0.60 |
| orc_educacao | orc_cont | Merenda escolar | -4.3 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12+0.001 idh@24+0.001 pob@24-0.04 pib@24+0.03 conf@12+1.65 | idh@12-0.002 idh@24-0.002 conf@12+0.61 conf@24+0.58 |
| orc_saude | orc_cut | Atenção básica | -5.0 → -5.0 | ok (piora social) | ok (piora social) | = | idh@12-0.003 idh@24-0.003 conf@12+0.63 conf@24+0.65 | idh@12-0.003 idh@24-0.003 conf@12+0.63 conf@24+0.61 |
| orc_saude | orc_cont | Hospitais federais | -4.3 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | pob@24-0.04 conf@12+1.61 conf@24+1.27 | idh@12-0.003 idh@24-0.003 conf@12+0.60 conf@24+0.58 |
| orc_saude | orc_inv | Vacinação | +5.6 → +5.4 | ok | ok | = | idh@12+0.007 idh@24+0.008 conf@12-0.48 | idh@12+0.007 idh@24+0.008 conf@12-0.47 |
| orc_seguranca | orc_cut | Toda a Segurança Pública | -5.0 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | hom@12-0.39 hom@24-0.33 | hom@12+0.40 hom@24+0.32 |
| orc_seguranca | orc_inv | PRF | +5.7 → +5.7 | ok | ok | = | hom@12-0.41 hom@24-0.34 ipca@24+0.03 conf@12-0.74 conf@24-1.11 | hom@12-0.41 hom@24-0.34 ipca@24+0.03 conf@12-0.74 conf@24-1.11 |
| orc_seguranca | orc_cut | Força Nacional | -5.0 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | hom@12-0.39 hom@24-0.32 | hom@12+0.40 hom@24+0.32 |
| orc_seguranca | orc_cont | Presídios | -4.3 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12-0.001 hom@12-0.54 hom@24-0.44 conf@12+1.24 | hom@12+0.60 hom@24+0.47 |
| orc_infra | orc_cut | Rodovias | -5.1 → -5.1 | ok (piora social) | ok (piora social) | = | pob@24+0.04 des@24+0.05 | pob@24+0.04 des@24+0.05 |
| orc_infra | orc_cont | Ferrovias | -3.7 → -5.1 | só fiscal | **ok (piora social)** | = | ipca@12-0.12 | pob@24+0.07 des@24+0.07 |
| orc_infra | orc_inv | Energia | +5.1 → +5.6 | misto | misto | = | pob@24-0.11 pib@24+0.04 des@24-0.13 ipca@24+0.05 desm@12+37.61 | pob@12-0.03 pob@24-0.12 pib@24+0.04 des@24-0.13 ipca@24+0.05 |
| orc_infra | orc_cut | Habitação | -5.0 → -5.0 | ok (piora social) | ok (piora social) | = | pob@24+0.04 des@24+0.05 conf@12+0.43 | pob@24+0.04 des@24+0.05 conf@12+0.40 |
| orc_trabalho | orc_inv | Qualificação | +5.2 → +5.4 | só fiscal | **ok** | = | des@12-0.03 | pob@12-0.05 pob@24-0.04 des@12-0.09 des@24-0.04 conf@12-0.60 |
| orc_trabalho | orc_cut | Seguro-desemprego | -5.3 → -5.2 | ok (piora social) | ok (piora social) | = | pob@12+0.42 pob@24+0.29 conf@12+0.81 conf@24+0.72 | pob@12+0.42 pob@24+0.29 conf@12+0.81 conf@24+0.72 |
| orc_sociedade | orc_inv | Toda a assistência social | +5.2 → +5.3 | ok | ok | = | pob@12-0.45 pob@24-0.32 conf@12-0.57 | pob@12-0.44 pob@24-0.28 des@12-0.04 ipca@24+0.04 conf@12-0.73 |
| orc_sociedade | orc_inv | BPC | +5.4 → +5.3 | ok | ok | = | idh@24+0.001 pob@12-0.53 pob@24-0.38 conf@12-0.58 | pob@12-0.52 pob@24-0.34 des@12-0.04 ipca@24+0.04 conf@12-0.73 |
| orc_sociedade | orc_cut | Cozinha Solidária | -5.1 → -5.2 | ok (piora social) | ok (piora social) | = | idh@24-0.001 pob@12+0.75 pob@24+0.54 conf@12+0.80 conf@24+0.67 | idh@24-0.001 pob@12+0.76 pob@24+0.54 conf@12+0.82 conf@24+0.72 |
| orc_justica | orc_cont | Polícia Federal | -4.3 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12-0.001 pob@24-0.04 hom@12-0.39 hom@24-0.33 conf@12+1.66 | hom@12+0.39 hom@24+0.31 conf@12+0.90 |
| orc_justica | orc_cut | Judiciário: penduricalhos | -5.1 → -5.1 | só fiscal | só fiscal | = | ipca@12-0.11 conf@12-1.51 | ipca@12-0.11 conf@12-1.52 |
| industria | ind_cred | Soja em grão | +0.8 → +0.7 | ok | ok | = | idh@24+0.001 pob@12-1.07 pob@24-0.79 pib@12+0.06 des@12-0.05 | pob@24-0.04 pib@12+0.04 des@12-0.03 |
| industria | ind_cred | Farelo de soja | +0.8 → +0.7 | ok | **só fiscal** | = | idh@24+0.001 pob@12-1.07 pob@24-0.78 pib@12+0.04 des@12-0.05 | — |
| industria | ind_cred | Café solúvel | +0.7 → +0.6 | ok | **só fiscal** | = | idh@24+0.001 pob@12-1.06 pob@24-0.78 pib@12+0.04 pib@24+0.03 | — |
| industria | ind_cred | Couros e peles | +0.7 → +0.6 | ok | **só fiscal** | = | idh@24+0.001 pob@12-1.06 pob@24-0.78 pib@12+0.04 pib@24+0.03 | — |
| industria | ind_cred | Etanol | +1.8 → +1.6 | ok | ok | = | idh@24+0.001 pob@12-1.08 pob@24-0.92 pib@12+0.10 pib@24+0.12 | pob@12-0.05 pob@24-0.09 pib@12+0.07 pib@24+0.05 des@24-0.08 |
| industria | ind_cred | Petróleo bruto | +0.7 → +0.6 | ok | **só fiscal** | = | idh@24+0.001 pob@12-1.06 pob@24-0.78 pib@12+0.04 des@12-0.04 | — |
| industria | ind_cred | Minério de ferro | +1.7 → +1.3 | misto | **só fiscal** | = | idh@24+0.001 pob@12-1.11 pob@24-1.01 pib@12+0.18 pib@24+0.18 | — |
| industria | ind_cred | Ouro | +0.7 → +0.6 | ok | **só fiscal** | = | idh@24+0.001 pob@12-1.06 pob@24-0.78 pib@12+0.04 pib@24+0.03 | — |
| industria | ind_cred | Semicondutores / chips | +1.1 → +0.7 | misto | **só fiscal** | = | idh@24+0.002 pob@12-1.10 pob@24-0.87 pib@12+0.13 pib@24+0.11 | — |
| industria | ind_cred | Fertilizante potássico (KCl) | +1.6 → +1.2 | misto | **só fiscal** | = | idh@24+0.002 pob@12-1.10 pob@24-0.95 pib@12+0.14 pib@24+0.16 | — |
| industria | ind_cred | Fertilizantes nitrogenados (ureia, amônia) | +1.8 → +1.2 | misto | **só fiscal** | = | idh@24+0.002 pob@12-1.11 pob@24-0.96 pib@12+0.16 pib@24+0.15 | — |
| seguranca | programa | Operação integrada PF + inteligência contra  | +1.9 → +1.9 | ok | ok | misto | hom@12-0.12 pib@24-0.05 conf@12-1.16 conf@24-1.21 | hom@12-0.23 hom@24-0.19 pib@24-0.04 conf@12-1.16 conf@24-1.21 |
| seguranca | programa | Centros de Juventude nas periferias | +2.0 → +2.1 | só fiscal | **ok** | = | conf@24-0.35 | hom@12-0.16 hom@24-0.13 conf@24-0.35 |
| justica | dup | Mais 3 mil cargos na PF | +0.0 → +0.0 | ok: repetida não soma | ok: repetida não soma | = | — | — |
| orc_slider | slider | slider educação +5% (~R$ 9 bi) | +0.0 → +0.0 | ok | ok | = | idh@12+0.001 idh@24+0.002 ipca@24+0.03 conf@12-0.69 conf@24-0.99 | idh@12+0.001 idh@24+0.002 ipca@24+0.03 conf@12-0.69 conf@24-0.99 |
| conv_seg | conv_cobrar | Crime organizado e facções · cobrar | +0.0 → +0.0 | extra 0; sem efeito nacional (só indicador do estado) | extra 0; sem efeito nacional (só indicador do estado) | = | — | — |
| conv_sau | conv_plano | Filas de cirurgias e consultas · plano | +0.0 → +0.0 | extra +0.8; sem efeito nacional (só indicador do estado) | extra +0.8; sem efeito nacional (só indicador do estado) | = | — | — |
| conv_infra | conv_apoio | Estado das rodovias · apoio | +0.0 → +0.0 | extra +0.6; sem efeito nacional (só indicador do estado) | extra +0.6; sem efeito nacional (só indicador do estado) | = | — | — |
| saude | programa | Prazo máximo para cirurgias eletivas | +3.2 → +3.2 | ok | ok | = | idh@12+0.002 idh@24+0.002 | idh@12+0.002 idh@24+0.002 |
| saude | programa | Vacina contra herpes-zóster | +1.6 → +1.6 | ok | ok | = | idh@12+0.004 idh@24+0.004 | idh@12+0.004 idh@24+0.004 |
| educacao | programa | Pé-de-Meia no fundamental II | +3.2 → +3.2 | ok | ok | = | idh@12+0.001 idh@24+0.001 pob@12-0.45 pob@24-0.32 conf@12-0.41 | idh@12+0.001 idh@24+0.001 pob@12-0.45 pob@24-0.32 conf@12-0.41 |
| educacao | programa | Vaga garantida em creche | +5.3 → +5.3 | ok | ok | = | idh@24+0.001 pob@12-0.77 pob@24-0.52 des@12-0.04 ipca@24+0.04 | idh@24+0.001 pob@12-0.77 pob@24-0.52 des@12-0.04 ipca@24+0.04 |
| educacao | programa | Reforço em leitura | +2.1 → +2.1 | ok | ok | = | idh@12+0.002 idh@24+0.004 conf@24-0.33 | idh@12+0.002 idh@24+0.004 conf@24-0.33 |
| educacao | programa | Merenda: valor por refeição +30% | +1.8 → +1.8 | ok | ok | = | idh@12+0.002 idh@24+0.002 | idh@12+0.002 idh@24+0.002 |
| infraestrutura | programa | Esgoto nos municípios pequenos | +7.4 → +7.4 | ok | ok | = | idh@12+0.002 idh@24+0.003 pob@12-0.08 pob@24-0.19 pib@12+0.08 | idh@12+0.002 idh@24+0.003 pob@12-0.08 pob@24-0.19 pib@12+0.08 |
| infraestrutura | programa | Novo PAC 2027-2030 | +75.2 → +75.2 | ok | ok | = | idh@24+0.001 pob@12-0.15 pob@24-0.32 pib@12+0.25 des@12-0.39 | idh@24+0.001 pob@12-0.15 pob@24-0.32 pib@12+0.25 des@12-0.39 |
| infraestrutura | programa | Internet rural por satélite | +2.3 → +2.1 | misto | **só fiscal** | = | pob@12-0.04 pob@24-0.08 pib@12+0.08 des@12-0.04 ipca@24+0.03 | — |
| infraestrutura | programa | Leilão de 6 mil km de rodovias | +0.0 → +0.0 | ok | ok | = | pob@12-0.04 pob@24-0.08 pib@12+0.12 pib@24+0.06 des@24-0.05 | pob@12-0.04 pob@24-0.08 pib@12+0.12 pib@24+0.06 des@24-0.05 |
| infraestrutura | programa | Fundo de mobilidade urbana | +6.0 → +6.0 | ok | ok | = | idh@24+0.001 pob@12-0.27 pob@24-0.58 pib@12+0.17 des@12-0.29 | idh@24+0.001 pob@12-0.27 pob@24-0.58 pib@12+0.17 des@12-0.29 |
| justica | programa | Mais 3 mil cargos na PF | +1.0 → +1.0 | ok | ok | = | hom@12-0.39 hom@24-0.33 | hom@12-0.39 hom@24-0.33 |
| justica | programa | Cortar penduricalhos (PLP) | +0.8 → +0.8 | só fiscal | **ok** | = | — | hom@12-0.12 |
| justica | programa | Sem delação de preso preventivo | +0.6 → +0.6 | ok | ok | = | hom@12-0.38 hom@24-0.32 | hom@12-0.38 hom@24-0.32 |
| orc_educacao | orc_cut | Todo o MEC | -5.0 → -3.7 | só fiscal | **ok (piora social)** | = | conf@12+0.63 conf@24+0.58 | idh@12-0.001 idh@24-0.002 |
| orc_educacao | orc_cut | Universidades e IFs | -5.0 → -5.0 | ok (piora social) | ok (piora social) | = | idh@12-0.002 idh@24-0.002 conf@12+0.59 conf@24+0.61 | idh@12-0.002 idh@24-0.002 conf@12+0.59 conf@24+0.61 |
| orc_educacao | orc_cont | Creches | -3.9 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12+0.001 idh@24+0.003 pob@24-0.04 conf@12+1.59 conf@24+1.16 | idh@12-0.003 idh@24-0.003 conf@12+0.62 conf@24+0.64 |
| orc_saude | orc_inv | Todo o Ministério da Saúde | +5.2 → +5.2 | ok | ok | = | idh@12+0.003 idh@24+0.004 ipca@24+0.03 conf@12-0.64 conf@24-1.05 | idh@12+0.003 idh@24+0.004 ipca@24+0.03 conf@12-0.64 conf@24-1.05 |
| orc_saude | orc_cont | Atenção básica | -4.4 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12+0.001 idh@24+0.001 pob@24-0.03 pib@24+0.04 conf@12+1.63 | idh@12-0.003 idh@24-0.003 conf@12+0.64 conf@24+0.61 |
| orc_saude | orc_inv | Remédios | +5.2 → +5.2 | ok | ok | = | idh@12+0.002 idh@24+0.002 ipca@24+0.03 conf@12-0.67 conf@24-1.05 | idh@12+0.002 idh@24+0.002 ipca@24+0.03 conf@12-0.67 conf@24-1.05 |
| orc_saude | orc_cut | Vacinação | -5.0 → -5.0 | ok (piora social) | ok (piora social) | = | idh@12-0.004 idh@24-0.004 conf@12+0.63 conf@24+0.59 | idh@12-0.004 idh@24-0.004 conf@12+0.63 conf@24+0.59 |
| orc_seguranca | orc_inv | Polícia Federal | +5.4 → +5.4 | ok | ok | = | hom@12-0.40 hom@24-0.34 ipca@24+0.03 conf@12-0.69 conf@24-1.07 | hom@12-0.40 hom@24-0.34 ipca@24+0.03 conf@12-0.69 conf@24-1.07 |
| orc_seguranca | orc_cut | PRF | -5.0 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | hom@12-0.38 hom@24-0.31 | hom@12+0.39 hom@24+0.31 |
| orc_seguranca | orc_cont | Força Nacional | -4.1 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12-0.001 pob@24-0.04 hom@12-0.39 hom@24-0.33 conf@12+1.60 | hom@12+0.39 hom@24+0.32 |
| orc_infra | orc_inv | Toda a infraestrutura | +5.6 → +5.2 | ok | ok | = | pob@12-0.05 pob@24-0.10 pib@12+0.07 des@12-0.10 des@24-0.09 | pob@12-0.04 pob@24-0.09 pib@12+0.07 pib@24+0.03 des@12-0.09 |
| orc_infra | orc_cont | Rodovias | -3.4 → -5.1 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | pob@24-0.09 des@24-0.09 ipca@12-0.12 | pob@24+0.04 des@24+0.05 |
| orc_infra | orc_inv | Saneamento | +5.4 → +5.6 | ok | ok | = | idh@12+0.001 idh@24+0.002 pob@24-0.08 des@24-0.10 ipca@24+0.05 | idh@12+0.001 idh@24+0.002 pob@24-0.09 pib@24+0.05 des@24-0.12 |
| orc_infra | orc_cut | Energia | -5.0 → -5.1 | só fiscal | **INVERTIDO (melhora ao cortar)** | = | conf@12+0.73 conf@24+0.67 | pob@24+0.03 des@12+0.03 ipca@24-0.04 desm@12-54.37 |
| orc_infra | orc_cont | Habitação | -3.5 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12-0.001 pob@12-0.44 pob@24-0.41 pib@12+0.10 pib@24+0.06 | pob@24+0.04 des@24+0.05 conf@12+0.49 conf@24+0.50 |
| orc_trabalho | orc_cut | Qualificação | -5.1 → -5.2 | INVERTIDO (melhora ao cortar) | **só fiscal** | ok (piora social) | idh@24+0.002 ipca@12-0.12 conf@12-0.95 | des@12+0.04 conf@12-0.62 |
| orc_trabalho | orc_cont | Seguro-desemprego | -3.6 → -5.5 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12-0.001 idh@24-0.001 pob@12-0.25 pob@24-0.21 conf@12+1.39 | idh@24-0.001 pob@12+0.47 pob@24+0.39 pib@24-0.04 des@24+0.06 |
| orc_sociedade | orc_cut | Toda a assistência social | -5.1 → -5.3 | ok (piora social) | ok (piora social) | = | pob@12+0.41 pob@24+0.29 conf@12+0.66 conf@24+0.60 | pob@12+0.41 pob@24+0.30 conf@12+0.67 conf@24+0.68 |
| orc_sociedade | orc_cut | BPC | -5.2 → -5.1 | ok (piora social) | ok (piora social) | = | pob@12+0.49 pob@24+0.37 conf@12+0.67 conf@24+0.64 | pob@12+0.49 pob@24+0.36 conf@12+0.80 conf@24+0.70 |
| orc_sociedade | orc_cont | Cozinha Solidária | -4.3 → -5.1 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12-0.001 idh@24-0.001 pob@12-0.25 pob@24-0.20 conf@12+1.49 | idh@24-0.001 pob@12+0.75 pob@24+0.53 conf@12+0.80 conf@24+0.70 |
| orc_justica | orc_inv | CGU | +5.7 → +5.5 | misto | **só fiscal** | = | pob@12-0.05 pob@24-0.09 pib@12+0.11 des@12-0.08 ipca@12+0.03 | conf@12-1.10 conf@24-1.66 |
| industria | ind_imp | Soja em grão | +0.0 → +0.0 | ok | ok | = | pob@24-0.03 pib@12+0.04 des@24-0.03 | pob@24-0.03 pib@12+0.04 des@24-0.03 |
| industria | ind_imp | Farelo de soja | +0.0 → +0.0 | ok | ok | = | pob@24-0.03 pib@12+0.04 des@24-0.03 | pob@24-0.03 pib@12+0.04 des@24-0.03 |
| industria | ind_imp | Café solúvel | +0.0 → +0.0 | ok | ok | = | pob@24-0.03 pib@12+0.03 des@24-0.03 | pob@24-0.03 pib@12+0.03 des@24-0.03 |
| industria | ind_imp | Couros e peles | +0.0 → +0.0 | ok | ok | = | pob@24-0.04 pib@12+0.04 des@24-0.03 | pob@24-0.04 pib@12+0.04 des@24-0.03 |
| industria | ind_imp | Etanol | +0.0 → +0.0 | ok | ok | = | pob@24-0.03 pib@12+0.03 des@24-0.03 | pob@24-0.03 pib@12+0.03 des@24-0.03 |
| industria | ind_imp | Petróleo bruto | +0.0 → +0.0 | ok | ok | = | pob@24-0.03 pib@12+0.03 | pob@24-0.03 pib@12+0.03 |
| industria | ind_imp | Minério de ferro | +0.0 → +0.0 | ok | ok | = | pob@24-0.04 pib@12+0.04 des@24-0.03 | pob@24-0.04 pib@12+0.04 des@24-0.03 |
| industria | ind_imp | Ouro | +0.0 → +0.0 | ok | ok | = | pob@24-0.04 pib@12+0.04 des@24-0.03 | pob@24-0.04 pib@12+0.04 des@24-0.03 |
| industria | ind_imp | Semicondutores / chips | +0.0 → +0.0 | ok | ok | = | pob@24-0.04 pib@12+0.04 des@24-0.03 | pob@24-0.04 pib@12+0.04 des@24-0.03 |
| industria | ind_imp | Fertilizante potássico (KCl) | +0.0 → +0.0 | ok | ok | = | pob@24-0.03 pib@12+0.03 | pob@24-0.03 pib@12+0.03 |
| industria | ind_imp | Fertilizantes nitrogenados (ureia, amônia) | +0.0 → +0.0 | ok | ok | = | pob@24-0.03 pib@12+0.03 | pob@24-0.03 pib@12+0.03 |
| seguranca | programa | Transferir lideranças de Pernambuco para pre | +0.5 → +0.5 | só fiscal | **ok** | = | conf@12-0.46 conf@24-0.45 | hom@12-0.18 hom@24-0.14 conf@12-0.46 conf@24-0.45 |
| saude | dup | Mais 5 mil leitos de UTI | +0.0 → +0.0 | ok: repetida não soma | ok: repetida não soma | = | — | — |
| orc_slider | slider | slider saúde +2% (~R$ 4,8 bi) | +0.0 → +0.0 | ok | ok | = | idh@24+0.001 conf@12-0.36 conf@24-0.52 | idh@24+0.001 conf@12-0.36 conf@24-0.52 |
| orc_slider | slider | slider infra +10% (~R$ 7 bi) | +0.3 → +0.3 | ok | ok | = | pob@12-0.04 pob@24-0.06 pib@12+0.06 pib@24+0.03 des@12-0.04 | pob@12-0.04 pob@24-0.06 pib@12+0.06 pib@24+0.03 des@12-0.04 |
| conv_seg | conv_plano | Crime organizado e facções · plano | +0.0 → +0.0 | extra 0; sem efeito nacional (só indicador do estado) | extra 0; sem efeito nacional (só indicador do estado) | = | — | — |
| conv_edu | conv_apoio | Alfabetização e anos iniciais · apoio | +0.0 → +0.0 | extra 0; sem efeito nacional (só indicador do estado) | extra 0; sem efeito nacional (só indicador do estado) | = | — | — |
| conv_infra | conv_cobrar | Estado das rodovias · cobrar | +0.0 → +0.0 | extra 0; sem efeito nacional (só indicador do estado) | extra 0; sem efeito nacional (só indicador do estado) | = | — | — |
| saude | programa_p2 | Prazo máximo para cirurgias eletivas > Prazo | +2.1 → +2.1 | ok | ok | = | idh@12+0.002 idh@24+0.002 conf@24-0.33 | idh@12+0.002 idh@24+0.002 conf@24-0.33 |
| saude | programa | Mosquitos com Wolbachia | +0.8 → +0.8 | ok | ok | = | idh@12+0.002 idh@24+0.002 | idh@12+0.002 idh@24+0.002 |
| educacao | programa_p2 | Pé-de-Meia no fundamental II > Mais R$ 2 bi  | +2.1 → +2.1 | ok | ok | = | idh@12+0.001 idh@24+0.001 pob@12-0.36 pob@24-0.25 conf@24-0.35 | idh@12+0.001 idh@24+0.001 pob@12-0.36 pob@24-0.25 conf@24-0.35 |
| educacao | programa_p2 | Vaga garantida em creche > Mais R$ 3 bi por  | +3.2 → +3.2 | ok | ok | = | pob@12-0.56 pob@24-0.36 | pob@12-0.56 pob@24-0.36 |
| educacao | programa | Notebooks para o ensino médio | +4.6 → +4.6 | ok | ok | = | idh@12+0.002 idh@24+0.002 conf@12-0.58 conf@24-0.92 | idh@12+0.002 idh@24+0.002 conf@12-0.58 conf@24-0.92 |
| educacao | programa | Passe livre estudantil | +4.9 → +4.9 | ok | ok | = | idh@24+0.001 pob@12-0.23 pob@24-0.51 pib@12+0.19 pib@24+0.06 | idh@24+0.001 pob@12-0.23 pob@24-0.51 pib@12+0.19 pib@24+0.06 |
| infraestrutura | programa_p2 | Esgoto nos municípios pequenos > Mais R$ 3 b | +3.3 → +3.3 | ok | ok | = | pob@24-0.11 pib@24+0.05 des@24-0.12 ipca@24+0.04 conf@12-0.31 | pob@24-0.11 pib@24+0.05 des@24-0.12 ipca@24+0.04 conf@12-0.31 |
| infraestrutura | programa | Energia solar para famílias de baixa renda | +5.7 → +5.7 | ok | ok | = | pob@24-0.17 pib@24+0.07 des@24-0.18 conf@12-0.91 conf@24-1.68 | pob@24-0.17 pib@24+0.07 des@24-0.18 conf@12-0.91 conf@24-1.68 |
| infraestrutura | programa | Duplicar trechos de BRs | +10.4 → +10.4 | ok | ok | = | pob@12-0.04 pob@24-0.13 des@12-0.08 des@24-0.14 ipca@12+0.03 | pob@12-0.04 pob@24-0.13 des@12-0.08 des@24-0.14 ipca@12+0.03 |
| infraestrutura | programa | Conceder a BR-319 (polêmica ambiental) | +3.5 → +3.5 | misto | misto | = | idh@24+0.001 pob@12-0.06 pob@24-0.24 pib@12+0.16 pib@24+0.18 | idh@24+0.001 pob@12-0.06 pob@24-0.24 pib@12+0.16 pib@24+0.18 |
| infraestrutura | programa_p2 | Fundo de mobilidade urbana > Mais R$ 3 bi de | +3.1 → +3.1 | ok | ok | = | pob@24-0.10 pib@24+0.06 des@24-0.12 ipca@24+0.04 conf@12-0.31 | pob@24-0.10 pib@24+0.06 des@24-0.12 ipca@24+0.04 conf@12-0.31 |
| justica | programa_p2 | Mais 3 mil cargos na PF > Mais 2 mil cargos  | +0.7 → +0.7 | ok | ok | = | hom@12-0.40 hom@24-0.33 | hom@12-0.40 hom@24-0.33 |
| justica | programa | Punir quem paga acima do teto | +0.0 → +0.0 | misto | **nulo** | = | pob@12-0.03 pob@24-0.07 pib@12+0.07 des@12-0.04 desm@12+284.08 | — | lote Justiça: **ok (efeito próprio)** |
| justica | programa | Sigilo de 100 anos: vetar para gastos | +0.0 → +0.0 | nulo | nulo | ok | pib@12+0.05 conf@12+2.01 conf@24+1.08 | pib@12+0.05 conf@12+2.01 conf@24+1.08 | lote Justiça: **ok (efeito próprio)** |
| orc_educacao | orc_inv | Educação básica | +5.3 → +5.4 | ok | ok | = | idh@12+0.003 idh@24+0.004 conf@12-1.05 conf@24-1.63 | idh@12+0.004 idh@24+0.004 ipca@24+0.03 conf@12-0.68 conf@24-1.07 |
| orc_educacao | orc_cont | Universidades e IFs | -3.9 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@24+0.001 pob@24-0.04 pib@24+0.03 conf@12+1.58 conf@24+1.21 | idh@12-0.002 idh@24-0.002 conf@12+0.62 conf@24+0.58 |
| orc_educacao | orc_inv | Merenda escolar | +5.5 → +5.7 | ok | ok | = | idh@12+0.004 idh@24+0.004 conf@12-0.49 | idh@12+0.004 idh@24+0.004 conf@12-0.45 |
| orc_saude | orc_cut | Todo o Ministério da Saúde | -5.0 → -4.8 | ok (piora social) | ok (piora social) | = | idh@12-0.001 idh@24-0.002 conf@12+0.44 conf@24+0.63 | idh@12-0.001 idh@24-0.002 conf@12+0.41 conf@24+0.61 |
| orc_saude | orc_inv | Hospitais federais | +5.2 → +5.8 | ok | ok | = | idh@12+0.002 idh@24+0.003 ipca@24+0.03 conf@12-0.67 conf@24-1.05 | idh@12+0.002 idh@24+0.003 conf@12-1.01 conf@24-1.65 |
| orc_saude | orc_cut | Remédios | -5.0 → -5.0 | ok (piora social) | ok (piora social) | = | idh@12-0.001 idh@24-0.001 conf@12+0.62 conf@24+0.59 | idh@12-0.001 idh@24-0.001 conf@12+0.62 conf@24+0.62 |
| orc_saude | orc_cont | Vacinação | -3.4 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12+0.003 idh@24+0.003 pob@24-0.04 pib@24+0.04 conf@12+1.43 | idh@12-0.004 idh@24-0.004 conf@12+0.64 conf@24+0.62 |
| orc_seguranca | orc_cut | Polícia Federal | -5.0 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | hom@12-0.39 hom@24-0.33 | hom@12+0.40 hom@24+0.32 |
| orc_seguranca | orc_cont | PRF | -4.3 → -5.0 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12-0.001 pob@24-0.04 hom@12-0.41 hom@24-0.34 conf@12+1.65 | hom@12+0.41 hom@24+0.33 conf@12+0.90 |
| orc_seguranca | orc_inv | Presídios | +5.2 → +5.2 | ok | ok | = | hom@12-0.55 hom@24-0.44 pib@24-0.05 ipca@24+0.03 conf@12-1.13 | hom@12-0.55 hom@24-0.45 conf@12-1.43 conf@24-1.97 |
| orc_infra | orc_cut | Toda a infraestrutura | -5.1 → -5.1 | ok (piora social) | ok (piora social) | = | pob@24+0.04 des@24+0.04 | pob@24+0.04 des@24+0.04 |
| orc_infra | orc_inv | Ferrovias | +5.4 → +5.6 | só fiscal | **ok** | = | ipca@24+0.04 conf@12-0.60 conf@24-1.27 | pob@24-0.13 pib@24+0.06 des@12-0.07 des@24-0.14 ipca@12+0.03 |
| orc_infra | orc_cut | Saneamento | -5.0 → -5.0 | ok (piora social) | ok (piora social) | = | idh@12-0.002 idh@24-0.002 des@24+0.03 conf@12+0.52 conf@24+0.50 | idh@12-0.002 idh@24-0.002 des@24+0.03 conf@12+0.51 conf@24+0.50 |
| orc_infra | orc_cont | Energia | -4.8 → -5.1 | INVERTIDO (melhora ao cortar) | INVERTIDO (melhora ao cortar) | = | idh@12-0.001 idh@24-0.001 pob@24-0.04 pib@24+0.04 conf@12+1.74 | pob@24+0.03 des@12+0.03 ipca@24-0.04 desm@12-54.37 |
| orc_trabalho | orc_inv | Todo o Trabalho | +5.3 → +5.2 | só fiscal | **ok** | = | conf@12-0.60 conf@24-0.62 | pob@12-0.05 pob@24-0.04 des@12-0.09 des@24-0.04 conf@12-0.60 |
| orc_trabalho | orc_cont | Qualificação | -4.3 → -5.2 | INVERTIDO (melhora ao cortar) | **só fiscal** | ok (piora social) | idh@12-0.001 idh@24-0.001 pob@24-0.03 conf@12+1.41 conf@24+1.18 | des@12+0.04 conf@12-0.67 |
| orc_trabalho | orc_inv | Intermediação (Sine) | +5.2 → +5.2 | só fiscal | **ok** | = | conf@12-0.60 conf@24-0.62 | pob@12-0.04 des@12-0.06 |
| orc_sociedade | orc_inv | Bolsa Família | +5.4 → +5.2 | ok | ok | = | pob@12-0.46 pob@24-0.30 des@12-0.04 ipca@24+0.04 conf@12-0.73 | pob@12-0.47 pob@24-0.34 conf@12-0.57 |
| orc_sociedade | orc_cont | BPC | -3.3 → -5.1 | INVERTIDO (melhora ao cortar) | **ok (piora social)** | = | idh@12-0.001 idh@24-0.001 pob@12-0.30 pob@24-0.24 conf@12+1.43 | pob@12+0.48 pob@24+0.36 conf@12+0.80 conf@24+0.70 |
| orc_justica | orc_inv | Polícia Federal | +5.4 → +5.4 | ok | ok | = | hom@12-0.40 hom@24-0.34 ipca@24+0.03 conf@12-0.73 conf@24-1.07 | hom@12-0.40 hom@24-0.34 ipca@24+0.03 conf@12-0.74 conf@24-1.07 |
| orc_justica | orc_cut | CGU | -4.7 → -5.3 | só fiscal | **ok (piora social)** | = | pib@12+0.09 conf@12+4.21 conf@24+3.10 | pob@12+0.03 pib@12-0.06 conf@12-2.55 conf@24-1.21 |
| industria | ind_isen | Soja em grão | +0.0 → +0.0 | ok | ok | = | pob@12-0.03 pob@24-0.06 pib@12+0.06 des@12-0.04 des@24-0.05 | pob@12-0.03 pob@24-0.06 pib@12+0.06 des@12-0.04 des@24-0.05 |
| industria | ind_isen | Farelo de soja | +0.0 → +0.0 | ok | ok | = | pob@12-0.03 pob@24-0.05 pib@12+0.06 des@12-0.04 des@24-0.04 | pob@12-0.03 pob@24-0.05 pib@12+0.06 des@12-0.04 des@24-0.04 |
| industria | ind_isen | Café solúvel | +0.0 → +0.0 | ok | ok | = | pob@24-0.05 pib@12+0.05 des@12-0.03 des@24-0.04 | pob@24-0.05 pib@12+0.05 des@12-0.03 des@24-0.04 |
| industria | ind_isen | Couros e peles | +0.0 → +0.0 | ok | ok | = | pob@12-0.03 pob@24-0.06 pib@12+0.06 pib@24+0.03 des@12-0.04 | pob@12-0.03 pob@24-0.06 pib@12+0.06 pib@24+0.03 des@12-0.04 |
| industria | ind_isen | Etanol | +0.0 → +0.0 | ok | ok | = | pob@12-0.03 pob@24-0.06 pib@12+0.05 pib@24+0.03 des@12-0.04 | pob@12-0.03 pob@24-0.06 pib@12+0.05 pib@24+0.03 des@12-0.04 |
| industria | ind_isen | Petróleo bruto | +0.0 → +0.0 | ok | ok | = | pob@24-0.05 pib@12+0.05 des@12-0.03 des@24-0.04 | pob@24-0.05 pib@12+0.05 des@12-0.03 des@24-0.04 |
| industria | ind_isen | Minério de ferro | +0.0 → +0.0 | ok | ok | = | pob@12-0.03 pob@24-0.06 pib@12+0.06 pib@24+0.03 des@12-0.04 | pob@12-0.03 pob@24-0.06 pib@12+0.06 pib@24+0.03 des@12-0.04 |
| industria | ind_isen | Ouro | +0.0 → +0.0 | ok | ok | = | pob@12-0.03 pob@24-0.06 pib@12+0.06 pib@24+0.03 des@12-0.04 | pob@12-0.03 pob@24-0.06 pib@12+0.06 pib@24+0.03 des@12-0.04 |
| industria | ind_isen | Semicondutores / chips | +0.0 → +0.0 | ok | ok | = | pob@12-0.03 pob@24-0.06 pib@12+0.06 pib@24+0.03 des@12-0.04 | pob@12-0.03 pob@24-0.06 pib@12+0.06 pib@24+0.03 des@12-0.04 |
| industria | ind_isen | Fertilizante potássico (KCl) | +0.0 → +0.0 | ok | ok | = | pob@24-0.05 pib@12+0.05 des@12-0.03 des@24-0.04 | pob@24-0.05 pib@12+0.05 des@12-0.03 des@24-0.04 |
| industria | ind_isen | Fertilizantes nitrogenados (ureia, amônia) | +0.0 → +0.0 | ok | ok | = | pob@24-0.05 pib@12+0.05 des@12-0.03 des@24-0.04 | pob@24-0.05 pib@12+0.05 des@12-0.03 des@24-0.04 |
| seguranca | programa | Decretar GLO em Pernambuco | +0.0 → +0.0 | nulo | **ok** | misto | pib@24-0.03 conf@12-1.10 conf@24-0.82 | hom@12-0.14 hom@24-0.11 pib@24-0.03 conf@12-1.10 conf@24-0.78 |
| educacao | dup | Vaga garantida em creche | +0.0 → +0.0 | ok: repetida não soma | ok: repetida não soma | = | — | — |
| orc_slider | slider | slider saúde +10% (~R$ 24 bi) | +0.0 → +0.0 | ok | ok | = | idh@12+0.003 idh@24+0.005 pob@12-0.07 pib@24-0.16 des@24+0.07 | idh@12+0.003 idh@24+0.005 pob@12-0.07 pib@24-0.16 des@24+0.07 |
| orc_slider | slider | slider social −5% (~−R$ 14,5 bi) | +0.0 → +0.0 | ok | ok | = | pob@12+0.20 pob@24+0.23 pib@24+0.05 conf@12+1.10 conf@24+1.57 | pob@12+0.20 pob@24+0.23 pib@24+0.05 conf@12+1.10 conf@24+1.57 |
| conv_sau | conv_apoio | Filas de cirurgias e consultas · apoio | +0.0 → +0.0 | extra +0.4; sem efeito nacional (só indicador do estado) | extra +0.4; sem efeito nacional (só indicador do estado) | = | — | — |
| conv_edu | conv_cobrar | Alfabetização e anos iniciais · cobrar | +0.0 → +0.0 | extra 0; sem efeito nacional (só indicador do estado) | extra 0; sem efeito nacional (só indicador do estado) | = | — | — |
| conv_infra | conv_plano | Estado das rodovias · plano | +0.0 → +0.0 | extra +1.2; sem efeito nacional (só indicador do estado) | extra +1.2; sem efeito nacional (só indicador do estado) | = | — | — |
| infraestrutura | programa_p2 | Cabotagem: AFRMM pela metade > Linha de créd (novo) | — → +0.3 | — | **só fiscal** | = | — | — |

## O que mudou de veredito (57 ações)

- justica · programa · Mais 1.500 auditores na CGU: misto → só fiscal
- orc_saude · orc_cont · Remédios: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_seguranca · orc_cont · Polícia Federal: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_seguranca · orc_cut · Presídios: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_infra · orc_cont · Saneamento: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_justica · orc_cut · Polícia Federal: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_justica · orc_cont · CGU: INVERTIDO (melhora ao cortar) → ok (piora social)
- industria · ind_inv · Couros e peles: misto → ok
- industria · ind_inv · Minério de ferro: misto → ok
- seguranca · programa · Enviar a Força Nacional para Pernambuco: misto → ok
- seguranca · programa · Mais 100 mil câmeras corporais: só fiscal → ok
- justica · programa · Balcão único da leniência: misto → nulo
- orc_educacao · orc_cont · Merenda escolar: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_saude · orc_cont · Hospitais federais: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_seguranca · orc_cut · Toda a Segurança Pública: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_seguranca · orc_cut · Força Nacional: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_seguranca · orc_cont · Presídios: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_infra · orc_cont · Ferrovias: só fiscal → ok (piora social)
- orc_trabalho · orc_inv · Qualificação: só fiscal → ok
- orc_justica · orc_cont · Polícia Federal: INVERTIDO (melhora ao cortar) → ok (piora social)
- industria · ind_cred · Farelo de soja: ok → só fiscal
- industria · ind_cred · Café solúvel: ok → só fiscal
- industria · ind_cred · Couros e peles: ok → só fiscal
- industria · ind_cred · Petróleo bruto: ok → só fiscal
- industria · ind_cred · Minério de ferro: misto → só fiscal
- industria · ind_cred · Ouro: ok → só fiscal
- industria · ind_cred · Semicondutores / chips: misto → só fiscal
- industria · ind_cred · Fertilizante potássico (KCl): misto → só fiscal
- industria · ind_cred · Fertilizantes nitrogenados (ureia, amônia): misto → só fiscal
- seguranca · programa · Centros de Juventude nas periferias: só fiscal → ok
- infraestrutura · programa · Internet rural por satélite: misto → só fiscal
- justica · programa · Cortar penduricalhos (PLP): só fiscal → ok
- orc_educacao · orc_cut · Todo o MEC: só fiscal → ok (piora social)
- orc_educacao · orc_cont · Creches: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_saude · orc_cont · Atenção básica: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_seguranca · orc_cut · PRF: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_seguranca · orc_cont · Força Nacional: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_infra · orc_cont · Rodovias: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_infra · orc_cut · Energia: só fiscal → INVERTIDO (melhora ao cortar)
- orc_infra · orc_cont · Habitação: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_trabalho · orc_cut · Qualificação: INVERTIDO (melhora ao cortar) → só fiscal
- orc_trabalho · orc_cont · Seguro-desemprego: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_sociedade · orc_cont · Cozinha Solidária: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_justica · orc_inv · CGU: misto → só fiscal
- seguranca · programa · Transferir lideranças de Pernambuco para presídios federais: só fiscal → ok
- justica · programa · Punir quem paga acima do teto: misto → nulo
- orc_educacao · orc_cont · Universidades e IFs: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_saude · orc_cont · Vacinação: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_seguranca · orc_cut · Polícia Federal: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_seguranca · orc_cont · PRF: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_infra · orc_inv · Ferrovias: só fiscal → ok
- orc_trabalho · orc_inv · Todo o Trabalho: só fiscal → ok
- orc_trabalho · orc_cont · Qualificação: INVERTIDO (melhora ao cortar) → só fiscal
- orc_trabalho · orc_inv · Intermediação (Sine): só fiscal → ok
- orc_sociedade · orc_cont · BPC: INVERTIDO (melhora ao cortar) → ok (piora social)
- orc_justica · orc_cut · CGU: só fiscal → ok (piora social)
- seguranca · programa · Decretar GLO em Pernambuco: nulo → ok

## Trabalho (34 alavancas) e Conversas (12)

Sem gabarito de sinal (o relatório os trata como informativos). As alavancas de Trabalho não foram alteradas por este lote (usam `tbMensal`, não o objeto de qualificação); as conversas mudaram só no sorteio da cobrança e nos textos do cartão (E4), e seus efeitos continuam no indicador do estado.


## Não-ok que restam, com justificativa (28 de 203 depois do lote Justiça; os 4 "nulo" de Justiça saíram, ver a seção do lote Justiça)

| veredito | área | grupo | ação | justificativa |
|---|---|---|---|---|
| INVERTIDO | orc_infra | orc_cut | Energia | Troca real, não erro de sinal: cortar obras de energia e transmissão reduz o desmatamento (o avaliador conta como melhora) e piora pobreza e desemprego em 24 meses. |
| INVERTIDO | orc_infra | orc_cont | Energia | Troca real, não erro de sinal: cortar obras de energia e transmissão reduz o desmatamento (o avaliador conta como melhora) e piora pobreza e desemprego em 24 meses. |
| misto | industria | ind_inv | Café solúvel | Gasto novo: pobreza, PIB e desemprego melhoram; confiança e inflação pioram (custo de oportunidade do gasto sem lastro) e, em mineração e ouro, o desmatamento sobe. Troca coerente. |
| misto | industria | ind_inv | Farelo de soja | Gasto novo: pobreza, PIB e desemprego melhoram; confiança e inflação pioram (custo de oportunidade do gasto sem lastro) e, em mineração e ouro, o desmatamento sobe. Troca coerente. |
| misto | industria | ind_inv | Fertilizante potássico (KCl) | Gasto novo: pobreza, PIB e desemprego melhoram; confiança e inflação pioram (custo de oportunidade do gasto sem lastro) e, em mineração e ouro, o desmatamento sobe. Troca coerente. |
| misto | industria | ind_inv | Fertilizantes nitrogenados (ureia, amônia) | Gasto novo: pobreza, PIB e desemprego melhoram; confiança e inflação pioram (custo de oportunidade do gasto sem lastro) e, em mineração e ouro, o desmatamento sobe. Troca coerente. |
| misto | industria | ind_inv | Ouro | Gasto novo: pobreza, PIB e desemprego melhoram; confiança e inflação pioram (custo de oportunidade do gasto sem lastro) e, em mineração e ouro, o desmatamento sobe. Troca coerente. |
| misto | industria | ind_inv | Soja em grão | Gasto novo: pobreza, PIB e desemprego melhoram; confiança e inflação pioram (custo de oportunidade do gasto sem lastro) e, em mineração e ouro, o desmatamento sobe. Troca coerente. |
| misto | infraestrutura | programa | Conceder a BR-319 (polêmica ambiental) | Troca declarada no próprio texto do programa (polêmica ambiental): PIB e pobreza melhoram, desmatamento e inflação pioram. |
| misto | orc_infra | orc_inv | Energia | Troca real: obras de energia e transmissão ganham PIB, emprego e menos pobreza, e pressionam desmatamento, inflação e a confiança (gasto novo). |
| só fiscal | industria | ind_cred | Café solúvel | Crédito a produto: efeito na produção do setor (aba Indústria), sem renda direta das famílias. O impulso macro é de 25% do investimento direto; abaixo do ruído nos indicadores nacionais. |
| só fiscal | industria | ind_cred | Couros e peles | Crédito a produto: efeito na produção do setor (aba Indústria), sem renda direta das famílias. O impulso macro é de 25% do investimento direto; abaixo do ruído nos indicadores nacionais. |
| só fiscal | industria | ind_cred | Farelo de soja | Crédito a produto: efeito na produção do setor (aba Indústria), sem renda direta das famílias. O impulso macro é de 25% do investimento direto; abaixo do ruído nos indicadores nacionais. |
| só fiscal | industria | ind_cred | Fertilizante potássico (KCl) | Crédito a produto: efeito na produção do setor (aba Indústria), sem renda direta das famílias. O impulso macro é de 25% do investimento direto; abaixo do ruído nos indicadores nacionais. |
| só fiscal | industria | ind_cred | Fertilizantes nitrogenados (ureia, amônia) | Crédito a produto: efeito na produção do setor (aba Indústria), sem renda direta das famílias. O impulso macro é de 25% do investimento direto; abaixo do ruído nos indicadores nacionais. |
| só fiscal | industria | ind_cred | Minério de ferro | Crédito a produto: efeito na produção do setor (aba Indústria), sem renda direta das famílias. O impulso macro é de 25% do investimento direto; abaixo do ruído nos indicadores nacionais. |
| só fiscal | industria | ind_cred | Ouro | Crédito a produto: efeito na produção do setor (aba Indústria), sem renda direta das famílias. O impulso macro é de 25% do investimento direto; abaixo do ruído nos indicadores nacionais. |
| só fiscal | industria | ind_cred | Petróleo bruto | Crédito a produto: efeito na produção do setor (aba Indústria), sem renda direta das famílias. O impulso macro é de 25% do investimento direto; abaixo do ruído nos indicadores nacionais. |
| só fiscal | industria | ind_cred | Semicondutores / chips | Crédito a produto: efeito na produção do setor (aba Indústria), sem renda direta das famílias. O impulso macro é de 25% do investimento direto; abaixo do ruído nos indicadores nacionais. |
| só fiscal | infraestrutura | programa_p2 | Cabotagem: AFRMM pela metade > Linha de crédit | Sem canal social ou macro modelado para esta ação (fiscalização, conectividade ou crédito setorial); entra o custo e a reação de grupos. |
| só fiscal | infraestrutura | programa | Internet rural por satélite | Sem canal social ou macro modelado para esta ação (fiscalização, conectividade ou crédito setorial); entra o custo e a reação de grupos. |
| só fiscal | justica | programa | Mais 1.500 auditores na CGU | Sem canal social ou macro modelado para esta ação (fiscalização, conectividade ou crédito setorial); entra o custo e a reação de grupos. |
| só fiscal | orc_justica | orc_inv | CGU | Sem canal social ou macro modelado para esta ação (fiscalização, conectividade ou crédito setorial); entra o custo e a reação de grupos. |
| só fiscal | orc_justica | orc_cut | Judiciário: penduricalhos | Cortar penduricalhos é economia que não retira serviço público: só fiscal e reação dos servidores/Judiciário, por desenho. |
| só fiscal | orc_trabalho | orc_cut | Intermediação (Sine) | Cortar qualificação e intermediação aumenta o desemprego (+0,04 p.p. em 12 meses, acima do ruído), que a regra do avaliador não conta como indicador social; na 2ª leitura (com desemprego e PIB) é ok. |
| só fiscal | orc_trabalho | orc_cut | Qualificação | Cortar qualificação e intermediação aumenta o desemprego (+0,04 p.p. em 12 meses, acima do ruído), que a regra do avaliador não conta como indicador social; na 2ª leitura (com desemprego e PIB) é ok. |
| só fiscal | orc_trabalho | orc_cont | Qualificação | Cortar qualificação e intermediação aumenta o desemprego (+0,04 p.p. em 12 meses, acima do ruído), que a regra do avaliador não conta como indicador social; na 2ª leitura (com desemprego e PIB) é ok. |
| só fiscal | orc_trabalho | orc_cut | Todo o Trabalho | Cortar qualificação e intermediação aumenta o desemprego (+0,04 p.p. em 12 meses, acima do ruído), que a regra do avaliador não conta como indicador social; na 2ª leitura (com desemprego e PIB) é ok. |

Nenhum caso fica INVERTIDO sem explicação; com 24 repetições, os 8 que apareciam como INVERTIDO por IDH viraram "só fiscal" ou "ok".

## Lote Justiça: os 4 programas "nulo" agora têm o efeito do texto

Branch `justica-efeitos` (a partir de `motor-v3.5`, commit a9075cb). Os programas de Justiça → "Programas: ações do governo" PGR de mandato único, Punir quem paga acima do teto, Balcão único da leniência e Sigilo de 100 anos eram "nulo" (só a análise jurídica e a reação de grupos do anúncio). Agora um hook mensal (`jusProgMensal`, chamado depois de `areasMensal`) lê a medida em vigor do programa pela mesma `psVigor` do cartão (ativa, suspensa, aguardando gatilho ou consolidada) e aplica o efeito pela rampa da própria medida (`medRamp`, vezes a intensidade `M.k`), em incrementos: se a medida for revogada, derrubada ou caducar, o efeito é desfeito aos poucos (15% ao mês). O fiscal entra em `M.fis` (a medida já o sincroniza e o desfaz na revogação); o escândalo e os casos entram por `jusProgAtivo(g, id)` (0 a 1) em `eqEscDecaimento`, `jusNovoCaso` e `jusMensal`. Cada cartão ganhou uma linha "Efeito: ...".

| programa | efeito pleno (medida em vigor) | onde entra |
|---|---|---|
| PGR com mandato único (PEC) | casos da Justiça que atingem o governo avançam +15% (chance de mudar de fase); confiança (índice de confiança da economia) +1,5; mercado +1,5, classe média +1, universitários +1; sem custo | `jusMensal` (agilidade do caso), `applyFx` |
| Punir quem paga acima do teto | despesa −R$ 3 bi/ano; receita única de R$ 1 bi (abate a dívida pela rampa); servidores −2, tensão com o STF +2, classe média +1 | `M.fis.custo`, `M.once`, `applyFx` |
| Balcão único da leniência | receita +R$ 2 bi/ano; empresariado +2; PIB +0,07 de impulso (0,04 medido); o indicador "tempo de processo" (`ind`) continua | `M.fis.receita`, `applyFx` |
| Sigilo de 100 anos: vetar para gastos | decaimento do escândalo sem caso novo +20%; impacto de um caso novo da Justiça +10%; classe média +1, universitários/artistas +1 (o jogo não tem grupo "imprensa"), confiança +0,5 | `eqEscDecaimento`, `jusNovoCaso`, `applyFx` |

Δ pareado (8 repetições, mesma semente; `~` = dentro do ruído) antes → depois, em 6, 12 e 24 meses. "Antes" = a9075cb. Em PGR e Sigilo o antes já traz um Δ de confiança (+1,86 em 12 meses), escândalo (−2,3) e grupos que vem do anúncio da medida e de uma diferença de eventos entre os braços, igual nos dois programas; o efeito do lote é a diferença entre as duas colunas.

| programa | indicador | m6 | m12 | m24 |
|---|---|---|---|---|
| PGR | confiança | +0,00~ → +0,18~ | +1,86 → +3,06 | +1,13 → +2,14 |
| PGR | mercado | +0,30 → +0,48 | +0,93 → +2,28 | +1,13 → +1,66~ |
| PGR | classe média | +1,21 → +1,28 | +1,03 → +1,59 | +0,52 → +0,38~ |
| PGR | universitários | +0,97 → +1,05 | +0,84 → +1,40 | +0,41 → +0,18~ |
| Punir | despesa (custo, R$ bi) | 0~ → −3,00 | 0~ → −3,00 | −0,01~ → −3,04 |
| Punir | servidores | +0,04~ → −1,21 | +0,03~ → −0,97 | +0,01~ → −0,34 |
| Punir | tensão com o STF | −0,24~ → +1,15 | −0,38~ → +1,29 | −0,39~ → +0,63 |
| Punir | classe média | +0,04~ → +0,66 | −0,03~ → +0,47 | −0,01~ → +0,12~ |
| Punir | dívida (p.p. do PIB) | 0~ → −0,01~ | 0~ → −0,03~ | +0,01~ → −0,05~ (R$ 1 bi de receita única é pequeno) |
| Leniência | receita (R$ bi) | 0~ → +2,00 | 0~ → +2,00 | 0~ → +2,00 |
| Leniência | empresariado | +0,07~ → +1,27 | +0,08~ → +1,24 | +0,04~ → +0,62 |
| Leniência | PIB (p.p.) | 0~ → +0,04 | 0~ → +0,04 | 0~ → +0,04 |
| Sigilo | confiança | 0~ → +0,43 | +1,86 → +2,18 | +1,13 → +1,33 |
| Sigilo | classe média | +2,19 → +2,97 | +1,45 → +1,74 | +0,59 → +0,69 |
| Sigilo | universitários | +2,23 → +2,99 | +1,46 → +1,74 | +0,54 → +0,63 |
| Sigilo | escândalo | 0~ → −0,06~ | −2,33 → −2,32 | −0,54 → −0,55 |

Os grupos voltam para perto de onde estavam em 24 meses porque a dinâmica mensal do jogo os puxa de volta, como acontece com qualquer medida; a economia fiscal e a receita ficam. O decaimento do escândalo +20% só vale nos meses sem caso aberto; na simulação o escândalo cai 2,3 pontos nos dois braços por causa do anúncio e o efeito do decaimento fica dentro do ruído (o multiplicador está medido de forma direta em `ui_pais_efeitos.py`, check J4: 0,170 → 0,204 de decaimento mensal; caso novo 5,83 → 6,41 de escândalo).

Veredito do `pais_relatorio.py` (que só conta IDH, pobreza, homicídios e desmatamento como "social"): continua "nulo" por regra, porque nenhum dos 4 muda indicador social. Aqui o "nulo" deixa de ser verdade: cada um mexe nos indicadores que o texto diz (fiscal, grupos, confiança, STF, PIB, escândalo e casos), todos acima do ruído e na direção prevista, exceto o decaimento do escândalo, travado só na checagem direta.

Checagens novas (`ui_pais_efeitos.py`, seção 8, 29 no total): J1 PGR (efeitos de grupo e confiança; 3.000 sorteios por braço de `jusMensal`: 28,5% → 32,8% de avanço de fase, razão 1,15), J2 Punir, J3 Leniência, J4 Sigilo (decaimento 1,2x e impacto 1,1x; grupos e confiança) e a linha "Efeito:" nos 4 cartões.
