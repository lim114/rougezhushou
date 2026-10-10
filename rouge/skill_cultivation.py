"""Explicit read-source selection and skill qualification explanations.

The default rank is the existing UI policy. An optional account reference is a
user-selected offline simulation input; it never changes account/run records,
fills a missing run fact or truncates mastery to a common skill rank. Original
training requirements are not reinterpreted as current-use restrictions.
"""
from functools import lru_cache
import json
from pathlib import Path


_SOURCE_LABELS = {
    'run_confirmed': '本局读取',
    'account_reference': '账号档案参考，本局未确认',
    'preview_unconfirmed': '未确认，档案预览',
    'manual_account_reference': '已选账号等级作局外模拟，本局未确认',
}


@lru_cache(maxsize=1)
def _source_data():
    return json.loads((Path(__file__).parent / 'data' / 'skill-cultivation-reference.json')
                      .read_text(encoding='utf-8'))


def _rank(record, skill):
    ranks = record.get('skill_ranks', {})
    return (ranks.get(str(skill), ranks.get(skill)),
            str(skill) in ranks or skill in ranks)


def select_rank(profile, skill, elite, *, state=None, account=None, account_reference=False):
    """Return the original rank or an explicitly selected, compatible reference.

    Inputs are already qualified public UI views. The optional account branch
    has its own narrow guards because only that new branch consumes its value.
    Existing default state leaves, rank defaults and numerical gates stay as-is.
    """
    state, account = state or {}, account or {}
    if profile is None or type(skill) is not int or not 1 <= skill <= len(profile['skills']):
        return {'rank': None, 'source': 'preview_unconfirmed', 'known': False,
                'account_usable': False, 'account_rank': None,
                'account_reason': '请先选择当前开放的技能。', 'manual_reference_applied': False}
    rank, known = _rank(state, skill)
    baseline = rank if known else 10 if elite == 2 else 7
    source = ('run_confirmed' if state.get('scope') == 'run' else 'account_reference') if known else 'preview_unconfirmed'
    reference, reference_known = _rank(account, skill)
    invalid = account.get('invalid_skill_ranks', ())
    selected = profile['skills'][skill - 1]
    if not reference_known or str(skill) in invalid or skill in invalid:
        reason = '账号档案没有该技能的有效已读等级。'
    elif type(reference) is not int or not 1 <= reference <= min(10, len(selected['levels'])):
        reason = '账号档案等级不符合当前技能的整数范围。'
    elif selected.get('unlock_elite', skill - 1) > elite:
        reason = '当前精英阶段尚未开放该技能，不能选择账号等级参考。'
    elif elite < 2 and reference > 7:
        reason = '账号等级包含专精；当前精英阶段不能采用，且不会自动改成7级。'
    else:
        reason = ''
    applied = bool(account_reference and not reason)
    return {'rank': reference if applied else baseline,
            'source': 'manual_account_reference' if applied else source,
            'known': known, 'account_usable': not reason,
            'account_rank': reference if reference_known else None,
            'account_reason': reason, 'manual_reference_applied': applied}


def rank_label(selection):
    rank = selection['rank']
    if rank is None:
        return '无可用技能'
    text = f'等级 {rank}' if rank <= 7 else f'专精 {rank - 7}'
    # Keep the old label byte-for-byte unless the user explicitly chooses the
    # new account simulation. Detailed default provenance is in the new row.
    suffix = ('（账号等级参考，局外模拟）' if selection['manual_reference_applied'] else
              '（读取）' if selection['known'] else '（未确认，档案预览）')
    return text + suffix


