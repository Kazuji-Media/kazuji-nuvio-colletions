"""Generate the static Oscar Best Picture proof without network calls or API keys."""

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "catalogos/premiacoes/oscar-melhor-filme.json"
CATALOGS = {
    "oscar-vencedores": "Oscar · Vencedores (prova: Melhor Filme)",
    "oscar-melhor-filme-indicados": "Oscar · Melhor Filme · Indicados",
}


def validate(data):
    if data.get("schemaVersion") != 1 or data.get("category") != "best-picture":
        raise ValueError("A prova aceita schemaVersion=1 e category=best-picture.")
    editions = data.get("editions", [])
    if not editions:
        raise ValueError("É necessária ao menos uma edição com indicações anunciadas.")
    years = set()
    for edition in editions:
        year = edition.get("year")
        if type(year) is not int or year < 2000 or year in years:
            raise ValueError(f"Ano da cerimônia inválido ou repetido: {year}.")
        years.add(year)
        if edition.get("source") != f"https://www.oscars.org/oscars/ceremonies/{year}":
            raise ValueError(f"Fonte oficial ausente ou incompatível com {year}.")
        status = edition.get("status")
        if status not in ("announced", "results"):
            raise ValueError(f"Estado inválido em {year}: {status}.")
        nominees = edition.get("nominees", [])
        if not nominees:
            raise ValueError(f"A edição {year} não possui indicados conferidos.")
        ids = set()
        for movie in nominees:
            identifier = movie.get("id", "")
            if not re.fullmatch(r"tt\d{7,}", identifier) or identifier in ids:
                raise ValueError(f"ID ausente, inválido ou repetido em {year}: {identifier}.")
            ids.add(identifier)
            if not isinstance(movie.get("name"), str) or not movie["name"].strip():
                raise ValueError(f"Nome ausente em {year}: {identifier}.")
            release_year = movie.get("releaseYear")
            if type(release_year) is not int or not 1888 <= release_year <= year:
                raise ValueError(f"Ano de lançamento inválido: {identifier}.")
            if type(movie.get("winner")) is not bool:
                raise ValueError(f"Resultado deve ser booleano: {identifier}.")
            for field in ("poster", "idSource"):
                url = urlparse(movie.get(field, ""))
                if url.scheme != "https" or not url.netloc:
                    raise ValueError(f"{field} HTTPS ausente: {identifier}.")
        winners = sum(movie["winner"] for movie in nominees)
        if status == "announced" and winners:
            raise ValueError(f"A edição {year} ainda não pode ter vencedores.")
        if status == "results" and not winners:
            raise ValueError(f"A edição {year} tem resultados, mas nenhum vencedor.")
    return sorted(editions, key=lambda edition: edition["year"], reverse=True)


def catalog_response(edition, winners_only):
    metas = []
    for movie in edition["nominees"]:
        if winners_only and not movie["winner"]:
            continue
        result = "Vencedor" if movie["winner"] else "Indicado"
        metas.append({
            "id": movie["id"], "type": "movie", "name": movie["name"],
            "poster": movie["poster"], "posterShape": "poster",
            "releaseInfo": str(movie["releaseYear"]),
            "description": f"{result} a Melhor Filme no Oscar {edition['year']}.",
        })
    # An announced latest edition deliberately yields no winners, never old results.
    return {"metas": metas}


