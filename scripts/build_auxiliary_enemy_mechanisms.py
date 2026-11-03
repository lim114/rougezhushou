"""Build source-scoped supplemental mechanisms for four auxiliary identities."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from rouge.battle_preview import battle_data,DATA
BASE=ROOT/'research/p3-auxiliary-mechanisms';OUTPUT=DATA/'auxiliary-enemy-mechanisms.json'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(write=False):
    receipt=read(BASE/'source-receipt.json')
    for name,digest in receipt['frozen_sha256'].items():
        if sha(BASE/name)!=digest:raise ValueError('Frozen auxiliary source changed: '+name)
    source=read(BASE/'selected-original.json');docs=read(BASE/'documented-references.json')
    if source['enemy_database']!=battle_data()['source']['enemy_database']:raise ValueError('Pinned enemy database identity changed.')
    records={v['Key']:v for v in source['database_records']};prefabs={};native_sources=[]
    for bundle in source['native_sources']:
        native_sources.append({k:bundle[k] for k in ('source','source_sha256','source_md5','source_bytes','manifest_version')})
        for prefab in bundle['selected_prefabs']:
            objects={v['path_id']:v for v in prefab['objects']}
            if len(objects)!=len(prefab['objects']) or not all(v['read_exact'] for v in objects.values()):raise ValueError('Selected native graph is not exact.')
            components=[]
            for obj in objects.values():
                if obj['class_id']!=114:continue
                matches=obj['script_matches']
                if len(matches)!=1:raise ValueError('Component script hash binding is ambiguous.')
                match=matches[0]
                if not match['namespace'].startswith('Torappu.Battle'):continue
                name=objects[obj['data']['m_GameObject']['m_PathID']]['data']['m_Name']
                components.append({'path_id':obj['path_id'],'game_object_name':name,'class_name':match['namespace']+'.'+match['class_name'],
                    'properties_hash':obj['properties_hash'],'script_source_sha256':match['source_sha256'],
                    'declared_data':copy.deepcopy(obj['data'])})
            key=Path(prefab['asset_path']).stem
            if key in prefabs:raise ValueError('Prefab identity is not unique.')
            prefabs[key]={'asset_path':prefab['asset_path'],'bundle_sha256':bundle['source_sha256'],
                'selected_graph_exact':True,'components':components,'activation_verified':False}
    output={'source':{'game_commit':battle_data()['source']['game_commit'],'enemy_database':source['enemy_database'],
        'native_snapshots':native_sources,'document_references':copy.deepcopy(docs),'scope':'Fixed source declarations and separately qualified community descriptions; no event/timing/quantity computation.'},
        'profiles':{},'bindings':{}}
    for eid,record in records.items():
        levels=[v for v in record['Value'] if v['level']==0]
        if len(levels)!=1:raise ValueError('Auxiliary database grade0 must be explicit.')
        raw=levels[0]['enemyData'];key=raw['prefabKey']
        if key['m_defined'] is not True or key['m_value'] not in prefabs:raise ValueError('No explicit raw prefabKey binding; name suffix fallback forbidden.')
        output['profiles'][eid]={'enemy_id':eid,'level':0,'database_prefab_key':key['m_value'],
            'native_prefab':copy.deepcopy(prefabs[key['m_value']]),'documentation':copy.deepcopy(docs['profiles'][eid]),
            'full_current_mechanics_verified':False,'official_portrait_obtained':False}
    for sid,record in source['stages'].items():
        stage=battle_data()['stages'][sid]
        if (stage['name'],stage['difficulty'],stage['level_source'])!=(record['name'],record['difficulty'],record['level_source']):raise ValueError('Stage declaration changed.')
        level=BASE/record['level_source']['url'].rsplit('/',1)[1]
        if sha(level)!=record['level_source']['sha256'] or level.stat().st_size!=record['level_source']['bytes']:raise ValueError('Full original level bytes changed.')
        refs=read(level)['enemyDbRefs'];bound={}
        for selected in record['source_refs']:
            ref=selected['reference'];index=selected['source_index'];eid=ref['id'];grade=ref['level']
            if refs[index]!=ref or type(grade) is not int or grade!=0 or type(ref['useDb']) is not bool:raise ValueError('Exact original enemyRef changed.')
            preview=[v for v in stage['enemies'] if v['id']==eid and v['level']==grade]
            if len(preview)!=1:raise ValueError('Preview enemy grade is not unique.')
            override=ref['overwrittenData'];raw=next(v for v in records[eid]['Value'] if v['level']==grade)['enemyData']
            declared=copy.deepcopy(raw['talentBlackboard']) if ref['useDb'] else None
            prefab=raw['prefabKey']['m_value'] if ref['useDb'] else None;mode='database' if ref['useDb'] else 'stage_constructor'
            if override is not None:
                field=override.get('prefabKey')
                if field and field['m_defined'] is True:prefab=field['m_value']
                if override.get('talentBlackboard') is not None:declared=copy.deepcopy(override['talentBlackboard'])
            if prefab!=output['profiles'][eid]['database_prefab_key'] or declared is None:raise ValueError('A different or missing source prefab/blackboard cannot inherit this profile.')
            bound[eid+'@0']={'enemy_id':eid,'level':0,'name':preview[0]['name'],'stage_name':stage['name'],'difficulty':stage['difficulty'],
                'level_source_sha256':stage['level_source']['sha256'],'source_index':index,'source_constructor_mode':mode,
                'prefab_key':prefab,'declared_talent_blackboard':declared,'original_reference':copy.deepcopy(ref),
                'actual_blackboard_initialization_verified':False,'actual_instance_present':None}
        output['bindings'][sid]=bound
    result={'status':'PASS_FOUR_SOURCE_SCOPED_AUXILIARY_PROFILES','profiles':len(output['profiles']),'stage_bindings':len(output['bindings']),
        'enemy_stage_references':sum(len(v) for v in output['bindings'].values()),'native_selected_prefabs':len(prefabs),
        'independent_constructor_refs':sum(v['source_constructor_mode']=='stage_constructor' for rows in output['bindings'].values() for v in rows.values()),
        'actual_runtime_mechanics_verified':False,'quantities_applied_to_prediction':False,'official_portraits_added':0,
        'game_actions':0,'chat_requests':0,'process_memory_read':False,'dll_executed':False,
        'output_sha256':hashlib.sha256(json.dumps(output,ensure_ascii=False,indent=2).encode('utf8')).hexdigest()}
    if write:
        OUTPUT.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf8',newline='\n')
        (BASE/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    return output,result
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args();_,r=build(write=args.write);print(json.dumps(r,ensure_ascii=False))
