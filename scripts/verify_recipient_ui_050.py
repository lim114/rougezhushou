"""Isolated Qt recipient/inventory wiring; no live sample or chat request."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import copy
import hashlib
import json
import sys
import tempfile
import time
import traceback
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication, QScrollArea

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_relic_ui_025 import OfflineWindow, module
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from rouge.run_state import RunState


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    start = time.perf_counter()
    out = ROOT / '.cache/recipient-050'
    out.mkdir(parents=True, exist_ok=True)
    source_names = ('rouge/app.py', 'rouge/relics.py', 'rouge/reporting.py', 'rouge/run_state.py',
                    'rouge/offline_scope.py', 'rouge/data/relic-mechanics.json',
                    'scripts/verify_recipient_ui_050.py', 'scripts/verify_relic_ui_025.py')
    source_hashes = {name: sha(ROOT / name) for name in source_names}
    cases = []
    screenshots = []
    counter = 0
    last_input = []
    original_calculate = module.calculate_damage
    def tracked_calculate(value):
        last_input[:] = [copy.deepcopy(value)]
        return original_calculate(value)
    module.calculate_damage = tracked_calculate
    with tempfile.TemporaryDirectory() as folder:
        isolated = Path(folder)
        module.RUN_STATE = isolated / 'run.json'
        module.OPERATOR_STATE = isolated / 'operators.json'
        module.SETTINGS = isolated / 'settings.json'
        backend = module.DesktopBackend
        module.DesktopBackend = lambda _path, callback: backend(isolated / 'chat', callback)
        app = QApplication([])
        fid = QFontDatabase.addApplicationFont(str(Path(os.environ['WINDIR']) / 'Fonts/msyh.ttc'))
        assert fid >= 0
        app.setFont(QFont(QFontDatabase.applicationFontFamilies(fid)[0], 9))
        window = OfflineWindow()
        window.resize(1300, 1000)
        window.show()
        window.centralWidget().setCurrentIndex(1)

        def chosen_relics(rids):
            window.relic_list.blockSignals(True)
            for i in range(window.relic_list.count()):
                item = window.relic_list.item(i)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in rids
                                   else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False)

        def scenario(op, rid, bids=(), complete=False):
            nonlocal counter
            counter += 1
            profile = module.catalog()['operators'][op]
            window.run = RunState(isolated / f'case-{counter}.json')
            member = {'id': op, 'scope': 'run', 'fields': {'elite': 2,
                'level': profile['phases'][2]['max_level'], 'trust': 100, 'potential': 1,
                'module_id': None, 'module_level': 0, 'selected_skill': 1},
                'skill_ranks': {'1': 10}, 'char_buff_ids': list(bids), 'char_buffs_complete': complete}
            window.run.apply({'operators': [member], 'relics': {'ids': [rid],
                'icons': [{'id': rid, 'candidates': [rid], 'confirmed': True}],
                'count': 1, 'source': 'synthetic_held_bar'}}, window.run.state['started_at'] + 1)
            window.use_run_training.setChecked(True)
            window.refresh_operator_overview()
            window.select_operator(op)
            window.skill.setCurrentIndex(window.skill.findData(1))
            window.auto_relics.setChecked(False)
            window.target_buff_test.setChecked(False)
            chosen_relics([rid])
            window.calculate()
            if not window.damage_result and rid == 'rogue_6_relic_assign_10' and 'rogue_6_from_relic_10' in bids:
                assert '指中狼禁止开启技能' in window.damage_text.toPlainText()
                return {'scenario': copy.deepcopy(last_input[0]), 'forbidden': True}
            assert window.damage_result, window.damage_text.toPlainText()
            return window.damage_result

        def parent_record(payload, rid):
            return next(r for r in payload['result']['relic_resolution']['records'] if r['id'] == rid)

        def screenshot(name):
            app.processEvents()
            scroll = next(s for s in window.findChildren(QScrollArea) if s.isAncestorOf(window.target_buff_status))
            scroll.ensureWidgetVisible(window.target_buff_status, 30, 55)
            text = window.damage_text.toPlainText()
            pos = text.find('本局藏品读取未完整') if name == 'inventory-unread.png' else text.find('藏品核验')
            if pos >= 0:
                cursor = window.damage_text.textCursor()
                cursor.setPosition(pos)
                window.damage_text.setTextCursor(cursor)
                window.damage_text.centerCursor()
            app.processEvents()
            path = out / name
            assert window.grab().save(str(path))
            screenshots.append(path)

        try:
            assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
            parents = {rid: data for rid, data in mechanics()['relics'].items() if data.get('recipient_binding')}
            assert len(parents) == 7, len(parents)
            for rid, data in parents.items():
                bid = data['recipient_binding']['char_buff_ids'][0]
                profession = mechanics()['char_buffs'][bid]['required_profession']
                op = 'char_133_mm' if profession == 'sniper' else 'char_1029_yato2' if profession == 'special' else 'mechanist'
                payload = scenario(op, rid)
                record = parent_record(payload, rid)
                assert record['recipient_binding']['state'] == 'unknown', (rid, record)
                assert record['status'] == 'incomplete' and '当前干员强化归属' in record['missing_conditions']
                assert payload['scenario']['char_buffs_complete'] is False
                assert not record['applied']
                assert '当前干员强化归属' in window.damage_text.toPlainText()
                cases.append({'parent': rid, 'operator': op, 'state': 'unknown', 'passed': True})

                payload = scenario(op, rid, [bid, bid], False)
                reference_args = copy.deepcopy(payload['scenario'])
                reference_args['relic_ids'] = []
                if payload.get('forbidden'):
                    assert payload['scenario']['char_buff_ids'] == [bid]
                    try:
                        calculate_damage(reference_args)
                    except ValueError as error:
                        assert str(error) == window.damage_text.toPlainText()
                    else:
                        raise AssertionError('The verified forbidden buff must also prevent its buff-only skill calculation.')
                    cases.append({'parent': rid, 'operator': op, 'state': 'present_skill_forbidden_once', 'passed': True})
                else:
                    record = parent_record(payload, rid)
                    assert record['recipient_binding']['state'] == 'confirmed' and record['status'] == 'bound'
                    assert not record['applied'], record
                    bound = [r for r in payload['result']['relic_resolution']['records'] if r['id'] == bid]
                    assert len(bound) == 1 and bound[0]['recipient'] == op
                    reference = calculate_damage(reference_args)
                    for key in ('base_stats', 'skill'):
                        assert payload['result']['estimate'][key] == reference['estimate'][key], (rid, key)
                    for key in ('total_damage', 'total_healing'):
                        assert payload['result'].get(key) == reference.get(key), (rid, key)
                    assert '领取干员：' in window.damage_text.toPlainText()
                    cases.append({'parent': rid, 'operator': op, 'state': 'present_once', 'passed': True})
                if rid == 'rogue_6_relic_assign_9':
                    screenshot('confirmed-recipient.png')

                payload = scenario(op, rid, [], True)
                record = parent_record(payload, rid)
                assert payload['scenario']['char_buffs_complete'] is True
                assert record['recipient_binding']['state'] == 'absent' and record['status'] == 'inapplicable'
                assert not record['missing_conditions'] and not record['applied']
                assert '已核对：无个人强化' in window.target_buff_status.text()
                cases.append({'parent': rid, 'operator': op, 'state': 'complete_absent', 'passed': True})

                if profession:
                    payload = scenario('mechanist', rid)
                    record = parent_record(payload, rid)
                    assert record['recipient_binding']['state'] == 'absent' and record['status'] == 'inapplicable'
                    assert bid not in [window.target_buff_list.item(i).data(Qt.ItemDataRole.UserRole)
                                       for i in range(window.target_buff_list.count())]
                    cases.append({'parent': rid, 'operator': 'mechanist', 'state': 'profession_mismatch', 'passed': True})

            # An account observation cannot assert this run's personal list complete.
            rid = 'rogue_6_relic_assign_9'
            scenario('mechanist', rid, [], True)
            window.operator_observations['mechanist'] = {'id': 'mechanist', 'scope': 'account',
                'fields': copy.deepcopy(window.run.state['operators']['mechanist']['fields']),
                'skill_ranks': {'1': 10}, 'char_buff_ids': ['rogue_6_from_relic_9'], 'char_buffs_complete': True}
            window.use_run_training.setChecked(False)
            window.calculate()
            assert window.damage_result
            assert window.damage_result['scenario']['char_buff_ids'] == []
            assert window.damage_result['scenario']['char_buffs_complete'] is False
            assert parent_record(window.damage_result, rid)['recipient_binding']['state'] == 'unknown'
            cases.append({'parent': rid, 'operator': 'mechanist', 'state': 'account_is_not_run_proof', 'passed': True})
            screenshot('unknown-recipient.png')

            # One member's binding is not inherited by a different recruited member.
            scenario('mechanist', rid, ['rogue_6_from_relic_9'], True)
            other = 'kaltsit'
            window.run.apply({'operators': [{'id': other, 'scope': 'run',
                'fields': {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1,
                           'module_id': None, 'module_level': 0, 'selected_skill': 1},
                'skill_ranks': {'1': 10}, 'char_buff_ids': [], 'char_buffs_complete': True}]},
                window.run.state['started_at'] + 2)
            window.refresh_operator_overview()
            window.select_operator(other)
            window.calculate()
            assert window.damage_result['scenario']['char_buff_ids'] == []
            assert parent_record(window.damage_result, rid)['recipient_binding']['state'] == 'absent'
            assert window.run.state['operators']['mechanist']['char_buff_ids'] == ['rogue_6_from_relic_9']
            cases.append({'parent': rid, 'operator': other, 'state': 'different_member_not_recipient', 'passed': True})

            # Contradictory ambiguous partial artwork revokes proof but preserves the old item.
            scenario('mechanist', rid)
            at = window.run.state['started_at'] + 2
            identities = [rid, 'rogue_6_relic_cargo_1', 'rogue_6_active_tool_5']
            window.apply_run_observation({'relics': {'ids': identities[:2], 'icons': [
                {'id': item, 'candidates': [item], 'confirmed': True} for item in identities],
                'count': 3, 'source': 'synthetic_complete_bar'}}, at)
            assert window.run.inventory_status()['complete']
            foreign = {'id': 'rogue_6_relic_legacy_22',
                'candidates': ['rogue_6_relic_legacy_22', 'rogue_6_relic_legacy_23'], 'confirmed': False}
            window.apply_run_observation({'relics': {'ids': [], 'icons': [foreign],
                'count': 3, 'source': 'synthetic_partial_bar'}}, at + 1)
            window.auto_relics.setChecked(True)
            window.calculate()
            assert not window.run.inventory_status()['complete']
            assert rid in window.run.held_relic_ids()
            assert '本局藏品读取未完整' in window.damage_text.toPlainText()
            assert '变更待核对或尚未读全' in window.run_summary.text()
            cases.append({'parent': rid, 'operator': 'mechanist', 'state': 'inventory_unread_warning', 'passed': True})
            screenshot('inventory-unread.png')

            assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
            assert not (isolated / 'chat').exists() and not (isolated / 'settings.json').exists()
            assert source_hashes == {name: sha(ROOT / name) for name in source_names}, 'Source changed during UI validation.'
            receipt = {'version': '0.50.0', 'window_title': window.windowTitle(), 'passed': True,
                'verified_at': time.time(), 'seconds': round(time.perf_counter() - start, 3),
                'parents_checked': len(parents), 'cases': cases, 'screenshots': {
                    p.relative_to(ROOT).as_posix(): sha(p) for p in screenshots},
                'private_state_isolated': True, 'game_captures': 0, 'game_actions': 0, 'chat_requests': 0,
                'source_sha256': source_hashes,
                'limits': ['Offscreen real Qt with temporary synthetic run observations; not automatic recipient acquisition or live inventory coverage.',
                           'Recipient belongs only to the current operator; complete absent evidence belongs only to run scope.']}
            (ROOT / 'UI_0.50_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps({'passed': True, 'parents_checked': len(parents), 'cases': len(cases),
                              'screenshots': len(screenshots), 'window_title': window.windowTitle()}, ensure_ascii=True))
        except Exception:
            attempt = len(list(out.glob('failed-attempt-*.json'))) + 1
            failure = {'passed': False, 'cases_completed': cases, 'traceback': traceback.format_exc(),
                       'source_sha256_start': source_hashes, 'window_title': window.windowTitle()}
            (out / f'failed-attempt-{attempt}.json').write_text(json.dumps(failure, ensure_ascii=False, indent=2), encoding='utf-8')
            raise
        finally:
            window.close()
            app.processEvents()


if __name__ == '__main__':
    main()
