"""Independent limited public-source and adversarial qualification review."""
from copy import deepcopy
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
from unittest.mock import patch

from rouge import moving_reward_reference as model
from rouge import battle_reward_planning as integration
from rouge import node_catalog
from rouge.player_node_information import node_information_text

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
checks = []
probes = []


def check(label, actual, expected):
    checks.append({'label': label, 'actual': actual, 'expected': expected, 'passed': actual == expected})


def refs(level=0, **changes):
    raw = {'id': model.ENTITY, 'useDb': True, 'level': level, 'overwrittenData': None}
    raw.update(changes)
    return {'raw': raw}


def snapshot(relative):
    raw = (ROOT / relative).read_bytes()
    target = HERE / 'frozen-source' / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as output:
        output.write(raw)
    return hashlib.sha256(raw).hexdigest()


class Sections(HTMLParser):
    def __init__(self):
        super().__init__()
        self.heading = None
        self.active = None
        self.rows = []
        self.excluded = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.excluded += 1
        if tag == 'h2' and not self.excluded:
            self.heading = []
            self.active = None

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.excluded = max(0, self.excluded - 1)
        if tag == 'h2' and self.heading is not None:
            self.active = {'heading': ''.join(self.heading).strip(), 'text': []}
            self.rows.append(self.active)
            self.heading = None

    def handle_data(self, data):
        if self.excluded:
            return
        if self.heading is not None:
            self.heading.append(data)
        elif self.active is not None:
            self.active['text'].append(data)


