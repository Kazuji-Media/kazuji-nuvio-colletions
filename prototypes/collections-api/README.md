# Protótipo descartável — Collection A via API Nuvio

Pergunta: conseguimos criar uma coleção, trocar seu filme por uma nova versão e voltar à anterior usando a API, preservando as demais coleções?

| Versão | Título na conta | Filme |
|---|---|---|
| v1 | A - v1 | Madrugada dos Mortos (2004), IMDb tt0363547 |
| v2 | A - v2 | O Rei Leão (1994), IMDb tt0110357 |

As duas versões usam `kazuji-prototype-collection-a` e a mesma pasta. Aplicar v2 atualiza A, sem criar uma segunda coleção. Os JSONs são as versões editáveis; o addon mínimo contém os dois catálogos, com um filme em cada um.

## Rodar

Python 3.10+; sem bibliotecas externas. Na raiz do checkout:

```powershell
python prototypes/collections-api/serve.py
```

Abra http://127.0.0.1:8766. Entre com email/senha Nuvio. O programa lista somente os perfis reais, pelo nome, quantidade e títulos das coleções. Se houver um único perfil acessível, ele é selecionado automaticamente. Selecione o perfil correto, prepare v1 e aplique. Depois repita para v2. Os botões fazem chamadas reais à conta; não é uma simulação. O cliente instalado pode precisar de sincronização/reabertura para refletir a mudança.

A senha é encaminhada à API oficial e descartada após o login. Access/refresh tokens ficam somente na memória do processo. Fechar o servidor descarta a sessão local; nenhuma sessão é salva em arquivos. A renovação usa a validade recebida da API. O programa escuta apenas em 127.0.0.1 e exige origem local, token CSRF e cookie de sessão para operações autenticadas. Não hospedar esse servidor na internet.

## Chamadas implementadas

- Login e renovação: `/auth/v1/token?grant_type=password` e `grant_type=refresh_token`.
- Perfis reais: `sync_pull_profiles`, usando `profile_index` e `name`. Perfis com PIN ficam indisponíveis neste protótipo; não há implementação de desbloqueio.
- Leitura: `sync_pull_collections` por `p_profile_id`.
- Gravação: `sync_push_collections`, com o array completo após incorporar apenas a coleção A.
- Leitura dos addons e `sync_push_addons`: instala o addon do protótipo uma vez, mantendo URLs, nomes, estados e ordem dos demais. Se o perfil compartilha addons do principal, a instalação usa o perfil 1; a coleção continua no perfil selecionado.

O addon está em uma URL Raw da branch `prototype/collections-api`, no mesmo repositório Kazuji. A instalação só é tentada depois que manifest e catálogo públicos correspondem aos IDs esperados. Esta branch é necessária enquanto o addon estiver instalado.

Antes da escrita, o programa salva coleções/addons em `.private/`, ignorada pelo Git. Essas cópias podem conter URLs privadas de outros addons; não publicá-las. Uma impressão digital vincula a aplicação à prévia. Uma segunda leitura detecta alterações anteriores à escrita; depois do push, outra leitura compara o array inteiro. Propriedades desconhecidas das demais coleções são preservadas, incluindo `community`.

Não há transação/compare-and-swap documentada entre essas RPCs: ainda existe uma janela entre a última leitura e o push. A instalação do addon e a alteração da coleção também são duas operações distintas. Uma falha não provoca repetição automática de escrita; releia o estado. Não há botão de restauração integral do perfil: reaplicar v1 é a reversão limitada à coleção A.

## Verificação

```powershell
python prototypes/collections-api/verify.py
```

As sete verificações offline passaram em 16/10/2026. Cobrem o ciclo v1 → v2 → v1, preservação de campos desconhecidos e demais coleções, instalação única do addon, aplicação idempotente, prévia desatualizada, alteração concorrente detectável, perfis reais/protegidos e addons compartilhados, contrato das chamadas e correspondência dos filmes/catálogos. Os cinco arquivos públicos do addon responderam HTTP 200 e CORS `*`. A comprovação na conta e nos aplicativos deve ser registrada separadamente; o teste offline não a substitui.

## Fontes

- [API pública oficial Nuvio](https://nuvio.tv/docs/nuvio-public-api.md): autenticação, Collections e Addons.
- [Protocolo oficial de addons](https://github.com/Stremio/stremio-addon-sdk/blob/master/docs/protocol.md).
- [Madrugada dos Mortos no TMDB](https://www.themoviedb.org/movie/924-dawn-of-the-dead).
- [O Rei Leão no TMDB](https://www.themoviedb.org/movie/8587-the-lion-king).
- Metadados/IDs conferidos no Cinemeta: `https://v3-cinemeta.strem.io/meta/movie/tt0363547.json` e `tt0110357.json`.

Estado inicial: implementação preparada; aplicação autenticada na conta ainda pendente.
