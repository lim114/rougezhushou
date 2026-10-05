"""Keep tactical equipment identities separate from damage-modifying relics."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=root/'.cache/game-data/roguelike_topic_table.json'
data=json.loads(source.read_text(encoding='utf-8'))['details']['rogue_6']
receipt=json.loads((root/'.cache/game-data/receipt.json').read_text(encoding='utf-8'))
items={k:v for k,v in data['items'].items() if v['type']=='ACTIVE_TOOL'}
(root/'rouge/data/inventory-items.json').write_text(json.dumps({'schema_version':1,'commit':receipt['commit'],
    'source':receipt['files']['roguelike_topic_table']['url'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'active_tools':items},ensure_ascii=False,indent=2),encoding='utf-8')
print(len(items))
