import csv, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys_path=str(ROOT/'scripts')
import sys; sys.path.insert(0,sys_path)
import gerar_m3u
row={"emissora_id":"candidato-nao-catalogado","url":"https://example.test/live.m3u8","origem":"iptv_org_candidato","status":"validated","nome_stream":"Canal Teste","tvg_id":"CanalTeste.br@HD","tipo_stream":"universitaria"}
assert gerar_m3u.allowed(row)
print('TESTE CANDIDATO FORA DO CATALOGO: aceito para M3U quando validado: OK')
