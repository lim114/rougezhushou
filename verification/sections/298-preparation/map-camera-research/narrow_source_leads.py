"""Select concrete render/preview and camera leads from the original mapped names."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
all_methods=json.loads((ROOT/'.cache/research/p2-native-current-263/script.json').read_bytes())['ScriptMethod']
types={'Torappu.UI.CommonMapPreviewDlg','Torappu.StageDataUtil','Torappu.Battle.Map','Torappu.Battle.MapGraphic',
 'Torappu.Battle.CameraController','Torappu.Battle.VCameraController','Torappu.Battle.BattleCamera',
 'Torappu.UI.Roguelike.RoguelikeFocusView','Torappu.UI.Roguelike.RL06.RL06FocusViewPlugin'}
rows=[m for m in all_methods if m['Name'].split('$$')[0]in types]
filtered=[]
for row in rows:
 name=row['Name']
 if ('CommonMapPreviewDlg' in name or 'Camera' in name or 'LoadStagePreviewMap' in name
     or 'Preview' in name or 'TilePos' in name or 'World' in name or 'Grid' in name):filtered.append(row)
(HERE/'target-method-leads.json').write_bytes((json.dumps(filtered,ensure_ascii=False,indent=2)+'\n').encode())
print('\n'.join(str(m['metadata_method_index'])+' '+hex(m['Address'])+' '+m['Name'] for m in filtered[:95]))
data=json.loads((ROOT/'rouge/data/battle-previews.json').read_bytes())
stages=data['stages'].values() if type(data['stages'])is dict else data['stages']
url_rows={}
for stage in stages:url_rows.setdefault(stage['level_source']['url'],[]).append(stage['id'])
missing=[];mismatches=[]
from hashlib import sha256
for url,ids in url_rows.items():
 path=ROOT/'.cache/game-data/levels'/url.split('/gamedata/levels/',1)[1]
 if not path.is_file():missing.append({'url':url,'stage_ids':ids})
 else:
  for stage_id in ids:
   expected=next(s['level_source']['sha256']for s in (data['stages'].values()if type(data['stages'])is dict else data['stages'])if s['id']==stage_id)
   if sha256(path.read_bytes()).hexdigest()!=expected:mismatches.append(stage_id)
print(json.dumps({'stage_count':sum(map(len,url_rows.values())),'unique_level_urls':len(url_rows),
 'missing_level_urls':missing,'sha_mismatch_stage_ids':mismatches},ensure_ascii=False))
summary=json.loads((ROOT/'.cache/research/map-projection-044/resource-summary.json').read_bytes())
ro6={k:v for k,v in summary.items()if 'roguelike/ro6/' in k}
(HERE/'ro6-resource-camera-records.json').write_bytes((json.dumps(ro6,ensure_ascii=False,indent=2)+'\n').encode())
for name in ('obt/roguelike/ro6/level_rogue6_c-2','obt/roguelike/ro6/level_rogue6_c-4'):
 print(name,json.dumps(ro6.get(name),ensure_ascii=False))
(HERE/'level-coverage.json').write_bytes((json.dumps({'stage_count':sum(map(len,url_rows.values())),
 'unique_level_urls':len(url_rows),'missing_level_urls':missing,'sha_mismatch_stage_ids':mismatches,
 'pinned_resource_ro6_records':len(ro6)},ensure_ascii=False,indent=2)+'\n').encode())
