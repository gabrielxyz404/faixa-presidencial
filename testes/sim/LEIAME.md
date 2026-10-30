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
`--traj=<id>[:ind1,ind2]` imprime a diferença tratamento-controle mês a mês (para depurar um cenário). 18 cenários x 8 repetições levam ~1,5 min.

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
