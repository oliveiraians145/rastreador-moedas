# AGENTS.md

## O que é este projeto
- `rastreador.py` — script CLI original (Python + `requests`). Consulta preços de bitcoin/ethereum/solana em BRL na API pública da CoinGecko, imprime no terminal, permite consultar uma moeda via `input()` e salva em `cotacoes.txt`.
- `app.py` — versão web mínima (Flask) com a mesma lógica, criada para funcionar no preview do Base44 (o preview só exibe páginas web, não terminal). Não altera o script original.

## Como rodar (Base44)
```
docker compose -f docker-compose.base44.yml up -d
```
- Serviço `web`: imagem `python:3.12-slim` com o código bind-mountado em `/app`; instala `flask` e `requests` no startup e roda `flask --app app run --debug` (live reload) na porta 3000.
- Nenhuma credencial é necessária: a API da CoinGecko é pública e gratuita. Se a API rate-limitar (HTTP 429), aguarde ~1 minuto.

## Verificação
- `curl -s http://localhost:3000/ | grep -i bitcoin` deve retornar o card do Bitcoin com preço em BRL.
- `docker compose -f docker-compose.base44.yml ps` deve mostrar o serviço `web` como healthy.
