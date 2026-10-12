"""Rastreador de cotações usando a API pública da CoinGecko (valores em BRL).

Além das moedas populares mostradas no início, permite consultar qualquer
moeda cadastrada na CoinGecko pelo nome ou pelo símbolo (ex.: cardano, doge, xrp).
"""

import time

import requests

API = "https://api.coingecko.com/api/v3"
POPULARES = ["bitcoin", "ethereum", "solana"]
ARQUIVO = "cotacoes.txt"


def pedir(caminho, params):
    """GET na API, repetindo uma vez quando a CoinGecko limita (HTTP 429)."""
    resposta = requests.get(f"{API}{caminho}", params=params, timeout=10)
    if resposta.status_code == 429:
        time.sleep(float(resposta.headers.get("Retry-After", 5)))
        resposta = requests.get(f"{API}{caminho}", params=params, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


def buscar_moeda(termo):
    """Acha qualquer moeda da CoinGecko pelo nome ou símbolo."""
    moedas = pedir("/search", {"query": termo}).get("coins", [])
    iguais = [
        moeda
        for moeda in moedas
        if termo.lower() in (moeda["id"], moeda["symbol"].lower(), moeda["name"].lower())
    ]
    return (iguais or moedas or [None])[0]


def obter_cotacoes(ids):
    """Preço em BRL e variação de 24h para os ids informados."""
    return pedir(
        "/simple/price",
        {"ids": ",".join(ids), "vs_currencies": "brl", "include_24hr_change": "true"},
    )


def formatar(nome, dados):
    variacao = dados.get("brl_24h_change") or 0.0
    return f"{nome}: R$ {dados['brl']:,.2f}  ({variacao:+.2f}% em 24h)"


def salvar(texto):
    with open(ARQUIVO, "a", encoding="utf-8") as arquivo:
        arquivo.write(texto + "\n")


def mostrar_populares():
    dados = obter_cotacoes(POPULARES)
    print()
    for moeda in POPULARES:
        texto = formatar(moeda.capitalize(), dados[moeda])
        print(texto)
        salvar(texto)


def consultar(termo):
    moeda = buscar_moeda(termo)
    if moeda is None:
        print(f"\nMoeda '{termo}' não encontrada")
        return
    dados = obter_cotacoes([moeda["id"]]).get(moeda["id"], {})
    if dados.get("brl") is None:
        print(f"\nSem cotação em BRL para {moeda['name']}")
        return
    texto = formatar(f"{moeda['name']} ({moeda['symbol'].upper()})", dados)
    print(f"\n{texto}")
    salvar(texto)
    print(f"Cotação salva em {ARQUIVO}")


def main():
    print("Tentando conectar à API...")
    try:
        mostrar_populares()
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    while True:
        termo = input("\nQual moeda você quer consultar? (nome ou símbolo, ou 'sair'): ").strip()
        if termo.lower() in ("sair", "exit", "q"):
            break
        if not termo:
            continue
        try:
            consultar(termo)
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                print("\nA API da CoinGecko limitou as consultas (429). Aguarde ~1 minuto.")
            else:
                print(f"Ocorreu um erro: {e}")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")


if __name__ == "__main__":
    main()