def render(data):
    editions = validate(data)
    latest = editions[0]
    years = [str(edition["year"]) for edition in editions]
    manifest = {
        "id": "org.kazuji.premiacoes", "version": "0.1.0",
        "name": "Kazuji · Premiações (prova)",
        "description": f"Prova de Melhor Filme no Oscar: {', '.join(reversed(years))}. "
                       "Sem filtro: última edição cadastrada. Histórico no filtro de gênero/ano. "
                       "Metadados e reprodução dependem dos outros addons instalados.",
        "resources": ["catalog"], "types": ["movie"], "idPrefixes": ["tt"],
        "catalogs": [
            {"type": "movie", "id": identifier, "name": name,
             "extra": [{"name": "genre", "isRequired": False, "options": years}]}
            for identifier, name in CATALOGS.items()
        ],
    }
    files = {"premiacoes/manifest.json": manifest}
    for identifier in CATALOGS:
        winners_only = identifier == "oscar-vencedores"
        base = f"premiacoes/catalog/movie/{identifier}"
        for edition in editions:
            files[f"{base}/genre={edition['year']}.json"] = catalog_response(edition, winners_only)
        response = catalog_response(latest, winners_only)
        files[f"{base}.json"] = response
        files[f"{base}/genre=latest.json"] = response
    files["premiacoes/cobertura.json"] = {
        "family": "oscar", "category": "best-picture", "latest": latest["year"],
        "editions": [{"year": e["year"], "status": e["status"],
                      "nominees": len(e["nominees"]),
                      "winners": sum(m["winner"] for m in e["nominees"]),
                      "source": e["source"]} for e in editions],
        "scope": "Somente Melhor Filme. Dados conferidos; coleta automática ainda não implementada.",
    }
    return files


def build(data, output, base_url):
    files = render(data)  # Validate everything before writing any artifact.
    output = Path(output)
    for relative, value in files.items():
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    url = html.escape(base_url.rstrip("/") + "/premiacoes/manifest.json", quote=True)
    report = files["premiacoes/cobertura.json"]
    rows = "".join(
        f"<tr><td>{e['year']}</td><td>{e['nominees']}</td><td>{e['winners']}</td>"
        f"<td><a href='{html.escape(e['source'], quote=True)}'>Academy</a></td></tr>"
        for e in report["editions"]
    )
    page = """<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kazuji · Premiações</title>
<style>body{font:18px system-ui;background:#111;color:#eee;max-width:760px;margin:48px auto;padding:0 20px;line-height:1.5}a{color:#eee}code{overflow-wrap:anywhere}table{border-collapse:collapse}td,th{padding:8px 16px;border:1px solid #666}th{text-align:left}</style>
<h1>Kazuji · Premiações</h1><p>Prova: Oscar de Melhor Filme. Edições cadastradas abaixo.</p>
<p>Adicione este endereço como addon no Nuvio:</p>
<p><a href="{url}"><code>{url}</code></a></p>
<p>Sem filtro, o catálogo abre a última edição cadastrada ({latest}). Em Buscar → Descobrir, selecione um dos dois catálogos e use o filtro de gênero para escolher o ano da cerimônia.</p>
<table><tr><th>Cerimônia</th><th>Indicados</th><th>Vencedores</th><th>Fonte</th></tr>{rows}</table>
<p>Esta prova cobre apenas Melhor Filme. O Actions gera e publica os arquivos; novos resultados ainda precisam ser conferidos e adicionados ao arquivo de dados. Os indicados incluem o vencedor.</p>
<p>O addon fornece catálogos. Metadados completos e fontes de reprodução dependem dos outros addons instalados. A instalação e a navegação em TV/mobile ainda precisam de validação nos aplicativos.</p>
</html>""".replace("{url}", url).replace("{latest}", str(report["latest"])).replace("{rows}", rows)
    (output / "index.html").write_text(page, encoding="utf-8")
    (output / ".nojekyll").write_text("", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=ROOT / ".build/premiacoes")
    parser.add_argument("--base-url", default="https://kazuji-media.github.io/kazuji-nuvio-colletions")
    args = parser.parse_args()
    try:
        data = json.loads(args.source.read_text(encoding="utf-8"))
        report = build(data, args.output, args.base_url)
    except (ValueError, OSError, TypeError) as error:
        parser.exit(1, f"Falha ao gerar Premiações: {error}\n")
    print(f"Gerado: {len(report['editions'])} edições; última {report['latest']}; {args.output}")


if __name__ == "__main__":
    main()
