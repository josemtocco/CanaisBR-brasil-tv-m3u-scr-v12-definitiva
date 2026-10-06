#!/usr/bin/env python3
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; OUT=ROOT/'output'

def rows(path):
    if not path.exists(): return []
    with open(path,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def clean(v):return (v or '').strip()
def esc(v):return clean(v).replace('"',"'")
def allowed(s):
    u=clean(s.get('url')).lower(); st=clean(s.get('status'))
    return u.startswith(('http://','https://')) and not any(x in u for x in ('xtream','get.php','player_api','username=','password=','token=')) and st in {'active','validated'}

def main():
    OUT.mkdir(exist_ok=True)
    channels={x['id']:x for x in rows(DATA/'emissoras.csv') if clean(x.get('id'))}
    streams=[s for s in rows(DATA/'streams.csv') if allowed(s)]
    entries=[]; rejected=0
    for s in streams:
        c=channels.get(clean(s.get('emissora_id')), {})
        # Candidatos do arquivo da v10 podem ter sido associados a registros que
        # mudaram/foram consolidados no catálogo SCR. Eles continuam válidos se o
        # próprio candidato trouxe nome/tvg-id e o stream foi validado.
        if not c and clean(s.get('origem')) != 'iptv_org_candidato':
            rejected+=1; continue
        name=clean(s.get('nome_stream')) or clean(c.get('Emissora')) or clean(s.get('emissora_id'))
        tvgid=clean(s.get('tvg_id')) or clean(c.get('tvg-id')) or clean(c.get('id')) or clean(s.get('emissora_id'))
        group=clean(s.get('tipo_stream')) or clean(c.get('Tipo')) or 'tv'
        group=group.replace('_',' ').title()
        attrs=[f'tvg-name="{esc(name)}"',f'tvg-id="{esc(tvgid)}"',f'group-title="{esc(group)}"']
        logo=clean(c.get('Logo'))
        if logo: attrs.append(f'tvg-logo="{esc(logo)}"')
        entries.append(f'#EXTINF:-1 {" ".join(attrs)},{name}\n{clean(s["url"])}')
    entries.sort(key=str.lower)
    (OUT/'brasil-tv.m3u').write_text('#EXTM3U\n'+('\n'.join(entries)+'\n' if entries else ''),encoding='utf-8')
    predicates=[('universitarios',lambda c:c.get('Tipo')=='universitaria'),('legislativos',lambda c:'legisl' in c.get('Tipo','')),('publicos',lambda c:c.get('Tipo') in {'publica','institucional','governamental'})]
    for suf,pred in predicates:
        selected=[]
        for e in entries:
            # category is already encoded in group-title; use matching catalog IDs for official streams
            if any(f'tvg-id="{i}"' in e for i in {c['id'] for c in channels.values() if pred(c)}): selected.append(e)
        (OUT/f'brasil-tv-{suf}.m3u').write_text('#EXTM3U\n'+('\n'.join(selected)+'\n' if selected else ''),encoding='utf-8')
    diag=OUT/'m3u-diagnostico.txt'
    diag.write_text(f'Emissoras no catálogo: {len(channels)}\nStreams no CSV: {len(rows(DATA/"streams.csv"))}\nStreams aprovados para M3U: {len(streams)}\nEntradas geradas: {len(entries)}\nStreams sem emissora correspondente: {rejected}\nCandidatos IPTV-org acumulados: {len(rows(DATA/"iptv-org-candidatos.csv"))}\nArquivo principal: {OUT/"brasil-tv.m3u"}\n',encoding='utf-8')
    print(diag.read_text())
if __name__=='__main__':main()
