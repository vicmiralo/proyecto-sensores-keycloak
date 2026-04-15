from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse

KEYCLOAK_TOKEN_URL = "http://keycloak-server:8080/auth/realms/SensoresRealm/protocol/openid-connect/token"

class TokenProxy(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        print(f"[TOKEN-PROXY] Body recibido: {body}")

        # Parsear parámetros del body
        params = urllib.parse.parse_qs(body, keep_blank_values=True)

        # Eliminar scope vacío o 'default' (WSO2 lo envía, Keycloak no lo reconoce)
        if 'scope' in params and params['scope'][0] in ('', 'default'):
            scope_val = params['scope'][0]
            del params['scope']
            print(f"[TOKEN-PROXY] scope='{scope_val}' eliminado")

        fixed_body = urllib.parse.urlencode({k: v[0] for k, v in params.items()})
        print(f"[TOKEN-PROXY] Body corregido: {fixed_body}")

        # Construir headers para reenviar a Keycloak
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        # Reenviar Authorization (Basic Auth) si WSO2 la incluye
        auth_header = self.headers.get('Authorization')
        if auth_header:
            headers['Authorization'] = auth_header
            print(f"[TOKEN-PROXY] Authorization header reenviado")

        # Reenviar a Keycloak
        req = urllib.request.Request(
            KEYCLOAK_TOKEN_URL,
            data=fixed_body.encode('utf-8'),
            headers=headers
        )

        try:
            with urllib.request.urlopen(req) as response:
                resp_body = response.read()
                print(f"[TOKEN-PROXY] Keycloak respondio: {response.status}")
                self.send_response(response.status)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            resp_body = e.read()
            print(f"[TOKEN-PROXY] Keycloak error: {e.code} - {resp_body.decode()}")
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(resp_body)

    def log_message(self, format, *args):
        print(f"[TOKEN-PROXY] {format % args}")

if __name__ == '__main__':
    print("[TOKEN-PROXY] Escuchando en puerto 9090...")
    server = HTTPServer(('0.0.0.0', 9090), TokenProxy)
    server.serve_forever()
