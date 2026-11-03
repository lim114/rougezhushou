from pathlib import Path
import json,hashlib,collections,datetime,re

base=Path(__file__).parent
snapshot=base/'baseline'
source=Path('/workspace/.continuation/p2-after-055-audit/relic-scope/roguelike_topic_table.json')
if (base/'roguelike_topic_table.json').exists():source=base/'roguelike_topic_table.json'
raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
assert len(raw)==17943244 and sha=='f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
table=json.loads(raw);details=table['details']['rogue_6'];common=table['customizeData']['rogue_6']['commonDevelopment']
config=json.loads((snapshot/'rouge/data/run-config.json').read_bytes())
technology=json.loads((snapshot/'rouge/data/technology-reference.json').read_bytes())
assert config['source_sha256']==sha and technology['source']['sha256']==sha
assert config['squads']=={key:{**band,**details['items'][key],'buffs':details['relics'][key]['buffs']} for key,band in details['bandRef'].items()}
assert {key:technology[key] for key in common}==common
assert len(config['squads'])==22 and len(common['developments'])==57
mapping={'rogue_6_band_2':'rogue_6_difficulty_1','rogue_6_band_5':'rogue_6_difficulty_2',
         'rogue_6_band_7':'rogue_6_difficulty_3','rogue_6_band_16':'rogue_6_outbuff_43',
         'rogue_6_band_18':'rogue_6_outbuff_45','rogue_6_band_20':'rogue_6_outbuff_44'}
upgrades=[]
for key,band in details['bandRef'].items():
    if band['bandLevel']!=1:continue
    item=details['items'][key];condition=item['unlockCondDesc']
    row={'id':key,'band_selector':f'$.details.rogue_6.bandRef.{key}','raw_band_complete':band,
         'item_selector':f'$.details.rogue_6.items.{key}','raw_item_complete':item,
         'relic_selector':f'$.details.rogue_6.relics.{key}','raw_relic_complete':details['relics'][key]}
    if key in mapping:
        node_id=mapping[key];node=common['developments'][node_id]
        assert condition=='生命游戏中激活“'+node['buffName']+'”'
        assert '“'+item['name']+'”效果提升' in node['rawDesc']
        assert sum(n['buffName']==node['buffName'] for n in common['developments'].values())==1
        row.update(technology_selector=f'$.customizeData.rogue_6.commonDevelopment.developments.{node_id}',raw_technology_node_complete=node,
                   forward_condition_name_exact=True,reverse_squad_effect_name_exact=True)
        gate=common['developmentsDifficultyNodeInfos'].get(node_id)
        if gate:
            row.update(gate_selector=f'$.customizeData.rogue_6.commonDevelopment.developmentsDifficultyNodeInfos.{node_id}',raw_gate_complete=gate)
            grade=gate['enableGrade'];assert grade=={'rogue_6_difficulty_1':3,'rogue_6_difficulty_2':6,'rogue_6_difficulty_3':9}[node_id]
            diff=[d for d in table['customizeData']['rogue_6']['difficulties'] if d['modeDifficulty']=='NORMAL']
            assert len(diff)==16 and all((node_id in (d['buffs'] or []))==(d['grade']>=grade) for d in diff)
            row['raw_custom_normal_mode_grade_reference']=[d for d in diff if node_id in (d['buffs'] or [])]
            row['custom_other_modes_reference']=[d for d in table['customizeData']['rogue_6']['difficulties'] if d['modeDifficulty']!='NORMAL']
    else:
        assert key=='rogue_6_band_22' and condition=='机械师提升至精英二阶段'
        row['selected_operator_training_does_not_prove_account_mechanist_training']=True
    upgrades.append(row)
