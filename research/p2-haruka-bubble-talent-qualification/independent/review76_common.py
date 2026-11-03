import copy
import json

OP = 'char_4202_haruka'
NOTE = '当前培养尚未解锁扶摇花火；浮泡破碎声明保留，但不产生该天赋治疗或二技能中依赖该治疗的派生伤害。'

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)

def locked_positive(scenario, outcome):
    return (scenario['operator'] == OP and scenario.get('elite', 2) < 2
            and 'result' in outcome and float(scenario.get('bubble_bursts', 0)) > 0)

def normalized_locked_result(result, count):
    result = copy.deepcopy(result)
    ref = result['external_event_reference']
    for item in (ref, ref['window_reference']):
        row = item['parameter_rows'][0]
        assert row[0] == '声明窗口内浮泡破碎次数' and row[2] == '次'
        assert canonical(row[1]) == canonical(float(count)), row
        assert item['notes'].count(NOTE) == 1
        item['parameter_rows'][0] = [row[0], 0.0, row[2]]
        item['notes'].remove(NOTE)
    section = next(x for x in result['report']['sections'] if x['id'] == 'external_events')
    assert section['notes'].count(NOTE) == 1
    section['notes'].remove(NOTE)
    metric = next(x for x in section['metrics'] if x['key'] == 'parameter_0')
    assert canonical(metric['value']) == canonical(float(count))
    metric['value'] = 0.0
    return result

def check_pair(baseline, draft):
    assert canonical(baseline['scenario']) == canonical(draft['scenario'])
    scenario = baseline['scenario']
    old, new = baseline['outcome'], draft['outcome']
    if locked_positive(scenario, old):
        bc, dc = baseline['zero_count_control'], draft['zero_count_control']
        expected = dict(scenario, bubble_bursts=0)
        assert canonical(bc['scenario']) == canonical(expected)
        assert canonical(dc['scenario']) == canonical(expected)
        assert canonical(bc['outcome']) == canonical(dc['outcome'])
        assert NOTE not in canonical(bc['outcome'])
        normalized = normalized_locked_result(new['result'], scenario['bubble_bursts'])
        assert canonical({'result': normalized}) == canonical(bc['outcome'])
        assert canonical(old) != canonical(new)
        return 'locked_positive_corrected'
    assert 'zero_count_control' not in baseline and 'zero_count_control' not in draft
    assert canonical(old) == canonical(new)
    return 'old_error_preserved' if 'error_type' in old else 'whole_accepted_preserved'
