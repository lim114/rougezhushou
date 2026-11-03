"""Create an external presentation-only draft from the sealed section-055 copy."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'p2-after-055-audit/derived-report/frozen'
DRAFT = ROOT / 'draft'
path = DRAFT / 'rouge/reporting.py'
before = (BASE / 'rouge/reporting.py').read_text(encoding='utf-8')
start = before.index("    subtotals=result.get('known_damage_subtotals')")
end = before.index("    healing_subtotals=result.get('known_healing_subtotals')", start)
replacement = '''    subtotals=result.get('known_damage_subtotals')
    if subtotals:
        generic_note='这些数值只包含已保留的本体来源参考，不含未核验的次生事件，不能当作完整输出。'
        river_note='这些数值不包含河谷祭祈未排程的额外持续伤害，不能当作完整总伤或完整 DPS。'
        subtotal_notes=['这些数值仅包含可确定法伤，不含持续损伤及受其影响的未知爆发，不能当作完整总伤或完整 DPS。'
            if neural_skill else '这些数值仅包含已排程的本体法伤，不含诱饵持续效果和受其影响的未知爆发，不能当作完整输出。'
            if bait_reference else generic_note
            if amiya_continuous or wisdel or mizuki or mizuki_amb_y or ines_dot or manual_close or liftoff or snow or unbound or external or chen_phase or result.get('drone_lifecycle_reference') or binding or incoming else
            river_note if neural_reference else generic_note]
        if binding:
            subtotal_notes.append('暗夜回声的束缚倍率首次生效与刷新顺序尚未核验；小计不含受其影响的未知神经爆发。')
        if incoming:
            subtotal_notes.append('堕梦的目标普通攻击次数没有事件时刻；小计不含受其影响的未知神经爆发。')
        if neural_reference and subtotal_notes[0]!=river_note:
            subtotal_notes.append(river_note)
        sections.append(section('known_damage_subtotals','已建模伤害小计',[
            metric('cast','单次技能已计伤害小计',subtotals['total_damage']),
            metric('window','观察窗口已计伤害小计',subtotals['window_damage']),
            metric('cycle','本轮周期已计伤害小计',subtotals['cycle_damage']),
            metric('cycle_dps','已计部分本轮周期 DPS',subtotals['cycle_dps'],'伤害/秒')],subtotal_notes))
'''
path.write_text(before[:start]+replacement+before[end:],encoding='utf-8',newline='')
(ROOT / 'reporting.baseline-055.py').write_bytes((BASE / 'rouge/reporting.py').read_bytes())
(ROOT / 'reporting.draft-055.py').write_bytes(path.read_bytes())
manifest=json.loads((ROOT.parent / 'p2-after-055-audit/derived-report/freeze-manifest.json').read_text())
assert hashlib.sha256((BASE / 'rouge/reporting.py').read_bytes()).hexdigest()==manifest['files']['rouge/reporting.py']
(ROOT / 'draft-freeze-055.json').write_text(json.dumps({'head':manifest['head'],
    'baseline_directory':str(BASE),'draft_directory':str(DRAFT),
    'baseline_reporting_sha256':hashlib.sha256((BASE / 'rouge/reporting.py').read_bytes()).hexdigest(),
    'draft_reporting_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'tracked_repository_edited':False,'baseline_manifest_reused':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared external presentation-only draft against archived section-055 source.')
