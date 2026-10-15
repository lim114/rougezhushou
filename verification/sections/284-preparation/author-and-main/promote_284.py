"""Authorized two-file284 promotion with exact source guards; no other edits."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'rouge/app.py').is_file())
manifest = json.loads((HERE / 'draft-manifest.json').read_bytes())
original = HERE / 'production-before'
original.mkdir(exist_ok=False)
for name, expected in manifest['original_source_sha256'].items():
    raw = (ROOT / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected, name
    candidate = (HERE / 'draft' / name).read_bytes()
    assert hashlib.sha256(candidate).hexdigest() == manifest['draft_sha256'][name]
    ast.parse(candidate)
    backup = original / name
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_bytes(raw)
test = HERE / 'test_extended_skill_native_284.py'
ast.parse(test.read_bytes())
test_target = ROOT / 'tests/test_extended_skill_native_284.py'
assert not test_target.exists()
for name in manifest['draft_sha256']:
    (ROOT / name).write_bytes((HERE / 'draft' / name).read_bytes())
test_target.write_bytes(test.read_bytes())
record = {'kind': 'SECTION284_AUTHORIZED_PRODUCTION_PROMOTION',
          'before_sha256': manifest['original_source_sha256'],
          'after_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                           for name in manifest['draft_sha256']},
          'new_test': 'tests/test_extended_skill_native_284.py',
          'new_test_sha256': hashlib.sha256(test_target.read_bytes()).hexdigest(),
          'other_production_files_modified_by_this_agent': False,
          'private_state_used': False, 'game_or_chat_actions': 0,
          'committed_or_pushed': False}
(HERE / 'promotion.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps(record, ensure_ascii=False))
