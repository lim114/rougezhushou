"""Source preparation only. Root executes this stdlib-only saved-evidence auditor."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import traceback
from native_evidence import assert_native_equal as same, freeze, read_record, source_map

HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
RUNNERS = {112: 'c1f9c1dd06943c3099a36b4475db27cf72e18a28a27d30237544619c0ce93ea1',
           113: '5020397e44e59a791decadde41aba8d2560b735eb43b8bb8aa4a66dc59a26a09',
           114: '97731c090d7f7b4445be9a8f65b67cb777bef60e2566e6f6e21f41c44db8ecda'}
CLOCK_KEYS = ('initial_seconds', 'recharge_seconds', 'cycle_seconds', 'duration_seconds',
              'sp_recovery_per_second', 'mode')
VIEW_KEYS = ('subject', 'operator_summary', 'preview', 'observed_text', 'capture_status', 'stage_tooltip')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def json_file(path):
    raw = Path(path).read_bytes()
    return json.loads(raw), raw

def exact_true(value):
    assert value is True

def equal_flag(left, right):
    try:
        same(left, right)
        return True
    except AssertionError:
        return False

def load(section, folder, guard_path, phase):
    folder = Path(folder).resolve(); guard, guard_raw = json_file(guard_path)
    receipt, raw = json_file(folder / 'receipt.json')
    assert guard['section'] == section and receipt['phase'] == phase
    for key in ('passed', 'workflow_complete'):
        exact_true(receipt[key])
    assert not receipt.get('failure') and receipt['Qt_errors'] == [] and receipt['source_drift'] == []
    assert receipt['runner_sha256'] == RUNNERS[section] and receipt['native_helper_sha256'] == HELPER_SHA
    assert receipt['source_guard_sha256'] == sha(guard_raw)
    same(receipt['source_before'], guard['source_sha256'], 'guard source before')
    same(receipt['source_after'], guard['source_sha256'], 'guard source after')
    same(receipt['source_additional_before'], guard['source_additional_sha256'], 'CORE before')
    same(receipt['source_additional_after'], guard['source_additional_sha256'], 'CORE after')
    assert set(guard['source_additional_sha256']) == {'CORE_0.70_VERIFICATION.json'}
    assert type(receipt['source_count']) is int and receipt['source_count'] == len(guard['source_sha256'])
    assert receipt['actual_windows'] == 1 and receipt['private_state_access'] is False
    if section == 112:
        exact_true(receipt['observation_complete'])
        assert receipt['observation_only'] is (phase == 'original') and receipt['product_pass'] is (phase == 'candidate')
        assert receipt['game_OCR_chat_sampling_executed'] is False and receipt['native_Windows_verified'] is False
    else:
        assert receipt['game_chat_sampling_executed'] is False and receipt['native_windows_verified'] is False
    rows = receipt['records']; assert rows and type(rows) is list
    values = {}; positions = {}
    for number, ref in enumerate(rows, 1):
        assert ref['path'] == '%06d.pickle.gz' % number and ref['path'] not in values
        value = read_record(folder / 'records', ref)
        assert value['kind'] == ref['kind']
        for key in ('step', 'case', 'phase'):
            if key in ref:
                same(value[key], ref[key], 'saved active metadata')
        values[ref['path']] = value; positions[ref['path']] = number
    assert {p.name for p in (folder / 'records').iterdir()} == set(values)
    def get(ref, kind):
        name = ref['path']; assert name in values
        same(ref, rows[positions[name] - 1], 'reference must match entire ledger metadata')
        assert values[name]['kind'] == kind
        return values[name]
    numeric = [value for value in values.values() if value['kind'] in ('actual_calculate_result', 'actual_calculate_exception')]
    assert type(receipt['actual_numeric_calls']) is int and receipt['actual_numeric_calls'] == len(numeric)
    for value in numeric:
        same(value['after'], value['before'], 'whole saved numerical caller/context purity')
    return {'section': section, 'folder': folder, 'guard': guard, 'guard_raw': guard_raw,
            'receipt': receipt, 'receipt_sha256': sha(raw), 'values': values, 'positions': positions,
            'get': get, 'numeric': numeric}

def png(bundle, row):
    name = row['path']; assert type(name) is str and Path(name).name == name and name.endswith('.png')
    path = bundle['folder'] / name; assert not path.is_symlink()
    raw = path.read_bytes(); assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    assert raw[:8] == b'\x89PNG\r\n\x1a\n' and raw[12:16] == b'IHDR'
    width, height = struct.unpack('>II', raw[16:24]); assert width > 0 and height > 0
    return {'path': name, 'sha256': sha(raw), 'width': width, 'height': height}

def audit112(bundle, phase):
    receipt = bundle['receipt']; get = bundle['get']; values = list(bundle['values'].values())
    allowed = {'actual_calculate_result', 'actual_calculate_exception', 'actual_window_snapshot', 'actual_sample_received',
               'actual_reset_run', 'actual_sampling_tab_PNG', 'actual_close_direct_reload'}
    assert all(v['kind'] in allowed for v in values)
    steps = ('before_reset', 'after_reset', 'after_old_rejections', 'new_valid_sample')
    assert [r['step'] for r in receipt['snapshots']] == list(steps)
    snapshots = [get(r['snapshot'], 'actual_window_snapshot') for r in receipt['snapshots']]
    assert [v['step'] for v in snapshots] == list(steps)
    assert [r['path'] for r in receipt['records'] if r['kind'] == 'actual_window_snapshot'] == [r['snapshot']['path'] for r in receipt['snapshots']]
    pre, post, rejected, fresh = [v['value'] for v in snapshots]
    for value in (pre, post, rejected, fresh):
        assert tuple(value['views']) == VIEW_KEYS
    assert pre['run']['operators']['mechanist']['fields']['level'] == 20
    assert pre['run']['resources']['gold']['value'] == 10
    assert pre['views']['subject']['key'][:2] == ('operator', 'mechanist')
    assert pre['views']['preview']['image_png'] is not None
    assert json.loads(pre['views']['observed_text'])['page'] == 'crew'
    assert '最近节点详情' in pre['views']['stage_tooltip']
    assert post['run']['id'] != pre['run']['id'] and post['run']['operators'] == {} and post['run']['resources'] == {}
    assert post['observation'] is None
    account = pre['account']; account_disk = pre['disks']['account.json']
    same(account['mechanist']['fields'], {'elite': 2, 'level': 90, 'trust': 100, 'potential': 1,
        'module_id': None, 'module_level': 0}, 'accepted actual account profile')
    same(account['mechanist']['skill_ranks'], {'1': 10, '2': 10, '3': 10}, 'accepted account ranks')
    for value in (post, rejected, fresh):
        same(value['account'], account, 'whole original account retained')
        same(value['disks']['account.json'], account_disk, 'exact original account disk retained')
    resets = [v for v in values if v['kind'] == 'actual_reset_run']; assert len(resets) == 1
    same(resets[0]['before'], pre, 'saved reset before'); same(resets[0]['after'], post, 'saved reset after')
    samples = [v for v in values if v['kind'] == 'actual_sample_received']
    sample_steps = ('accepted_node_detail', 'accepted_old_crew', 'old_epoch_rejected', 'old_time_rejected', 'accepted_new_crew')
    assert [v['step'] for v in samples] == list(sample_steps)
    for value, expected in zip(samples, (False, False, True, True, False)):
        assert value['rejected_expected'] is expected
        if expected:
            same(value['after'], value['before'], 'exact refused-sample graph/disks/six views')
            same(value['before'], post, 'refused sample starts in saved reset graph')
    same(samples[1]['after'], pre, 'accepted old crew snapshot')
    same(rejected, post, 'snapshot after both old sample refusals')
    same(samples[-1]['before'], post, 'fresh sample starts after unchanged refusals')
    same(samples[-1]['after'], fresh, 'fresh sample captured graph')
    assert fresh['run']['id'] == post['run']['id']
    assert fresh['run']['operators']['mechanist']['fields']['level'] == 30 and fresh['run']['resources']['gold']['value'] == 2
    assert fresh['views']['subject']['key'][:2] == ('operator', 'mechanist') and fresh['views']['preview']['image_png'] is not None
    assert json.loads(fresh['views']['observed_text'])['run']['resources']['gold']['value'] == 2
    assert 'crew' in fresh['views']['capture_status'] and '等待新的页面采样' not in fresh['views']['capture_status']
    original_preserved = {key: equal_flag(post['views'][key], pre['views'][key]) for key in VIEW_KEYS}
    if phase == 'candidate':
        expected_views = {'subject': {'key': (None, None, ''), 'caption': '', 'image_png': None},
            'operator_summary': '本局已重置，等待新的干员页面读取；账号档案仍保留。',
            'preview': {'image_png': None, 'text': '本局尚未采样'}, 'observed_text': '',
            'capture_status': '已开始新局，等待新的页面采样；账号档案已保留。',
            'stage_tooltip': '本局节点详情尚未确认；可手动选择关卡进行局外预览。'}
        same(post['views'], expected_views, 'all six actual reset views')
        assert '待识别0帧' in snapshots[1]['sampling_status']
    close = get(receipt['close_reload'], 'actual_close_direct_reload')
    same(close['live'], fresh, 'actual close graph')
    expected_notice = '已恢复同一局的记忆；切换另一局时请手动点击“开始新局”。'
    same(close['restart_state']['notice'], expected_notice, 'exact original constructor recovery notice')
    expected_transition = {'key': 'notice', 'live': fresh['run']['notice'], 'restart': close['restart_state']['notice'],
        'expected_restart_literal': expected_notice, 'constructor_source_path': 'rouge/run_state.py',
        'constructor_source_sha256': bundle['guard']['source_sha256']['rouge/run_state.py']}
    same(close['notice_transition'], expected_transition, 'whole saved notice transition and constructor Source binding')
    normalized_restart = freeze(close['restart_state']); normalized_restart['notice'] = fresh['run']['notice']
    same(normalized_restart, fresh['run'], 'whole direct RunState reload except qualified constructor notice transition')
    same(close['restart_account'], account, 'direct original AccountCache reload')
    same(close['disks_after'], fresh['disks'], 'direct close/reload disks')
    assert len(receipt['pngs']) == 2
    pngs = []
    for row, name, value in zip(receipt['pngs'], (phase + '-after-reset.png', phase + '-new-sample.png'), (post, fresh)):
        assert row['path'] == name
        saved = get(row['snapshot'], 'actual_sampling_tab_PNG')
        same(saved['value'], value, 'sampling PNG bound saved graph')
        pngs.append(png(bundle, row))
    assert len([v for v in values if v['kind'] == 'actual_sampling_tab_PNG']) == 2
    assert len([v for v in values if v['kind'] == 'actual_close_direct_reload']) == 1
    return {'phase': phase, 'product_pass': phase == 'candidate', 'original_six_views_preserved_observations': original_preserved,
        'snapshots': len(snapshots), 'saved_records': len(values), 'actual_numeric_calls': len(bundle['numeric']),
        'saved_numeric_exceptions': sum(v['kind'] == 'actual_calculate_exception' for v in bundle['numeric']), 'PNGs': pngs,
        'sample_caller_initial_not_saved': True, 'sample_caller_independent_saved_purity_proven': False,
        'PNG_capture_independent_before_after_purity_proven': False,
        'scope': 'Each phase independently audited; original stale-view observations are not product success. No whole cross-run graph comparison.'}

def cast_fields(result):
    skill = result['estimate']['skill']
    keys = (*CLOCK_KEYS, 'total_damage', 'total_healing', 'phase_damage', 'phase_healing', 'cycle_damage',
        'cycle_healing', 'cycle_dps', 'cycle_hps', 'hit_counts', 'skill_attack', 'skill_attack_speed', 'skill_attack_speed_reference')
    return {'skill': {key: skill[key] for key in keys},
        'estimate_fields': {key: value for key, value in result['estimate'].items() if key == 'sp_events'},
        'timing_report': next(section for section in result['report']['sections'] if section['id'] == 'timing')}

def audit113(bundle):
    receipt = bundle['receipt']; get = bundle['get']; values = list(bundle['values'].values())
    allowed = {'actual_calculate_result', 'actual_calculate_exception', 'actual_UI_step', 'actual_public_fixture_loaded',
        'actual_three_formatter_group', 'actual_window_snapshot', 'actual_PNG_visible_damage_rows', 'actual_close_RunState_reload'}
    assert all(v['kind'] in allowed for v in values)
    for value in values:
        if value['kind'] == 'actual_UI_step':
            same(value['after']['joint'], value['before']['joint'], 'every actual UI-step joint purity')
        elif value['kind'] == 'actual_three_formatter_group':
            same(value['after'], value['before'], 'whole saved three-formatter joint purity')
    expected = [('window5-travel0', 5, 0), ('window60-travel0', 60, 0), ('window5-travel20', 5, 20), ('window60-travel20', 60, 20)]
    assert [(r['id'], r['window_seconds'], r['travel_seconds']) for r in receipt['rows']] == expected
    initial = get(receipt['initial'], 'actual_public_fixture_loaded'); snapshots = []; denominator_types = []
    assert len([v for v in values if v['kind'] == 'actual_public_fixture_loaded']) == 1
    assert [r['path'] for r in receipt['records'] if r['kind'] == 'actual_window_snapshot'] == [r['snapshot']['path'] for r in receipt['rows']]
    assert len({r['numeric']['path'] for r in receipt['rows']}) == 4
    for row, (identity, seconds, travel) in zip(receipt['rows'], expected):
        saved = get(row['snapshot'], 'actual_window_snapshot'); value = saved['value']; snapshots.append(value)
        numeric = get(row['numeric'], 'actual_calculate_result'); assert numeric['case'] == saved['case'] == identity
        assert bundle['positions'][row['numeric']['path']] < bundle['positions'][row['snapshot']['path']]
        caller = value['caller']; result = value['damage_result']['result']; skill = result['estimate']['skill']
        same(caller, numeric['before']['args'][0], 'whole actual UI caller to numeric caller')
        same(value['damage_result']['scenario'], caller, 'whole actual UI scenario')
        same(result, numeric['result'], 'whole actual numerical return to UI result')
        assert caller['operator'] == 'char_1041_angel2' and caller['skill'] == 1 and caller['timing_mode'] == 'frames'
        assert (caller['elite'], caller['level'], caller['skill_rank'], caller['trust'], caller['potential']) == (2, 1, 7, 0, 1)
        assert caller['module_id'] is None and caller['module_level'] == 0 and caller['continuous_attacks'] is True
        assert caller['relic_ids'] == [] and caller['enemy_defense'] == 0 and caller['enemy_resistance'] == 0
        assert 'base_attack' not in caller and 'target_enemy' not in caller and row['denominator_from_actual_UI'] is True
        same(caller['timing'], {'windup_frames': 0, 'recovery_frames': 0, 'projectile_travel_seconds': travel}, 'actual timing input')
        assert type(caller['window_seconds']) in (int, float) and caller['window_seconds'] == seconds
        assert type(skill['window_seconds']) in (int, float) and skill['window_seconds'] == caller['window_seconds'] and skill['mode'] == 'ammo'
        same(skill['window_dps'], result['total_damage'] / caller['window_seconds'], 'exact actual caller denominator DPS')
        same(skill['window_hps'], result['total_healing'] / caller['window_seconds'], 'exact actual caller denominator HPS')
        same(skill['window_healing'], result['total_healing'], 'actual healing numerator')
        metrics = {r['key']: r for r in next(s for s in result['report']['sections'] if s['id'] == 'damage')['metrics']}
        assert type(metrics['window_seconds']['value']) in (int, float) and metrics['window_seconds']['value'] == caller['window_seconds']
        same(metrics['window_damage']['value'], result['total_damage'], 'report actual damage numerator')
        same(metrics['window_dps']['value'], skill['window_dps'], 'report actual window average')
        times = [t for component in result['components'] for t in component.get('times_seconds', [])]
        assert all(0 <= t < caller['window_seconds'] for t in times)
        assert (result['total_damage'] == 0 and not times) if travel and seconds == 5 else (result['total_damage'] > 0 and bool(times))
        groups = [v for v in values if v['kind'] == 'actual_three_formatter_group' and v['case'] == identity]; assert len(groups) == 1
        group = groups[0]; same(group['texts'], value['texts'], 'whole three saved texts')
        same(group['after'], {'damage_result': value['damage_result'], 'joint': value['state_and_disks']}, 'formatter/snapshot complete graph')
        assert tuple(value['texts']) == ('estimate', 'default', 'technical') and all(type(t) is str for t in value['texts'].values())
        assert value['texts']['estimate'] == value['texts']['default'] and value['displayed_damage'] == value['texts']['default'].replace(chr(160), ' ')
        same(saved['cast'], cast_fields(result), 'saved full cast fields')
        same(value['state_and_disks'], initial['value'], 'every complete state/account/disk graph retained')
        denominator_types.append({'case': identity, 'caller': type(caller['window_seconds']).__name__,
            'skill': type(skill['window_seconds']).__name__, 'report': type(metrics['window_seconds']['value']).__name__})
    assert len([v for v in values if v['kind'] == 'actual_window_snapshot']) == 4
    assert len([v for v in values if v['kind'] == 'actual_three_formatter_group']) == 4
    assert len(receipt['pairs']) == 2
    for pair, travel, offset in zip(receipt['pairs'], (0, 20), (0, 2)):
        assert pair['travel_seconds'] == travel and pair['cast_and_SP_preserved'] is True and pair['observation_domain_checked'] is True
        same(pair['short_snapshot'], receipt['rows'][offset]['snapshot'], 'explicit short pair reference')
        same(pair['long_snapshot'], receipt['rows'][offset + 1]['snapshot'], 'explicit long pair reference')
        short, long = snapshots[offset:offset + 2]; adjusted = freeze(long['caller']); adjusted['window_seconds'] = short['caller']['window_seconds']
        same(adjusted, short['caller'], 'whole paired caller except requested actual window')
        same(cast_fields(long['damage_result']['result']), cast_fields(short['damage_result']['result']), 'whole cast/phase/cycle/SP/timing report preserved')
        same(short['state_and_disks'], long['state_and_disks'], 'paired complete graph')
    assert len(receipt['pngs']) == 2; pngs = []
    for row, identity, snapshot in zip(receipt['pngs'], ('window5-travel20', 'window60-travel20'), snapshots[2:]):
        assert row['path'] == identity + '.png'
        visual = get(row['visual'], 'actual_PNG_visible_damage_rows'); assert visual['case'] == identity
        same(visual['displayed_text'], snapshot['displayed_damage'], 'complete PNG-bound displayed text')
        same(visual['anchors'], ('【伤害输出】', '伤害观察窗口：', '窗口平均每秒伤害：'), 'exact visual anchors')
        blocks = visual['visible_blocks']; assert blocks and len(blocks) < 12
        assert visual['anchors'][0] in blocks[0] and visual['anchors'][2] in blocks[-1] and any(visual['anchors'][1] in b for b in blocks)
        all_blocks = visual['displayed_text'].split('\n'); assert any(all_blocks[i:i + len(blocks)] == blocks for i in range(len(all_blocks)))
        vx, vy, vw, vh = visual['viewport_rect']; assert vw > 0 and vh > 0
        assert len(visual['cursor_rects']) == len(blocks) * 2
        for rx, ry, rw, rh in visual['cursor_rects']:
            assert rw > 0 and rh > 0 and vx <= rx and vy <= ry and rx + rw <= vx + vw and ry + rh <= vy + vh
        pngs.append(png(bundle, row))
    assert len([v for v in values if v['kind'] == 'actual_PNG_visible_damage_rows']) == 2
    close = get(receipt['close_reload'], 'actual_close_RunState_reload')
    same(close['live_before'], initial['value'], 'actual close original complete graph')
    same(close['restart_state'], initial['value']['run'], 'direct original RunState reload')
    same(close['disks_after'], initial['value']['disks'], 'close/reload original disks')
    same(close['persisted_json'], json.loads(initial['run_bytes']), 'actual original persisted JSON bytes decoded value')
    assert len([v for v in values if v['kind'] == 'actual_close_RunState_reload']) == 1
    return {'phase': 'candidate', 'product_pass': True, 'snapshots': 4, 'pairs': 2, 'saved_records': len(values),
        'actual_numeric_calls': len(bundle['numeric']),
        'saved_numeric_exceptions': sum(v['kind'] == 'actual_calculate_exception' for v in bundle['numeric']),
        'denominator_types_preserved_in_native_records': denominator_types,
        'PNGs': pngs, 'scope': 'Current real cultivation UI, whole saved numerical returns and three formatter texts, explicit same-input window pairs. No base_attack override or original GUI Gold claim.'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--section', type=int, choices=(112, 113, 114), required=True)
    for name in ('guard', 'window', 'out'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--root', default='/workspace/rougezhushou')
    parser.add_argument('--original'); parser.add_argument('--original-guard')
    args = parser.parse_args(); target = Path(args.out).resolve(); root = Path(args.root).resolve()
    assert not target.exists() and target != root and root not in target.parents
    assert (args.original is None) is (args.original_guard is None)
    assert args.section == 112 or args.original is None
    result = {'kind': 'ROOT_ACTUAL_SAVED_WINDOW_%d_AUDIT' % args.section, 'passed': False,
        'workflow_complete': False, 'source_drift': [], 'native_helper_sha256': HELPER_SHA,
        'auditor_sha256': sha(Path(__file__).read_bytes()), 'PNG_pixels_visually_reviewed_by_this_auditor': False,
        'native_Windows_verified': False, 'project_API_reexecution': False}
    try:
        assert sha(Path(__file__).with_name('native_evidence.py').read_bytes()) == HELPER_SHA
        bundle = load(args.section, args.window, args.guard, 'candidate')
        same(source_map(root), bundle['guard']['source_sha256'], 'current maintained source guard')
        for name, expected in bundle['guard']['source_additional_sha256'].items():
            assert sha((root / name).read_bytes()) == expected
        result.update(source_guard_sha256=sha(bundle['guard_raw']), window_receipt_sha256=bundle['receipt_sha256'],
            candidate=audit112(bundle, 'candidate') if args.section == 112 else audit113(bundle))
        if args.original:
            original = load(112, args.original, args.original_guard, 'original')
            result['original_observations'] = audit112(original, 'original')
            result['original_guard_sha256'] = sha(original['guard_raw']); result['original_receipt_sha256'] = original['receipt_sha256']
            assert Path(args.original_guard).read_bytes() == original['guard_raw']
        current = source_map(root); expected = bundle['guard']['source_sha256']
        result['source_drift'] = [name for name in set(current) | set(expected) if current.get(name) != expected.get(name)]
        assert not result['source_drift'] and Path(args.guard).read_bytes() == bundle['guard_raw']
        assert sha((bundle['folder'] / 'receipt.json').read_bytes()) == bundle['receipt_sha256']
        if args.original:
            assert sha((original['folder'] / 'receipt.json').read_bytes()) == original['receipt_sha256']
        for name, expected in bundle['guard']['source_additional_sha256'].items():
            assert sha((root / name).read_bytes()) == expected
        result.update(passed=True, workflow_complete=True)
    except BaseException as error:
        result['failure'] = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n'); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({'passed': result['passed'], 'section': args.section, 'out': str(target)}))
    return 0 if result['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
