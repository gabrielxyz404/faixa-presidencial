# Faixa Presidencial: onde paramos (para continuar numa conversa nova)

## Estado
- **Jogo publicado:** https://claude.ai/artifact/9XaM9Kxc1943bT2zQpmhef (versão 67, privada; para outros jogarem, compartilhar pelo menu da página).
- **Código:** `index.html`, um app React/htm de arquivo único. Junto vão `fotos.json` e `logos.json`.
- **Ramos:**
  - `main` é o que está publicado;
  - `motor-v3.5` é o ramo de trabalho (nome antigo, pode ser renomeado), e hoje main = motor-v3.5 (commit 604c0ff).
- **Motor do jogo:** v4.3. O conjunto cego hold3 (700 frases) tem 48,0% totalmente certos. Nas 103 frases do Fable (fresh2), 78,6%.

## Regras do usuário (Gabriel, pt-BR, joga no PC Windows)
- Responder sempre em pt-BR. **Mandar prints de PC (1440 px) a cada entrega.** Testar só em desktop, nunca em celular.
- **Explicar antes de executar** quando ele perguntar algo. Publicar tudo junto quando ele pedir.
- **Pessoas reais:**
  - escândalo fictício cita só cargo e partido (nunca + estado);
  - sem acusações nem @ inventados;
  - selo "simulado" discreto (cinza, 12px, opacidade 0,5) só ao lado de falas inventadas de pessoas reais.
- **Tema visual:** preto, com Bricolage Grotesque + IBM Plex Sans. Helpers GV_CSS/MX_CSS/PD_CSS/PS_CSS.
- **Trailer dos commits:** `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` + `Claude-Session: ...`

## Como testar
- **Runner:** `python3 testes/motor/run_sandbox.py <script> <pasta com index.html, fotos.json, logos.json> ...`
- **Testes de UI:** `testes/motor/ui_*.py` (28 testes). Contra a versão atual, todos passam, com estas ressalvas:
  - o `ui_lote_d` falha em 2 checagens (D8, saves em 2 colunas) só porque o sandbox não carrega o Tailwind; com o tw.css injetado passa 37/37;
  - o `ui_equilibrio` e o `ui_industria_comercio` às vezes falham 1 checagem por eventos sorteados; repetir.
- **Simulação de saves:** `testes/sim/sim.py` com `testes/sim/cenarios.json`; referência 242 ok / 2 falhas (bf_pl e zoeira_feriado_samba, antigas) / 4 inconclusivos.
- **Programas:** `testes/motor/programas_probe.py` (190 programas, 0 alertas). Motor: `testes/motor/motor_lote_b.py` (27/27).
- **Bench do motor:** `testes/motor/probe.py` + `testes/bench/score.py`. Progresso em `testes/bench/mega_progresso.md`.
- **Prints com estilo:** compilar Tailwind (`npx tailwindcss`) e injetar `<link rel="stylesheet" href="tw.css">` numa cópia do index.html.

## Feito recentemente (todo publicado)
- **Correções e conteúdo:**
  - correções da revisão do Fable;
  - equilíbrio v2 + 4º ano;
  - eleger sucessor;
  - eventos do 2º mandato.
- **Aba País:**
  - aba País corrigida (sinais invertidos e efeitos nulos);
  - 71 programas trocados por medidas novas + cartão "Em vigor";
  - metas por área (24 indicadores);
  - 4 programas da Justiça com efeito literal.
- **Motor e decisões:** motor v4.3 e crises com custo explícito.
- **Eleições municipais:** com efeito real (100 cidades, verba de campanha com risco no TSE, mapa).
- **Comércio exterior e Indústria:**
  - clareza nas telas;
  - contratos reais iniciais (Itaipu, gás boliviano);
  - negociação de contratos;
  - preço mostrado como "↓ cai X%";
  - transmissão de preços (derivados no IPCA, grupos, fertilizantes, diesel, instrumentos de abastecimento: TEC zero, Conab, crédito, leilão).

## Próximos passos possíveis (aguardando decisão do usuário)
1. **Motor 5**, em etapas medidas no hold3:
   - (1) tabela de bases e preços reais;
   - (2) tabela de tipo de proposta;
   - (3) "ficha" de leitura (ação, objeto, quantias, público…) no lugar das 6 camadas antigas;
   - (4) opcional: a IA (conta Claude do jogador ou chave própria) preenche só a ficha.
   - Meta: hold3 ≥ 60%. Diagnóstico da v4.3: o valor em R$ é o maior erro (171 itens só com valor errado).
2. Feijão e carne com instrumentos de abastecimento (hoje sem mercado ou sem tela de compra).
3. Renomear o ramo `motor-v3.5` (ex.: `desenvolvimento`).
4. Ideias do Fable ainda não feitas: painel "o que sua ação fez", Mesa em duas camadas, modo leve com placar, comparador "e se", acessibilidade, jornal do dia seguinte. A lista completa está na seção (I) do relatório do Fable; o arquivo do relatório ficou no scratchpad da sessão anterior e não está no repositório.
