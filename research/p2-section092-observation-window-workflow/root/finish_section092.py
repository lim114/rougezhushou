"""Close a verified complete group; force-stage and verify every public blob."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
BASE = '59961ec3d633ac91b01014fb06b357d45e5979f7'
spec_path = Path(sys.argv[1])
spec = json.loads(spec_path.read_bytes())
assert spec['number'] == 92 and spec['verification']['actual_window_verified_by_root'] is True
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/p2-development'
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == BASE
archive = ROOT / spec['verification']['research_archive']
assert archive.is_dir()
log = (LOCAL / 'root-related-092.log').read_text()
assert log.rstrip().endswith('OK')
run = int(re.search(r'Ran (\d+) tests', log).group(1))
selected = json.loads((LOCAL / 'root-selected-092.log').read_text().strip().splitlines()[-1])
assert selected['passed'] is True and selected['failures'] == selected['errors'] == 0
source = json.loads((LOCAL / 'root-source-092.json').read_bytes())
assert source['passed'] is True and source['current_maintained'] == 730 and source['unchanged_maintained'] == 728
current = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
           for directory in ('rouge', 'tests', 'scripts') for p in sorted((ROOT / directory).rglob('*'))
           if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
assert current == source['source_sha256_after']
spec['verification']['checks'] = [
    {'command': spec['related_scope'], 'run': run, 'passed': run, 'skipped': 0, 'failures': 0, 'errors': 0},
    {'command': '.venv/bin/python scripts/verify_cloud.py', 'run': selected['tests_run'], 'passed': selected['tests_run'] - selected['skipped'], 'skipped': selected['skipped'], 'failures': 0, 'errors': 0}
]
for label in ('related', 'selected', 'source'):
    extension = 'json' if label == 'source' else 'log'
    path = LOCAL / f'root-{label}-092.{extension}'
    shutil.copyfile(path, archive / path.name)
script = Path(spec['root_source_script'])
shutil.copyfile(script, archive / script.name)
manifest = {p.relative_to(archive).as_posix(): {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
            for p in sorted(archive.rglob('*')) if p.is_file() and p.name != 'archive-manifest.json'}
(archive / 'archive-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + '\n')
subprocess.run(['.venv/bin/python', str(LOCAL / 'record_section.py'), str(spec_path)], cwd=ROOT, check=True)
subprocess.run(['git', '-c', 'core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol', 'diff', '--check'], cwd=ROOT, check=True)
changed = spec['changed_paths'] + ['DEVELOPMENT_CHECKPOINT.json', 'WORK_IN_PROGRESS.md', 'PROJECT_COMPLETED.md', 'BATCH_CONTINUOUS_P2.md', 'verification/sections/092.json']
subprocess.run(['git', 'add', '--', *changed], cwd=ROOT, check=True)
archive_names = [str((archive / name).relative_to(ROOT)) for name in manifest] + [str((archive / 'archive-manifest.json').relative_to(ROOT))]
subprocess.run(['git', 'add', '-f', '--', *archive_names], cwd=ROOT, check=True)
staged = {}
for item in subprocess.check_output(['git', 'ls-files', '--stage', '-z', '--', str(archive.relative_to(ROOT))], cwd=ROOT).split(b'\0'):
    if item:
        header, name = item.split(b'\t', 1)
        staged[name.decode()] = header.decode().split()[1]
assert set(staged) == set(archive_names)
for name in archive_names:
    data = (ROOT / name).read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    assert staged[name] == blob, name
subprocess.run(['git', 'commit', '--quiet', '-m', spec['commit_message']], cwd=ROOT, check=True)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
for name in archive_names + changed:
    assert subprocess.check_output(['git', 'show', f'{head}:{name}'], cwd=ROOT) == (ROOT / name).read_bytes(), name
subprocess.run(['git', 'tag', 'p2-section-092'], cwd=ROOT, check=True)
assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT).strip()
with (LOCAL / 'section092-committed-closure.json').open('xb') as stream:
    stream.write((json.dumps({'format_version': 1, 'section': 92, 'head': head, 'tag': 'p2-section-092', 'archive_files': len(archive_names), 'all_index_and_commit_blobs_exact': True, 'changed_paths_commit_exact': changed, 'archive_manifest_sha256': hashlib.sha256((archive / 'archive-manifest.json').read_bytes()).hexdigest(), 'working_tree_clean': True}, ensure_ascii=False, indent=2) + '\n').encode())
print(json.dumps({'section': 92, 'related_passed': run, 'selected': selected, 'head': head, 'archive_files': len(archive_names), 'commit_blobs_exact': True, 'working_tree_clean': True}, ensure_ascii=False))
