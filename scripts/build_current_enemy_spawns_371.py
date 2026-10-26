"""Rebuild the complete source relation inventory from pinned current levels."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
PACK='research/p3-current-enemy-spawns-371'
def encoded(value):return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
def build(root=ROOT):
    from rouge import current_battle_reference as battle
    current=battle.packet()
    if current is None:raise ValueError('Pinned complete current battle source required')
    stages={};counts=Counter()
    for sid,stage in sorted(current['version']['current']['details']['stages'].items()):
        level_key='levels/'+stage['levelId'].lower()+'.json';level=current['inputs']['levels'][level_key]
        # Keys are ordinals over ALL actions, including non-SPAWN placeholders.
        ordinal=0;spawns=[]
        for q in battle.queues(level):
            for i,a in enumerate(q['actions']):
                if a.get('actionType')=='SPAWN':spawns.append({'key':str(ordinal),'selector':q['source_selector']+f'.actions[{i}]','entity_id':a.get('key'),'queue_kind':q['kind']})
                ordinal+=1
        refs=[{'enemy_key':str(i),'entity_id':e['id'],'binding_sha256':sha256(encoded(e)).hexdigest(),'action_keys':[a['key']for a in spawns if a['entity_id']==e['id']]}for i,e in enumerate(level['enemyDbRefs'])]
        stages[sid]={'level_key':level_key,'original_source':current['selection']['original_sources'][level_key],'references':refs,'spawn_records':spawns}
        counts.update(stages=1,enemy_references=len(refs),spawn_records=len(spawns),no_direct_spawn_references=sum(not r['action_keys']for r in refs))
    data={'schema':'current_enemy_spawns_371_scope_v1','source_identity':current['identity'],'stages':stages,'counts':dict(counts),'actual_occurrence':None,'actual_time':None,'actual_server_verified':False}
    notes={'schema':'current_enemy_spawns_371_notes_v1','game_commit':battle.version.NEW_COMMIT,'source':'research/p3-current-battle-314/source-selection.json','established':['逐条原enemyDbRefs位置保留','仅以原SPAWN.key完全一致关联，原动作包含非SPAWN的顺序位置不改变','主波次与条件分支、候选与隐藏组均分别保留','未找到直接SPAWN不证明不会被技能或其它脚本生成'],'not_established':['实际分支/候选选择与次数','开场绝对时间与实际出生位置','多份同id时实际引用等级选择','当前服务器或实际最终数值']}
    blobs={PACK+'/scope-inventory.json':encoded(data),PACK+'/source-notes.json':encoded(notes)}
    manifest={'schema':'current_enemy_spawns_371_manifest_v1','source_identity':current['identity'],'files':{n:{'bytes':len(raw),'sha256':sha256(raw).hexdigest()}for n,raw in blobs.items()}}
    blobs[PACK+'/runtime-manifest.json']=encoded(manifest)
    return blobs,dict(counts)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();blobs,counts=build()
    for name,raw in blobs.items():
        path=ROOT/name
        if args.check:
            if not path.is_file()or path.read_bytes()!=raw:raise AssertionError(name)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    print(json.dumps({'passed':True,'counts':counts,'check_only':args.check},ensure_ascii=False))
if __name__=='__main__':main()
