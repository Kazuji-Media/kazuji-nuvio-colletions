# Artes de Estúdios de produção

11 capas landscape em PNG **1920 × 1080**, capa Apple em **3840 × 2160**, 12 fundos **3840 × 2160** e cinco GIFs de foco.
Os arquivos estão em [assets/covers/estudios/revisao-2026-10-18](../assets/covers/estudios/revisao-2026-10-18).
O [manifesto](../assets/covers/estudios/revisao-2026-10-18/manifest.json) registra origem, crédito, resolução nativa, quadros, bytes e SHA-256 de cada imagem.

## Importação

- [estudios-producao.json](https://raw.githubusercontent.com/Kazuji-Media/kazuji-nuvio-colletions/feat/ptbr-collections-artwork/collections/estudios-producao.json): capas HD e animação ao focar A24, Disney, DreamWorks, Pixar e Cartoon Network.
- [estudios-producao-estatico.json](https://raw.githubusercontent.com/Kazuji-Media/kazuji-nuvio-colletions/feat/ptbr-collections-artwork/collections/estudios-producao-estatico.json): mesmas capas e fundos, com animação desativada.
- [estudios-artwork.json](../collections/estudios-artwork.json): mapeamento parcial por ID, destinado a atualização por script; **não importar este arquivo diretamente**.

Os dois arquivos de importação são arrays contendo somente a coleção `collection-09ca5279-community`.
Preservam os 12 IDs de pasta, a ordem, as 25 fontes de filmes e séries e os campos não visuais do backup local de 11/10/2026.
A conta não foi alterada nesta publicação. Se a coleção foi editada desde esse backup, use uma exportação atual e aplique somente as artes:

```sh
python scripts/apply_studio_artwork.py export-atual.json estudios-atualizados.json
python scripts/apply_studio_artwork.py export-atual.json estudios-estaticos.json --static
```

O script exige os IDs conhecidos, mantém fontes, pastas extras e campos desconhecidos e grava em um arquivo separado.
O resultado contém somente a coleção de estúdios. No fluxo de importação do Nuvio TV, ela é atualizada pelo mesmo ID; as outras coleções não fazem parte deste pacote.
Publicar no GitHub não altera automaticamente uma coleção já instalada: importe ou aplique o novo JSON.

## Campos visuais

| Campo | Uso |
|---|---|
| `tileShape` | `LANDSCAPE` em todas as pastas |
| `hideTitle` | `true`, pois o logotipo já identifica o estúdio |
| `coverImageUrl` | PNG estático 1080p; Apple em 4K |
| `heroBackdropUrl` | Fundo 4K |
| `focusGifUrl` | GIF quando disponível; capa estática nas outras pastas |
| `focusGifEnabled` | Ativado somente para os cinco GIFs na versão animada |

Os campos de foco e hero dependem do cliente e layout. Não houve teste nesta entrega em TV/celular.
As capas são 16:9; os GIFs preservam a proporção original e podem receber recorte conforme o cliente.

## Qualidade e fontes

As capas de 10 estúdios e 11 fundos foram copiadas sem alteração de [Prism Wallpapers, de bramst0ne](https://github.com/bramst0ne/prism-wallpapers).
A Apple Studios usa agora a [imagem Apple Original Films selecionada pelo usuário no AVID](https://www.avid.wiki/File:Apple_Original_Films_(A).png), em 3840 × 2160, copiada sem alteração para `apple-studios/apple-original-films-4k.png`. O mesmo arquivo serve como capa, fundo e referência de foco estático. A marca e as fontes de catálogo da pasta Apple Studios permanecem as mesmas. O AVID identifica a captura como material protegido usado sob fair use; isso não concede uma licença geral de reutilização.
A opção anterior baseada no [SVG da marca no Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Apple_Studios.svg) continua preservada em `apple-studios/original.svg`, `cover.svg`, `cover.png` e `hero.png`; o manifesto registra essa opção em `previousArtwork`.
A capa Cartoon Network Studios usa o logotipo branco do Prism em um layout SVG; o original está preservado em `cartoon-network/logo.png`.
O layout Cartoon Network e a opção anterior da Apple mantêm fontes vetoriais/editáveis em `cover.svg`. As demais capas são os arquivos nativos do acervo.

Os GIFs vêm dos acervos [rrevanth/nuvio-assets](https://github.com/rrevanth/nuvio-assets) e [MuditGuptaR/nuvio-assets](https://github.com/MuditGuptaR/nuvio-assets), além do GIF A24 já usado na coleção, agora copiado para o repositório.

| Estúdio | GIF nativo | Quadros |
|---|---|---|
| A24 | 480 × 269 | 174 |
| Disney | 500 × 304 | 17 |
| DreamWorks | 498 × 208 | 65 |
| Pixar | 500 × 333 | 83 |
| Cartoon Network | 500 × 395 | 57 |

Os GIFs **não são HD** e não foram ampliados para simular detalhe. A versão estática mantém melhor definição no foco.
Os arquivos antigos da Apple Studios no Postimg retornaram HTTP 404 durante a pesquisa.
Foram escolhidas variantes claras para manter legibilidade em fundo escuro e o escudo WB para identificar Warner Bros.

Os créditos dos acervos identificam a origem das cópias; logos e artes de filmes continuam pertencendo aos titulares.
Não foi identificada licença geral dos acervos que relicencie essas marcas e artes. O SVG Apple está descrito no Commons como PD-textlogo, sujeito aos direitos de marca.

## Prévia e conferência

Abra [a galeria](estudios/index.html) localmente para ver capas, animações e fundos.
Foi conferida a identidade visual das 12 capas, a decodificação de todos os quadros dos GIFs, dimensões, hashes e preservação integral das 25 fontes na geração dos dois JSONs.
