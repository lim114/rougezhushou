"""Rebuild declaration inventory; optionally recheck original full source assets."""
from pathlib import Path
from hashlib import sha256,sha1
from collections import Counter
import json,argparse,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
PACK='research/p3-current-stage-objects-373'
def encoded(value):return(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
def inventory(current,selected):
    from rouge import current_battle_reference as battle
    counts=Counter();stages={};entities=set()
    for sid,s in sorted(current['version']['current']['details']['stages'].items()):
        level_key='levels/'+s['levelId'].lower()+'.json';level=current['inputs']['levels'][level_key];actions=[]
        for q in battle.queues(level):
            for i,a in enumerate(q['actions']):actions.append({'key':str(len(actions)),'raw':a})
        rows=[]
        for container in('predefines','hardPredefines'):
            for field in('characterInsts','tokenInsts','characterCards','tokenCards'):
                for i,raw in enumerate((level.get(container)or{}).get(field)or[]):
                    key=f'$.{container}.{field}[{i}]';entity=(raw.get('inst')or{}).get('characterKey')or raw.get('characterKey');kind='instance'if field.endswith('Insts')else'card';alias=raw.get('alias')
                    if entity not in selected['characters']:raise ValueError('Exact original object missing')
                    linked=[a['key']for a in actions if kind=='instance'and type(alias)is str and alias and a['raw']['actionType']=='ACTIVATE_PREDEFINED'and a['raw'].get('key')==alias]
                    rows.append({'key':key,'entity_id':entity,'kind':kind,'raw_sha256':sha256(encoded(raw)).hexdigest(),'activation_action_keys':linked});counts[kind]+=1;counts['with_direct_activations'if linked else'without_direct_activations']+=1;entities.add(entity)
        stages[sid]={'level_key':level_key,'entries':rows,'original_source':current['selection']['original_sources'][level_key]}
    counts.update(stages=len(stages),entity_types=len(entities),skill_records=len(selected['skills']))
    return{'schema':'current_stage_objects_373_scope_v1','battle_identity':current['identity'],'stages':stages,'counts':dict(counts),'actual_activation':None,'actual_reward':None,'actual_server_verified':False}
def full_original_audit(folder,selection,selected):
    objects={};observed={}
    for name,pin in selection['original_sources'].items():
        raw=(Path(folder)/name).read_bytes();blob=sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if len(raw)!=pin['bytes']or sha256(raw).hexdigest()!=pin['sha256']or blob!=pin['git_blob_sha1']:raise ValueError('Full original asset pin differs: '+name)
        objects[name]=json.loads(raw);observed[name]={'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'git_blob_sha1':blob,'original_url':pin['url']}
    exact={'commit':selected['commit'],'characters':{k:objects['character_table.json'][k]for k in selected['characters']},'skills':{k:objects['skill_table.json'][k]for k in selected['skills']}}
    if exact!=selected:raise ValueError('Selected complete records differ from original full assets')
    return{'schema':'current_stage_objects_373_extraction_audit_v1','source_assets':observed,'selected_character_records':len(selected['characters']),'selected_skill_records':len(selected['skills']),'complete_selected_records_equal_originals':True,'private_source_used':False,'server_verified':False}
def build(root=ROOT,original_root=None):
    from rouge import current_battle_reference as battle
    current=battle.packet()
    if current is None:raise ValueError('Actual pinned current source chain required')
    root=Path(root);base=root/PACK;names=('selected-originals.json','source-selection.json','source-notes.json','source-extraction-audit.json');blobs={PACK+'/'+n:(base/n).read_bytes()for n in names};selected=json.loads(blobs[PACK+'/selected-originals.json']);selection=json.loads(blobs[PACK+'/source-selection.json'])
    if original_root is not None:
        audit=full_original_audit(original_root,selection,selected)
        if encoded(audit)!=blobs[PACK+'/source-extraction-audit.json']:raise ValueError('Retained full-source extraction audit differs')
    data=inventory(current,selected);blobs[PACK+'/scope-inventory.json']=encoded(data)
    manifest={'schema':'current_stage_objects_373_manifest_v1','game_commit':battle.version.NEW_COMMIT,'files':{n:{'bytes':len(raw),'sha256':sha256(raw).hexdigest()}for n,raw in blobs.items()}}
    blobs[PACK+'/runtime-manifest.json']=encoded(manifest);return blobs,data['counts']
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--original-root',type=Path);args=parser.parse_args();blobs,counts=build(original_root=args.original_root)
    for n,raw in blobs.items():
        p=ROOT/n
        if args.check:
            if not p.is_file()or p.read_bytes()!=raw:raise AssertionError(n)
        else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    print(json.dumps({'passed':True,'counts':counts,'check_only':args.check,'full_original_assets_rechecked':args.original_root is not None},ensure_ascii=False))
if __name__=='__main__':main()
