"""Verify shared artwork from a table containing all four game-data variants."""
from pathlib import Path
import re,json,html,hashlib
ROOT=Path(__file__).resolve().parents[1]
page=ROOT/'.cache/research/priority1/wiki-relic-0.html';source=page.read_text(encoding='utf8')
data=json.loads((ROOT/'rouge/data/relic-mechanics.json').read_text(encoding='utf8'))['relics']
receipt=json.loads((ROOT/'rouge/data/relic-icon-receipt.json').read_text(encoding='utf8'))
missing=[r['id'] for r in receipt['unavailable']];families={};failed=[]
def normalize(text):return re.sub(r'\s+','',html.unescape(re.sub(r'<[^>]*>','',text)))
for base in sorted({rid.rsplit('_',1)[0] for rid in missing}):
    name=data[base]['name'];marker=f'<p id="{html.escape(name,quote=True)}"'
    start=source.find(marker);end=source.find('</table>',start)
    table=source[start:end] if start>=0 and end>start else ''
    ids=[base]+[rid for rid in missing if rid.startswith(base+'_')]
    images=set(re.findall(r'roguelike_topic_itempic/([^/" >]+)\.png',table))
    usages=all(normalize(data[rid]['usage']) in normalize(table) for rid in ids)
    if images!={base} or not usages:failed.append({'id':base,'images':sorted(images),'all_usages_present':usages});continue
    families[base]={'ids':ids,'file':f'relic-icons/{base}.png','source_table_sha256':hashlib.sha256(table.encode()).hexdigest(),
        'basis':'One named wiki table lists all four data-matching effects and uses a single base-ID artwork.',
        'independent_tier_artwork':False,'identity_requires':'exact owned name/usage or confirmed difficulty upgrade mapping'}
result={'source_url':'https://m.prts.wiki/w/沉沦者的黑流树海/拟造物质编目',
    'source_sha256':hashlib.sha256(page.read_bytes()).hexdigest(),'families':families,'unverified':failed,
    'equivalent_reference_variants':sum(len(x['ids'])-1 for x in families.values())}
(ROOT/'rouge/data/relic-reference-equivalence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'verified_variants':result['equivalent_reference_variants'],'unverified':failed},ensure_ascii=True))
