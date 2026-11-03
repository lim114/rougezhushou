"""Source-only preparation. Root alone runs this Saved evidence auditor.

No project import or calculation is performed. Cross-observation comparisons
assert each complete graph's internal aliases, not shared objects across calls.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
FIXTURE = Path('/workspace/.continuation/section111-token-tail-original-scenarios-source-v1/scenarios.json')
FIXTURE_SHA = '1ca3fea10355d9eaead373b2092e9ae6c1d96a70f96b5d281f942882b1d29e0c'
PROBE_SHA = 'b4e574e54d7798d06707ad7f80a2efe268209a5b8e22645f9d976ac86dd7e1d3'
WINDOW_SHA = '65a9b2247b705472a9eaeb910dffef6cb5973a75327153dad1a4391bf5d657a2'
TOKEN = 'token_10001_deepcl_tentac'
OP = 'char_110_deepcl'
PHASES = ('calculate_damage', 'format_estimate', 'format_report', 'format_report_technical')
CLOCK_KEYS = ('initial_seconds', 'recharge_seconds', 'cycle_seconds', 'duration_seconds',
              'sp_recovery_per_second', 'mode')
CHANGED = {f's{s}-{tail}' for s in (1, 2) for tail in
           ('unit-travel-ten', 'unit-travel-two-hundred',
            'unit-travel-ten-window-five', 'unit-travel-ten-window-zero')}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def file_meta(path):
    path = Path(path); raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}

def main():
    p = argparse.ArgumentParser()
    for key in ('root', 'guard', 'original', 'candidate', 'original-exit', 'candidate-exit', 'out'):
        p.add_argument('--' + key, required=True)
    p.add_argument('--window'); p.add_argument('--window-exit')
    args = p.parse_args()
    root = Path(args.root).resolve(); out = Path(args.out).resolve()
    assert not out.exists() and root not in out.parents and root != out
    assert sha((HERE / 'native_evidence.py').read_bytes()) == HELPER_SHA
    assert sha(FIXTURE.read_bytes()) == FIXTURE_SHA
    sys.dont_write_bytecode = True; sys.path.insert(0, str(HERE))
    from native_evidence import assert_native_equal as exact, freeze, read_record, source_map
    guard_path = Path(args.guard).resolve(); guard_raw = guard_path.read_bytes(); guard = json.loads(guard_raw)
    expected = guard['source_sha256']; extra = guard['source_additional_sha256']
    assert guard['section'] == 111 and set(extra) == {'CORE_0.70_VERIFICATION.json'}
    def source_check():
        assert source_map(root) == expected
        assert guard_path.read_bytes() == guard_raw
        assert {name: sha((root/name).read_bytes()) for name in extra} == extra
    source_check(); cases = load(FIXTURE)['cases']; assert len(cases) == 18
    fixture_by_id = {row['id']: row['scenario'] for row in cases}
    assert len(fixture_by_id) == 18 and CHANGED <= set(fixture_by_id)
    decoded = 0; observations = []; checks = []
    def assert_raw_zero(path):
        assert Path(path).read_text().strip() == '0', str(path)
        return file_meta(path)
    def api(folder, phase, exit_path):
        nonlocal decoded
        folder = Path(folder).resolve(); receipt = load(folder/'observations.json')
        raw = assert_raw_zero(exit_path)
        assert receipt['kind'] == 'ROOT_ACTUAL_PUBLIC_API_THREE_FORMATTER_OBSERVATION'
        assert receipt['phase'] == phase and receipt['observation_only'] is True
        assert receipt['product_pass'] is False and receipt['observation_complete'] is True
        assert receipt['source_and_CORE_unchanged'] is True and 'fatal_error' not in receipt
        assert receipt['runner']['sha256'] == PROBE_SHA
        assert receipt['fixture']['sha256'] == FIXTURE_SHA
        assert receipt['actual_completed_cases'] == 18 and receipt['actual_public_calls'] == 72
        assert receipt['actual_native_records'] == 90 and receipt['consumer_error_count'] == 0
        assert receipt['source_before'] == receipt['source_after']
        assert receipt['CORE_before'] == receipt['CORE_after'] == extra
        old_guard = load(receipt['guard']['path'])
        assert file_meta(receipt['guard']['path']) == receipt['guard']
        assert receipt['source_before'] == old_guard['source_sha256']
        assert receipt['CORE_before'] == old_guard['source_additional_sha256']
        if phase == 'candidate': exact(receipt['source_after'], expected, 'candidate complete source guard')
        refs = receipt['records']; assert len(refs) == 90
        index = [json.loads(line) for line in (folder/'native/index.jsonl').read_text().splitlines()]
        assert index == refs and len({ref['path'] for ref in refs}) == 90
        values = {}
        for ref in refs:
            value = read_record(folder/'native', ref); decoded += 1
            values[(ref['case'], ref['phase'])] = value
            if ref['kind'] == 'actual-public-consumer':
                assert value['error'] is None
                exact(value['after'], value['before'], 'complete per-call caller: ' + str((ref['case'], ref['phase'])))
            else:
                assert ref['kind'] == 'whole-case-caller' and ref['phase'] == 'caller'
                exact(value['after'], value['before'], 'whole-case caller')
        assert len(values) == 90 and len(receipt['calls']) == 72
        assert [row['id'] for row in receipt['rows']] == [row['id'] for row in cases]
        for index, call in enumerate(receipt['calls']):
            identity = cases[index//4]['id']; stage = PHASES[index%4]
            assert (call['case'], call['phase']) == (identity, stage)
            assert call['error'] is None and call['caller_unchanged'] is True
            assert call['native'] == refs[(index//4)*5 + index%4]
        result = {}
        for row in receipt['rows']:
            identity = row['id']; assert row['calculate_error'] is None and not row['formatters_blocked']
            numeric = values[(identity, 'calculate_damage')]; scenario = fixture_by_id[identity]
            exact(numeric['before'], (scenario,), 'fixture and complete numeric caller')
            whole = values[(identity, 'caller')]; exact(whole['before'], scenario, 'whole fixture caller')
            texts = []
            for stage in PHASES[1:]:
                record = values[(identity, stage)]
                exact(record['before'], (numeric['result'],), 'complete formatter input matches saved result')
                assert type(record['result']) is str; texts.append(record['result'])
            assert texts[0] == texts[1]
            result[identity] = {'result': numeric['result'], 'texts': tuple(texts)}
        observations.append({'phase': phase, 'receipt': file_meta(folder/'observations.json'), 'raw_exit': raw,
                             'cases': 18, 'calls': 72, 'native_records': 90})
        return result
    original = api(args.original, 'original', args.original_exit)
    candidate = api(args.candidate, 'candidate', args.candidate_exit)
    def component(result, name):
        matches = [c for c in result['components'] if c['name'] == name]; assert len(matches) == 1
        return matches[0]
    def stream(result, normal=False):
        matches = [s for s in result['timing']['recharge_streams' if normal else 'streams'] if s['unit'] == TOKEN]
        assert len(matches) == 1; return matches[0]
    def clock(result):
        skill = result['estimate']['skill']
        return {'skill': {k: skill[k] for k in CLOCK_KEYS},
                'sp_events': {k: v for k, v in result['estimate'].items() if k == 'sp_events'},
                'timing_report': next(s for s in result['report']['sections'] if s['id'] == 'timing')}
    def damage_section(result, scenario):
        skill = result['estimate']['skill']; metrics = []
        def metric(key, label, value, unit=''):
            return {'key': key, 'label': label, 'value': value, 'unit': unit}
        metrics.append(metric('per_cast', '单次技能总伤', skill['total_damage']))
        if skill['duration_seconds'] and skill['total_damage'] is not None:
            metrics.append(metric('active_dps', '技能阶段平均 DPS', skill['phase_damage']/skill['duration_seconds'], '伤害/秒'))
        damage = skill.get('window_damage', result['total_damage'])
        if 'window_seconds' in scenario or skill['total_damage'] != damage:
            metrics.append(metric('window_damage', '观察窗口总伤', damage))
            if skill.get('window_seconds') is not None:
                metrics.append(metric('window_seconds', '伤害观察窗口', skill['window_seconds'], '秒'))
            if skill.get('window_seconds'):
                metrics.append(metric('window_dps', '窗口平均 DPS', damage/skill['window_seconds'], '伤害/秒'))
        metrics.append(metric('cycle_dps', '本轮周期 DPS', skill['cycle_dps'], '伤害/秒'))
        return {'id': 'damage', 'title': '伤害输出', 'metrics': metrics, 'notes': []}
    for row in cases:
        identity = row['id']; old = original[identity]['result']; new = candidate[identity]['result']
        if identity not in CHANGED:
            exact(new, old, 'complete unaffected result ' + identity)
            exact(candidate[identity]['texts'], original[identity]['texts'], 'three complete unaffected texts ' + identity)
            checks.append({'id': identity, 'scope': 'complete result and all three complete texts exactly unchanged'})
            continue
        scenario = row['scenario']; skill = scenario['skill']; before = old['estimate']['skill']; after = new['estimate']['skill']
        # A short public window does not expose the complete-cast producer stream.
        reference_id = f's{skill}-unit-travel-' + ('two-hundred' if scenario['timing']['units'][TOKEN]['projectile_travel_seconds'] == 200 else 'ten')
        reference = candidate[reference_id]['result']; emitted = stream(reference)['emitted_times_seconds']
        nominal = [t for t in emitted if t < after['duration_seconds']]
        count = scenario['summon_count']; late_count = (len(emitted) - len(nominal))*count
        assert late_count > 0
        assert after['hit_counts']['触手'] == len(emitted)*count
        assert before['hit_counts']['触手'] == len(nominal)*count
        token = component(new, '触手'); delta = late_count*token['per_hit']
        assert math.isclose(after['total_damage']-before['total_damage'], delta, rel_tol=1e-12, abs_tol=1e-7)
        exact(after['total_damage'], reference['estimate']['skill']['total_damage'], 'full cast independent of shown window')
        exact(after['hit_counts'], reference['estimate']['skill']['hit_counts'], 'complete cast hit counts independent of shown window')
        exact(clock(new), clock(old), 'whole public SP clocks/events/report unchanged')
        exact(new['components'], old['components'], 'all shown components unchanged')
        exact(new['timing'], old['timing'], 'complete shown and normal timing unchanged')
        # Reproduce timing.phase_totals Source operation order, rather than
        # accepting a broad phase tolerance. Full token totals/counts changed;
        # amount * inside / len(times) can consequently move by one float ULP.
        assert [c['name'] for c in reference['components']] == ['本体普攻', '触手']
        owner = component(reference, '本体普攻')
        owner_stream = next(s for s in reference['timing']['streams'] if s['unit'] == OP)
        exact(owner['times_seconds'], owner_stream['emitted_times_seconds'], 'complete owner producer reference has no clipped tail')
        exact(owner, component(original[reference_id]['result'], '本体普攻'), 'complete owner reference old/new identical')
        assert type(after['hit_counts']['触手']) is float and len(emitted) > 0
        actual_float_count = after['hit_counts']['触手']/len(emitted)
        assert type(actual_float_count) is float and actual_float_count == scenario['summon_count']
        exact(before['hit_counts']['触手'], len(nominal)*actual_float_count, 'old producer floating hit count')
        exact(after['hit_counts']['触手'], len(emitted)*actual_float_count, 'new producer floating hit count')
        exact(component(reference, '触手')['per_hit'], token['per_hit'], 'complete cast and shown actual token unit amount')
        exact(component(original[reference_id]['result'], '触手')['per_hit'], token['per_hit'], 'old/new complete producer unit amount')
        boundary = after['duration_seconds']
        inside_nominal = sum(0 <= t < boundary for t in nominal)
        inside_emitted = sum(0 <= t < boundary for t in emitted)
        assert inside_nominal == inside_emitted
        phase_expectations = []
        for placed, actual_cast in ((nominal, before), (emitted, after)):
            full_components = freeze(reference['components'])
            full_token = next(c for c in full_components if c['name'] == '触手')
            full_token['hits'] = len(placed)*actual_float_count
            full_token['total'] = full_token['per_hit']*full_token['hits']
            full_token['times_seconds'] = [t for t in placed for _ in range(int(actual_float_count))]
            damage = healing = 0
            for c in full_components:
                assert 'event_amounts' not in c  # these exact sourced emit branches
                times = c.get('times_seconds'); amount = c['total']
                if times is not None:
                    amount = amount*sum(0 <= t < boundary for t in times)/len(times) if times else 0
                if c.get('damage_type') == 'healing': healing += amount
                elif c.get('damage_type') not in ('regeneration', 'buildup'): damage += amount
            exact(actual_cast['phase_damage'], damage, 'phase Source multiply/count/divide/add exact type and bits')
            exact(actual_cast['phase_healing'], healing, 'phase Source healing exact type and bits')
            phase_expectations.append(damage)
        assert type(before['phase_damage']) is type(after['phase_damage']) is float
        assert math.isfinite(before['phase_damage']) and math.isfinite(after['phase_damage'])
        assert after['phase_damage'] in (before['phase_damage'],
            math.nextafter(before['phase_damage'], math.inf),
            math.nextafter(before['phase_damage'], -math.inf))
        assert all(t < after['window_seconds'] for t in stream(new)['times_seconds'])
        for current in (old, new):
            actual = [s for s in current['report']['sections'] if s['id'] == 'damage']; assert len(actual) == 1
            exact(actual[0], damage_section(current, scenario), 'complete damage metric identities/values/order')
        # Cycle totals keep impacts strictly inside this cycle, not every cast tail.
        inside_count = sum(t < after['cycle_seconds'] for t in emitted)
        inside_before = sum(t < after['cycle_seconds'] for t in nominal)
        cycle_delta = (inside_count-inside_before)*count*token['per_hit']
        assert math.isclose(after['cycle_damage']-before['cycle_damage'], cycle_delta, rel_tol=1e-12, abs_tol=1e-7)
        assert math.isclose(after['cycle_dps'], after['cycle_damage']/after['cycle_seconds'], rel_tol=1e-12, abs_tol=1e-7)
        normalized = freeze(new)
        for key in ('total_damage', 'cycle_damage', 'cycle_dps'):
            normalized['estimate']['skill'][key] = before[key]
        normalized['estimate']['skill']['hit_counts']['触手'] = before['hit_counts']['触手']
        normalized['estimate']['skill']['phase_damage'] = before['phase_damage']
        old_damage = next(s for s in old['report']['sections'] if s['id'] == 'damage')
        normalized['report']['sections'] = [freeze(old_damage) if s['id'] == 'damage' else s for s in normalized['report']['sections']]
        exact(normalized, old, 'complete result excluding only audited complete-cast/cycle scalar leaves, exactly reproduced phase rounding, and damage presentation')
        checks.append({'id': identity, 'scope': 'whole remainder exact; emitted full cast, finite phase/window/recharge and cycle arithmetic independently checked',
                       'phase_arithmetic_exact_bits_checked': True,
                       'phase_inside_impact_count_unchanged': inside_emitted,
                       'phase_old_hex': phase_expectations[0].hex(), 'phase_new_hex': phase_expectations[1].hex(),
                       'phase_difference_at_most_one_ULP': True,
                       'actual_late_impacts': late_count, 'actual_cast_damage_delta': delta,
                       'actual_inside_cycle_damage_delta': cycle_delta,
                       'changed_text_scope': 'all three complete actual formatter inputs/texts retained; intended changed report text has no old-text equality claim'})
    window_summary = None
    if args.window:
        assert args.window_exit
        folder = Path(args.window).resolve(); receipt = load(folder/'receipt.json'); raw = assert_raw_zero(args.window_exit)
        assert receipt['kind'] == 'ROOT_ACTUAL_111_REAL_MAINWINDOW' and receipt['phase'] == 'candidate'
        assert receipt['passed'] is True and receipt['workflow_complete'] is True
        assert receipt['runner_sha256'] == WINDOW_SHA and receipt['native_helper_sha256'] == HELPER_SHA
        assert receipt['source_guard_sha256'] == sha(guard_raw) and receipt['source_count'] == len(expected)
        assert receipt['source_before'] == receipt['source_after'] == expected
        assert receipt['source_additional_before'] == receipt['source_additional_after'] == extra
        assert receipt['source_drift'] == [] and receipt['Qt_errors'] == []
        assert receipt['actual_windows'] == 1 and len(receipt['rows']) == 4 and len(receipt['pairs']) == 2 and len(receipt['pngs']) == 2
        refs = receipt['records']; assert len({ref['path'] for ref in refs}) == len(refs)
        saved = {}; calculations = []; formats = {}
        for ref in refs:
            value = read_record(folder/'records', ref); decoded += 1; saved[ref['path']] = value
            assert (value['kind'], value['case'], value['phase']) == (ref['kind'], ref['case'], ref['phase'])
            kind = value['kind']
            if kind in ('actual_UI_step', 'actual_calculate_result', 'actual_three_formatter_group'):
                exact(value['after'], value['before'], 'complete saved window joint/caller purity')
            if kind == 'actual_calculate_exception': raise AssertionError('actual window numeric exception')
            if kind == 'actual_calculate_result': calculations.append(value)
            if kind == 'actual_three_formatter_group': formats[value['case']] = value
            assert kind in ('actual_UI_step', 'actual_calculate_result', 'actual_three_formatter_group',
                            'actual_window_snapshot', 'actual_PNG_visible_damage_rows', 'actual_close_RunState_reload')
        assert len(calculations) == receipt['actual_numeric_calls']
        def resolve(ref):
            assert ref in refs; return saved[ref['path']]
        snapshots = {}
        assert [row['id'] for row in receipt['rows']] == ['s1-travel0', 's1-travel10', 's2-travel0', 's2-travel10']
        for row in receipt['rows']:
            identity = row['id']; snap = resolve(row['snapshot'])['value']; numeric = resolve(row['numeric'])
            result = snap['damage_result']['result']; caller = snap['caller']; skill = result['estimate']['skill']
            exact(numeric['result'], result, 'whole real numeric/snapshot result')
            exact(numeric['before'], {'args': (caller,), 'kwargs': {}}, 'whole real numeric/snapshot caller')
            exact(snap['damage_result']['scenario'], caller, 'whole actual UI caller')
            exact(formats[identity]['before']['result'], result, 'whole formatter numeric result')
            exact(formats[identity]['texts'], snap['texts'], 'all three complete saved window texts')
            assert snap['texts']['estimate'] == snap['texts']['default']
            assert snap['displayed_damage'] == snap['texts']['default'].replace(chr(160), ' ')
            assert caller['operator'] == OP and caller['skill'] == row['skill'] and caller['timing_mode'] == 'frames'
            assert caller['elite'] == 2 and caller['level'] == 70 and caller['skill_rank'] == 10
            assert caller['module_id'] is None and caller['module_level'] == 0 and caller['summon_count'] == 1
            assert caller['continuous_attacks'] is True and caller['relic_ids'] == []
            assert caller['enemy_defense'] == 0 and caller['enemy_resistance'] == 0 and 'window_seconds' not in caller
            exact(caller['timing'], {'windup_frames': 1, 'recovery_frames': 0, 'units': {TOKEN: {
                'windup_frames': 1, 'recovery_frames': 0, 'projectile_travel_seconds': row['travel_seconds']}}}, 'complete manual timing')
            duration, cast_hits, delayed_hits = (30, 24, 16) if row['skill'] == 1 else (55, 44, 36)
            assert skill['duration_seconds'] == skill['window_seconds'] == duration
            assert skill['hit_counts']['触手'] == len(stream(result)['emitted_times_seconds']) == cast_hits
            assert component(result, '触手')['hits'] == len(stream(result)['times_seconds']) == (delayed_hits if row['travel_seconds'] else cast_hits)
            exact(component(result, '触手')['times_seconds'], stream(result)['times_seconds'], 'bounded shown token attribution')
            assert all(t < duration for t in stream(result)['times_seconds'])
            assert all(t < skill['recharge_seconds'] for t in stream(result, True)['times_seconds'])
            assert math.isclose(skill['phase_damage'], result['total_damage'], rel_tol=1e-12, abs_tol=1e-7)
            snapshots[identity] = snap
        for pair in receipt['pairs']:
            old = resolve(pair['baseline_snapshot'])['value']; new = resolve(pair['delayed_snapshot'])['value']
            caller = freeze(new['caller']); caller['timing']['units'][TOKEN]['projectile_travel_seconds'] = 0
            exact(caller, old['caller'], 'same entire caller except explicitly declared token travel')
            before = old['damage_result']['result']; after = new['damage_result']['result']
            exact(clock(after), clock(before), 'complete SP fields/events/report pair')
            exact(after['estimate']['skill']['total_damage'], before['estimate']['skill']['total_damage'], 'fullcast damage pair')
            exact(after['estimate']['skill']['hit_counts'], before['estimate']['skill']['hit_counts'], 'fullcast hit counts pair')
            exact(component(after, '本体普攻'), component(before, '本体普攻'), 'independent owner component pair')
            exact(new['state_and_disks'], old['state_and_disks'], 'whole account/run/disk pair')
        close = resolve(receipt['close_reload']); assert close['kind'] == 'actual_close_RunState_reload'
        exact(close['restart_state'], close['live_before']['run'], 'complete accepted run close/direct reload')
        exact(close['disks_after'], close['live_before']['disks'], 'complete close/reload disks unchanged')
        png_meta = []
        for item in receipt['pngs']:
            path = folder/item['path']; assert path.parent == folder and not path.is_symlink()
            meta = file_meta(path); assert meta['bytes'] == item['bytes'] and meta['sha256'] == item['sha256']
            assert path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
            visual = resolve(item['visual']); assert visual['kind'] == 'actual_PNG_visible_damage_rows'
            assert visual['anchor'] == '【伤害输出】' and len(visual['visible_blocks']) == len(visual['cursor_rects']) == 4
            snap = snapshots[visual['case']]; assert visual['displayed_text'] == snap['displayed_damage']
            lines = visual['displayed_text'].splitlines(); first = lines.index(visual['anchor'])
            assert visual['visible_blocks'] == lines[first:first+4]
            x, y, w, h = visual['viewport_rect']; assert w > 0 and h > 0
            for cx, cy, cw, ch in visual['cursor_rects']:
                assert cw > 0 and ch > 0 and x <= cx and y <= cy and cx+cw <= x+w and cy+ch <= y+h
            png_meta.append(meta)
        window_summary = {'receipt': file_meta(folder/'receipt.json'), 'raw_exit': raw,
                          'native_records': len(refs), 'actual_numeric_calls': len(calculations),
                          'snapshots': 4, 'SP_pairs': 2, 'close_direct_RunState_reload': True,
                          'PNGs': png_meta,
                          'visual_scope': 'Saved actual visible header and following three text blocks plus PNG bytes/hash; Root separately views images. No hit-count visual claim.'}
    else:
        assert not args.window_exit
    source_check()
    report = {'kind': 'ROOT_ACTUAL_111_SAVED_NATIVE_AUDIT', 'passed': True, 'workflow_complete': True,
              'source_guard_sha256': sha(guard_raw), 'source_count': len(expected), 'source_drift': [],
              'CORE_unchanged': True, 'actual_native_records_decoded': decoded, 'API': observations,
              'case_checks': checks, 'window': window_summary,
              'alias_scope': 'Whole graph internal aliases checked per independent record/comparison; no shared identity claim across separately captured observations.',
              'native_windows_game_chat_verified': False, 'private_state_access': False,
              'runner': file_meta(Path(__file__).resolve())}
    with out.open('x', encoding='utf-8') as stream_out:
        json.dump(report, stream_out, ensure_ascii=False, allow_nan=False, indent=2)
        stream_out.write('\n'); stream_out.flush(); os.fsync(stream_out.fileno())
    print(json.dumps({'passed': True, 'native_records_decoded': decoded, 'API_cases': 18,
                      'window_snapshots': 4 if window_summary else None}))

if __name__ == '__main__':
    main()
