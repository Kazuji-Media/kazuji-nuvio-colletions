# Prova de Premiações

Q32=A aceita: gerar e publicar catálogos estáticos por GitHub Actions. Esta primeira prova cobre **Oscar de Melhor Filme, cerimônias de 2025 e 2026**, com dez indicados e um vencedor por edição. Indicados incluem o vencedor. Não representa ainda todos os vencedores do Oscar nem a cobertura de Emmy/BAFTA.

Fontes oficiais: [97ª edição, 2025](https://www.oscars.org/oscars/ceremonies/2025) e [98ª edição, 2026](https://www.oscars.org/oscars/ceremonies/2026). Anora venceu em 2025; One Battle after Another venceu em 2026. Os IDs IMDb e URLs de pôster foram conferidos no catálogo público Cinemeta; cada item registra seu endereço de consulta. Rótulos do addon em pt-BR; títulos seguem o catálogo, com os filmes brasileiros usando Ainda Estou Aqui e O Agente Secreto. As imagens permanecem nas URLs do provedor, sem cópia de arquivos. O Brutalista foi identificado por título e ID, apesar de o Cinemeta informar 2025; esta prova registra 2024 como ano do filme elegível na cerimônia de 2025, sem confundi-lo com o ano da premiação.

## Instalação e navegação

Manifest publicado: `https://kazuji-media.github.io/kazuji-nuvio-colletions/premiacoes/manifest.json`.

No Nuvio, adicionar esse endereço como addon. Ele declara somente `catalog`; outros addons instalados resolvem os metadados completos e a reprodução pelos IDs IMDb.

Na tela **Buscar → Descobrir**, selecionar `Oscar · Melhor Filme · Indicados` ou `Oscar · Vencedores (prova: Melhor Filme)`. O filtro nativo de gênero apresenta os anos **2026** e **2025**. O controle continua chamado gênero porque o cliente oferece esse campo; os valores representam anos de cerimônia.

Sem filtro, a URL estável abre a última edição cadastrada com indicações anunciadas. As fontes das coleções podem usar esse catálogo sem ano fixo. O acesso ao histórico ocorre na tela nativa, conforme Q30; nenhum cliente foi modificado.

## Gerar e conferir localmente

```powershell
python -m unittest discover -s tests -p 'test_premiacoes.py' -v
python scripts/build_premiacoes.py
python -m http.server 8765 --directory .build/premiacoes
```

O resultado fica em `.build/premiacoes`, ignorado pelo Git. Sem dependências externas, acesso à rede ou credenciais para gerar.

```text
premiacoes/manifest.json
premiacoes/cobertura.json
premiacoes/catalog/movie/oscar-vencedores.json
premiacoes/catalog/movie/oscar-vencedores/genre=2025.json
premiacoes/catalog/movie/oscar-vencedores/genre=2026.json
premiacoes/catalog/movie/oscar-vencedores/genre=latest.json
premiacoes/catalog/movie/oscar-melhor-filme-indicados.json
premiacoes/catalog/movie/oscar-melhor-filme-indicados/genre=2025.json
premiacoes/catalog/movie/oscar-melhor-filme-indicados/genre=2026.json
premiacoes/catalog/movie/oscar-melhor-filme-indicados/genre=latest.json
```

Não se declara paginação (`skip`) nesta prova: cada catálogo tem no máximo dez filmes. O manifesto declara apenas as opções de ano para as quais foram gerados arquivos.

## Atualização e publicação

O arquivo `catalogos/premiacoes/oscar-melhor-filme.json` é a entrada conferida. Atualizar indicados/resultados nele dispara a geração e publicação ao enviar a alteração para `main` ou para a branch inicial `feat/premiacoes-prova`. O workflow também valida PRs, permite disparo manual e contém um agendamento diário às 06:17 UTC que passa a operar quando estiver na branch padrão. O agendamento recompila os dados existentes; **não coleta novos resultados**.

Uma nova edição com `status: announced` e indicados conferidos assume o alias automaticamente. Seu catálogo de vencedores fica vazio até `status: results` e marcação dos vencedores. Jamais se empresta o vencedor da edição anterior. Dados inválidos, IDs duplicados/ausentes ou resultados inconsistentes fazem o build falhar antes da publicação; o site anterior continua disponível.

Não há scraper nesta prova. A consulta direta ao HTML da Academy retornou HTTP 403 no ambiente local, embora as páginas oficiais estejam acessíveis pela ferramenta de pesquisa. A montagem inicial foi conferida nas páginas oficiais. A aquisição automática completa precisa de fonte validada antes de ampliar o job; não foi contratado serviço pago.

Pages publica um artefato e não cria commits de arquivos gerados. A primeira publicação usa a branch da prova, sem mesclar as alterações de capas ou alterar as URLs GitHub Raw existentes. Quando este workflow estiver integrado em `main`, `main` será a origem das atualizações normais; o deploy provisório da branch deve ser removido após essa integração.

Referências técnicas: [protocolo estático Stremio](https://github.com/Stremio/stremio-addon-sdk/blob/master/docs/protocol.md), [manifest](https://github.com/Stremio/stremio-addon-sdk/blob/master/docs/api/responses/manifest.md) e [Pages via Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Aceite da prova

Verificação em 08/10/2026 (America/Sao_Paulo): seis testes locais aprovados e testes/build aprovados no runner Linux. [Execução de publicação](https://github.com/Kazuji-Media/kazuji-nuvio-colletions/actions/runs/37863169734) concluída com sucesso. Os dez JSONs públicos responderam HTTP 200, `application/json` e `Access-Control-Allow-Origin: *`; conferidos dez indicados por edição, os vencedores Anora/One Battle After Another e equivalência do alias com 2026. [Página da prova](https://kazuji-media.github.io/kazuji-nuvio-colletions/) e [manifest](https://kazuji-media.github.io/kazuji-nuvio-colletions/premiacoes/manifest.json) publicados. [PR #2](https://github.com/Kazuji-Media/kazuji-nuvio-colletions/pull/2) em rascunho para revisão, sem merge.

O primeiro deploy foi rejeitado pela regra automática de ambiente que permitia somente `main`. Foi acrescentada a permissão específica `feat/premiacoes-prova`, preservando `main`, e a execução foi repetida com sucesso. Não foi uma falha do catálogo nem dos testes. Remover essa permissão provisória após a integração em `main`.

- Geração determinística, duas edições, dez indicados e vencedor correto em cada uma.
- Alias aponta para a edição mais recente e fica sem vencedores quando a edição ainda aguarda resultados.
- Workflow executa os testes, gera e publica; manifesto e todos os caminhos respondem como JSON público.
- Instalação e navegação aprovadas no Nuvio Desktop descrito abaixo. TV/mobile e atualização após uma nova publicação continuam a validar; a leitura dos caminhos e filtros no código público desses clientes não substitui o teste de uso.

### Configuração da conta e teste no aplicativo

Em 08/10/2026, a pedido do usuário, o manifest foi adicionado pelo Nuvio Account e habilitado. A página de addons confirmou 30 instalações. No Profile 1, foi salva a coleção `kazuji-premiacoes`, título Premiações, com duas pastas e duas fontes: Melhor Filme · Vencedores (`oscar-vencedores`) e Melhor Filme · Indicados (`oscar-melhor-filme-indicados`). Cada fonte usa seu catálogo correspondente sem gênero fixo, abrindo a última edição.

Também foi salva a pasta `premiacoes` dentro da coleção Descobrir, com as mesmas duas fontes. A revisão preservou as seis pastas/fontes anteriores; Descobrir passou a sete pastas e oito fontes. A conta passou a dez coleções. Não foi obtido um export local completo: as capturas de validação não são um backup. A ordenação completa da home e as artes não foram alteradas nesta prova.

Validação por interface no **Nuvio Desktop 0.1.25-alpha (25), Tapframe, baseado em Nuvio 0.4.26**, instalado no Windows:

- Após reiniciar o aplicativo e selecionar o perfil, o novo addon e a coleção apareceram sem instalação local adicional.
- Buscar → Descobrir → Oscar · Vencedores abriu One Battle After Another no catálogo sem filtro; escolher 2025 no filtro nativo de gênero abriu Anora. Os valores 2026 e 2025 foram apresentados no seletor.
- O catálogo de indicados sem filtro mostrou os dez filmes de 2026, incluindo o vencedor. Um detalhe de filme abriu Sonhos de Trem com sinopse, arte e metadados em português. Não foi testada reprodução.
- Na home, Premiações → Melhor Filme · Vencedores mostrou o vencedor de 2026 e Premiações → Melhor Filme · Indicados mostrou os dez indicados.
- Descobrir → Premiações abriu abas de vencedores e indicados, com o mesmo vencedor e os mesmos dez filmes. Foram conferidos os dois acessos solicitados.

As capturas de conta, coleção, atalho e catálogo foram mantidas localmente, fora do repositório público. Este teste confirma o cliente Desktop observado; não certifica Google TV ou Android mobile e não amplia a cobertura além de Melhor Filme 2025/2026.

Durante a montagem, mudar o ID de uma pasta nova fez o builder web retornar a seleção para a primeira pasta. As alterações involuntárias no rascunho foram detectadas na revisão e restauradas antes de salvar. Ao editar IDs, reselecionar a pasta desejada e conferir a revisão final.

Somente depois desta prova, ampliar para todas as categorias/famílias e histórico desde 2000, preservar vencedores únicos por edição e usar a mesma origem nos dois acessos de Premiações.
