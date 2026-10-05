"""Extract event identities; classify separately with attributed community facts."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
file=ROOT/'.cache/game-data/roguelike_topic_table.json'
receipt=json.loads((ROOT/'.cache/game-data/receipt.json').read_text(encoding='utf-8'))
source=receipt['files']['roguelike_topic_table']
assert hashlib.sha256(file.read_bytes()).hexdigest()==source['sha256']
detail=json.loads(file.read_text(encoding='utf-8'))['details']['rogue_6']
research=json.loads((ROOT/'.cache/research/events-0.19/findings.json').read_text(encoding='utf-8'))
classes={row['title']:{'node_types':row['node_types'],'evidence':'community_event_catalog'}
         for row in research['community_classifications']}
data={'source':{'game_data':source,'commit':receipt['commit'],'classification':research['source']},
      'scenes':{key:{field:s.get(field) for field in ('title','description','background')}
                for key,s in detail['choiceScenes'].items()},
      'choices':{key:{field:c.get(field) for field in ('title','description','lockedCoverDesc','nextSceneId','type','isHiddenChoice')}
                 for key,c in detail['choices'].items()},
      'title_classes':classes,
      'limits':['节点类型分类来自社区目录；层数/出场前提和生成权重未恢复。',
                '同名/同描述场景可能对应不同分支，不强行合并ID或拼接完整选择链。']}
(ROOT/'rouge/data/node-events.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(data['scenes']),'scene records,',len({s['title'] for s in data['scenes'].values()}),'titles,',len(classes),'classified titles')
