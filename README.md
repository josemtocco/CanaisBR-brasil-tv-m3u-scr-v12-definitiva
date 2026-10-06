# Brasil TV M3U — v12 definitiva

Projeto GitHub para manter um catálogo nacional de emissoras brasileiras e gerar playlists M3U compatíveis com SS IPTV.

## Base preservada da v10

A v12 preserva a estrutura da v10: SCR/MCom, Map TVU, catálogo nacional, descoberta automática de candidatos IPTV-org, validação de streams, deduplicação, geração M3U e atualização automática a cada 6 horas.

## Nova regra de streams

O arquivo `data/iptv-org-candidatos.csv` fornecido como resultado da v10 é mantido como **fonte-semente**. Ele contém os candidatos já descobertos, incluindo as URLs de playlist.

Em cada execução:

1. o projeto atualiza o catálogo SCR/Map TVU;
2. faz novamente a descoberta automática no IPTV-org;
3. incorpora os novos candidatos ao arquivo-semente, sem apagar os anteriores;
4. valida as URLs do arquivo acumulado;
5. revalida os streams que já estavam funcionando;
6. elimina URLs inativas, inválidas, privadas ou tokenizadas;
7. deduplica globalmente as URLs;
8. gera `output/brasil-tv.m3u` e playlists por categoria.

Assim, **a v10 não perde o que já encontrou**, mas a v12 continua procurando canais novos nas execuções futuras.

## Arquivos principais

- `data/emissoras.csv` — cadastro nacional.
- `data/iptv-org-candidatos.csv` — candidatos acumulados, com as URLs encontradas.
- `data/streams.csv` — somente streams validados.
- `output/brasil-tv.m3u` — playlist principal.
- `output/streams-diagnostico.csv` — resultado da validação de cada candidato.
- `output/m3u-diagnostico.txt` — resumo da geração.

## Atualização

GitHub Actions executa a rotina a cada 6 horas e também permite execução manual.
