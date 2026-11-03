"""Read-only account references and session-local protection of damaged files.

This boundary uses the profiles already selected by the UI. It does not validate
or modify RunState, and it does not change the calculation API's input rules.
"""
import json
import math
import time
from copy import deepcopy
from pathlib import Path


FIELD_LABELS = {'elite': '精英阶段', 'level': '等级', 'trust': '信赖',
                'potential': '潜能', 'module_id': '模组', 'module_level': '模组阶段'}
RUN_METADATA = frozenset(('recruitment_kind', 'advanced', 'run_confirmed_fields',
                         'char_buff_ids', 'char_buffs_complete', 'char_buff_absent_ids',
                         'char_buff_pending_ids'))


def _integer(value, minimum, maximum):
    return isinstance(value, int) and not isinstance(value, bool) and minimum <= value <= maximum


def _timestamp(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        if not math.isfinite(value):
            return False
        time.strftime('%H:%M:%S', time.localtime(value))
    except (OverflowError, OSError, TypeError, ValueError):
        return False
    return True


def _record_issue(op, record, profiles, implemented_ids):
    # Future catalog entries are opaque here: the current app cannot consume them.
    if op not in profiles:
        return None
    if not isinstance(record, dict):
        return '记录结构'
    if not isinstance(record.get('id'), str) or record['id'] != op:
        return '干员身份'
    for key in ('fields', 'skill_ranks', 'sources', 'field_times', 'skill_times'):
        if key in record and not isinstance(record[key], dict):
            return {'fields': '培养字段', 'skill_ranks': '技能等级', 'sources': '读取来源',
                    'field_times': '字段读取时间', 'skill_times': '技能读取时间'}[key]
    if 'captured_at' in record and not _timestamp(record['captured_at']):
        return '读取时间'
    if record.get('scope') == 'run':
        return '本局来源'
    try:
        set(record.get('invalid_fields', []))
    except TypeError:
        return '培养字段读取状态'
    try:
        iter(record.get('invalid_skill_ranks', []))
    except TypeError:
        return '技能读取状态'
    try:
        if any(not isinstance(key, str) for key in record.get('missing_fields', [])):
            return '未读取字段状态'
    except TypeError:
        return '未读取字段状态'

    profile = profiles[op]
    fields = record.get('fields', {})
    elite = fields.get('elite', len(profile['phases']) - 1)
    if not _integer(elite, 0, len(profile['phases']) - 1):
        return FIELD_LABELS['elite']
    maximum = profile['phases'][elite]['max_level']
    if not _integer(fields.get('level', maximum), 1, maximum):
        return FIELD_LABELS['level']
    trust = fields.get('trust', 100)
    try:
        if not math.isfinite(trust) or not 0 <= trust <= 100:
            return FIELD_LABELS['trust']
    except (TypeError, OverflowError):
        return FIELD_LABELS['trust']
    if not _integer(fields.get('potential', 1), 1, 6):
        return FIELD_LABELS['potential']
    module_id = fields.get('module_id')
    if module_id:
        module = next((module for module in profile['modules'] if module['id'] == module_id), None)
        if module is None:
            return FIELD_LABELS['module_id']
        if not _integer(fields.get('module_level', 0), 1, len(module['levels'])):
            return FIELD_LABELS['module_level']
        # The original catalog applies this valid module only after its unlock.

    ranks = record.get('skill_ranks', {})
    invalid_ranks = record.get('invalid_skill_ranks', [])
    for index, skill in enumerate(profile['skills'], 1):
        key = str(index)
        if key not in ranks and index not in ranks:
            continue
        rank = ranks.get(key, ranks.get(index))
        if skill.get('unlock_elite', index - 1) <= elite:
            if not _integer(rank, 1, min(10, len(skill['levels']))):
                return f'第{index}技能等级'
            if op in implemented_ids and elite < 2 and rank > 7:
                return f'第{index}技能专精'
        elif key not in invalid_ranks and rank is not None:
            # Locked ranks are formatter-only. Preserve values it already handles.
            try:
                if not rank <= 7:
                    rank - 7
            except (TypeError, ValueError):
                return f'第{index}技能等级'
    # selected_skill outside the unlocked GUI choices is an ignored preference;
    # the QComboBox supplies the actual integer skill used by the calculation.
    return None


class AccountCache:
    def __init__(self, path, profiles, implemented_ids=()):
        self.path = Path(path)
        self.profiles = profiles
        self.implemented_ids = frozenset(implemented_ids)
        self.records = {}
        self.issues = {}
        self.load_issue = None
        self.preserve_original = False
        try:
            decoded = json.loads(self.path.read_text(encoding='utf-8'))
        except FileNotFoundError:
            # A dangling symlink is an existing path. A failing lstat is unknown,
            # never evidence that it is safe to replace the original.
            try:
                self.path.lstat()
            except FileNotFoundError:
                return
            except OSError:
                pass
            self._protect('账号档案未能读取')
            return
        except (OSError, ValueError):
            self._protect('账号档案未能读取')
            return
        if not isinstance(decoded, dict):
            self._protect('账号档案结构不可用')
            return
        self.records = decoded
        self._screen_all()

    def _protect(self, issue=None):
        self.preserve_original = True
        if issue is not None:
            self.load_issue = issue

    def _screen_all(self):
        for op, record in self.records.items():
            issue = _record_issue(op, record, self.profiles, self.implemented_ids)
            if issue:
                self.issues[op] = issue
                self._protect()

    def view(self, op):
        if op not in self.profiles or op not in self.records:
            return {}
        if op in self.issues:
            return {}
        record = self.records[op]
        issue = _record_issue(op, record, self.profiles, self.implemented_ids)
        if issue:
            self.issues[op] = issue
            self._protect()
            return {}
        return {key: deepcopy(value) for key, value in record.items() if key not in RUN_METADATA}

    def notice(self, op, *, run_confirmed=False):
        issue = self.issues.get(op)
        if issue:
            text = f'账号参考的{issue}不可用；'
            text += '本局已确认培养继续使用。' if run_confirmed else '缺失项使用标注的档案预览。'
        elif self.load_issue:
            text = self.load_issue + '；'
            text += '本局已确认培养继续使用。' if run_confirmed else '未确认项使用标注的档案预览。'
        else:
            text = ''
        if self.preserve_original:
            text += ' 原账号档案文件已保留，本次不会自动覆盖。'
        return text.strip()

    def observe(self, operator, captured_at):
        if not isinstance(operator, dict):
            return False
        op = operator.get('id')
        if not isinstance(op, str) or op not in self.profiles or not _timestamp(captured_at):
            return False
        if _record_issue(op, operator, self.profiles, self.implemented_ids):
            return False
        saved = self.records.get(op, {})
        damaged = op in self.records and (op in self.issues or
                    _record_issue(op, saved, self.profiles, self.implemented_ids))
        if damaged:
            self._protect()
            saved = {}
        if not damaged and captured_at < saved.get('captured_at', 0):
            return False
        observed_fields = operator.get('fields', {})
        fields = {**saved.get('fields', {}), **observed_fields}
        ranks = {**{str(key): value for key, value in saved.get('skill_ranks', {}).items()},
                 **{str(key): value for key, value in operator.get('skill_ranks', {}).items()}}
        changed = (fields != saved.get('fields') or ranks != saved.get('skill_ranks')
                   or saved.get('scope') != operator.get('scope'))
        self.records[op] = {**deepcopy(operator), 'fields': deepcopy(fields),
                           'skill_ranks': deepcopy(ranks), 'captured_at': captured_at,
                           'sources': {**deepcopy(saved.get('sources', {})),
                                       **deepcopy(operator.get('sources', {}))},
                           'field_times': {**deepcopy(saved.get('field_times', {})),
                                           **{key: captured_at for key in observed_fields}},
                           'skill_times': {**deepcopy(saved.get('skill_times', {})),
                                           **{str(key): captured_at for key in operator.get('skill_ranks', {})}},
                           'merged_from_pages': True}
        if not _record_issue(op, self.records[op], self.profiles, self.implemented_ids):
            self.issues.pop(op, None)
        self._screen_all()
        if changed:
            self.save()
        return True

    def save(self):
        self._screen_all()
        if self.preserve_original:
            return False
        self.path.parent.mkdir(exist_ok=True)
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.records, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(self.path)
        return True
