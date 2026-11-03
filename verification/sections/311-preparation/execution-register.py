from pathlib import Path
from hashlib import sha256
import json, runpy, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
path = ROOT / 'scripts/verify_full_available.py'
before_bytes = path.read_bytes()
before = tuple(runpy.run_path(str(path))['maintained_selectors']())
assert len(before) == 481
text = before_bytes.decode('utf8')
anchor = "ADDITIONAL_MODULES += ('tests.test_boss_cycle_reference_310', 'tests.test_boss_cycle_view_310', 'tests.test_boss_cycle_integration_310')"
assert text.count(anchor) == 1 and 'test_boss_hunt_reference_311' not in text
addition = "ADDITIONAL_MODULES += ('tests.test_boss_hunt_reference_311', 'tests.test_boss_hunt_view_311', 'tests.test_boss_hunt_integration_311')"
path.write_text(text.replace(anchor, anchor + '\n' + addition, 1), encoding='utf8')
after = tuple(runpy.run_path(str(path))['maintained_selectors']())
assert len(after) == 484 and after[:len(before)] == before
out = ROOT / 'verification/sections/311-preparation/maintained-registration.json'
out.write_text(json.dumps({'section': 311, 'before_count': len(before), 'after_count': len(after),
    'original_ordered_prefix_unchanged': after[:len(before)] == before,
    'added': list(after[len(before):]), 'before_sha256': sha256(before_bytes).hexdigest(),
    'source_sha256': sha256(path.read_bytes()).hexdigest(),
    'full_suite_executed': False, 'next_periodic_full_section': 320,
    'new_selectors_registered_not_acceptance': True}, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
(out.parent / 'execution-register.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'maintained_selectors': len(after), 'old_ordered_prefix_preserved': True}))