def main():
    paths = ['rouge/moving_reward_reference.py', 'rouge/battle_reward_planning.py',
             'rouge/player_node_information.py', 'scripts/build_moving_reward_current_reference.py',
             'rouge/data/moving-reward-current-reference.json',
             'tests/test_moving_reward_reference_287.py', 'tests/test_moving_reward_integration_287.py']
    source_hashes = {relative: snapshot(relative) for relative in paths}
    manifest_bytes = (ROOT / model.MANIFEST).read_bytes()
    manifest = json.loads(manifest_bytes)
    check('manifest_core_pin', hashlib.sha256(manifest_bytes).hexdigest(), model.MANIFEST_SHA256)
    for name, expected in manifest['files'].items():
        raw = (ROOT / name).read_bytes()
        check('file_sha:' + name, hashlib.sha256(raw).hexdigest(), expected['sha256'])
        check('file_size:' + name, len(raw), expected['bytes'])

    html = (ROOT / 'research/p3-moving-reward-current/moving-mobile-response.html').read_bytes()
    extraction = json.loads((ROOT / 'research/p3-moving-reward-current/extraction.json').read_text(encoding='utf-8'))
    parser = Sections()
    parser.feed(html.decode('utf-8'))
    sentence = '被击倒时战斗结束后额外获得10源石锭；到达路径终点时战斗结束后扣除10源石锭'
    source_probe = []
    for level in range(3):
        found = [row for row in parser.rows if row['heading'] == '级别' + str(level)]
        check(f'actual_grade_heading_{level}', len(found), 1)
        body = re.sub(r'\s+', '', ''.join(found[0]['text']))
        check(f'actual_grade_signed_sentence_{level}', body.count(sentence), 1)
        row = extraction['grades'][level]
        segment = html[row['start_byte']:row['end_byte']]
        check(f'actual_grade_span_{level}', hashlib.sha256(segment).hexdigest(), row['source_span_sha256'])
        check(f'actual_grade_span_sentence_{level}', segment.count(sentence.encode('utf-8')), 1)
        source_probe.append({'level': level, 'exact_signed_sentence_occurrences': body.count(sentence),
                             'span_sha256': hashlib.sha256(segment).hexdigest()})
    probes.append({'name': 'independent_original_html_grade_read', 'output': source_probe})

    values = [refs(2), refs(0), refs(2), refs(1)]
    before = deepcopy(values)
    good = model.moving_reward_rule(values)
    check('mixed_duplicate_legal_grades_quantities', [row['quantity'] for row in good['outcomes']], [10, -10])
    check('mixed_legal_not_unique_level', good['action_level_binding_unique'], False)
    check('reference_array_not_mutated', values, before)
    check('mixed_actual_spawn_unknown', good['actual_spawn_level'], None)
    check('mixed_actual_total_unknown', good['actual_reward_total'], None)
    probes.append({'name': 'legal_mixed_grade_consensus_no_total', 'input': values, 'output': good})

    class DictionarySubclass(dict):
        pass

    class ListSubclass(list):
        pass

    class StringSubclass(str):
        pass

    invalid = [
        ('list_subclass', ListSubclass([refs(2)])),
        ('reference_subclass', [DictionarySubclass(refs(2))]),
        ('raw_subclass', [{'raw': DictionarySubclass(refs(2)['raw'])}]),
        ('identity_subclass', [refs(2, id=StringSubclass(model.ENTITY))]),
        ('mixed_invalid_db_number', [refs(0), refs(2, useDb=1), refs(1)]),
        ('mixed_invalid_level_bool', [refs(0), refs(True), refs(2)]),
        ('mixed_unknown_entity', [refs(2), refs(1, id='trap_323_shsbox')]),
        ('mixed_override_false', [refs(2), refs(1, overwrittenData=False)]),
    ]
    for name, value in invalid:
        result = model.moving_reward_rule(value)
        check(name + ':quantities', [row['quantity'] for row in result['outcomes']], [None, None])
        check(name + ':whole_group_unknown', result['all_fixed_level_candidates_documented'], False)
        probes.append({'name': name, 'input': value, 'output': result})

    public_stage = 'ro6_n_5_3'
    original_rules = deepcopy(integration.reward_data())
    stage = integration.stage_reward_sources(public_stage)
    rows = [row for row in stage['rows'] if row['entity_id'] == model.ENTITY]
    check('actual_high_grade_source_present', bool(rows), True)
    check('actual_high_grade_reference', rows[0]['rule']['referenced_levels'], [2])
    check('actual_high_grade_quantities', [row['quantity'] for row in rows[0]['rule']['outcomes']], [10, -10])
    record = next(row for row in node_catalog.battle_candidates(context='all')['rows'] if row['id'] == public_stage)
    text = node_information_text({'kind': 'battle', 'record': record})
    check('player_positive_amount', '10源石锭' in text, True)
    check('player_negative_amount', '-10源石锭' in text, True)
    check('player_no_raw_entity', model.ENTITY in text, False)
    check('player_no_source_url', 'https://' in text, False)
    check('all_actual_total_unknown', stage['actual_reward_total'], None)
    check('old_rule_catalog_unchanged', integration.reward_data(), original_rules)
    probes.append({'name': 'actual_high_grade_stage_public_summary', 'input': public_stage,
                   'output': {'moving_rows': rows, 'player_text': text}})

    clone = HERE / 'source-clone'
    clone.mkdir(exist_ok=False)
    for relative in [model.MANIFEST, *manifest['files']]:
        destination = clone / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / relative).read_bytes())
    with patch.object(model, 'ROOT', clone):
        check('clone_warm_source', model.source_data() is not None, True)
        document = clone / 'research/p3-moving-reward-current/moving-mobile-response.html'
        document.write_bytes(document.read_bytes() + b' ')
        failed_rule = model.moving_reward_rule([refs(2)])
        check('warm_then_changed_source_invalid', failed_rule['source_valid'], False)
        check('warm_then_changed_quantities_unknown', [row['quantity'] for row in failed_rule['outcomes']], [None, None])
        failed_stage = integration.stage_reward_sources(public_stage)
        output = {}
        for technical in (False, True):
            rendered = integration.reward_source_text(failed_stage, technical=technical)
            output[str(technical)] = rendered
            check(f'invalid_source_render_nonempty_{technical}', bool(rendered), True)
            check(f'invalid_source_render_unknown_{technical}', '数量未知' in rendered or '数量暂时未知' in rendered, True)
        player = node_information_text({'kind': 'battle', 'record': record})
        check('invalid_source_player_not_failure_fallback', '资料暂时无法整理' in player, False)
        check('invalid_source_player_quantity_unknown', '源石锭数量未知' in player, True)
        probes.append({'name': 'warm_source_invalid_default_and_technical_no_crash',
                       'output': {'rule': failed_rule, 'source_text': output, 'player_text': player}})
    check('real_source_unmodified_after_clone_probe', model.source_data() is not None, True)
    box = integration.stage_reward_sources('ro6_n_1_1')
    check('box_current_total_unknown', box['actual_reward_total'], None)
    check('box_source_text_explicit_no_duplicate', '不能把两条来源各算一次10' in integration.reward_source_text(box), True)
    findings = []
    box_record = next(row for row in node_catalog.battle_candidates(context='all')['rows'] if row['id'] == 'ro6_n_1_1')
    box_player = node_information_text({'kind': 'battle', 'record': box_record})
    if '箱型恶笼草' in box_player and '恶笼草（移动敌人）' in box_player and '不能把两条来源各算一次10' not in box_player:
        findings.append({'severity': 'wording_only', 'stage': 'ro6_n_1_1',
            'fact': 'Player summary shows box conditional10 and moving enemy conditional10, with a global do-not-add notice but no specific box/moving duplicate warning; full source renderer has the explicit warning.',
            'actual_total_claimed': False})
    for relative, expected in source_hashes.items():
        check('frozen_source_still_same:' + relative, hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), expected)
    result = {'scope': 'independent_limited_source_and_control_review_no_Qt_or_game',
        'source_sha256': source_hashes, 'probe_count': len(probes), 'check_count': len(checks),
        'failed_check_count': sum(not check['passed'] for check in checks), 'checks': checks,
        'probes': probes, 'findings': findings,
        'full_suite_or_actual_window_run': False, 'game_chat_private_accessed': False}
    with (HERE / 'review.json').open('x', encoding='utf-8') as output:
        json.dump(result, output, ensure_ascii=False, indent=2)
    print(json.dumps({key: result[key] for key in ('probe_count', 'check_count', 'failed_check_count', 'findings')}, ensure_ascii=False))
    raise SystemExit(int(result['failed_check_count'] > 0))


if __name__ == '__main__':
    main()
