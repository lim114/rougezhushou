def selected_talents(profile, scenario):
    elite=scenario.get('elite',2)
    level=scenario.get('level') or profile['phases'][elite]['max_level']
    potential=scenario.get('potential',1)-1
    def eligible(candidate):
        condition=candidate.get('unlockCondition')
        phase=int(condition['phase'][-1]) if condition else candidate['phase']
        minimum=condition['level'] if condition else candidate['level']
        rank=candidate.get('requiredPotentialRank',candidate.get('potential_rank',0))
        return phase<=elite and (phase<elite or minimum<=level) and rank<=potential
    talents={}
    for i,candidates in enumerate(profile['talents']):
        candidates=[t for t in candidates if eligible(t)]
        if candidates:talents[i]=candidates[-1]
    module=next((m for m in profile['modules'] if m['id']==scenario.get('module_id')),None)
    parts=[]
    if module and elite>=module['unlock_elite'] and level>=module['unlock_level']:
        parts=module['levels'][scenario['module_level']-1]['parts']
        from .gnosis_module_reference import selected_reference
        gnosis_reference=selected_reference(profile,module,scenario['module_level'],parts,talents.get(0),eligible)
        if gnosis_reference:
            talents[0]={**talents[0],'reference_only':True,
                'reference_identity':{'talent_index':0,'prefab_key':'1'},
                'gnosis_isw_a_reference':gnosis_reference}
        for part in parts:
            if part.get('isToken'):continue
            candidates=(part.get('addOrOverrideTalentDataBundle') or {}).get('candidates') or []
            grouped={}
            for candidate in candidates:
                index=candidate.get('talentIndex',-1)
                if index>=0 and eligible(candidate):grouped[index]=candidate
            for index,talent in grouped.items():
                if gnosis_reference and index==0:continue
                if (profile['id']=='char_437_mizuki' and module['id']=='uniequip_003_mizuki' and
                        part.get('target')=='TALENT' and index==0 and talent.get('prefabKey')=='10' and
                        talent.get('isHideTalent') is True and talent.get('name') is None and
                        talents.get(index,{}).get('name')=='创伤性癔症' and
                        talents[index]['values'].get('attack@mizuki_t_1.atk_scale')==.5):
                    # Pinned original prefab 1 remains a conditional reference.
                    # Prefab 10's attachment/retention CFG is not available;
                    # keep its distinct fields without merging talent values.
                    talents[index]={**talents[index],'reference_only':True,
                        'reference_identity':{'talent_index':0,'prefab_key':'1'},
                        'unresolved_module_ability':{
                            'target':part['target'],'talent_index':index,
                            'prefab_key':talent['prefabKey'],'res_key':part.get('resKey'),
                            'hidden':True,'name':talent['name'],
                            'blackboard':{b['key']:b['value'] for b in talent['blackboard']},
                            'attachment_verified':False}}
                    continue
                name=talent['name']
                if (profile['id']=='char_437_mizuki' and module['id']=='uniequip_004_mizuki' and
                        part.get('target')=='TALENT_DATA_ONLY' and index==0 and name is None):
                    # Reviewed IS data-only overlay targets the same existing
                    # talent; its null label must not erase that identity.
                    name=talents.get(index,{}).get('name')
                talents[index]={'name':name,'description':talent.get('upgradeDescription'),
                    'values':{b['key']:b['value'] for b in talent['blackboard']}}
    return list(talents.values()),parts
