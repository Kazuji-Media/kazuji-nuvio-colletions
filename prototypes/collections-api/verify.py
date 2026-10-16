"""Focused offline checks for the full-replacement API's data preservation risks."""

import copy
import json
import tempfile
import unittest

from client import (ADDON_ID, COLLECTION_ID, FILMS, MANIFEST_URL, NuvioClient,
                    PrototypeError, Publisher, collection_for, fingerprint,
                    merge_collection)


class FakeNuvio:
    def __init__(self):
        self.collections = [{"id": "existing", "title": "Preservar",
                             "community": {"revision": 7}, "unknown": {"nested": [1, 2]},
                             "folders": [{"id": "old", "sources": [{"provider": "tmdb", "tmdbId": 123}]}]}]
        self.addon_rows = [{"url": "https://example.invalid/private-addon/manifest.json",
                            "name": "Existing", "enabled": False, "sort_order": 0}]
        self.collection_writes = 0
        self.addon_writes = 0
        self.last_addon_profile = None

    def profiles(self):
        return [{"profile_index": 1, "name": "Principal", "pin_enabled": False},
                {"profile_index": 2, "name": "Compartilhado", "uses_primary_addons": True},
                {"profile_index": 3, "name": "Protegido", "pin_enabled": True}]

    def pull(self, profile):
        return copy.deepcopy(self.collections)

    def push(self, profile, collections):
        self.collection_writes += 1
        self.collections = copy.deepcopy(collections)

    def addons(self, profile):
        return copy.deepcopy(self.addon_rows)

    def push_addons(self, profile, addons):
        self.addon_writes += 1
        self.last_addon_profile = profile
        self.addon_rows = copy.deepcopy(addons)


class PrototypeChecks(unittest.TestCase):
    def test_v1_v2_v1_preserves_others_and_installs_addon_once(self):
        fake = FakeNuvio()
        original_collections = copy.deepcopy(fake.collections)
        original_addons = copy.deepcopy(fake.addon_rows)
        with tempfile.TemporaryDirectory() as private:
            publisher = Publisher(fake, private)
            publisher.preflight_catalog = lambda version: None
            for version in ("v1", "v2", "v1"):
                preview = publisher.preview(1, version)
                result = publisher.apply(1, version, preview["expectedFingerprint"])
                self.assertTrue(result["verified"])
                self.assertEqual(fake.collections[:-1], original_collections)
                self.assertEqual(fake.collections[-1], collection_for(version))
                self.assertEqual(fake.addon_rows[:-1], original_addons)
                self.assertEqual(len(fake.collections), 2)
            self.assertEqual(fake.addon_writes, 1)
            self.assertEqual(fake.collection_writes, 3)
            publisher.apply(1, "v1", fingerprint(fake.collections))
            self.assertEqual(fake.collection_writes, 3)  # idempotent
            self.assertEqual(fake.addon_writes, 1)

    def test_stale_preview_blocks_both_writes(self):
        fake = FakeNuvio()
        with tempfile.TemporaryDirectory() as private:
            publisher = Publisher(fake, private)
            publisher.preflight_catalog = lambda version: None
            preview = publisher.preview(1, "v1")
            fake.collections[0]["title"] = "Editado no aplicativo"
            with self.assertRaises(PrototypeError):
                publisher.apply(1, "v1", preview["expectedFingerprint"])
            self.assertEqual(fake.addon_writes, 0)
            self.assertEqual(fake.collection_writes, 0)

    def test_profiles_use_names_reject_missing_or_locked_and_resolve_shared_addons(self):
        fake = FakeNuvio()
        with tempfile.TemporaryDirectory() as private:
            publisher = Publisher(fake, private)
            publisher.preflight_catalog = lambda version: None
            for profile in (3, 6):
                with self.assertRaises(PrototypeError):
                    publisher.preview(profile, "v1")
            preview = publisher.preview(2, "v1")
            self.assertEqual(preview["profileName"], "Compartilhado")
            publisher.apply(2, "v1", preview["expectedFingerprint"])
            self.assertEqual(fake.last_addon_profile, 1)

    def test_change_after_backup_blocks_collection_write(self):
        fake = FakeNuvio()
        fake.addon_rows.append({"url": MANIFEST_URL, "name": "Prototype", "enabled": True, "sort_order": 1})
        real_pull = fake.pull
        reads = 0

        def race(profile):
            nonlocal reads
            reads += 1
            if reads == 3:  # preview, apply's initial read, immediate pre-write read
                fake.collections.append({"id": "new", "title": "New", "folders": []})
            return real_pull(profile)

        fake.pull = race
        with tempfile.TemporaryDirectory() as private:
            publisher = Publisher(fake, private)
            publisher.preflight_catalog = lambda version: None
            preview = publisher.preview(1, "v1")
            with self.assertRaises(PrototypeError):
                publisher.apply(1, "v1", preview["expectedFingerprint"])
            self.assertEqual(fake.collection_writes, 0)

    def test_unknown_fields_and_position_are_preserved(self):
        current = [{"id": "other", "community": {"x": 1}},
                   {**collection_for("v1"), "extension": {"future": True}}]
        merged = merge_collection(current, collection_for("v2"))
        self.assertEqual(merged[0], current[0])
        self.assertEqual(merged[1]["extension"], {"future": True})
        self.assertEqual(current[1]["title"], "A - v1")
        with self.assertRaises(PrototypeError):
            merge_collection(current + [current[0]], collection_for("v1"))

    def test_api_contract_for_auth_refresh_read_and_full_write(self):
        client = NuvioClient()
        calls = []

        def http(path, body=None, authenticated=True, method=None):
            calls.append((path, body, authenticated))
            if "token?" in path:
                return {"access_token": "test-only-access", "refresh_token": "test-only-refresh", "expires_in": 3600}
            if "sync_pull_collections" in path:
                return [{"profile_id": 1, "collections_json": [{"id": "x"}]}]

        client._http = http
        client.login("test@example.invalid", "not-real")
        self.assertEqual(client.pull(1), [{"id": "x"}])
        client.push(1, [{"id": "x"}, collection_for("v2")])
        self.assertEqual(calls[-1][1]["p_collections_json"][0], {"id": "x"})
        client.refresh()
        self.assertEqual(calls[-1], ("/auth/v1/token?grant_type=refresh_token",
                                    {"refresh_token": "test-only-refresh"}, False))

    def test_static_addon_matches_versions_and_expected_films(self):
        from client import ROOT
        manifest = json.loads((ROOT / "addon/manifest.json").read_text("utf-8"))
        self.assertEqual(manifest["id"], ADDON_ID)
        self.assertEqual({c["id"] for c in manifest["catalogs"]}, {"a-v1", "a-v2"})
        for version, (imdb, _) in FILMS.items():
            data = json.loads((ROOT / f"addon/catalog/movie/a-{version}.json").read_text("utf-8"))
            self.assertEqual([m["id"] for m in data["metas"]], [imdb])
            self.assertEqual(collection_for(version)["folders"][0]["sources"][0]["catalogId"], f"a-{version}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
