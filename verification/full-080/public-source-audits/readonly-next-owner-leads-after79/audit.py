import copy, gzip, hashlib, json, pathlib, subprocess, sys

sys.dont_write_bytecode = True
OUT = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path('/workspace/rougezhushou')
HEAD = '4b1e4d1f0bd9c60bc87523d6ac05c61f77f2a52b'
public = [p for p in subprocess.check_output(['git', '-C', str(ROOT), 'ls-tree', '-r', '--name-only', HEAD], text=True).splitlines() if p.startswith('rouge/') and pathlib.PurePosixPath(p).suffix in ('.py', '.json')]
hashes = {}
for name in public:
    raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', HEAD + ':' + name])
    dest = OUT / 'frozen77' / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    hashes[name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
(OUT / 'freeze77-receipt.json').write_text(json.dumps({'baseline_head': HEAD, 'files': hashes, 'source': 'immutable public git blobs only', 'private_state_copied': False, 'root_working_tree_used': False}, indent=2) + '\n')
original_path = ROOT / '.cache/p2-s1-binding/character_table.json'
original_bytes = original_path.read_bytes()
assert hashlib.sha256(original_bytes).hexdigest() == '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'
original = json.loads(original_bytes)
owners = ('char_1041_angel2', 'char_1046_sbell2', 'char_1048_orchd2', 'char_196_sunbr')
selectors = {owner: {'name': original[owner]['name'], 'talents': original[owner]['talents'], 'skills': original[owner]['skills']} for owner in owners}
(OUT / 'original-talent-skill-selectors.json').write_text(json.dumps(selectors, ensure_ascii=False, indent=2) + '\n')
sys.path.insert(0, str(OUT / 'frozen77'))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.operator_engine import selected_talents
from rouge.reporting import format_report
strict = lambda obj: json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
before = strict(catalog())
records = []
for owner in owners:
    for elite in (0, 1, 2):
        for mode in ('frames', 'continuous'):
            for skill in (1, 2, 3):
                args = {'operator': owner, 'elite': elite, 'skill': skill, 'skill_rank': 7, 'base_attack': 1000, 'window_seconds': 10, 'timing_mode': mode}
                if owner == 'char_1046_sbell2': args['snow_entries'] = 1
                if owner == 'char_1048_orchd2': args['power_coating'] = True
                talents, parts = selected_talents(catalog()['operators'][owner], args)
                given = copy.deepcopy(args)
                try:
                    result = calculate_damage(given)
                    outcome = {'accepted': True, 'result': result, 'formatted_report': format_report(result), 'technical_report': format_report(result, technical=True), 'formatted_estimate': format_estimate(result)}
                except Exception as exc:
                    outcome = {'accepted': False, 'error_type': type(exc).__name__, 'error': str(exc)}
                assert given == args
                records.append({'id': len(records), 'input': args, 'selected_talents': talents, 'outcome': outcome})
assert strict(catalog()) == before
raw = (strict(records) + '\n').encode()
blob = gzip.compress(raw, mtime=0)
(OUT / 'public-whole-outcomes.json.gz').write_bytes(blob)
facts = []
for owner, name in (('char_1041_angel2', '火力电台'), ('char_1046_sbell2', '无垠的雪景'), ('char_1048_orchd2', '强击瓶专家')):
    first = next(c for group in original[owner]['talents'] for c in group['candidates'] if c['name'] == name and c['requiredPotentialRank'] == 0)
    assert first['unlockCondition'] == {'phase': 'PHASE_0', 'level': 1}
    samples = [r for r in records if r['input']['operator'] == owner and r['input']['elite'] == 0 and r['input']['skill'] == 1]
    assert all(any(t['name'] == name for t in r['selected_talents']) for r in samples)
    facts.append({'operator': owner, 'talent': name, 'original_minimum': first['unlockCondition'], 'original_blackboard': first['blackboard'], 'public_record_ids': [r['id'] for r in samples], 'conclusion': 'Talent already exists at E0; do not clear its source/count under a guessed E1/E2 gate.'})
receipt = {'schema_version': 1, 'kind': 'readonly negative owner-source lead audit; not a completed numbered section', 'baseline_head': HEAD, 'sources': {'character_table': {'path': str(original_path), 'bytes': len(original_bytes), 'sha256': hashlib.sha256(original_bytes).hexdigest(), 'game_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'reused_full_original_bytes_rehashed': True}}, 'facts': facts, 'Gummy_scope': 'Raw frying-pan talent begins E1; missing prob defaults0, so expected extra-hit count is0 while ordinary attacks remain. No missing-talent false unplaced source demonstrated; this is not an actual frying-pan clock/random-independence proof.', 'actual_public_calls': len(records), 'accepted': sum(r['outcome']['accepted'] for r in records), 'exact_errors': sum(not r['outcome']['accepted'] for r in records), 'strict_whole_json_and_three_formatted_texts_or_error_recorded': True, 'input_or_catalog_mutations': 0, 'raw_bytes': len(raw), 'raw_sha256': hashlib.sha256(raw).hexdigest(), 'gzip_bytes': len(blob), 'gzip_sha256': hashlib.sha256(blob).hexdigest(), 'no_supported_new_patch': True, 'no_native_download_no_wine_no_private_no_tracked_edits': True}
(OUT / 'readonly-audit-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
files = []
for name in ('audit.py', 'freeze77-receipt.json', 'original-talent-skill-selectors.json', 'public-whole-outcomes.json.gz', 'readonly-audit-receipt.json'):
    data = (OUT / name).read_bytes()
    files.append({'source_path': str(OUT / name), 'archive_path': 'readonly-next-owner-leads-after79/' + name, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
(OUT / 'public-artifacts-manifest-v1.json').write_text(json.dumps({'schema_version': 1, 'kind': 'negative public owner-source audit; no implementation section', 'files': files}, indent=2) + '\n')
print(json.dumps({'records': len(records), 'accepted': receipt['accepted'], 'errors': receipt['exact_errors'], 'manifest_sha256': hashlib.sha256((OUT / 'public-artifacts-manifest-v1.json').read_bytes()).hexdigest(), 'receipt_sha256': hashlib.sha256((OUT / 'readonly-audit-receipt.json').read_bytes()).hexdigest()}))
