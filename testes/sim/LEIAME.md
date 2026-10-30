# Teste de simulação: o jogo reage como esperado à ação do jogador?

Compara, para cada cenário, uma partida COM a ação do jogador (tratamento) com a mesma partida SEM ela (controle), e confere se a direção do efeito
nos indicadores (meses 3, 12 e 24 depois do início) bate com o que a economia ensina. Não mede o motor de leitura de texto (isso é o bench em
`testes/bench`); mede o que o jogo faz com a proposta depois de entendida: efeito imediato ou defasado, MP que caduca, anterioridade tributária,
STF que suspende, revogação, arquivamento.

## Como rodar
```
S=<pasta de trabalho>   # LIBS=<pasta com react-18.3.1/, react-dom-18.3.1/, htm-3.1.1/, lucide-0.460.0/>
python3 testes/motor/run_sandbox.py testes/sim/sim.py <pasta com index.html> testes/sim/cenarios.json $S/sim_saida.json 8841 8
python3 testes/sim/relatorio.py $S/sim_saida.json                  # tabela cenário x indicador x mês
python3 testes/sim/relatorio.py $S/sim_v35.json $S/sim_v36.json    # só o que mudou de veredito entre duas versões
```
Opções de `sim.py`: `--so=id1,id2` roda só alguns cenários; `--z=2.3` (limiar em erros-padrão); `--com-impeachment` deixa o impeachment encerrar a rodada;
`--traj=<id>[:ind1,ind2]` imprime a diferença tratamento-controle mês a mês (para depurar um cenário). 39 cenários x 8 repetições levam ~3 min.

## Método
1. Uma partida é criada pela interface (mesmo roteiro de `testes/regressao/batch3.py`) e o estado `g` logo após "Tomar posse" é guardado. Todas as rodadas partem de um clone dele.
2. O HTML servido recebe, antes de `ReactDOM.createRoot(...)`, um gancho que expõe `window.__SIM` (executaProposta, fimDoMes, analisaLocal, aprovacao, primario,
   enviaParaPauta, fechaMP, retiraItem, decideVotacao, quorum, minMarca, gvMarca, tbMarca, riscoImpeachment) e `window.__QV` (onde mora o `gRef` do React).
   Funciona nas duas versões porque só usa nomes de funções e uma âncora que existem nas duas. Se a âncora ou uma função obrigatória sumir, o script
   termina com a mensagem `ERRO: ...` (código de saída 3).
3. `Math.random` é trocado por um PRNG com semente (mulberry32) antes de o app iniciar (`add_init_script`). Antes de CADA `fimDoMes` a semente é refeita
   a partir de (repetição, mês) e `g.seed` varia por repetição. Tratamento e controle da mesma repetição veem o mesmo ruído e os mesmos eventos de crise; diferem só
   pelo efeito da ação. A comparação é pareada, por isso o erro-padrão é pequeno e dá para medir efeitos de décimos de ponto com 8 repetições.
4. As ações rodam em JS dentro da página, sem digitar: `propor` = `analisaLocal(g, texto)` e depois
   - decreto, despacho ou nota (DEC/ADM/COM): `executaProposta` na hora (como "Assinar e publicar no DOU");
   - PL/PEC: `enviaParaPauta` e voto FORÇADO (remove o item da pauta e chama `executaProposta(g, prop, resultado)`, como `aplicaPlano`);
   - MP: `enviaParaPauta` já a coloca em vigor; `propor` a converte com `fechaMP`; `enviar` a deixa correr até caducar (4 meses, 70% desfeito).
   `enviar` põe na pauta e não faz mais nada ("deixar morrer": o PL é arquivado em 3 meses). `votar` e `retirar` agem depois sobre um item enviado (`ref` = `id` da ação).
   O instrumento é escolhido pelo próprio texto ("por decreto", "por projeto de lei", "por PEC", "por medida provisória"), como o jogador faria.
5. `resultado` de cada ação: `aprovada` (padrão, força), `stf` (força o Congresso e deixa o STF do jogo decidir, determinístico por `g.seed`), `derrubada` (força), `auto` (o jogo decide tudo).
6. O impeachment não encerra a rodada (o controle passivo, que ignora as crises, seria cassado em ~3 de 8 repetições em 24 meses); o número aparece como `impeachment_evitado_*`.

