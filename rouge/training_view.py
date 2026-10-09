"""Source-only proposal for qualification before the existing UI consumes state.

This file has not been imported or executed by its author. It is not a RunState
schema, a time policy, a numerical model, or a repair of a persisted record.
Root must bind the actual 98/99 sources and run the accompanying acceptance plan.
"""
import time

from .account_cache import _record_issue
from .operator_summary import format_operator_observation


def spinbox_level_usable(value):
    """UI-binding qualification, not an account cultivation range.

    Root's actual Wine Qt6.9.3 probe proves integer/bool and finite fractional
    inputs can be truncated and clamped, while int32 overflows cannot enter
    setValue. The supplementary actual Wine probe also confirms safe .1/.5/.9
    outside the raw int32 limits when truncation still yields an int32 value.
    These are UI binding limits, not a new game-level schema or normalization.
    """
    if not isinstance(value, (int, float)):
        return False
    try:
        integer = int(value)
    except (OverflowError, ValueError):
        return False
    return -(2 ** 31) <= integer <= 2 ** 31 - 1


def run_operator_metadata(member, *, enabled=True):
    """Keep existing present/current-run gates separate from cultivation.

    This is an opaque original reference, not a new metadata schema or copy.
    A bad training value does not revoke independent recruitment/buff evidence.
    """
    if (not enabled or not member or not member.get('present', True)
            or member.get('scope') != 'run'):
        return {}
    return member


def training_view_issue(op, state, profiles, implemented_ids, *, use_record_level=True):
    """Use the existing cultivation policy on only the effective UI inputs.

    The caller already removes invalid run fields/ranks. Account-only scope and
    timestamp rules must not be applied to this UI view. The exact existing UI
    timestamp conversion accepts None; do not turn it into a new damage rule.
    Level comes from QSpinBox in training_conditions. Its existing integer
    clamping is separate from account-cache validation and is preserved here.
    """
    if op not in profiles:
        return None
    if not isinstance(state, dict):
        return '记录结构'
    fields = state.get('fields', {})
    if not isinstance(fields, dict):
        return '培养字段'
    checked_fields = dict(fields)
    if 'level' in checked_fields and use_record_level:
        level = checked_fields['level']
        if not spinbox_level_usable(level):
            return '等级'
    # training_conditions always consumes the widget's integer value. A saved
    # level is relevant only when update_operator will set that widget from it.
    checked_fields.pop('level', None)
    # The selected catalog key is already the UI's authoritative identity.
    # Implemented calculation does not consume optional member id metadata;
    # do not turn the account cache's identity rule into a new RunState schema.
    checked = {**state, 'id': op, 'scope': 'operator_profile', 'fields': checked_fields}
    checked.pop('captured_at', None)
    issue = _record_issue(op, checked, profiles, implemented_ids)
    if issue:
        return issue
    try:
        time.strftime('%H:%M:%S', time.localtime(state.get('captured_at', 0)))
    except (OverflowError, OSError, TypeError, ValueError):
        return '读取时间'
    return None


def select_training_view(op, account, member, profiles, implemented_ids, *, use_record_level=True):
    """Prefer run facts and qualify their actual mixture before returning it.

    Return a presentation notice without changing either stored record/file.
    A failed combination does not prove that a separately valid file is damaged.
    Unknown extras remain shallow, opaque references as in the existing method.
    """
    if not member or not member.get('present', True):
        return {'state': account, 'notice': '', 'selection': 'account'}
    current = {key: value for key, value in member.get('fields', {}).items()
               if key not in member.get('invalid_fields', [])}
    ranks = {key: value for key, value in member.get('skill_ranks', {}).items()
             if key not in member.get('invalid_skill_ranks', [])}
    combined = {**account, **member,
                'fields': {**account.get('fields', {}), **current},
                'skill_ranks': ranks, 'run_confirmed_fields': list(current)}
    issue = training_view_issue(op, combined, profiles, implemented_ids,
                                use_record_level=use_record_level)
    if not issue:
        return {'state': combined, 'notice': '', 'selection': 'run_and_account'}
    run_only = {**member, 'fields': current, 'skill_ranks': ranks,
                'run_confirmed_fields': list(current)}
    if not training_view_issue(op, run_only, profiles, implemented_ids,
                               use_record_level=use_record_level):
        return {'state': run_only,
                'notice': '账号参考与本局培养条件不兼容；继续使用本局已确认字段，缺失项使用标注的档案预览。',
                'selection': 'run_without_account'}
    return {'state': account,
            'notice': f'本局当前培养输入的{issue}不可用；暂用标注的账号参考或档案预览，原本局记录未修改。',
            'selection': 'account_after_unusable_run'}


def format_run_training_observation(op, member):
    """Guard the separate raw-run summary path by its actual formatter call.

    This path does not call the calculation API or adopt the account cache's
    numerical schema. The already selected catalog key supplies display identity;
    original member metadata and all stored leaves remain untouched.
    """
    try:
        return format_operator_observation({**member, 'id': op})
    except (KeyError, TypeError, ValueError, OverflowError):
        return '本局培养记录的部分读取值暂不可显示；原记录未修改，请重新读取相应培养页面确认。'
