"""Read public source/AST only; do not execute any publication producer."""
import ast
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def sha(path): return sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads((ROOT / path).read_bytes())

tools = ('stage_section_299.py', 'push_section_299.py', 'verify_publication_299.py', 'finish_publication_299.py')
before = {name: sha(HERE / name) for name in tools}
for name in tools:
    text = (HERE / name).read_bytes().decode('utf8')
    tree = ast.parse(text, filename=name); compile(tree, name, 'exec')
    assert 'b56cbf352cf5d171f52ba05839312950df462e8c' in text
    assert 'bb4927a2a2760d48882f3945b750053d7a5617fc' not in text
    assert 'tests/test_node_catalog.py' not in text and 'historical_test_maintenance' not in text
    assert 'next_section' not in text or ('300' in text or name.startswith('push_'))
stage = (HERE / tools[0]).read_text(encoding='utf8')
tree = ast.parse(stage)
tracked = ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'tracked' for t in n.targets)))
assert len(tracked) == 9 and 'PROJECT_PROGRESS.md' not in tracked
assert set(n for n in tracked if n.startswith('rouge/')) == {'rouge/battle_event_references.py', 'rouge/battle_view.py'}
assert not any(n.startswith('tests/') for n in tracked)
assert "'HEAD:refs/heads/codex/p2-development'" in (HERE / tools[1]).read_text(encoding='utf8')
assert "['ls-remote','origin','refs/heads/codex/p2-development']" in (HERE / tools[2]).read_text(encoding='utf8')
assert "idx=text.index('## 功能第298节')" in (HERE / tools[2]).read_text(encoding='utf8')
assert "'next_section':300" in (HERE / tools[3]).read_text(encoding='utf8')
assert "'.exit'" not in stage and "'.bin'" not in stage
baseline = json.loads((HERE / 'BASELINE.json').read_bytes())
promotion_raw = (ROOT / baseline['promotion_receipt']).read_bytes()
assert sha256(promotion_raw).hexdigest() == baseline['promotion_receipt_sha256']
promotion = json.loads(promotion_raw)
assert len(promotion['promoted']) == 53 and len(promotion['existing_production_changes']) == 2
for name, pin in {**promotion['promoted'], **promotion['existing_production_changes']}.items():
    assert sha(ROOT / name) == pin['sha256'] and (ROOT / name).stat().st_size == pin['bytes'], name
archive = read(baseline['public_preparation_archive_manifest'])
assert sha(ROOT / baseline['public_preparation_archive_manifest']) == baseline['public_preparation_archive_manifest_sha256']
assert len(archive['files']) == 115
for name, pin in archive['files'].items():
    path = ROOT / 'verification/sections/299-preparation' / name
    assert not path.is_symlink() and sha(path) == pin['sha256'] and path.stat().st_size == pin['bytes'], name
for name, pin in baseline['raw_public_files_exact'].items():
    assert sha(ROOT / name) == pin['sha256'] and (ROOT / name).stat().st_size == pin['bytes']
assert len(baseline['raw_public_files_exact']) == 5
regular = {'.json', '.log', '.md', '.png', '.py', '.txt', '.diff', '.stderr', '.stdout', '.html'}
actual_nonstandard = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'verification/sections/299-preparation').rglob('*') if p.is_file() and p.suffix not in regular}
assert actual_nonstandard == set(baseline['raw_public_files_exact'])
repair = read(baseline['source_compatibility_repair'])
assert sha(ROOT / baseline['source_compatibility_repair']) == baseline['source_compatibility_repair_sha256']
assert repair['all_existing_tests_preserved'] is True and repair['data_or_game_mechanics_changed'] is False
old = ast.parse((ROOT / repair['old_controller']).read_bytes()); new = ast.parse((ROOT / repair['new_controller']).read_bytes())
def without_authority(tree):
    return ast.dump(ast.Module(body=[n for n in tree.body if not (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ('MANIFEST', 'MANIFEST_SHA256') for t in n.targets))], type_ignores=[]), include_attributes=False)
assert without_authority(old) == without_authority(new)
old_manifest = read(repair['old_manifest']); new_manifest = read(repair['new_manifest'])
assert old_manifest['files'].keys() == new_manifest['files'].keys()
assert {name for name in old_manifest['files'] if old_manifest['files'][name] != new_manifest['files'][name]} == {'rouge/event_planning.py', 'rouge/node_catalog.py'}
necessary_name = 'verification/sections/299-necessary-final/process.json'
necessary = read(necessary_name)
assert necessary['exit_code'] == 0 and necessary['source_sha256_before'] == necessary['source_sha256_after']
assert len(necessary['modules']) == 11 and len(necessary['source_sha256_after']) == 453
assert 'Ran 168 tests' in (ROOT / 'verification/sections/299-necessary-final/stderr.txt').read_text(encoding='utf8')
for name, value in necessary['source_sha256_after'].items():
    assert not name.startswith(('.cache/', '.local/')) and sha(ROOT / name) == value, name
for name, pin in baseline['files'].items(): assert sha(ROOT / '.cache/p3-298-publication-prep' / name) == pin['sha256']
after = {name: sha(HERE / name) for name in tools}
assert before == after
value = {'kind': 'SECTION299_PUBLICATION_CACHE_PREPARATION_ONLY', 'publication_tools_executed': False,
         'Git_mutation_Qt_tests_executed': False, 'parent_commit': 'b56cbf352cf5d171f52ba05839312950df462e8c',
         'functional_commit': None, 'metadata_commit': None, 'remote_ref': None, 'publication_passed': None,
         'final_section_receipt_required_at_execution': 'verification/sections/299.json',
         'final_native_main_visual_not_consumed_or_marked_pass_by_preparation': True,
         'native_validation_passed': None, 'main_window_validation_passed': None,
         'observed_necessary_only': {'receipt': necessary_name, 'sha256': sha(ROOT / necessary_name),
             'actual_exit': 0, 'methods': 168, 'modules': 11, 'source_files': 453,
             'first135_1F5E_and_author21_guard3_not_added_to_final_count': True},
         'tracked_allowlist': tracked, 'PROJECT_PROGRESS_staged': False,
         'new_promoted_entries': 53, 'existing_production_entries': 2, 'source_entries': 55,
         'old_tracked_test_maintenance': False, 'source_compatibility_only_two_code_pins_and_two_controller_constants': True,
         'exact_raw_public_files': baseline['raw_public_files_exact'],
         'next_section': 300, 'last_full_is_historical_after_section': 290, 'next_full_after_section': 305,
         'files': {name: {'sha256': sha(HERE / name), 'bytes': (HERE / name).stat().st_size}
                   for name in (*tools, 'prepare_tools_299.py', 'prepare_ready_299.py', 'RUN_PLAN.md', 'BASELINE.json')}}
with (HERE / 'READY.json').open('xb') as stream: stream.write((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps({'prepared': True, 'pure_AST_and_public_readback_only': True, 'tools_unchanged': True,
                  'four_tools_executed': False, 'new_source_entries': 55, 'tracked': 9, 'narrow_nonstandard_files': 5,
                  'observed_actual_necessary_methods': 168, 'publication_passed': None}))
