"""Reproduce current reward source pins, keeping prior documentation explicit."""
from pathlib import Path
from hashlib import sha256
import json,argparse
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-rewards-315'
EXPECTED={'trap_320_shtlbx':('sktok_shtlbx','消耗50点部署费用开启，战斗后获得1个零件'),
 'trap_321_shnbox':('sktok_shnbox','击破额外获得2源石锭'),'trap_322_shrbox':('sktok_shrbox','反弹部分受到的伤害，击破额外获得5源石锭'),
 'trap_323_shsbox':('sktok_shsbox','击破额外获得10源石锭'),'trap_327_shchst':('sktok_shchst','击破后，可部署干员偷取1-2个商店物品，部署的干员无法再部署')}

def build(root=ROOT):
 root=Path(root)
 def read(n):return json.loads((root/n).read_bytes())
 selected=read(PACK+'/selected-originals.json');sources=read(PACK+'/source-selection.json');scope=read(PACK+'/documentation-scope.json')
 assert sources['commit']=='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d'and scope['successful_new_HTML_downloads']==0
 assert set(selected['characters'])==set(EXPECTED)and len(selected['skills'])==5
 for eid,(sid,text)in EXPECTED.items():
  char=selected['characters'][eid];assert len(char['skills'])==1 and char['skills'][0]['skillId']==sid
  assert len(selected['skills'][sid]['levels'])==1 and selected['skills'][sid]['levels'][0]['description']==text
 names=[PACK+'/'+n for n in('selected-originals.json','source-selection.json','documentation-scope.json')]
 names+=['research/p3-rare-rewards/documented-outcomes.json','research/p3-moving-reward-current/source-manifest.json']
 moving=read('research/p3-moving-reward-current/source-manifest.json')
 for name,pin in moving['files'].items():
  raw=(root/name).read_bytes();assert sha256(raw).hexdigest()==pin['sha256']and len(raw)==pin['bytes']
  names.append(name)
 files={name:{'sha256':sha256((root/name).read_bytes()).hexdigest(),'bytes':(root/name).stat().st_size}for name in names}
 result={'schema':'current_rewards_315_v1','game_commit':sources['commit'],'files':files,'device_rules':5,'prior_community_documentation_reused_not_current_server_verified':True,'complete_reward_pool_known':False}
 return(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args();raw=build();dest=ROOT/PACK/'runtime-manifest.json'
 if a.check:assert dest.read_bytes()==raw
 if a.write:dest.write_bytes(raw)
 print(json.dumps({'manifest_sha256':sha256(raw).hexdigest(),'current_device_rules':5,'prior_docs_reused':True}))
