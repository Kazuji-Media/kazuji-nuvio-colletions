"""Throwaway prototype: authenticated Nuvio collections API, with scoped merges."""

import copy
import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COLLECTION_ID = "kazuji-prototype-collection-a"
ADDON_ID = "org.kazuji.prototype.collection.a"
MANIFEST_URL = (
    "https://raw.githubusercontent.com/Kazuji-Media/kazuji-nuvio-colletions/"
    "refs/heads/prototype/collections-api/prototypes/collections-api/addon/manifest.json"
)
PUBLISHABLE_KEY = "sb_publishable_1Clq8rlTVACkdcZuqr6_AD__xUUC_EN"
FILMS = {"v1": ("tt0363547", "Madrugada dos Mortos (2004)"),
         "v2": ("tt0110357", "O Rei Leão (1994)")}


class PrototypeError(Exception):
    pass


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def collection_for(version):
    if version not in FILMS:
        raise PrototypeError("Versão inválida; escolha v1 ou v2.")
    collection = json.loads((ROOT / "versions" / f"a-{version}.json").read_text("utf-8"))
    if collection.get("id") != COLLECTION_ID:
        raise PrototypeError("O arquivo não corresponde à coleção A deste protótipo.")
    return collection


def merge_collection(current, target):
    """Replace one managed ID in place, preserving every other raw object and order."""
    if not isinstance(current, list) or any(not isinstance(c, dict) for c in current):
        raise PrototypeError("Resposta de coleções inválida; nenhuma gravação realizada.")
    if target.get("id") != COLLECTION_ID:
        raise PrototypeError("Este protótipo só administra a coleção A.")
    identifiers = [c.get("id") for c in current]
    if any(not isinstance(i, str) or not i for i in identifiers) or len(set(identifiers)) != len(identifiers):
        raise PrototypeError("IDs de coleções ausentes ou repetidos; operação interrompida.")
    merged = copy.deepcopy(current)
    matches = [i for i, c in enumerate(current) if c["id"] == COLLECTION_ID]
    if matches:
        # Preserve unknown fields on A, too, while changing its managed definition.
        merged[matches[0]].update(copy.deepcopy(target))
    else:
        merged.append(copy.deepcopy(target))
    return merged


def addon_payload(rows):
    """Use the public API contract; never print these URLs (others can contain secrets)."""
    if not isinstance(rows, list):
        raise PrototypeError("Resposta de addons inválida.")
    required = ("url", "name", "enabled", "sort_order")
    if any(not isinstance(row, dict) or any(k not in row for k in required) for row in rows):
        raise PrototypeError("Addon sem campos esperados; nenhuma substituição realizada.")
    payload = [{key: copy.deepcopy(row[key]) for key in required} for row in rows]
    if len({row["url"] for row in payload}) != len(payload):
        raise PrototypeError("URLs de addons repetidas; operação interrompida.")
    return payload


class NuvioClient:
    def __init__(self, base="https://api.nuvio.tv"):
        self.base = base
        self.access_token = None
        self.refresh_token = None
        self.expires_at = 0

    def _http(self, path, body=None, authenticated=True, method=None):
        headers = {"apikey": PUBLISHABLE_KEY, "Content-Type": "application/json"}
        if authenticated:
            headers["Authorization"] = f"Bearer {self.access_token}"
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(self.base + path, data=data, headers=headers,
                                         method=method or ("POST" if body is not None else "GET"))
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            return json.loads(raw) if raw else None

    def _set_session(self, session):
        if not isinstance(session, dict) or not session.get("access_token") or not session.get("refresh_token"):
            raise PrototypeError("O login não retornou uma sessão válida.")
        self.access_token = session["access_token"]
        self.refresh_token = session["refresh_token"]
        self.expires_at = time.time() + session.get("expires_in", 3600)

    def login(self, email, password):
        try:
            self._set_session(self._http("/auth/v1/token?grant_type=password",
                                         {"email": email, "password": password}, False))
        except urllib.error.HTTPError as error:
            raise PrototypeError(f"Login recusado pelo Nuvio (HTTP {error.code}).") from None

    def refresh(self):
        if not self.refresh_token:
            raise PrototypeError("Entre na conta Nuvio para continuar.")
        self._set_session(self._http("/auth/v1/token?grant_type=refresh_token",
                                     {"refresh_token": self.refresh_token}, False))

    def request(self, path, body=None, method=None):
        if not self.access_token:
            raise PrototypeError("Entre na conta Nuvio para continuar.")
        try:
            if time.time() >= self.expires_at - 30:
                self.refresh()
            try:
                return self._http(path, body, method=method)
            except urllib.error.HTTPError as error:
                if error.code != 401:
                    raise
                self.refresh()
                return self._http(path, body, method=method)
        except urllib.error.HTTPError as error:
            # No bodies, URLs, session tokens or account details in UI/logs.
            raise PrototypeError(f"A API Nuvio respondeu HTTP {error.code}. Releia o estado antes de tentar novamente.") from None

    def pull(self, profile):
        rows = self.request("/rest/v1/rpc/sync_pull_collections", {"p_profile_id": profile})
        if rows == []:
            return []
        if not isinstance(rows, list) or len(rows) != 1 or rows[0].get("profile_id") != profile:
            raise PrototypeError("Resposta inesperada para o perfil selecionado.")
        value = rows[0].get("collections_json")
        if not isinstance(value, list):
            raise PrototypeError("collections_json não é um array; operação interrompida.")
        return value

    def push(self, profile, collections):
        self.request("/rest/v1/rpc/sync_push_collections",
                     {"p_profile_id": profile, "p_collections_json": collections})

    def addons(self, profile):
        return self.request(f"/rest/v1/addons?select=*&profile_id=eq.{profile}&order=sort_order")

    def push_addons(self, profile, addons):
        self.request("/rest/v1/rpc/sync_push_addons", {"p_profile_id": profile, "p_addons": addons})

    def profiles(self):
        rows = self.request("/rest/v1/rpc/sync_pull_profiles", method="POST")
        if not isinstance(rows, list) or any(not isinstance(p, dict) or p.get("profile_index") not in range(1, 7) for p in rows):
            raise PrototypeError("Resposta de perfis inválida.")
        return rows


