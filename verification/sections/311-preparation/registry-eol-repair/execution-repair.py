from pathlib import Path
from hashlib import sha256
import ast, json, runpy, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
path = ROOT / 'scripts/verify_full_available.py'
before = path.read_bytes()
assert before.count(b'\r\r\n') == 358
after = before.replace(b'\r\r\n', b'\n').replace(b'\r\n', b'\n')
assert b'\r' not in after
first, second = ast.parse(before.decode('utf8')), ast.parse(after.decode('utf8'))
first.body.pop(0)
second.body.pop(0)
assert ast.dump(first, include_attributes=False) == ast.dump(second, include_attributes=False)
selectors_before = tuple(runpy.run_path(str(path))['maintained_selectors']())
out = ROOT / 'verification/sections/311-preparation/registry-eol-repair'
out.mkdir()
(out / 'original-verify_full_available.py').write_bytes(before)
path.write_bytes(after)
selectors_after = tuple(runpy.run_path(str(path))['maintained_selectors']())
assert selectors_before == selectors_after and len(selectors_after) == 484
native = json.loads((ROOT / 'verification/sections/311-native-attempt1/actual/window.json').read_bytes())
assert path.relative_to(ROOT).as_posix() not in native['source_sha256_after']
for name, expected in native['source_sha256_after'].items():
    assert sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
exceptions = ['verification/sections/311-necessary-attempt1/stderr.txt',
              'verification/sections/311-index-validation/git-diff-check.txt',
              'verification/sections/311-preparation/registry-eol-repair/original-verify_full_available.py']
attrs = ROOT / '.gitattributes'
old_attrs = attrs.read_bytes()
addition = b'' if old_attrs.endswith(b'\n') else b'\n'
addition += ('# Exact archived311 failure bytes; active source whitespace checks remain enabled.\n' +
    '\n'.join(name + ' -text whitespace=cr-at-eol,-blank-at-eol' for name in exceptions) + '\n').encode('utf8')
attrs.write_bytes(old_attrs + addition)
record = {'section': 311, 'kind': 'root_registration_EOL_repair_after_public_staging_failure',
    'cause': 'The root registration helper decoded CRLF bytes then used Windows write_text newline conversion, duplicating carriage returns.',
    'before_sha256': sha256(before).hexdigest(), 'after_sha256': sha256(after).hexdigest(),
    'all_non_docstring_AST_unchanged': True, 'module_docstring_only_whitespace_restored': True,
    'all_484_selectors_and_order_unchanged': True,
    'all_actual_native_window_bound_sources_still_exact_current_bytes': True,
    'registry_was_outer_source_guard_member_but_not_native_runtime_dependency': True,
    'source_and_necessary_revalidation_required': True,
    'exact_archived_evidence_whitespace_exceptions': exceptions, 'active_source_whitespace_exempted': False}
(out / 'repair.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
(out / 'execution-repair.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'registry_EOls_repaired': True, 'selectors': 484,
                  'native_bound_sources_unchanged': True, 'new_validation_pending': True}))
