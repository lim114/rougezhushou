"""Locate community mechanic notes and asset references; keep source provenance."""
from html.parser import HTMLParser
from pathlib import Path
import urllib.request,urllib.parse,json,hashlib
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'.cache/research/priority1';DEST.mkdir(parents=True,exist_ok=True)
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            href=dict(attrs).get('href','')
            if any(t in urllib.parse.unquote(href) for t in ('藏品','收藏','收集','拟造物质编目')):self.links.append(href)
base='https://m.prts.wiki'
s=(ROOT/'.cache/research/events-0.19/prts-main.html').read_text(encoding='utf8');p=Links();p.feed(s)
links=sorted(set(urllib.parse.urldefrag(href)[0] for href in p.links if not href.startswith('#')))
print(json.dumps(links,ensure_ascii=True),flush=True)
receipt=[]
for href in links:
    url=urllib.parse.urljoin(base,href)
    if '/w/' not in url or 'action=' in url:continue
    url=urllib.parse.quote(url,safe=':/?=&%')
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'rouge-mechanism-research'}),timeout=25) as r:raw=r.read()
        file='wiki-relic-'+str(len(receipt))+'.html';(DEST/file).write_bytes(raw)
        receipt.append({'url':url,'file':file,'sha256':hashlib.sha256(raw).hexdigest()})
        print(file,len(raw),flush=True)
    except Exception as e:receipt.append({'url':url,'unavailable':str(e)[:100]})
(DEST/'wiki-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
