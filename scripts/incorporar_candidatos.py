#!/usr/bin/env python3
"""Incorpora candidatos novos do IPTV-org ao arquivo-semente da v10.

A lista enviada pelo usuário em data/iptv-org-candidatos.csv é preservada como
fonte-semente. Cada execução busca novamente a playlist brasileira do IPTV-org,
adiciona novos candidatos e nunca remove candidatos anteriores.
"""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
AUTO = ROOT / "output" / "iptv-org-candidatos-auto.csv"
SEED = DATA / "iptv-org-candidatos.csv"
FIELDS = ["emissora_id","emissora","estado","cidade","tipo","score","nome_iptv_org","tvg_id","host","url"]

def read(path):
    if not path.exists(): return []
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]

def key(r):
    return ((r.get("url") or "").strip().lower(), (r.get("tvg_id") or "").strip().lower(), (r.get("nome_iptv_org") or "").strip().lower())

def score(r):
    try: return int(r.get("score") or 0)
    except ValueError: return 0

def main():
    seed = read(SEED)
    fresh = read(AUTO)
    merged = {}
    for r in seed + fresh:
        if not r.get("url"): continue
        k = key(r)
        old = merged.get(k)
        if old is None or score(r) > score(old): merged[k] = {f: r.get(f, "") for f in FIELDS}
    rows = sorted(merged.values(), key=lambda r: ((r.get("nome_iptv_org") or "").lower(), (r.get("url") or "").lower(), (r.get("emissora_id") or "")))
    DATA.mkdir(exist_ok=True)
    with open(SEED, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    print(f"Candidatos preservados: {len(seed)}")
    print(f"Candidatos novos: {len(fresh)}")
    print(f"Candidatos acumulados: {len(rows)}")

if __name__ == "__main__": main()