assert len(upgrades)==7 and len(mapping)==6
direct=[key for key,r in config['squads'].items() if any(b['key']=='char_attribute_mul' for b in r['buffs'])]
assert direct==['rogue_6_band_6','rogue_6_band_7']
previews=json.loads((snapshot/'rouge/data/previews.json').read_bytes())
runes=[]
catalog=json.loads((snapshot/'rouge/data/catalog.json').read_bytes())
for sid,preview in previews['stages'].items():
    for index,rune in enumerate(preview['runes']):
        if rune['difficultyMask'] in (catalog['stages'][sid]['difficulty'],'ALL'):
            runes.append({'stage_id':sid,'selector':f'$.stages.{sid}.runes[{index}]','record':rune,
                          'existing_current_numerical_path':rune['key']=='enemy_attribute_mul',
                          'existing_hidden_group_excluded_from_pending':rune['key']=='level_hidden_group_enable'})
search_files=[];hits=[]
needles=('rogue_6_outbuff_','rogue_6_band_','commonDevelopment')
native_root=Path('/workspace/rougezhushou/.cache/research')
for p in sorted(native_root.rglob('*')):
    if not p.is_file() or p.suffix not in ('.json','.txt','.md'):continue
    data=p.read_bytes();search_files.append({'path':str(p),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
    text=data.decode(errors='replace')
    for needle in needles:
        if needle in text:hits.append({'path':str(p),'needle':needle,'occurrences':text.count(needle)})
files=['rouge/run_modifiers.py','rouge/run_config.py','rouge/reporting.py','rouge/technology.py',
       'rouge/data/run-config.json','rouge/data/technology-reference.json','rouge/data/previews.json',
       'scripts/build_run_config.py','scripts/build_technology_reference.py',
       'research/p2-technology/NOTE.md','research/p2-enemy-rune-selectors/RESEARCH.md',
       'research/p2-aglna-manual-weight/NOTE.md','research/p2-run-eligibility/source-receipt.json']
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'frozen_repository_commit':'59531ff2e9475410a84ef0e60836f89793fd35a9',
     'raw_topic_source':{'path':str(source),'bytes':len(raw),'sha256':sha,'commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
        'url':config['source_url'],'rehashed_current_full_raw_source':True},
     'all_22_squad_composites_equal_exact_original_band_item_buffs':True,
     'all_common_development_data_equal_exact_original':True,
     'strengthened_squads_complete_original_records':upgrades,
     'supported_reference_mapping':mapping,'existing_direct_attribute_squads':direct,
     'matched_stage_runes_current_public_archive':runes,
     'matched_stage_rune_key_counts':dict(collections.Counter(r['record']['key'] for r in runes)),
     'existing_native_text_exact_id_search':{'files':search_files,'count':len(search_files),'needles':needles,'hits':hits,
         'scope':'existing parsed public cache only; not current full installation, native binaries or hot-update binding'},
     'source_files':{name:{'sha256':hashlib.sha256((snapshot/name).read_bytes()).hexdigest(),'bytes':(snapshot/name).stat().st_size} for name in files},
     'authorized_next_scope':'selected strengthened squad conditional source reference only; no numerical, unlock, mode or private-state inference',
     'known_unknowns_and_restart_conditions':{
         'account_unlock':'Unknown; needs explicit account observation, never source display graph alone.',
         'actual_activation':'Unknown; needs actual mode/account/effect binding, cannot override explicit current effect_verified from raw grade references.',
         'long_term_buff_attribute_layer':'Needs exact rogue_6_outbuff ID binding and actual writer/target/layer proof; display percentages insufficient.',
         'remaining_enemy_scripts':'Needs named env_system_new/env_gbuff_new/global_buff script target and lifecycle binding; raw parameters alone are not static formulas.',
         'resource_and_recruit_callbacks':'Needs observed ownership/event/effective-count lifecycle; no inferred initial gifts or random inventory.'},
     'no_tracked_edits':True,'no_private_state_reads_or_resets':True,'no_native_binaries_downloaded':True,'no_wine_or_gui':True}
(base/'source-receipt071.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print({'source_sha256':sha,'strengthened_squads':len(upgrades),'node_references':len(mapping),
       'native_text_files':len(search_files),'native_exact_id_hits':len(hits),
       'matched_stage_rune_key_counts':out['matched_stage_rune_key_counts']})
