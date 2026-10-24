"""Read-only qualification of four existing documentary readers for exact bee3 refs.

Writes only the explicitly owned section369 cache candidate directory. This is a
source comparison, not a runtime test, server verification, or mechanism model.
"""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'rouge/current_battle_reference.py').is_file())
DEST = ROOT / '.cache/section369-prepared/research/p3-current-boss-documents-369'
PACK = 'research/p3-current-boss-documents-369'
OLD = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
NEW = 'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d'


def load(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def pin(name):
    raw = (ROOT / name).read_bytes()
    return {'file': name, 'bytes': len(raw), 'sha256': sha256(raw).hexdigest()}


def save(name, value):
    (DEST / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def build():
    inputs = load('research/p3-current-battle-314/source-inputs.json')
    stages = load('research/p3-expansion-313/current-topic.json')['details']['stages']
    current_sources = load('research/p3-current-battle-314/source-selection.json')['original_sources']
    specs = {
        'phase': {'section': 309, 'pack': 'research/p3-boss-phase-309', 'stage_ids': ['ro6_b_6'],
                  'related': ['enemy_2150_shchmr'], 'targets': [['ro6_b_6', 'enemy_2150_shchmr', 0]]},
        'cycle': {'section': 310, 'pack': 'research/p3-boss-cycle-310', 'stage_ids': ['ro6_b_5'],
                  'related': ['enemy_2147_shophm', 'enemy_2148_shorbb', 'enemy_2149_shorsm'],
                  'targets': [['ro6_b_5', 'enemy_2147_shophm', 0], ['ro6_b_5', 'enemy_2148_shorbb', 0]]},
        'hunt': {'section': 311, 'pack': 'research/p3-boss-hunt-311', 'stage_ids': ['ro6_b_4', 'ro6_b_4_b'],
                 'related': ['enemy_2145_cadejo', 'enemy_2146_cadesd', 'enemy_2137_shsdgo',
                             'enemy_2146_cadesd_2', 'enemy_2146_cadesd_3'],
                 'targets': [['ro6_b_4', 'enemy_2145_cadejo', 0], ['ro6_b_4', 'enemy_2146_cadesd', 0],
                             ['ro6_b_4', 'enemy_2137_shsdgo', 0]]},
        'gold': {'section': 312, 'pack': 'research/p3-gold-boss-312', 'stage_ids': ['ro6_b_2', 'ro6_b_2_b'],
                 'related': ['enemy_2140_shsgzd', 'enemy_2141_shsgz2', 'enemy_2142_shsggd'],
                 'targets': [['ro6_b_2', 'enemy_2140_shsgzd', 0], ['ro6_b_2', 'enemy_2142_shsggd', 0],
                             ['ro6_b_2_b', 'enemy_2141_shsgz2', 0]]},
    }
    selected_paths = {
        'phase': 'research/p3-boss-phase-309/selected-original-records.json',
        'cycle': 'research/p3-boss-cycle-310/selected-original-records.json',
        'hunt': 'research/p3-boss-hunt-311/selected-original-records.json',
        'gold': 'research/p3-gold-boss-312/selected-original-authority.json',
    }
    old_db_path = '.cache/game-data/levels/enemydata/enemy_database.json'
    new_db_path = '.cache/p3-expansion-314/levels/enemydata/enemy_database.json'
    assert pin(old_db_path)['sha256'] == 'f8dd03997d0e3eae65cc4b77bcb6b5ef198488504f738defc31cad5e13c3680c'
    assert pin(new_db_path)['sha256'] == '99f75bfe5460bf97a637c59f62cdaacb37770087f608c47480c581c2e6eff8c3'
    old_db = {r['Key']: r['Value'] for r in load(old_db_path)['enemies']}
    new_db = {r['Key']: r['Value'] for r in load(new_db_path)['enemies']}
    originals = {'stages': {}, 'levels': {}, 'enemy_definitions': {}, 'handbook': {}}
    old_levels = {}; families = {}; targets = []; ledger = []; pins = []
    for family, spec in specs.items():
        selected = load(selected_paths[family]); pins.append(pin(selected_paths[family]))
        if family == 'phase':
            old_path = '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_b-6.json'
            old = {'ro6_b_6': load(old_path)}
            old_pin = next(x for x in selected['source_files'] if x['file'] == old_path)
            assert pin(old_path) == old_pin
            records = {selected['enemy_database_complete_record']['Key']: selected['enemy_database_complete_record']['Value']}
        elif family == 'cycle':
            old = {'ro6_b_5': selected['complete_original_level']}
            records = {k: v['Value'] for k, v in selected['complete_original_enemy_records'].items()}
        else:
            old = selected['complete_original_levels']
            records = {}
            for eid, whole_records in selected['complete_original_enemy_records'].items():
                assert len(whole_records) in (0, 1)
                if whole_records:
                    assert whole_records[0]['Key'] == eid
                records[eid] = whole_records[0]['Value'] if whole_records else []
        documents = load(spec['pack'] + '/http-source-records.json')
        docs = [{'title': d['title'], 'revision': str(d['revision']), 'file': spec['pack'] + '/' + d['file'],
                 'url': d.get('fixed_revision_url') or 'https://prts.wiki/index.php?oldid=' + str(d['revision']),
                 'sha256': d['sha256'], 'bytes': d['bytes']} for d in documents]
        family_ledger = []
        for sid in spec['stage_ids']:
            key = 'levels/' + stages[sid]['levelId'].lower() + '.json'
            previous = old[sid]; current = inputs['levels'][key]
            changed = sorted(k for k in set(previous) | set(current) if previous.get(k) != current.get(k))
            assert changed == (['runes'] if sid == 'ro6_b_2_b' else [])
            originals['stages'][sid] = stages[sid]; originals['levels'][key] = current
            old_levels[sid] = previous
            family_ledger.append({'stage_id': sid, 'level_key': key, 'whole_level_equal': not changed,
                'changed_top_fields': changed, 'current_source': current_sources[key],
                'differences': [{'field': f, 'previous': previous.get(f), 'current': current.get(f)} for f in changed]})
        for eid in spec['related']:
            expected = records[eid]
            assert expected == old_db.get(eid, []) == new_db.get(eid, []) == inputs['enemy_definitions'].get(eid, [])
            if expected:
                originals['enemy_definitions'][eid] = expected
                originals['handbook'][eid] = inputs['handbook'].get(eid)
            ledger.append({'family': family, 'enemy_id': eid, 'complete_database_record_equal': bool(expected),
                'database_record_present': bool(expected), 'independent_level_entity': not bool(expected),
                'substitution_permitted': False})
        for sid, eid, level in spec['targets']:
            key = 'levels/' + stages[sid]['levelId'].lower() + '.json'
            found = [(i, b) for i, b in enumerate(inputs['levels'][key]['enemyDbRefs'])
                     if b['id'] == eid and type(b['level']) is int and b['level'] == level]
            assert len(found) == 1
            i, binding = found[0]
            targets.append({'stage_id': sid, 'enemy_key': str(i), 'enemy_id': eid, 'level': level,
                'family': family, 'legacy_identity': [sid, eid, level], 'raw_binding': binding,
                'source_selector': '$.enemyDbRefs[' + str(i) + ']'})
        families[family] = {'legacy_section': spec['section'], 'related_ids': spec['related'],
            'legacy_selected_file': selected_paths[family], 'document_sources': docs, 'level_qualification': family_ledger}
    save('qualified-current-records.json', {'schema': 'current_boss_documents_369_v1',
        'old_commit': OLD, 'current_commit': NEW, 'targets': targets, 'families': families,
        'originals': originals, 'old_levels': old_levels, 'database_comparison': ledger,
        'whole_database_pins': [pin(old_db_path), pin(new_db_path)], 'selected_original_pins': pins,
        'runtime_large_cache_required': False, 'actual_server_verified': False, 'numeric_model_added': False})
    save('source-notes.json', {'schema': 'current_boss_documents_369_source_notes_v1',
        'new_capability': 'One grouped migration of four already-existing complete documentary readers to nine exact current-stage enemy references; not new mechanism discovery.',
        'source_versions': {'previous': OLD, 'current': NEW, 'current_CN_date': '2026-10-16'},
        'qualification': 'Ten complete database entities unchanged; two absent DB entries are independent level-built avatars, not missing names to normalize. Six complete levels compared, five unchanged and only the specified runes difference in ro6_b_2_b.',
        'scope': ['Only the nine explicitly supported tuples may open the reader.',
            'The separately preserved ro6_b_4_b supplies comparison evidence, not a new supported target.',
            'ro6_b_5_b, DLC1 gold stages, and same-name hounds in other stages are not inferred eligible.',
            'Legacy readers run with their genuine legacy identity and all original guards, never a forged current identity.',
            'The shared numeric result, actual phase, actual skill time, server applicability and run state remain unknown/unchanged.'],
        'gold_rune_difference': {'stage_id': 'ro6_b_2_b', 'old': 'Two FOUR_STAR entries: global_token_cnt_add and enemy_attribute_mul.',
            'current': None, 'interpretation': 'The literal field differs. This does not prove server behavior or permit applying old rune values. Current reader exposes documentary conditions only, never old calculated panels or multipliers.'},
        'legacy_cards': 'Existing 309–312 source manifests retain full fixed HTML/cards, original tooltip qualifications and conflicts. Those sources remain versioned documentary references, not verified current server scripts.',
        'research_failures_preserved': [
            {'attempt': 'Initial full DB loop indexed independent avatar suffix as a DB key', 'outcome': 'KeyError enemy_2146_cadesd_2', 'correction': 'Record explicit absence and use exact complete level construction; no name stripping.'},
            {'attempt': 'Read-only shape print contained missing space in Python comprehension', 'outcome': 'SyntaxError before reads or writes', 'correction': 'Reran corrected source inspection; no test claimed.'},
            {'attempt': 'Initial preparation assumed all selected enemy containers were Value lists', 'outcome': 'AssertionError before any source output', 'correction': 'Hunt/gold selected authorities preserve a 0-or-1 whole Key/Value record list; explicitly unwrap only the matching complete record, retaining independent empty entries.'}],
        'testing': 'Preparation source comparisons only; no formal runtime tests, GUI, game, chat, private state, docs or cloud publication.'})
    web_time = (json.loads((DEST / 'web-check-record.json').read_text(encoding='utf-8'))['utc']
                if (DEST / 'web-check-record.json').is_file() else datetime.now(timezone.utc).isoformat())
    save('web-check-record.json', {'schema': 'current_boss_documents_369_web_check_v1',
        'utc': web_time, 'method': 'web search, not replacing fixed source revisions',
        'queries': ['site:prts.wiki 玻利瓦尔 症结之核 飞行形态', 'site:prts.wiki 洛伦茨 扰动之谬 源阶方 模块', 'site:prts.wiki 赤金厄运 征服者 德莱昂'],
        'located_pages': ['https://prts.wiki/w/玻利瓦尔，症结之核', 'https://prts.wiki/w/ISW-DF_混沌源阶理论', 'https://m.prts.wiki/w/“征服者”德莱昂'],
        'result': 'Relevant independently named mechanism and stage pages remain discoverable. No assertion that latest page revision matches fixed revisions or that server behavior is unchanged. Existing fixed complete HTML remains the documentary authority.',
        'new_mechanism_inferred_from_search': False})
    files = {PACK + '/' + n: {'bytes': len((DEST / n).read_bytes()), 'sha256': sha256((DEST / n).read_bytes()).hexdigest()}
             for n in ('qualified-current-records.json', 'source-notes.json', 'web-check-record.json')}
    for family, spec in specs.items():
        for name in (selected_paths[family], spec['pack'] + '/source-manifest.json'):
            data = pin(name); files[name] = {'bytes': data['bytes'], 'sha256': data['sha256']}
    save('runtime-manifest.json', {'schema': 'current_boss_documents_369_manifest_v1', 'game_commit': NEW,
        'files': files, 'legacy_guard_reused': True, 'numeric_model_added': False})
    raw = (DEST / 'runtime-manifest.json').read_bytes()
    print(json.dumps({'candidate': True, 'targets': len(targets), 'current_stage_ids': sorted({t['stage_id'] for t in targets}),
        'complete_levels_compared': len(old_levels), 'database_rows': len(ledger),
        'manifest_sha256': sha256(raw).hexdigest(), 'runtime_tests_run': False, 'gui_run': False}, ensure_ascii=False))


if __name__ == '__main__':
    build()
