#!/usr/bin/env python3
"""Valida e promove streams da v10 + candidatos IPTV-org acumulados.

A descoberta automática continua existindo. O arquivo data/iptv-org-candidatos.csv
é a fonte-semente enviada pelo usuário e também recebe candidatos novos a cada ciclo.
Nenhum domínio de CDN é descartado apenas por não ser o domínio da emissora: o
critério final é a URL pública responder como playlist HLS/M3U.
"""
from __future__ import annotations
import csv, re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "output"
STREAMS = DATA / "streams.csv"
CANDIDATES = DATA / "iptv-org-candidatos.csv"
REPORT = OUT / "streams-diagnostico.csv"
FORBIDDEN = ("xtream", "get.php", "player_api", "username=", "password=", "token=")
FIELDS = ["emissora_id","url","origem","status","observacao","nome_stream","tvg_id","tipo_stream","estado_stream","cidade_stream"]

def clean(v): return (v or "").strip()

def read_rows(path):
    if not path.exists(): return []
    with open(path, encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))

def test_stream(url):
    try:
        req = Request(url, headers={"User-Agent":"brasil-tv-m3u/12.0", "Accept":"application/vnd.apple.mpegurl,application/x-mpegURL,*/*"})
        with urlopen(req, timeout=15) as r:
            code = getattr(r, "status", 200)
            data = r.read(16384)
            ctype = (r.headers.get("Content-Type") or "").lower()
        text = data.decode("utf-8", "ignore")
        # HLS can be served without a useful content-type. Require actual M3U content
        # or a recognized MPEG playlist content-type.
        ok = code in (200, 206) and ("#EXTM3U" in text or "#EXTINF" in text or "mpegurl" in ctype or "vnd.apple.mpegurl" in ctype)
        return ok, f"HTTP {code}; {ctype or 'sem-content-type'}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

def valid_url(url):
    u=clean(url).lower()
    return u.startswith(("http://","https://")) and not any(x in u for x in FORBIDDEN)

def candidate_record(r):
    return {
        "emissora_id": clean(r.get("emissora_id")), "url": clean(r.get("url")),
        "origem": "iptv_org_candidato", "status": "validated",
        "observacao": f"Candidato IPTV-org; score={clean(r.get('score'))}; host={urlparse(clean(r.get('url'))).netloc.lower()}",
        "nome_stream": clean(r.get("nome_iptv_org")), "tvg_id": clean(r.get("tvg_id")),
        "tipo_stream": clean(r.get("tipo")), "estado_stream": clean(r.get("estado")), "cidade_stream": clean(r.get("cidade")),
    }

def main():
    channels = {clean(r.get("id")): r for r in read_rows(DATA/"emissoras.csv") if clean(r.get("id"))}
    existing = read_rows(STREAMS)
    candidates = read_rows(CANDIDATES)
    kept = {}
    report=[]

    # Existing v10 streams remain first-class and are revalidated.
    for r in existing:
        url=clean(r.get("url")); cid=clean(r.get("emissora_id"))
        if not cid or not valid_url(url): continue
        ok,detail=test_stream(url)
        c=channels.get(cid,{})
        report.append([cid, clean(c.get("Emissora")), clean(c.get("Estado")), clean(c.get("Cidade")), "existente", urlparse(url).netloc.lower(), url, "ATIVO" if ok else "INATIVO", detail])
        if ok:
            rr={f:r.get(f,"") for f in FIELDS}
            rr["status"]="validated"
            kept[url.lower()] = rr

    # Final source: the accumulated candidate file, including the seed uploaded by user
    # and candidates found automatically in this same workflow.
    for r in candidates:
        url=clean(r.get("url")); cid=clean(r.get("emissora_id"))
        if not cid or not valid_url(url):
            continue
        # The supplied file contains candidate scores 82/88. We intentionally do not
        # reject score 82 here: the user explicitly asked to use its playlists; activity
        # of the actual URL is the gate for publication.
        ok,detail=test_stream(url)
        channel = channels.get(cid, {})
        name=clean(r.get("nome_iptv_org")) or clean(channel.get("Emissora")) or cid
        report.append([cid, name, clean(r.get("estado")), clean(r.get("cidade")), clean(r.get("score")), urlparse(url).netloc.lower(), url, "ATIVO" if ok else "INATIVO", detail])
        if ok and url.lower() not in kept:
            kept[url.lower()] = candidate_record(r)

    final=list(kept.values())
    final.sort(key=lambda r:(clean(r.get("nome_stream")) or clean(r.get("emissora_id")), clean(r.get("url")).lower()))
    with open(STREAMS,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(final)
    OUT.mkdir(exist_ok=True)
    with open(REPORT,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["emissora_id","emissora","estado","cidade","score","host","url","resultado","detalhe"]); w.writerows(report)
    print(f"Candidatos acumulados analisados: {len(candidates)}")
    print(f"Streams ativos/validados: {len(final)}")
    print(f"Diagnóstico: {REPORT}")

if __name__=="__main__": main()