def explanation(operator, profile, skill, elite, selection):
    """Bind original coordinates to the current, unchanged numerical policy.

    Missing patch-form originals remain missing. A training gate or a recruit
    upper-bound parameter never proves E0 common-rank use, native attachment or
    a current game's actual state. This row contains only the selected skill.
    """
    if profile is None or selection['rank'] is None:
        return None
    rank = selection['rank']
    selected = profile['skills'][skill - 1]
    source = _source_data()
    original = source['operators'].get(operator)
    bound = bool(original and original['native_id'] == profile['id'] and
                 len(original['skills']) == len(profile['skills']) and
                 all(raw['skillId'] == current['id'] and
                     int(raw['unlockCond']['phase'][-1]) == current.get('unlock_elite', index)
                     for index, (raw, current) in enumerate(zip(original['skills'], profile['skills']))))
    training = None
    if bound and type(rank) is int and 2 <= rank <= 7:
        training = {'kind': 'common_upgrade',
                    'path': f'{original["native_id"]}.allSkillLvlup[{rank - 2}].unlockCond',
                    'raw': dict(original['allSkillLvlup'][rank - 2]['unlockCond'])}
    elif bound and type(rank) is int and 8 <= rank <= 10:
        training = {'kind': 'mastery_upgrade',
                    'path': f'{original["native_id"]}.skills[{skill - 1}].levelUpCostCond[{rank - 8}].unlockCond',
                    'raw': dict(original['skills'][skill - 1]['levelUpCostCond'][rank - 8]['unlockCond'])}
    policy_met = (selected.get('unlock_elite', skill - 1) <= elite and not (elite < 2 and rank > 7))
    return {'operator': operator, 'skill': skill, 'rank': rank, 'elite': elite,
            'rank_source': selection['source'], 'manual_reference_applied': selection['manual_reference_applied'],
            'model_gate_met': policy_met, 'skill_unlock_elite': selected.get('unlock_elite', skill - 1),
            'original_source_status': 'located' if bound else 'missing',
            'skill_original_gate': dict(original['skills'][skill - 1]['unlockCond']) if bound else None,
            'training_requirement': training,
            'topic': 'rogue_6', 'recruit_upper_bounds': {
                key: dict(value) for key, value in source['recruit_upper_bounds']['rogue_6'].items()},
            'e0_common_use_verified': None if elite == 0 and 5 <= rank <= 7 else 'not_applicable',
            'actual_activation_verified': None, 'account_training_verified': None,
            'arithmetic_changed_by_explanation': False}


def format_explanation(row):
    if row is None:
        return ''
    lines = ['本次技能等级来源：' + _SOURCE_LABELS[row['rank_source']] + '。']
    if row['manual_reference_applied']:
        lines.append('仅选择已读账号等级进行局外模拟；本局技能记录不变。取消勾选可恢复本局读取或原预览。')
    lines.append(f'当前计算开放门：S{row["skill"]}从精英{row["skill_unlock_elite"]}开放；专精8–10需精英2。' +
                 ('当前测算条件满足既有计算门。' if row['model_gate_met'] else '当前条件未满足；本行不扩大开放资格。'))
    if row['original_source_status'] != 'located':
        lines.append('该职业形态的固定原始训练资料未定位；不借用其他职业的训练门。')
    elif row['training_requirement']:
        gate = row['training_requirement']['raw']
        name = '公共等级升级' if row['training_requirement']['kind'] == 'common_upgrade' else '所选技能专精训练'
        lines.append(f'原表{name}门：精英{int(gate["phase"][-1])} Lv{gate["level"]}。这是训练条件，不作为当前形态使用资格的新判断。')
    else:
        lines.append('当前为公共等级1；本行不添加额外升级条件。')
    bounds = row['recruit_upper_bounds']
    first, advanced = bounds['0'], bounds['1']
    lines.append('黑流树海原表招募阶段上限参考：阶段0精英' + first['evolvePhase'][-1] +
                 f'、公共{first["skillLevel"]}级、专精{first["skillSpecializeLevel"]}；阶段1精英' +
                 advanced['evolvePhase'][-1] + f'、公共{advanced["skillLevel"]}级、专精{advanced["skillSpecializeLevel"]}。上限参数不填补账号或本局等级。')
    if row['e0_common_use_verified'] is None:
        lines.append('精英0受限形态使用已培养公共5–7级的肉鸽规则仍未核验；当前等级仅按既有局外测算口径展示。')
    lines.append('以上资料与已读等级不确认实际施放、原生附着或本局未观察到的培养。')
    return '\n'.join(lines)
