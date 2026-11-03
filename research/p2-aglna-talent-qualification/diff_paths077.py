from pathlib import Path
import json
base = Path(__file__).parent
old = json.loads((base / 'baseline-results077.json').read_bytes())
new = json.loads((base / 'draft-results077.json').read_bytes())
changes = {}


def differences(before, after, path='$'):
    if type(before) is not type(after):
        return [(path, before, after)]
    if isinstance(before, dict):
        result = []
        for key in before.keys() | after.keys():
            if key not in before or key not in after:
                result.append((path + '.' + key, before.get(key), after.get(key)))
            else:
                result.extend(differences(before[key], after[key], path + '.' + key))
        return result
    if isinstance(before, list):
        if len(before) != len(after):
            return [(path + '.length', len(before), len(after))]
        return [item for index, (one, two) in enumerate(zip(before, after))
                for item in differences(one, two, path + '[' + str(index) + ']')]
    return [] if before == after else [(path, before, after)]


for a, b in zip(old['records'], new['records']):
    assert a['request'] == b['request']
    if 'full_result' in a and a['full_result'] != b.get('full_result'):
        for path, before, after in differences(a['full_result'], b.get('full_result')):
            changes.setdefault(path, {'count': 0, 'sample': {'request': a['request'], 'before': before, 'after': after}})['count'] += 1
(base / 'complete-json-changed-paths077.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2) + '\n')
print({key: {'count': value['count'], 'before': value['sample']['before'], 'after': value['sample']['after']} for key, value in sorted(changes.items())})
