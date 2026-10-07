from pathlib import Path
import datetime, hashlib, json

base = Path(__file__).parent
before = json.loads((base / 'baseline-supplemental-sp075.json').read_bytes())
after = json.loads((base / 'draft075-supplemental-sp075.json').read_bytes())


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


assert before['public_calls'] == after['public_calls'] == 24
pairs = []
for old, new in zip(before['records'], after['records']):
    assert old['request'] == new['request']
    assert digest(old['full_result']) == old['full_result_sha256']
    assert digest(new['full_result']) == new['full_result_sha256']
    pairs.append({'request': old['request'], 'passed': old['full_result'] == new['full_result'],
                  'before_result_sha256': old['full_result_sha256'], 'after_result_sha256': new['full_result_sha256']})
out = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'paired_scenarios': len(pairs),
       'public_calls': before['public_calls'] + after['public_calls'], 'pairs': pairs,
       'complete_json_unchanged': all(pair['passed'] for pair in pairs),
       'mismatches': [pair for pair in pairs if not pair['passed']],
       'does_not_rerun_or_replace_completed_main_matrix': True}
(base / 'supplemental-sp-comparison075.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print({k: v for k, v in out.items() if k not in ('pairs', 'mismatches')})
assert not out['mismatches']
