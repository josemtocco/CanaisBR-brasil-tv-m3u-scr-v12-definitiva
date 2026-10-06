import csv,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; OUT=ROOT/'output'
seed=list(csv.DictReader(open(DATA/'iptv-org-candidatos.csv',encoding='utf-8-sig')))
assert len(seed)==215, len(seed)
assert len({r['url'].strip().lower() for r in seed})==129
assert all(r['url'].startswith(('http://','https://')) for r in seed)
assert all(r['tvg_id'] for r in seed)
print('TESTE CANDIDATOS IPTV-ORG: 215 registros / 129 URLs únicas: OK')
