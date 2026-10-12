# AGENTS.md

## O que é este projeto
- `rastreador.py` — script CLI (Python + `requests`). Mostra bitcoin/ethereum/solana em BRL e consulta **qualquer** moeda da CoinGecko pelo nome ou símbolo (ex.: `cardano`, `doge`, `xrp`), usando `/search` para achar a moeda e `/simple/price` para o preço em BRL + variação de 24h. Grava cada cotação em `cotacoes.txt` (arquivo gerado, não versionar).
- `preview.py` — **só para o preview do Base44**. O preview exibe páginas web, não terminal, então este arquivo serve na porta 3000 a mesma saída do rastreador em texto puro (`/?moeda=cardano`). Usa só a biblioteca padrão, redireciona a escrita de `cotacoes.txt` para `/tmp` e reaproveita os resultados (consulta por 60s, moedas populares por 120s).

## Como rodar (Base44)
```
docker compose -f docker-compose.base44.yml up -d
```
- Serviço `web`: imagem `python:3.12-slim`, código bind-mountado em `/app`, instala `requests` no startup e roda `python preview.py` na porta 3000 (sem live reload: após editar código use `docker compose -f docker-compose.base44.yml restart web`).
- Para rodar o script de terminal dentro do container:
```
docker compose -f docker-compose.base44.yml exec -T web sh -c "printf 'cardano\nsair\n' | python rastreador.py"
```

## Observações
- Nenhuma credencial é necessária: a API da CoinGecko é pública. Ela limita requisições (HTTP 429) — daí o cache de 60s no preview; no terminal, aguarde um minuto se aparecer 429.
- `cotacoes.txt` é saída de execução: apague antes de commitar se aparecer.

## Verificação
- `curl -s http://localhost:3000/` deve mostrar as três moedas em BRL.
- `curl -s "http://localhost:3000/?moeda=cardano"` deve mostrar `Cardano (ADA): R$ ...`.
- `docker compose -f docker-compose.base44.yml ps` deve mostrar `web` como healthy.
