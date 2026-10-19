# Capas de gêneros

## Versões de foco com silhuetas — 18/10/2026

Os dez arquivos `<gênero>-focus.png` usam as composições completas de
`images/genres/silhouettes/*-base-focus.png` do upstream, incluindo as silhuetas.
As capas normais existentes continuam nos arquivos `<gênero>.png`. Assim, os
personagens aparecem ao focar o card, mantendo o painel preto à esquerda e branco
à direita, conforme a referência `animation-base-focus.png` enviada pelo usuário.
Essa escolha substitui, para esta entrega, a proposta anterior de inverter as cores.

Os títulos de nove capas de foco foram localizados com imagegen; Crime foi copiado
sem edição. Todas têm 1672 × 941 pixels. Suspense é uma criação própria, sem par
upstream, e permanece com a configuração atual.

O [manifesto de foco](../assets/covers/generos/focus-manifest.json) registra o commit
da fonte, URLs, originais preservados, hashes, dimensões e os prompts de tradução.
O [mapeamento por pasta](../collections/generos-artwork.json) altera somente
`focusGifUrl` e `focusGifEnabled`; preserva capas normais, fontes e demais campos.
É uma atualização parcial de referência, **não um JSON para importar uma coleção**.
Apesar do nome do campo, as imagens de foco são PNGs estáticos.

| Normal | Foco com silhuetas |
|---|---|
| acao.png | acao-focus.png |
| animacao.png | animacao-focus.png |
| comedia.png | comedia-focus.png |
| crime.png | crime-focus.png |
| documentario.png | documentario-focus.png |
| fantasia.png | fantasia-focus.png |
| faroeste.png | faroeste-focus.png |
| ficcao-cientifica.png | ficcao-cientifica-focus.png |
| historia.png | historia-focus.png |
| terror.png | terror-focus.png |

## Origem e tratamento

As capas preto e branco vieram da pasta images/genres/silhouettes do projeto público [tolbertsol/nuvio](https://github.com/tolbertsol/nuvio/tree/main/images/genres/silhouettes). Os arquivos de origem foram preservados sem alteração em `assets/covers/generos/originais/`. Imagegen foi usado para criar versões localizadas em português, mantendo a linguagem de fundo, a textura diagonal, o contraste e o enquadramento panorâmico. A capa crime.png já estava em português e foi copiada sem edição.

| Capa localizada | Original no repositório | Origem da comunidade | Rótulo |
|---|---|---|---|
| acao.png | acao-original.png | action-base.png | ACTION → AÇÃO |
| fantasia.png | fantasia-original.png | fantasy-base.png | FANTASY → FANTASIA |
| ficcao-cientifica.png | ficcao-cientifica-original.png | sci-fi-base.png | SCI-FI → FICÇÃO CIENTÍFICA |
| terror.png | terror-original.png | horror-base.png | HORROR → TERROR |
| animacao.png | animacao-original.png | animation-base.png | ANIMATION → ANIMAÇÃO |
| crime.png | crime-original.png | cime-base.png | CRIME, sem alteração |
| comedia.png | comedia-original.png | comedy-base.png | COMEDY → COMÉDIA |
| historia.png | historia-original.png | history-base.png | HISTORY → HISTÓRIA |
| documentario.png | documentario-original.png | documentary-base.png | DOCUMENTARY → DOCUMENTÁRIO |
| faroeste.png | faroeste-original.png | western-base.png | WESTERN → FAROESTE |
| suspense.png | — | reinterpretação gráfica do rosto e da mariposa do cartaz de *O Silêncio dos Inocentes*, com a mesma linguagem visual | SUSPENSE |

As capas localizadas são servidas pelo GitHub Raw em `assets/covers/generos/`; as fontes originais podem ser abertas em [originais/](https://github.com/Kazuji-Media/kazuji-nuvio-colletions/tree/feat/ptbr-collections-artwork/assets/covers/generos/originais). As capas das décadas em `assets/covers/decadas/` são SVGs panorâmicos e autossuficientes.
