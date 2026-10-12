"""Extract direct special-entry proofs from pinned inputs; no ID-prefix inference."""
import argparse,hashlib,json,re
from pathlib import Path

GAME_SHA='f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
COLORS={'红':('red','红雾'),'蓝':('blue','蓝雾'),'绿':('green','绿雾'),
        '金':('gold','金雾'),'橙':('orange','橙雾'),'紫':('purple','紫雾')}


def build(game_path,catalog_path,online_path):
    raw=Path(game_path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=GAME_SHA:raise ValueError('原topic版本摘要不符。')
    topic=json.loads(raw)['details']['rogue_6']
    catalog=json.loads(Path(catalog_path).read_text(encoding='utf8'))
    online=json.loads(Path(online_path).read_text(encoding='utf8'))
    sources={'original':catalog['sources']['original_game_data'],
             'fixed_community':catalog['sources']['cached_community_catalog'],
             'online_independent_rules':[row for row in online['sources'] if row['key'] in ('topic_online','blackflow_database_online')]}
    startup_id='scene_ro6_startbuff_enter';legacy=[]
    for relic_id,relic in topic['relics'].items():
        for ordinal,buff in enumerate(relic['buffs']):
            board={row['key']:row['valueStr'] for row in buff['blackboard']}
            if buff['key']!='force_add_choice' or board.get('scene_ids')!=startup_id:continue
            choice_id=board['choice_id'];choice=topic['choices'][choice_id]
            if not choice['isHiddenChoice']:raise ValueError('隐藏入口来源与原choice标记不符。')
            legacy.append({'legacy_id':relic_id,'legacy_item':topic['items'][relic_id],
                'choice':choice,'scene_id':startup_id,'force_add_choice_buff':buff,
                'source_path':f'$.details.rogue_6.relics.{relic_id}.buffs[{ordinal}]'})
    if len(legacy)!=6:raise ValueError('固定版本应有六个直接force_add_choice绑定。')
    # This is a documented candidate pool, not an original sourceScene pointer.
    regular_names=('未编号物','调查预付款','空间租赁','退行补偿','林间代步','巢寄生')
    regular=[]
    for name in regular_names:
        matches=[row for row in topic['choices'].values() if row['title']==name]
        if len(matches)!=1:raise ValueError('公开初始选项名称不能唯一对应原choice。')
        regular.append(matches[0])
    event=next(row for row in catalog['events'] if row['title']=='溯源')
    entry=next(row for row in event['scenes'] if row['key'] in event['entry'])
    explanation=next(row for row in entry['choices'] if row['description'].startswith('该事件具有6种差分：'))
    marker='在你犹疑之际，'
    if entry['description'].count(marker)!=1:raise ValueError('固定公共入口前缀无法唯一分离。')
    prefix=entry['description'].split(marker)[0]+marker;variants=[]
    for clause in explanation['description'].splitlines()[1:]:
        match=re.match(r'^([红蓝绿金橙紫])色的雾气',clause)
        if not match:raise ValueError('雾色差分缺明确文字。')
        color,label=COLORS[match.group(1)];expected=prefix+clause
        aliases=[row for row in topic['choiceScenes'].values() if row['title']==event['title'] and row['description']==expected]
        if not aliases:raise ValueError('原description没有逐字匹配此明确差分。')
        variants.append({'fog_color':color,'label':label,'explicit_clause':clause,
            'exact_original_description':expected,'original_scenes':aliases})
    ids=[row['id'] for variant in variants for row in variant['original_scenes']]
    if len(variants)!=6 or len(ids)!=19 or len(set(ids))!=19:raise ValueError('固定19入口差分覆盖不符。')
    startup={'scene':topic['choiceScenes'][startup_id],'regular_choices':regular,
        'legacy_choices':legacy,'known_legacy_ids':list(topic['legacyItems']),
        'minimum_previous_completed_regions':2,'documented_regular_display_count':3,
        'documented_extra_blue_display_count':1,'regular_source_scene_pointer_verified':False,
        'extra_legacy_normal_mode_only_documented':True,
        'actual_displayed_choices':None,'generation_probability':None}
    portal={'event_id':event['id'],'community_entry_scene_key':entry['key'],
        'explanation_choice_key':explanation['key'],'common_prefix':prefix,'variants':variants,
        'identity_match_method':'shared literal prefix + explicitly documented complete variant sentence == original description',
        'original_id_suffix_used_as_evidence':False,'actual_original_scene_selected':None}
    records={startup_id:{'kind':'startup_scene','source_scene_link_verified':True,'source_scene_id':startup_id,
        'proof':'Six original force_add_choice records explicitly name this scene_ids value.'}}
    for row in regular:records[row['id']]={'kind':'startup_regular_pool','source_scene_link_verified':False,
        'source_scene_id':startup_id,'documented_initial_pool_identity_verified':True,
        'proof':'Current public initial reward candidate pool has a unique exact-title original match; sourceScene pointer absent.'}
    for row in legacy:records[row['choice']['id']]={'kind':'startup_legacy_extra','source_scene_link_verified':True,
        'source_scene_id':startup_id,'legacy_id':row['legacy_id'],'source_path':row['source_path'],
        'proof':'Original force_add_choice blackboard directly pairs choice_id and scene_ids.'}
    for variant in variants:
        for scene in variant['original_scenes']:records[scene['id']]={'kind':'portal_entry_variant','source_scene_link_verified':True,
            'source_event_id':event['id'],'source_community_scene':entry['key'],'fog_color':variant['fog_color'],
            'label':variant['label'],'explicit_clause':variant['explicit_clause'],'source_scene_id':scene['id'],
            'proof':'Exact original description equals shared entry prefix plus an explicitly listed community variation.'}
    return {'schema_version':1,'sources':sources,'license_note':catalog['license_note'],'startup':startup,'portal':portal,'records':records,
        'coverage':{'historical_unmapped_scenes':45,'historical_unmapped_choices':63,
            'portal_entry_description_aliases':19,'startup_scene_named_by_original_buff':1,
            'hidden_choice_direct_source_scene_links':6,'regular_choice_documented_pool_references':6,
            'all_original_source_scene_scripts_recovered':False},
        'limits':['Only direct original pointers or whole literal descriptions establish these bindings.',
            'nextSceneId only establishes a destination, never the source scene.',
            'The twelve initial candidates are not a claim that twelve choices are displayed.',
            'Previous completed-region count is not highest reached floor or current holdings.',
            'Natural portal-node generation restrictions do not prove portal-event scene eligibility.',
            'Fixed427904 catalog, existing440271 single-scene observation and online433770/434599 rules stay separate.',
            'Current server eligibility, exact startup shown subset and special-area AP remain unknown.']}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--game',required=True);parser.add_argument('--catalog',required=True)
    parser.add_argument('--online',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    data=build(args.game,args.catalog,args.online)
    Path(args.output).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
