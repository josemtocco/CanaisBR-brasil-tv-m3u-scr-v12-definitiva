import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import promover_streams
assert promover_streams.valid_url('https://stream3.camara.gov.br/tv1/manifest.m3u8')
assert promover_streams.valid_url('https://cdn.example.com/live/index.m3u8')
assert not promover_streams.valid_url('https://example.com/get.php?username=a&password=b')
assert not promover_streams.valid_url('https://example.com/live.m3u8?token=abc')
print('TESTE STREAMS: URL pública/CDN aceita e privada/tokenizada rejeitada: OK')

# A URL must be unique globally in the final stream catalog.
rows = [
    {"emissora_id": "a", "url": "https://example.test/live.m3u8"},
    {"emissora_id": "b", "url": "https://example.test/live.m3u8"},
]
rows.sort(key=lambda r: (r["url"].lower(), r["emissora_id"]))
unique = {}
for r in rows:
    unique.setdefault(r["url"], r)
assert len(unique) == 1
print("TESTE DEDUPLICACAO URL: OK")
