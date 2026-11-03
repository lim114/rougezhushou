"""Source-text and fixed Git blob identity review; no choices/helper imports."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent / 'p2-gummy-back-parser-source087'
COMMIT = '9ef5a469673502754db3be320a8eece9a7fd18d4'
SNAP = ROOT / 'choices-source-snapshots'
SNAP.mkdir(exist_ok=True)
bindings = []
for name in ['choices-source-scope-receipt.json', 'history/animation_reference.py']:
    src = PARENT / name
    dst = SNAP / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    raw = dst.read_bytes()
    assert raw == src.read_bytes()
    bindings.append({'source_path': str(src), 'archive_path': str(dst.relative_to(ROOT)),
        'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
source_path = SNAP / 'history/animation_reference.py'
raw = source_path.read_bytes()
receipt = json.loads((SNAP / 'choices-source-scope-receipt.json').read_text())
source = raw.decode('utf-8')
fixed_git_blob = subprocess.run(['git', '-C', '/workspace/rougezhushou', 'show',
    COMMIT + ':rouge/animation_reference.py'], check=True, capture_output=True).stdout
assert raw == fixed_git_blob
assert receipt['baseline_commit'] == COMMIT
assert receipt['bytes'] == len(raw)
assert receipt['sha256'] == hashlib.sha256(raw).hexdigest()
assert receipt['git_blob_sha1'] == hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
assert "if not record['selectable_as_conventional_reference']:continue" in source
assert "number=re.match(r'^Skill_?(\d+)(?:_|$)',name)" in source
assert "ordinary=name.startswith('Attack')" in source
assert "if (normal and ordinary) or (not normal and (ordinary or number and int(number[1])==skill)):" in source
assert "record=next((r for r in choices(operator,skill,normal=normal) if r['id']==identity),None)" in source
out = {'version': 1, 'status': 'PASS_SOURCE_ONLY_NO_UI_OPTION_COUNT',
    'reviewed_at_utc': datetime.now(timezone.utc).isoformat(), 'baseline_commit': COMMIT,
    'input_bindings': bindings, 'exact_named_git_source_verified': True,
    'selectable_record_gate': 'selectable_as_conventional_reference must be true before either branch',
    'literal_Skill_numbered_regex_match': False,
    'literal_Skill_Attack_prefix_match': False,
    'literal_Skill_choice_branch_eligibility': False,
    'Back_Attack_source_candidate': 'Attack prefix meets ordinary predicate; eligibility remains conditional on record publication/selectable gate and explicit selection. Existing function permits ordinary records for normal or skill branch.',
    'metadata_candidate_count_is_UI_choice_count': False,
    'Back_Skill_native_skill_number_inferred': False,
    'Back_Attack_native_normal_binding_inferred': False,
    'actual_UI_options_or_selection_verified': False,
    'choices_descriptor_or_other_production_helper_calls': 0,
    'application_API_formatter_tests_Qt_Wine_full_parser_calls': 0,
    'scope': 'Static exact function predicate; no helper invocation, new source record publication or UI operation.'}
dst = ROOT / 'choices-source-independent-review087.json'
dst.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': out['status'], 'bytes': dst.stat().st_size,
    'sha256': hashlib.sha256(dst.read_bytes()).hexdigest(), 'helper_calls': 0}))