class Publisher:
    def __init__(self, client, private_dir):
        self.client = client
        self.private_dir = Path(private_dir)

    def profile_info(self, profile):
        matches = [p for p in self.client.profiles() if p["profile_index"] == profile]
        if len(matches) != 1:
            raise PrototypeError("Selecione um perfil existente na conta.")
        if matches[0].get("pin_enabled"):
            raise PrototypeError("Perfil protegido por PIN. Use o fluxo normal do Nuvio para esse perfil.")
        return matches[0]

    def preview(self, profile, version):
        info = self.profile_info(profile)
        before = self.client.pull(profile)
        target = collection_for(version)
        after = merge_collection(before, target)
        current = next((c for c in before if c.get("id") == COLLECTION_ID), None)
        return {"profile": profile, "profileName": info["name"], "version": version, "film": FILMS[version][1],
                "collectionId": COLLECTION_ID, "currentTitle": current.get("title") if current else None,
                "targetTitle": target["title"], "collectionsBefore": len(before),
                "collectionsAfter": len(after), "otherCollectionsPreserved": len(before) - bool(current),
                "changed": before != after, "expectedFingerprint": fingerprint(before)}

    def preflight_catalog(self, version):
        base = MANIFEST_URL.removesuffix("manifest.json")
        def public_json(url):
            with urllib.request.urlopen(url, timeout=30) as response:
                return json.load(response)
        manifest = public_json(MANIFEST_URL)
        catalog = public_json(base + f"catalog/movie/a-{version}.json")
        if manifest.get("id") != ADDON_ID or [m.get("id") for m in catalog.get("metas", [])] != [FILMS[version][0]]:
            raise PrototypeError("O catálogo público não corresponde à versão solicitada.")

    def apply(self, profile, version, expected_fingerprint):
        info = self.profile_info(profile)
        addon_profile = 1 if info.get("uses_primary_addons") else profile
        target = collection_for(version)
        self.preflight_catalog(version)
        before = self.client.pull(profile)
        if fingerprint(before) != expected_fingerprint:
            raise PrototypeError("As coleções mudaram desde a prévia. Gere uma nova prévia.")
        after = merge_collection(before, target)
        addon_rows = self.client.addons(addon_profile)
        addons_before = addon_payload(addon_rows)
        addons_after = copy.deepcopy(addons_before)
        existing = next((a for a in addons_after if a["url"] == MANIFEST_URL), None)
        if existing is None:
            addons_after.append({"url": MANIFEST_URL, "name": "Kazuji · Protótipo A",
                                 "enabled": True,
                                 "sort_order": max((a["sort_order"] for a in addons_after), default=-1) + 1})
        else:
            existing["enabled"] = True
        self.private_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        backup = self.private_dir / f"before-profile-{profile}-{version}-{stamp}.json"
        backup.write_text(json.dumps({"profile": profile, "addonProfile": addon_profile, "collections": before,
                                     "addons": addon_rows}, ensure_ascii=False, indent=2), "utf-8")
        if addons_before != addons_after:
            if addon_payload(self.client.addons(addon_profile)) != addons_before:
                raise PrototypeError("Os addons mudaram durante a operação. Gere uma nova prévia.")
            self.client.push_addons(addon_profile, addons_after)
            actual_addons = addon_payload(self.client.addons(addon_profile))
            if actual_addons != addons_after:
                raise PrototypeError("Não foi possível confirmar os addons; a coleção não foi gravada.")
        if self.client.pull(profile) != before:
            raise PrototypeError("As coleções mudaram durante a operação. Gere uma nova prévia.")
        if after != before:
            self.client.push(profile, after)
        actual = self.client.pull(profile)
        if actual != after:
            raise PrototypeError("A releitura divergiu do esperado. Consulte o backup local; não houve nova tentativa de escrita.")
        result = {"profile": profile, "version": version, "title": target["title"],
                  "film": FILMS[version][1], "collectionId": COLLECTION_ID,
                  "collections": len(actual), "otherCollectionsPreserved": len(before) - int(any(c["id"] == COLLECTION_ID for c in before)),
                  "verified": True, "backup": backup.name,
                  "beforeFingerprint": fingerprint(before), "afterFingerprint": fingerprint(actual)}
        (self.private_dir / f"result-{stamp}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), "utf-8")
        return result
