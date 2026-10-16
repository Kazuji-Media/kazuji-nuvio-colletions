"""Run with: python prototypes/collections-api/serve.py (stdlib only)."""

import argparse
import hmac
import json
import secrets
import threading
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from client import COLLECTION_ID, ROOT, NuvioClient, PrototypeError, Publisher


def main():
    parser = argparse.ArgumentParser(description="Protótipo local de collections Nuvio via API")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    origin = f"http://127.0.0.1:{args.port}"
    csrf = secrets.token_urlsafe(32)
    session_cookie = secrets.token_urlsafe(32)
    lock = threading.Lock()
    client = NuvioClient()
    publisher = Publisher(client, ROOT / ".private")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # Do not log request data, credentials or addon URLs.

        def send(self, status, body, content_type="application/json; charset=utf-8", cookie=False):
            data = body.encode() if isinstance(body, str) else json.dumps(body, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; form-action 'self'")
            if cookie:
                self.send_header("Set-Cookie", f"prototype_session={session_cookie}; HttpOnly; SameSite=Strict; Path=/")
            self.end_headers()
            self.wfile.write(data)

        def host_valid(self):
            return self.headers.get("Host") == f"127.0.0.1:{args.port}"

        def do_GET(self):
            if not self.host_valid():
                return self.send(403, {"error": "Host inválido."})
            if self.path == "/":
                page = (ROOT / "index.html").read_text("utf-8").replace("__CSRF_TOKEN__", csrf)
                return self.send(200, page, "text/html; charset=utf-8")
            return self.send(404, {"error": "Rota inexistente."})

        def do_POST(self):
            if (not self.host_valid() or self.headers.get("Origin") != origin
                    or not hmac.compare_digest(self.headers.get("X-Prototype-CSRF", ""), csrf)):
                return self.send(403, {"error": "Abra o protótipo pelo endereço local informado."})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 16384:
                    return self.send(400, {"error": "Requisição inválida."})
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise PrototypeError("Corpo da requisição inválido.")
                with lock:
                    if self.path == "/api/login":
                        email, password = body.get("email"), body.get("password")
                        if not isinstance(email, str) or not isinstance(password, str) or not email or not password:
                            raise PrototypeError("Informe email e senha Nuvio.")
                        client.login(email, password)
                        return self.send(200, {"authenticated": True}, cookie=True)
                    cookies = self.headers.get("Cookie", "").split("; ")
                    if f"prototype_session={session_cookie}" not in cookies:
                        return self.send(401, {"error": "Entre na conta para continuar."})
                    if self.path == "/api/profiles":
                        profiles = []
                        for item in client.profiles():
                            locked = bool(item.get("pin_enabled"))
                            collections = [] if locked else client.pull(item["profile_index"])
                            profiles.append({"index": item["profile_index"], "name": item["name"],
                                             "locked": locked, "collections": None if locked else len(collections),
                                             "titles": [c.get("title", "") for c in collections],
                                             "usesPrimaryAddons": bool(item.get("uses_primary_addons"))})
                        return self.send(200, {"profiles": profiles})
                    profile = body.get("profile", 1)
                    if type(profile) is not int or profile not in range(1, 7):
                        raise PrototypeError("Perfil inválido; use 1 a 6.")
                    if self.path == "/api/state":
                        info = publisher.profile_info(profile)
                        collections = client.pull(profile)
                        managed = next((c for c in collections if c.get("id") == COLLECTION_ID), None)
                        return self.send(200, {"profile": profile, "profileName": info["name"], "collections": len(collections),
                                               "collectionA": managed, "collectionId": COLLECTION_ID})
                    if self.path == "/api/preview":
                        return self.send(200, publisher.preview(profile, body.get("version")))
                    if self.path == "/api/apply":
                        expected = body.get("expectedFingerprint")
                        if not isinstance(expected, str) or len(expected) != 64:
                            raise PrototypeError("Gere a prévia antes de aplicar.")
                        return self.send(200, publisher.apply(profile, body.get("version"), expected))
                    return self.send(404, {"error": "Rota inexistente."})
            except PrototypeError as error:
                return self.send(400, {"error": str(error)})
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                return self.send(502, {"error": "Falha de comunicação. A escrita pode ter ocorrido; releia o estado antes de repetir."})
            except (ValueError, KeyError, TypeError):
                return self.send(400, {"error": "Dados inesperados; nenhuma tentativa automática de escrita foi feita."})
            except Exception:
                return self.send(500, {"error": "Falha local. Releia o estado antes de repetir a ação."})

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Protótipo local: {origin}", flush=True)
    print("Sessão somente em memória. Backups locais em prototypes/collections-api/.private/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
