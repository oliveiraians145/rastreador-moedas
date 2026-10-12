"""Somente para o preview do Base44.

O app é o terminal (rastreador.py). Como o preview do Base44 exibe apenas
páginas web, este arquivo mostra, na porta 3000, a mesma saída do rastreador
em texto puro. Para consultar qualquer moeda: /?moeda=cardano
"""

import contextlib
import io
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import rastreador

PORTA = 3000
# A API pública da CoinGecko limita requisições (HTTP 429), então o preview
# reaproveita os resultados: moeda consultada por 60s, moedas populares por 120s.
CACHE_TERMO = 60
CACHE_POPULARES = 120

# O preview não deve escrever no cotacoes.txt do projeto.
rastreador.ARQUIVO = "/tmp/cotacoes-preview.txt"

_populares = {"texto": "", "quando": 0.0}
_termos = {}


def populares_texto():
    """Bloco das moedas populares, reaproveitado entre consultas."""
    agora = time.time()
    if _populares["texto"] and agora - _populares["quando"] < CACHE_POPULARES:
        return _populares["texto"]

    _populares["texto"] = capturar(rastreador.mostrar_populares)
    _populares["quando"] = agora
    return _populares["texto"]


def capturar(funcao):
    """Roda a função do rastreador e devolve o que ela imprimiria."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        try:
            funcao()
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
    linhas = [linha for linha in buffer.getvalue().splitlines() if "Cotação salva" not in linha]

    return "\n".join(linhas).strip() + "\n"


def renderizar(termo=""):
    """Saída do rastreador em texto para o preview."""
    partes = [populares_texto()]
    if termo:
        agora = time.time()
        guardado = _termos.get(termo)
        if not guardado or agora - guardado[0] >= CACHE_TERMO:
            guardado = (agora, capturar(lambda: rastreador.consultar(termo)))
            _termos[termo] = guardado
        partes.append("\n" + guardado[1])

    return "\n".join(partes) + "\n(para consultar outra moeda: /?moeda=cardano)\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        termo = parse_qs(urlparse(self.path).query).get("moeda", [""])[0].strip()
        corpo = renderizar(termo).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    populares_texto()  # aquece o cache antes do primeiro acesso
    ThreadingHTTPServer(("0.0.0.0", PORTA), Handler).serve_forever()
