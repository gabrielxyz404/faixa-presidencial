# Próximo pacote (aprovado por Gabriel em 30/10/2026)

## 1. Tela de proposta simplificada
Antes de enviar (parecer):
- Custo anual em destaque (ou "ganho" quando for corte/receita).
- Botão "Fazer pesquisa popular" (já existe: Encomendar pesquisa).
- Botão "Pedir opinião do ministro" da área (a análise do ministro passa a ser sob demanda).
- Chance de aprovar na Câmara e no Senado pelo viés dos partidos (mapa de votos já existe).
- Continuam visíveis: base jurídica e coerência com o partido.
- Faixa vermelha curta no topo quando inconstitucional/ilegal (ex.: "Inconstitucional: o STF deve derrubar (art. 5º, XLVII)").
- O resto (quem ganha/perde, riscos, consequências, calendário etc.) sai da tela (continua calculado).
Depois de aprovada (resultado):
- Quanto a aprovação sobe/desce em cada categoria da população.
- Reação dos jornais (manchetes).
- Pessoas aleatórias comentando ("José, 54 anos, Minas Gerais: Vai melhorar porque…").

## 2. Famosos com viés no X, podcasts, opositores/aliados nos podcasts
Ver dados/famosos_politicos_rascunho.json.

## 3. STF com viés e linha penal (base real + pequena variação por partida)
Ver dados/famosos_politicos_rascunho.json (chave "stf").

## 4. Propostas bizarras no motor normal (sem modo separado)
Não existe "modo zoeira": é o mesmo motor entendendo e simulando bem também propostas feitas na brincadeira.
Aceitar propostas bizarras legais (instrumento certo, custo pequeno, efeito de viralização/imprensa zoando), barrar ilegais (impessoalidade art. 37 §1º, liberdades do art. 5º, símbolos por lei) e manter "absurdo" só para o impossível. "kkk", emoji e gíria não tornam proposta absurda. Bateria: testes/bench/zoeira_dev.json (+ reservado fora do repo).

## 5. Programa do Missão (Livro Amarelo)
Hoje PROGRAMAS.MISSAO só tem o eixo economia (estatuto). Preencher os 9 eixos com base no Livro Amarelo (versão final lançada em 01/08/2026; 3 tomos, 14 capítulos: "Estado Novo", "Reformas de Base", "País do Futuro"). Sem texto integral público: usar resumos de imprensa, marcados como "resumo de imprensa" (sem número de página), até Gabriel enviar trechos do livro.
Pontos reportados: ajuste fiscal amplo e superávit nominal; economia liberal com Estado regulador; Selic abaixo de 6% (conflita com autonomia do BC); linha dura contra facções; combate a privilégios/anti-oligarquia; desdolarizar a América do Sul e "exportar o real"; parte da imprensa vê propostas parecidas com bandeiras da esquerda.
Fontes: bahianoticias.com.br/noticia/319085; fpabramo.org.br (convenção do Missão); jornaldebrasilia.com.br; correiodamanha.com.br/politica/2026/08/307261; infomoney.com.br/?p=3434705.
Danilo Gentili e Léo Lins (afinidade Missão) reagem segundo esse programa.

## 6. Programas dos outros partidos
Pesquisa em dados/programas_2026_pesquisa.json (planos de governo 2026 registrados no TSE e manifestos; só resumos de imprensa, sites bloqueados nesta sessão). Integrar com citação quando Gabriel enviar os PDFs (Flávio/PL, Caiado/PSD, Zema/Novo, Lula/PT, MDB "Caminhos para o Brasil" etc.).

## 7. Teste final grande (carta branca de Gabriel)
Depois de tudo: testar a fundo e melhorar — compreensão (inclusive propostas mal escritas: testes/bench/ruido.py gera versões com erro de digitação, sem acento, abreviações, caixa), teor/intenção da proposta, simulação dos efeitos (testes/sim) e reação às ações do jogador. Linha de base v3.6 no reservado geral: limpo 39% totalmente certos (5 critérios 50%); mal escrito 32% (43%); tema cai de 93% para 81%.
Programas extraídos (citações com página): dados/programa_missao.json, programa_pt_2025.json, programa_pl_2026.json, programa_psd_2026.json. Novo/Zema: sem plano encontrado.
Regra (Gabriel): a posição de cada partido combina programa + HISTÓRICO real no poder (governos do PT, governo Bolsonaro e votos de Flávio no Senado, Caiado em Goiás, Zema em Minas, votos de parlamentares do MBL). Pesquisa em dados/historico_partidos.json. No jogo, mostrar as duas fontes quando divergirem ("Programa 2026, p. X" e "No governo: fez Y (ano)").
