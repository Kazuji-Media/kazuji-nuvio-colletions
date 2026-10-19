# Artes e GIFs de Streamings

Sete GIFs de foco em **1280 × 720**, acompanhados de capas estáticas em **1920 × 1080**, extraídos de vídeos das identidades documentadas no AVID.
As animações usam 12,5 quadros por segundo, paleta de 256 cores e repetição contínua, sem áudio.
Os cortes duram aproximadamente 2,6 a 4,8 segundos e incluem uma breve pausa no último quadro.

Os arquivos ficam em [assets/covers/streamings/revisao-2026-10-18](../assets/covers/streamings/revisao-2026-10-18).
O [manifesto](../assets/covers/streamings/revisao-2026-10-18/manifest.json) registra fontes, autores dos uploads, resolução do vídeo, trecho utilizado, duração, número de quadros, tamanho e SHA-256 de cada arquivo.

## Seleção

| Serviço | Identidade e referência | Fonte do vídeo |
|---|---|---|
| Apple TV | [Vidro multicolorido, 2025](https://www.avid.wiki/Apple_TV_(2019-)) | Canal Apple TV |
| HBO Max | [Partículas roxas e marca HBO Max Original, 2020](https://www.avid.wiki/HBO_Max) | Captura publicada por Broken Saw; somente o trecho HBO Max foi usado |
| Netflix | [N vermelho e espectro de cores, 2019](https://www.avid.wiki/Netflix_(streaming_service)) | Canal Netflix |
| Disney+ | [Aurora, 2024](https://www.avid.wiki/Disney%2B_Originals) | Captura horizontal listada pelo AVID |
| Prime Video | [Sorriso metálico azul e holofote, 2022](https://www.avid.wiki/Amazon_Originals) | Captura publicada por Broken Saw |
| Hulu | [Marca verde e moldura multicolorida, 2021](https://www.avid.wiki/Hulu_Originals) | Zelig Sound, responsável pela identidade sonora |
| Paramount+ | [Montanha, estrelas e transição para azul, 2021](https://www.avid.wiki/Paramount%2B) | Canal Paramount |

A referência HBO Max de 2025 encontrada no AVID era uma filmagem de televisão e foi descartada. Foi escolhida a abertura HBO Max de 2020 em captura limpa; ela é histórica, não a versão de 2025. O portal oficial de motion também foi consultado, mas o vídeo correspondente disponível exigia autenticação.
A primeira referência Disney+ era uma gravação vertical de celular; a seleção final usa a abertura horizontal.

O tratamento limita-se a seleção de trechos, redimensionamento para baixo, conversão em GIF e extração de quadros para as capas. A composição original é preservada; a abertura Prime Video recebe faixas pretas para caber em 16:9 sem cortar a imagem.
As capas estáticas usam quadros em que a marca está legível, mantendo coerência com a animação de foco.

## Integração

- [streamings.json](https://raw.githubusercontent.com/Kazuji-Media/kazuji-nuvio-colletions/feat/ptbr-collections-artwork/collections/streamings.json): coleção pronta com animações de foco.
- [streamings-estatico.json](https://raw.githubusercontent.com/Kazuji-Media/kazuji-nuvio-colletions/feat/ptbr-collections-artwork/collections/streamings-estatico.json): mesmas capas com animação desativada.
- [streamings-artwork.json](../collections/streamings-artwork.json): mapeamento parcial por ID; **não importar diretamente**.

As coleções completas contêm somente `collection-beabeb28-community`. Os sete IDs, a ordem das pastas, as 15 fontes de catálogo, os filtros e as demais configurações foram preservados do backup atual do perfil.
Para preservar edições feitas depois dessa exportação, aplique apenas o mapeamento visual a um backup recente:

```sh
python scripts/apply_streaming_artwork.py export-atual.json streamings-atualizados.json
python scripts/apply_streaming_artwork.py export-atual.json streamings-estaticos.json --static
```

O script grava um arquivo separado contendo somente a coleção Streamings e modifica somente `coverImageUrl`, `focusGifUrl` e `focusGifEnabled`.
O foco animado depende do cliente e layout utilizados. A integração foi conferida no site; não houve teste em TV ou celular.

## Prévia e origem

Abra [a galeria](streamings/index.html) localmente. As capas carregam primeiro; as animações são exibidas ao passar o cursor ou tocar.
Os GIFs antigos de Netflix e Paramount+ permanecem nos caminhos anteriores para preservar links já publicados.
As marcas, animações e direitos dos vídeos continuam com seus respectivos titulares. O AVID documenta as identidades; a listagem pública de um vídeo não concede uma licença de reutilização.
