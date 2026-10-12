"""Supplemental auxiliary-unit source references, never effective damage/timing."""
import copy,json
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=1)
def reference_data():
    return json.loads((Path(__file__).with_name('data')/'auxiliary-enemy-mechanisms.json').read_text(encoding='utf8'))

def reference_for(stage_id,enemy_id,level,panel_reference=None):
    if not isinstance(stage_id,str) or not isinstance(enemy_id,str) or type(level) is not int or level!=0:return None
    data=reference_data();binding=data['bindings'].get(stage_id,{}).get(enemy_id+'@'+str(level))
    if binding is None:return None
    from .battle_preview import battle_data
    battle=battle_data();stage=battle['stages'].get(stage_id)
    if stage is None:return None
    if (battle['source']['game_commit'],battle['source']['enemy_database'])!=(data['source']['game_commit'],data['source']['enemy_database']):return None
    if (stage['name'],stage['difficulty'],stage['level_source']['sha256'])!=(binding['stage_name'],binding['difficulty'],binding['level_source_sha256']):return None
    if len([v for v in stage['enemies'] if v['id']==enemy_id and v['level']==level])!=1:return None
    if panel_reference is None:
        from .enemy_panel import enemy_panel_reference
        try:panel_reference=enemy_panel_reference(stage_id,enemy_id,level)
        except ValueError:return None
    panel=panel_reference
    if (panel['stage_id'],panel['enemy_id'],panel['requested_level'])!=(stage_id,enemy_id,level):return None
    if not panel['compiled_result_available'] or panel['construction_reference']['mode']!=binding['source_constructor_mode']:return None
    if panel['source']['enemy_database']!=data['source']['enemy_database'] or panel['source']['stage']['sha256']!=binding['level_source_sha256']:return None
    profile=data['profiles'][enemy_id]
    if profile['database_prefab_key']!=binding['prefab_key'] or profile['native_prefab']['asset_path'].rsplit('/',1)[1]!=binding['prefab_key']+'.prefab':return None
    result={'profile':copy.deepcopy(profile),'binding':copy.deepcopy(binding),
        'source_scope':'fixed_original_declarations_and_document_reference',
        'full_current_mechanics_verified':False,'actual_instance_present':None,'actual_target':None,
        'exact_first_tick':None,'exact_end_time':None,'complete_effective_values':None,
        'parameters_applied_to_prediction':False,'official_portrait_added':False}
    return result

def reference_text(reference,technical=False):
    if reference is None:return ''
    profile=reference['profile'];binding=reference['binding'];doc=profile['documentation']
    lines=['【辅助单位机制参考】','以下是公开说明与已核对的固定原件声明，当前完整脚本和实际触发仍未闭合。']
    lines.extend('• '+text for text in doc['facts'])
    if binding['source_constructor_mode']=='stage_constructor':
        lines.append('• 本关使用独立构造的专有配置；持续、爆炸等参数须按本关声明核对。')
    if doc.get('shared_prefab_document_only'):
        lines.append('• 原数据库明确绑定到同一预制体；本条派生参数保留，不继承公开原型的数值默认项。')
    lines.append('实际附着、当前目标、首次触发、结束相位和完整有效数值：未知。此资料不计入预计面板。')
    if technical:
        lines.extend(['','原件构造模式：'+binding['source_constructor_mode'],
            '原件预制体绑定：'+binding['prefab_key'],
            '本关原黑板声明（不表示实际初始化或最终效果）：'+json.dumps(binding['declared_talent_blackboard'],ensure_ascii=False),
            '选定原预制体组件：'+json.dumps([{'object':v['game_object_name'],'type':v['class_name'],'properties_hash':v['properties_hash']}
                for v in profile['native_prefab']['components']],ensure_ascii=False),
            '原关卡SHA256：'+binding['level_source_sha256'],
            '静态原包SHA256：'+profile['native_prefab']['bundle_sha256'],
            '公开说明：'+doc['url'],
            '缺图保持：未取得对应头像；公开通用占位符没有作为此单位图片。'])
    return '\n'.join(lines)
