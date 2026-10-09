import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_premiacoes import ROOT, SOURCE, build, render


class PremiacoesTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(SOURCE.read_text(encoding="utf-8"))

    def test_real_editions_have_ten_nominees_and_correct_winners(self):
        files = render(self.data)
        for year, winner in [(2025, "tt28607951"), (2026, "tt30144839")]:
            nominees = files[f"premiacoes/catalog/movie/oscar-melhor-filme-indicados/genre={year}.json"]["metas"]
            winners = files[f"premiacoes/catalog/movie/oscar-vencedores/genre={year}.json"]["metas"]
            self.assertEqual(10, len(nominees))
            self.assertEqual([winner], [m["id"] for m in winners])
            self.assertIn(winner, [m["id"] for m in nominees])

    def test_latest_is_ceremony_year_independent_of_input_order(self):
        self.data["editions"].reverse()
        files = render(self.data)
        for catalog in ("oscar-vencedores", "oscar-melhor-filme-indicados"):
            self.assertEqual(files[f"premiacoes/catalog/movie/{catalog}/genre=2026.json"],
                             files[f"premiacoes/catalog/movie/{catalog}.json"])
            self.assertEqual(files[f"premiacoes/catalog/movie/{catalog}.json"],
                             files[f"premiacoes/catalog/movie/{catalog}/genre=latest.json"])
        self.assertEqual("2025", files["premiacoes/catalog/movie/oscar-vencedores.json"]["metas"][0]["releaseInfo"])

    def test_new_announced_edition_does_not_reuse_previous_winner(self):
        edition = copy.deepcopy(self.data["editions"][-1])
        edition.update(year=2027, status="announced", source="https://www.oscars.org/oscars/ceremonies/2027")
        for movie in edition["nominees"]:
            movie["winner"] = False
        self.data["editions"].append(edition)
        files = render(self.data)
        self.assertEqual([], files["premiacoes/catalog/movie/oscar-vencedores.json"]["metas"])
        self.assertEqual(10, len(files["premiacoes/catalog/movie/oscar-melhor-filme-indicados.json"]["metas"]))
        self.assertEqual(2027, files["premiacoes/cobertura.json"]["latest"])

    def test_missing_ids_duplicate_ids_and_invalid_results_stop_generation(self):
        for mutation in ("missing", "duplicate", "pending-winner", "no-winner", "empty", "wrong-source"):
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(self.data)
                edition = data["editions"][0]
                if mutation == "missing":
                    edition["nominees"][0].pop("id")
                elif mutation == "duplicate":
                    edition["nominees"][1]["id"] = edition["nominees"][0]["id"]
                elif mutation == "pending-winner":
                    edition["status"] = "announced"
                elif mutation == "no-winner":
                    for movie in edition["nominees"]:
                        movie["winner"] = False
                elif mutation == "empty":
                    edition["nominees"] = []
                else:
                    edition["source"] = "https://www.oscars.org/oscars/ceremonies/2000"
                with self.assertRaises(ValueError):
                    render(data)

    def test_manifest_options_have_files_and_do_not_advertise_pagination(self):
        files = render(self.data)
        manifest = files["premiacoes/manifest.json"]
        self.assertEqual(["catalog"], manifest["resources"])
        for catalog in manifest["catalogs"]:
            self.assertEqual(["genre"], [extra["name"] for extra in catalog["extra"]])
            self.assertEqual(["2026", "2025"], catalog["extra"][0]["options"])
            for year in catalog["extra"][0]["options"]:
                self.assertIn(f"premiacoes/catalog/movie/{catalog['id']}/genre={year}.json", files)

    def test_build_is_deterministic_and_invalid_data_writes_nothing(self):
        temp_root = ROOT / ".build"
        temp_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as directory:
            self.assertTrue(Path(directory).resolve().is_relative_to(temp_root.resolve()))
            output = Path(directory) / "site"
            build(self.data, output, "https://example.org/project")
            before = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
            build(self.data, output, "https://example.org/project")
            after = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            self.assertIn("https://example.org/project/premiacoes/manifest.json", (output / "index.html").read_text(encoding="utf-8"))
            self.data["editions"][0]["nominees"][0].pop("id")
            invalid_output = Path(directory) / "invalid"
            with self.assertRaises(ValueError):
                build(self.data, invalid_output, "https://example.org")
            self.assertFalse(invalid_output.exists())


if __name__ == "__main__":
    unittest.main()
