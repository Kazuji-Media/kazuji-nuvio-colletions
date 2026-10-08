# Fontes TMDB para avaliar

As coleções do perfil já usam fontes TMDB. No editor do Nuvio, as opções disponíveis incluem descoberta personalizada de filmes e séries (Popular, Mais bem avaliados ou Recentes), listas públicas, companhias produtoras, redes, coleções de filmes, créditos de pessoas e créditos de diretores. A descoberta personalizada também aceita gênero, período, nota, votos, idioma, país, palavras-chave, empresa, rede, região e provedores de streaming.

## Catálogos do TMDB

| Ideia | Filmes | Séries |
|---|---|---|
| Populares | [Filmes populares](https://www.themoviedb.org/movie) | [Séries populares](https://www.themoviedb.org/tv) |
| Mais bem avaliados | [Filmes mais bem avaliados](https://www.themoviedb.org/movie/top-rated) | [Séries mais bem avaliadas](https://www.themoviedb.org/tv/top-rated) |
| Em cartaz / no ar | [Em cartaz](https://www.themoviedb.org/movie/now-playing) | [No ar hoje](https://www.themoviedb.org/tv/airing-today) |
| Próximos / em exibição | [Próximos filmes](https://www.themoviedb.org/movie/upcoming) | [Séries em exibição](https://www.themoviedb.org/tv/on-the-air) |
| Descoberta com filtros | [Descobrir filmes](https://www.themoviedb.org/discover/movie) | [Descobrir séries](https://www.themoviedb.org/discover/tv) |

A documentação oficial da API também descreve [descoberta de filmes](https://developer.themoviedb.org/reference/discover-movie) e [descoberta de séries](https://developer.themoviedb.org/reference/discover-tv).

## Oscar e edição da cerimônia

O TMDB identifica cada cerimônia pelo número da edição na URL:

`https://www.themoviedb.org/award/1-academy-awards/ceremony/{numero}`

- [97ª cerimônia (2025)](https://www.themoviedb.org/award/1-academy-awards/ceremony/97)
- [98ª cerimônia (2026)](https://www.themoviedb.org/award/1-academy-awards/ceremony/98)
- Para a 99ª, o mesmo formato termina em `/ceremony/99`; a página depende de o TMDB publicar os dados daquela edição.

No editor atual do Nuvio não existe um tipo de fonte “cerimônia de premiação”. A URL do Oscar é uma página útil para consultar a edição, mas não vira sozinha um feed de filmes dentro da coleção. A coleção comunitária [Kaptain's Awards Collection](https://nuvio.tv/community-collections/kaptain-s-awards-collection-easy-install) reúne vencedores por categoria e inclui listas mantidas até 2025; ela não troca automaticamente para a cerimônia seguinte.

Para uma coleção anual realmente dinâmica dentro do Nuvio, será preciso um tipo de fonte TMDB para cerimônias (ou uma lista pública que seja atualizada). Até essa opção existir, as fontes de descoberta por ano mostram lançamentos daquele ano, não indicados ou vencedores de uma premiação.
