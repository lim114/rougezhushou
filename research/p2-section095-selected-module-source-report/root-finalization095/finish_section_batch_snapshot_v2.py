"""Freeze exact archive/index evidence without a per-section commit or tag."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
spec_path = Path(sys.argv[1])
spec = json.loads(spec_path.read_bytes())
n = spec['number']
assert spec['verification']['actual_window_verified_by_root'] is True
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/p2-development'
archive = ROOT / spec['verification']['research_archive']
assert archive.is_dir() and not (archive / 'archive-manifest.json').exists()
source_path = Path(spec.get('root_source_guard', str(LOCAL / f'root-source-{n:03d}.json')))
assert source_path.resolve().parent == LOCAL.resolve()
assert source_path.name in (f'root-source-{n:03d}.json', f'root-source-{n:03d}-v2.json')
source = json.loads(source_path.read_bytes())
assert source['passed'] is True
assert source['current_maintained'] == spec['verification']['maintained_source_files']
assert source['unchanged_maintained'] == spec['verification']['unchanged_maintained_source_files']
current = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
    for directory in ('rouge', 'tests', 'scripts') for p in sorted((ROOT / directory).rglob('*'))
    if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
assert current == source['source_sha256_after']
related_path = Path(spec.get('root_related_log', str(LOCAL / f'root-related-{n:03d}.log')))
assert related_path.resolve().parent == LOCAL.resolve()
assert related_path.name in (f'root-related-{n:03d}.log', f'root-related-{n:03d}-v2.log')
assert related_path.with_suffix('.exit-code').read_bytes() == b'0\n'
related = related_path.read_text()
assert related.rstrip().endswith('OK')
run = int(re.search(r'Ran (\d+) tests', related).group(1))
selected_path = Path(spec.get('root_selected_log', str(LOCAL / f'root-selected-{n:03d}.log')))
assert selected_path.resolve().parent == LOCAL.resolve()
assert selected_path.name in (f'root-selected-{n:03d}.log', f'root-selected-{n:03d}-v2.log')
assert selected_path.with_suffix('.exit-code').read_bytes() == b'0\n'
selected = json.loads(selected_path.read_text().strip().splitlines()[-1])
assert selected['passed'] is True and selected['failures'] == selected['errors'] == 0
spec['verification']['checks'] = [
    {'command': spec['related_scope'], 'run': run, 'passed': run, 'skipped': 0, 'failures': 0, 'errors': 0},
    {'command': '.venv/bin/python scripts/verify_cloud.py', 'run': selected['tests_run'],
     'passed': selected['tests_run']-selected['skipped'], 'skipped': selected['skipped'], 'failures': 0, 'errors': 0}]
for path in (source_path, related_path, selected_path, Path(spec['root_source_script'])):
    shutil.copyfile(path, archive / path.name)
spec['verification']['actual_base_HEAD_at_archival'] = head
spec['verification']['commit_policy'] = 'archive each section; commit and push after each fifth-section full PASS'
spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + '\n')
manifest = {p.relative_to(archive).as_posix(): {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
    for p in sorted(archive.rglob('*')) if p.is_file()}
(archive / 'archive-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
subprocess.run(['git', '-c', 'core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol', 'diff', '--check'], cwd=ROOT, check=True)
names = [str((archive/name).relative_to(ROOT)) for name in manifest] + [str((archive/'archive-manifest.json').relative_to(ROOT))]
subprocess.run(['git', 'add', '-f', '--', *names], cwd=ROOT, check=True)
staged = {}
for item in subprocess.check_output(['git', 'ls-files', '--stage', '-z', '--', str(archive.relative_to(ROOT))], cwd=ROOT).split(b'\0'):
    if item:
        header, name = item.split(b'\t', 1)
        staged[name.decode()] = header.decode().split()[1]
assert set(staged) == set(names)
for name in names:
    data = (ROOT/name).read_bytes()
    assert staged[name] == hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(), name
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == head
subprocess.run(['.venv/bin/python', str(LOCAL / 'record_section_batch_snapshot.py'), str(spec_path)], cwd=ROOT, check=True)
out = LOCAL / f'section{n:03d}-archived-working-tree-closure.json'
with out.open('x') as stream:
    json.dump({'format_version':1, 'section':n, 'status':'VERIFIED_ARCHIVED_NOT_COMMITTED_OR_PUSHED',
        'actual_HEAD_unchanged':head, 'archive_files':len(names), 'all_archive_index_blobs_exact':True,
        'archive_manifest_sha256':hashlib.sha256((archive/'archive-manifest.json').read_bytes()).hexdigest(),
        'source_snapshot_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),
        'commit_and_push_after_next_fifth_section_full_PASS':True}, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'section':n,'related_passed':run,'selected':selected,'HEAD_unchanged':head,
    'archive_files':len(names),'archive_index_exact':True,'committed_or_pushed':False},ensure_ascii=False))