## Formato de `cenarios.json`
Lista de objetos: `id`, `descricao`, `acoes` (lista de `{mes, tipo: propor|enviar|votar|retirar, texto, resultado, id, ref}`; `mes` = meses decorridos desde o início),
`controle` (opcional: ações do braço de controle; padrão vazio; serve para comparar duas rotas, como decreto x lei) e `esperado`: lista de
`{ind, m3, m12, m24, just}` onde cada mês-alvo é `sobe`, `desce`, `estavel`, `qualquer`, `atenua`, `persiste` ou `cresce`, e `just` é a justificativa econômica.
`atenua`, `persiste` e `cresce` comparam a diferença do mês com a do primeiro mês da lista (efeito parcialmente desfeito, mantido, acumulado).

Indicadores: `pib ipca selic des dol risco conf divida prim ap pob hom desm idh stf esc imp receita custo extra n_medidas` (`receita`/`custo`/`extra` = `g.fiscal`, fluxo anual direto
das medidas; `prim` inclui o efeito do PIB; `n_medidas` = `g.medidas.length`, 0 antes da Etapa 2) e `g_<grupo>` (aprovação de cada grupo: `g_servidores`, `g_mercado`, ...).

## Ações do jogador no painel Medidas, na tela Parecer, em entrevistas e no X (v3.9 do teste)
Além de `propor`, `enviar`, `votar` e `retirar`, o `sim.py` executa as decisões abaixo chamando as funções do próprio jogo (todas expostas no gancho `window.__SIM`;
em versões sem a função, a ação registra `erro` em `acoes_executadas` em vez de derrubar o teste). Cada ação referencia, em `ref`, o `id` da proposta que criou a medida.

| tipo | campos | o que faz no jogo |
|---|---|---|
| `acelerar` | `ref` | botão "Acelerar" do painel Medidas (`medAcelera`): antecipa o efeito pleno em ~30% do prazo restante, custa 1 ação e ~6% a mais de custo. Registra `erro` se o jogo não permitir (fase, limite de 2, menos de 2 meses). |
| `ajustar` | `ref` | botão "Ajustar" (`medAjusta`): resolve o problema ativo da medida ou antecipa o regulamento. |
| `revogar` | `ref`, `resultado` | botão "Revogar" (`medRevoga`). Decreto/ato próprio: revoga na hora (85% do efeito desfeito, grupos -0,8, escândalo +1). MP/PL/PEC: o painel leva "Revogar ..." à Mesa (`g.revogPend`) e o sim o propõe como qualquer proposta (`resultado`, padrão `aprovada`). |
| `adi` | `ref`, `liminar` (padrão true), `meses` (padrão 2), `nivel` | simula uma ação no STF contra a medida: com liminar a medida fica `suspensa` (a rampa congela) até o julgamento, que o próprio jogo decide em `medProblemas` (`julgamentoSTF`). `nivel` (`ok`, `controverso`, `inconstitucional`) força o risco constitucional que o plenário enxerga: `ok` rejeita (cronograma retomado), `inconstitucional` derruba (efeitos desfeitos, tensão com o STF +8). Sem isso, a ADI só aparece por sorteio no jogo e não dá para testá-la. |
| `podcast` | `veic` (padrão `flow`), `aceitar` (padrão true), `resposta` (arquétipo: `ajuste`, `defesa`, `ataque`, `pivo`) | cria um convite do veículo e o recusa (`entRecusa`: custo de vitrine) ou o aceita (`entAceita`), responde a todas as perguntas com o arquétipo e conclui (`entConcluiEntrev`). |
| `live` | `nome` (ou `auto`: o famoso mais seguido entre os que já criticaram) | "Convidar para live" um famoso (`famLive`): gasta 1 ação e pode suavizar o próximo ataque dele. Sem cenário: o efeito (~0,1 ponto) fica abaixo do ruído, porque quem ataca cada medida é sorteado por texto e mês. |
| `propor`/`enviar` + `desidratar` | número de vezes (0 a 2) | "Desidratar o texto (-40% de impacto)" da tela Parecer: `scale *= 0,6`. |
| `propor`/`enviar` + `emendas` | número de partidos (os maiores fora o do jogador) ou lista de ids | "Emendas p/ partido": soma `custoEmenda` em `g.fiscal.extra` e o bônus de voto. Só o custo é testável aqui, porque o voto é forçado. |

