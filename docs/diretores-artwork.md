# Artes da coleção Diretores

A revisão de 17/10/2026 contém 38 diretores em três variantes PNG com transparência real:
portrait 2:3 colorido, portrait 2:3 preto e branco e landscape 16:9 colorido.

Os arquivos ficam em [`assets/covers/diretores/revisao-2026-10-17`](../assets/covers/diretores/revisao-2026-10-17).
O [manifesto](../assets/covers/diretores/revisao-2026-10-17/manifest.json) registra dimensões,
profundidade, SHA-256, fotografia de origem, crédito, licença informada e tratamento por diretor.
As licenças das fotografias continuam sendo as dos respectivos titulares; o manifesto não concede uma licença nova.

## Campos usados no Nuvio

| Campo | Conteúdo |
|---|---|
| `tileShape` | `POSTER` |
| `coverImageUrl` | Portrait P&B |
| `focusGifUrl` | Portrait colorido (PNG estático) |
| `focusGifEnabled` | `true` |
| `heroBackdropUrl` | Landscape colorido |

O [mapeamento por ID de pasta](../collections/diretores-artwork.json) contém somente esses campos.
É uma referência de atualização parcial, **não um arquivo de importação de coleção**.
As fontes de filmes e séries, seus parâmetros, a ordem das pastas e as demais coleções devem ser preservados.

O uso dos campos de foco e hero depende do cliente e do layout. Nos clientes examinados,
o banner interno de uma pasta ainda usa `coverImageUrl`; `heroBackdropUrl` não substitui esse banner em todos os dispositivos.

## Qualidade e seleção

Os arquivos preservam a resolução nativa, sem ampliação da fotografia para simular detalhe.
Wes Anderson mantém PNG de 16 bits; os demais mantêm a profundidade de suas fontes processadas.
A versão P&B deriva da colorida e conserva exatamente a mesma máscara alpha.
Os enquadramentos apoiam a figura na base; o landscape posiciona o rosto próximo do terço direito.

As extensões aprovadas nesta etapa completam ombros e roupa, preservando o núcleo fotográfico do rosto.
Os tratamentos sintéticos estão identificados no manifesto.
Akira Kurosawa usa a proposta de luz suave; Emir Kusturica usa ombros e correção de cor;
Gus Van Sant recebeu somente correção fotográfica de cor.

Bong Joon-ho, Stanley Kubrick, Chris Miller and Phil Lord e Ridley Scott conservam seus recortes fotográficos limpos:
os complementos propostos ainda precisavam de acabamento. As fotografias anteriormente aprovadas permanecem nas opções selecionadas.

## Verificação

Com Python, NumPy e OpenCV disponíveis:

```sh
python scripts/validate_director_artwork.py
```

A verificação cobre os 114 arquivos, hashes, dimensões, profundidade, proporções,
alpha real, alinhamento inferior, P&B neutro e correspondência entre manifesto e mapeamento.
As URLs usam o caminho versionado da revisão na branch `feat/ptbr-collections-artwork`.
