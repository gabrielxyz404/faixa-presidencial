# Faixa Presidencial

Simulador da Presidência do Brasil (2027–2030 e além). Página única em React (htm, sem build), publicada como artifact no claude.ai:
https://claude.ai/artifact/9XaM9Kxc1943bT2zQpmhef

## Arquivos do jogo
- `index.html` — o jogo inteiro (motor de decisão, Congresso, eleições, interface).
- `fotos.json` — fotos em base64 (`{fonte, fotos, creditos}`):
  - `UF|deputado|Nome`, `UF|senador|Nome`, `UF|senador2022|Nome`, `UF|governador|Nome`, `BR|presidente|Nome`, `BR|vice|Nome` — TSE, Portal de Dados Abertos;
  - `BR|stf|Nome` e `REAL|Nome` — Wikimedia Commons, licenças livres (créditos em `creditos`).
- `logos.json` — logotipos dos partidos.

Capacidades do artifact: `{sample: {}, downloads: true}`.

## Pastas
- `dados/` — índices reais por UF usados nas abas do País (`saude_uf.json`, `areas_uf.json`), com fonte, ano e confiança de cada indicador. São embutidos no `index.html` por `ferramentas/embed_uf.py` (bloco `/*<UFDATA>*/`).
- `ferramentas/` — scripts de dados (fotos do TSE, embutir índices). Os caminhos apontam para a pasta de trabalho da sessão; ajuste antes de usar.
- `testes/` — testes com Playwright (Python): `deep.py` percorre a interface por passos (`steps.json`); `batch.py`/`send.py` mandam 25 propostas ao motor e gravam o parecer para comparar antes/depois.

## Regras do projeto
- Texto do jogo em pt-BR. Visual: PC primeiro (1280–1920 px), fundo preto, verde e amarelo, fonte Outfit.
- Pessoas reais: falas simuladas sempre com chip "simulado", só posições políticas; nada de acusações, crimes, vida privada ou @ inventado. Nunca inventar rosto de pessoa real.
- Testar com Playwright antes de publicar: zero erros de página e de console.
