"""Complete original route inventory and exact main-action bindings."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import json,argparse,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));PACK='research/p3-current-route-itinerary-375'
def encoded(v):return(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
def build(root=ROOT):
    from rouge import current_battle_reference as battle
    current=battle.packet()
    if current is None:raise ValueError('Original current source chain required')
    stages={};counts=Counter();types=Counter()
    for sid,s in sorted(current['version']['current']['details']['stages'].items()):
        level_key='levels/'+s['levelId'].lower()+'.json';level=current['inputs']['levels'][level_key];routes=[];actions=[];bound=set()
        for q in battle.queues(level):
            for a in q['actions']:actions.append((str(len(actions)),q,a))
        for scope,field in(('base','routes'),('extra','extraRoutes')):
            for i,raw in enumerate(level.get(field)or[]):
                linked=[key for key,q,a in actions if scope=='base'and q['kind']=='main'and a['actionType']=='SPAWN'and type(a.get('routeIndex'))is int and a['routeIndex']==i];bound.update(linked)
                checkpoints=raw.get('checkpoints')or[];types.update(p.get('type')for p in checkpoints);routes.append({'key':f'$.{field}[{i}]','scope':scope,'raw_sha256':sha256(encoded(raw)).hexdigest(),'checkpoint_count':len(checkpoints),'action_keys':linked});counts[scope]+=1;counts['checkpoints']+=len(checkpoints)
        unassigned=[key for key,q,a in actions if a['actionType']=='SPAWN'and key not in bound];counts['main_bound_spawn_records']+=len(bound);counts['route_unassigned_spawn_records']+=len(unassigned);stages[sid]={'level_key':level_key,'original_source':current['selection']['original_sources'][level_key],'routes':routes,'unassigned_action_keys':unassigned}
    counts.update(stages=len(stages),routes=counts['base']+counts['extra'],steps=counts['checkpoints']+2*(counts['base']+counts['extra']))
    data={'schema':'current_route_itinerary_375_scope_v1','battle_identity':current['identity'],'stages':stages,'counts':dict(counts),'checkpoint_types':dict(types),'actual_global_clock':None,'actual_route_selection':None,'actual_server_verified':False}
    notes={'schema':'current_route_itinerary_375_notes_v1','game_commit':battle.version.NEW_COMMIT,'originals':'research/p3-current-battle-314/source-selection.json','existing_position_semantics':'rouge/current_action_positions.py','established':['全部routes与extraRoutes原位置逐项保留','按原数组顺序保留出生、五种检查点及终点','仅主波次SPAWN显式routeIndex关联基础路线；条件分支数组选择未知则不绑定','等待及消失的占位坐标不进入地图，未定义移动方式不标点','名义格沿用已有display_cell和地图准入，不投影未校准位置'],'not_established':['条件分支实际采用哪个数组和路线','实际经过、偏移、寻路与传送配对','等待实际计时起点和放行、全局出怪时钟','当前服务器执行或最终面板']}
    blobs={PACK+'/scope-inventory.json':encoded(data),PACK+'/source-notes.json':encoded(notes)};m={'schema':'current_route_itinerary_375_manifest_v1','game_commit':battle.version.NEW_COMMIT,'files':{n:{'bytes':len(raw),'sha256':sha256(raw).hexdigest()}for n,raw in blobs.items()}};blobs[PACK+'/runtime-manifest.json']=encoded(m);return blobs,dict(counts)
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args();blobs,counts=build()
    for n,raw in blobs.items():
        path=ROOT/n
        if args.check:
            if not path.is_file()or path.read_bytes()!=raw:raise AssertionError(n)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    print(json.dumps({'passed':True,'counts':counts,'check_only':args.check},ensure_ascii=False))
if __name__=='__main__':main()
