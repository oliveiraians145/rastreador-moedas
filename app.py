import time

import requests
from flask import Flask, request

app = Flask(__name__)

MOEDAS = ["bitcoin", "ethereum", "solana"]
URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin,ethereum,solana&vs_currencies=brl&include_24hr_change=true"
)

# A API pública da CoinGecko limita requisições (erro 429),
# então o resultado é reutilizado por 60 segundos.
CACHE_TTL = 60
_cache = {"dados": None, "quando": 0}


def obter_cotacoes():
    dados, quando = _cache["dados"], _cache["quando"]
    if dados is not None and time.time() - quando < CACHE_TTL:
        return dados
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
    _cache["dados"] = response.json()
    _cache["quando"] = time.time()
    return _cache["dados"]


def formatar_brl(valor):
    return f"R$ {valor:,.2f}"


@app.route("/")
def index():
    moeda = request.args.get("moeda", "").strip().lower()

    try:
        data = obter_cotacoes()
    except Exception as e:
        if _cache["dados"] is not None:
            data = _cache["dados"]  # usa os últimos preços conhecidos
        else:
            return (
                f"<!DOCTYPE html><html lang='pt-BR'><body>"
                f"<h1>Ocorreu um erro ao consultar a API</h1><p>{e}</p>"
                f"<a href='/'>Tentar novamente</a></body></html>"
            ), 502

    cards = ""
    for m in MOEDAS:
        preco = formatar_brl(data[m]["brl"])
        variacao = data[m]["brl_24h_change"]
        cor = "#16a34a" if variacao >= 0 else "#dc2626"
        cards += f"""
        <div class="card">
          <h2>{m.capitalize()}</h2>
          <p class="preco">{preco}</p>
          <p class="variacao" style="color:{cor}">{variacao:+.2f}% em 24h</p>
        </div>"""

    resultado = ""
    if moeda:
        preco = data.get(moeda, {}).get("brl")
        if preco:
            resultado = (
                f"<p class='resultado ok'>O preço de {moeda} é: {formatar_brl(preco)}</p>"
            )
        else:
            resultado = "<p class='resultado erro'>Moeda não encontrada</p>"

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rastreador de Cotações</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: system-ui, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      margin: 0;
      padding: 2rem 1rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1.5rem;
    }}
    h1 {{ margin: 0; font-size: 1.6rem; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1rem;
      width: 100%;
      max-width: 820px;
    }}
    .card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 1.2rem 1.5rem;
      text-align: center;
    }}
    .card h2 {{ margin: 0 0 .5rem; font-size: 1.1rem; text-transform: capitalize; }}
    .preco {{ margin: 0; font-size: 1.5rem; font-weight: 700; }}
    .variacao {{ margin: .4rem 0 0; font-size: .95rem; }}
    form {{ display: flex; gap: .5rem; }}
    input {{
      padding: .55rem .8rem;
      border-radius: 8px;
      border: 1px solid #334155;
      background: #1e293b;
      color: inherit;
    }}
    button {{
      padding: .55rem 1.1rem;
      border: none;
      border-radius: 8px;
      background: #2563eb;
      color: white;
      font-weight: 600;
      cursor: pointer;
    }}
    .resultado {{ margin: 0; font-size: 1.05rem; }}
    .ok {{ color: #38bdf8; }}
    .erro {{ color: #f87171; }}
    footer {{ color: #64748b; font-size: .85rem; }}
  </style>
</head>
<body>
  <h1>📊 Rastreador de Cotações</h1>
  <form method="get" action="/">
    <input type="text" name="moeda" placeholder="bitcoin, ethereum ou solana"
           value="{moeda}" required>
    <button type="submit">Consultar</button>
  </form>
  {resultado}
  <div class="grid">{cards}</div>
  <footer>Fonte: CoinGecko · Valores em BRL · <a href="/" style="color:#94a3b8">Atualizar</a></footer>
</body>
</html>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