Indicadores novos: `n_ativas`, `n_susp`, `n_derr`, `n_revog` (medidas em cada estado), `cred`, `feitas`, `recusas` (credibilidade e contagem de entrevistas), `fam_neg`, `fam_pos`
(posts de famosos contra e a favor das medidas, `g.x.fam.posts`). `acoes_executadas` também mostra `medida` (tipo, estado, prazo), `famosos` (quem comentou e o tom),
`emendas_custo`, `desidratada`, `cred` e `dap` do podcast. O jogo zera `g.fiscal.extra` a cada novo exercício (mês 12), por isso as emendas só aparecem no mês 3.

Cenários dessas decisões (17): `mp_converte_vs_pl`, `mp_caduca_vs_pl`, `emendas_custo`, `desidrata_vs_integral`, `acelera_obra`, `revoga_decreto_painel`, `revoga_lei_painel`,
`liminar_retoma`, `liminar_derruba`, `bizarra_ilegal_vs_legal`, `bets_creches`, `varias_medidas`, `corte_servidores`, `fonte_vs_sem_fonte`, `podcast_recusa`,
`podcast_aceita_vs_recusa`, `famoso_ataca` (o efeito do famoso vem misturado ao da própria medida; a prova de que ele atacou é o indicador `fam_neg`). Quase todos usam `controle` com a rota alternativa, para medir só o efeito da decisão.

## Veredito
Por repetição: `d = tratamento - controle`; `D` = média, `se` = dp/raiz(n); limiar = max(Z*se, materialidade do indicador) (tabela `MAT` em `sim.py`).
`sobe`/`desce`: ok se o sinal bate e |D| > limiar; falha se o sinal é oposto e |D| > limiar; senão inconclusivo (diferença dentro do ruído). `estavel`: ok se |D| <= max(Z*se, 2*materialidade).
`qualquer` só informa. A saída JSON guarda, por expectativa, médias, `D`, `se`, limiar e a justificativa; por cenário, as ações executadas (o que o motor entendeu: instrumento, custo, STF).

## Limitações
- O gabarito é direcional (sinal), não de magnitude. Efeitos de segunda ordem (juros, câmbio, ruído de eventos) podem inverter o sinal de indicadores indiretos; prefira indicadores de canal direto (`receita`, `custo`).
- Um único estado inicial (mesmo presidente, mesmo ministério, mesmo mês 1); só a semente varia. Efeitos que dependem de contexto (crise em curso, aprovação baixa) não são cobertos.
- O voto é forçado; a probabilidade de aprovar no Congresso e a articulação não são testadas aqui. A interface (modais, botões) não é exercitada: veja `testes/regressao/batch3.py`.
- O texto é lido pelo motor; se ele entender mal (ex.: capitalização lida como "reforma da Previdência" com economia), o cenário falha por erro do motor, não do efeito. Veja `acoes_executadas` na saída.
- Quem ignora todas as crises acumula penalidades nos dois braços; o controle é "governo omisso", não "governo ótimo".

## Medida condicional e finalidade (v3.9)
Ação nova `choque` (`{mes, tipo: "choque", ind: "dol", valor: 6.5}`): força um indicador de `g.eco` (ou `soc.` + nome para `g.soc`) para disparar o gatilho de uma medida condicional ("se o dólar passar de R$ 6, ..."). Coloque o choque nos dois braços (`acoes` e `controle`).
Cenários novos: `cond_nao_dispara` (a medida fica "aguardando gatilho": nada entra no fiscal), `cond_dispara` (choque no mês 2: a receita cai e a inflação alivia depois do disparo) e `fin_fonte_destino` (taxar a fonte para pagar o destino: receita e custo juntos).
