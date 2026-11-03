from pathlib import Path
import shutil,hashlib,json,datetime
base=Path(__file__).parent;draft=base/'draft075'
if not draft.exists():shutil.copytree(base/'baseline',draft,ignore=shutil.ignore_patterns('__pycache__'))
name='rouge/spawn_reference.py';text=(base/'baseline'/name).read_text()
needle="    return result\n\ndef sequence_text(row):"
replacement="""    # This pinned stage declares an additional parameter. Its native writer
    # and composition with options.moveMultiplier are not verified.
    if stage.get('id')=='ro6_e_3_6' and stage.get('difficulty')=='FOUR_STAR':
        runes=stage.get('runes')
        for index,rune in enumerate(runes if isinstance(runes,list) else []):
            if not isinstance(rune,dict) or rune.get('key')!='enemy_attribute_mul':continue
            if (rune.get('difficultyMask')!='FOUR_STAR' or rune.get('professionMask')!=1023
                    or rune.get('buildableMask')!='ALL'):continue
            blackboard=rune.get('blackboard')
            if not isinstance(blackboard,list) or any(not isinstance(b,dict) for b in blackboard):continue
            if any(b.get('key') in ('enemy','rune_alias') for b in blackboard):continue
            values=[(bi,b) for bi,b in enumerate(blackboard) if b.get('key')=='move_speed']
            if len(values)!=1:continue
            bi,value=values[0]
            if value.get('valueStr') is not None or not finite_nonnegative(value.get('value')):continue
            from copy import deepcopy
            result['stage_move_speed_rune_reference']={
                'parameter':value['value'],'rune_key':rune['key'],'blackboard_key':'move_speed',
                'source_selector':f'$.runes[{index}].blackboard[{bi}]',
                'source':deepcopy(stage.get('level_source')),
                'difficulty_mask_parameter':rune['difficultyMask'],
                'profession_mask_parameter':rune['professionMask'],
                'buildable_mask_parameter':rune['buildableMask'],
                'native_target_writer_layer_verified':False,
                'combined_with_stage_multiplier_speed':None,
                'complete_effective_speed_verified':False,
            }
    return result

def sequence_text(row):"""
assert text.count(needle)==1;text=text.replace(needle,replacement);(draft/name).write_text(text)
name='rouge/battle_preview.py';text=(base/'baseline'/name).read_text()
needle="        source=battle_data()['source']\n"
replacement="""        movement=entry['movement_reference']
        rune=movement.get('stage_move_speed_rune_reference')
        if rune:
            lines.extend(['关卡移速符文参数参考：'+value_text(rune['parameter']),
                '基础移速×关卡倍率小计：'+value_text(movement['base_times_stage_speed']),
                '符文与关卡倍率合成的移速：未知；原生目标、写入及叠加层尚未核验。'])
            if rune['source']:lines.append('关卡移速参数来源：'+rune['source']['url'])
        source=battle_data()['source']
"""
assert text.count(needle)==1;text=text.replace(needle,replacement);(draft/name).write_text(text)
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_commit':'dbf1e698f56cbba03793ed13769a9f6dae2c5ff6',
    'changes':{name:{'sha256':hashlib.sha256((draft/name).read_bytes()).hexdigest(),'bytes':(draft/name).stat().st_size} for name in ('rouge/spawn_reference.py','rouge/battle_preview.py')},
    'only_exact_ro6_e_3_6_parameter_reference_and_technical_text':True,'old_base_times_stage_speed_unchanged':True,
    'no_stage_rune_multiplication_or_native_binding_inferred':True,'full_effective_speed_stays_unverified':True}
(base/'draft-receipt075.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(receipt)
