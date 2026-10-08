"""Archive the sealed full-085 receipts after the root's actual Wine window run."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
OUT = Path('/workspace/.compat')
SRC = LOCAL / 'ui-085-draft'
BASE = ROOT / 'verification/full-085'
FROZEN = '2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b'

def sha(data):
    return hashlib.sha256(data).hexdigest()

assert Path.cwd() == ROOT
assert subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip() == 'codex/p2-development'
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == FROZEN
assert not subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip()
assert not BASE.exists(), 'Do not overwrite an archived or partially archived batch.'
preflight = json.loads((OUT / 'root-ui-preflight-085.json').read_text())
assert preflight['passed'] and preflight['source_commit'] == FROZEN
assert preflight['source_files_verified'] == 723
for name, digest in preflight['fixed_hashes'].items():
    assert sha((SRC / name).read_bytes()) == digest, name
manifest_path = SRC / preflight['public_manifest_name']
manifest_bytes = manifest_path.read_bytes()
manifest = json.loads(manifest_bytes)
assert manifest['format_version'] == 1
assert len(manifest['files']) == preflight['public_attachments_verified_before_actual_execution']
payloads = []
names = set()
for row in manifest['files']:
    name = Path(row['archive_path'])
    assert not name.is_absolute() and '..' not in name.parts and name.as_posix() not in names
    names.add(name.as_posix())
    data = Path(row['source_path']).read_bytes()
    assert len(data) == row['bytes'] and sha(data) == row['sha256'], row['source_path']
    payloads.append((name, data))
readonly_payloads = []
readonly_counts = []
for packet in preflight.get('additional_readonly_audits', []):
    prefix = Path(packet['archive_prefix'])
    assert not prefix.is_absolute() and '..' not in prefix.parts
    path = Path(packet['manifest_path'])
    data = path.read_bytes()
    assert sha(data) == packet['manifest_sha256']
    info = json.loads(data)
    assert info['format_version'] == 1 and len(info['files']) == packet['files']
    seen = set()
    readonly_payloads.append((prefix / path.name, data))
    for row in info['files']:
        name = Path(row['archive_path'])
        assert not name.is_absolute() and '..' not in name.parts and name.as_posix() not in seen
        seen.add(name.as_posix())
        raw = Path(row['source_path']).read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
        readonly_payloads.append((prefix / name, raw))
    readonly_counts.append({'archive_prefix': prefix.as_posix(), 'files': packet['files'],
                            'manifest_sha256': packet['manifest_sha256'], 'numbered_section': False})
assert len({name.as_posix() for name, _ in readonly_payloads}) == len(readonly_payloads)
ui = json.loads((OUT / 'wine-ui-085.json').read_text())
ctx = json.loads((OUT / 'wine-validation-085-context.json').read_text())
inspection = json.loads((OUT / 'root-window-inspection-085.json').read_text())
assert ui['passed'] and ui['complete_ui_validation'] and len(ui['checks']) == 4217
assert ui['preserved_full_080_checks'] == 3063 and ui['supplemental_checks_81_85'] == 1154
assert not ui['source_drift'] and ui['private_state_isolated']
assert not ui['native_windows_verified'] and not ui['game_captures'] and not ui['chat_requests']
assert ctx['available_checks_passed'] and not ctx['source_drift'] and len(ctx['source_sha256']) == 723
assert inspection['passed'] and len(inspection['root_viewed_actual_pngs']) == 4
for name, digest in ctx['source_sha256'].items():
    assert sha((ROOT / name).read_bytes()) == digest, name
assert sha((OUT / 'wine-ui-smoke-085.py').read_bytes()) == preflight['fixed_hashes']['wine-ui-smoke-085.py']
for name, row in inspection['root_viewed_actual_pngs'].items():
    assert sha((OUT / name).read_bytes()) == row['sha256'], name

BASE.mkdir()
design = BASE / 'ui-source-design'
design.mkdir()
for name, data in payloads:
    target = design / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    assert target.read_bytes() == data
(design / manifest_path.name).write_bytes(manifest_bytes)
subprocess.run(['.venv/bin/python', str(LOCAL / 'archive-module-negative-audits085.py')], check=True)
for name, data in readonly_payloads:
    target = BASE / 'public-source-audits' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    assert target.read_bytes() == data
if readonly_counts:
    (BASE / 'public-source-audits/additional-root-byte-verification.json').write_text(json.dumps(
        {'passed': True, 'packets': readonly_counts, 'root_new_API_helper_test_Qt_Wine_calls': 0,
         'fresh_nonfinite_runtime_behavior_verified': False, 'numbered_section': False}, indent=2) + '\n')
next_action = '自动推进86–90；先按已封来源与独审修正剩余12个实际条件文本输入，保留天赋资格、覆盖与旧错误顺序；每节回归存档，第90节后全量并自动继续'
subprocess.run(['.venv/bin/python', str(LOCAL / 'archive_full.py'), '85', str(LOCAL / 'linux-full-085.json'), next_action], check=True)
copies = [
    (LOCAL / 'linux-full-085.log', 'linux-full.log'),
    (LOCAL / 'selected-085.log', 'linux-selected.log'),
    (LOCAL / 'linux-pipcheck-085.log', 'linux-pipcheck.log'),
    (LOCAL / 'linux-selected-085-byte-identity.json', 'linux-selected-byte-identity.json'),
    (LOCAL / 'root-selected-source-snapshot085.json', 'root-selected-source-snapshot.json'),
    (OUT / 'wine-available-full-085.log', 'wine-full.log'),
    (OUT / 'wine-cloud-085.log', 'wine-selected.log'),
    (OUT / 'wine-ui-085-process.log', 'wine-ui-process.log'),
    (OUT / 'root-ui-preflight-085.json', 'root-ui-preflight.json'),
    (OUT / 'root-window-inspection-085.json', 'root-window-inspection.json'),
    (OUT / 'wine-sown-tile-control-085.png', 'wine-sown-tile-control.png'),
    (OUT / 'wine-movement-reference-085.png', 'wine-movement-reference.png'),
    (OUT / 'wine-medical-trait-085.png', 'wine-medical-trait.png'),
]
for source, name in copies:
    assert source.is_file(), source
    shutil.copyfile(source, BASE / name)
for name in ('full_context.py', 'selected_snapshot_full.py', 'archive-module-negative-audits085.py', 'archive-full-085.py',
             'root-ui-preflight085.py', 'root-ui-preflight085-spec.json'):
    shutil.copyfile(LOCAL / name, BASE / name)
limits = (
    f'Frozen code {FROZEN}; all723 maintained product/test/script source bytes remained identical. '
    'Linux1839run/1679pass/84historical skips/126unavailable records and Wine1903run/1753pass/84skips/123unavailable; zero failures, errors or source drift. '
    'Actual MainWindow87 skills/4217 records includes all3063 older checks plus1154 new state designs. '
    f'Elapsed actual window time: {ui["elapsed_seconds"]} seconds. '
    'Root independently viewed four actual PNGs; visible controls and report excerpts are recorded separately from underlying receipt assertions. '
    f'All{len(payloads)} explicitly sealed UI evidence files and the original manifest are included, preserving every preparation/contract diagnostic and saved-result continuation proof. '
    'UI API preflight state count, unique calculation parameters, actual calculation requests, report-string requests and formatter function entries are separate measured fields in its final receipt; saved results were reasserted without new calls. '
    'Linux selected1019run/1018pass/1historical skip were reused only after all723source hashes matched; Wine selected ran anew with the same counts. Both pip checks passed. '
    'Attached source-gap and finite-input audits are bounded negative read-only audits, not numbered sections; the module audit original six independent API probes are not rerun, and the finite audit does not establish fresh NaN/inf behavior or comprehensive overflow protection. '
    'Missing original/private fixtures were never reconstructed or counted as passed. Complete repository/native Windows/game capture/account actuality/desktop chat/multiple-machine installation remain unverified.\n'
)
(BASE / 'LIMITS.md').write_text(limits)
cp = json.loads((ROOT / 'DEVELOPMENT_CHECKPOINT.json').read_text())
cp['wine_validation'] = '第85节后2dfd9fa：Wine1753可用项、MainWindow87技能/4217条实际检查通过；保留旧3063；723源码零漂移。完整仓库/原生Windows/game/desktop未验收，缺失记录不计通过。'
(ROOT / 'DEVELOPMENT_CHECKPOINT.json').write_text(json.dumps(cp, ensure_ascii=False, indent=2) + '\n')
entries = {p.relative_to(BASE).as_posix(): {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
           for p in sorted(BASE.rglob('*')) if p.is_file() and p != BASE / 'archive-manifest.json'}
(BASE / 'archive-manifest.json').write_text(json.dumps(entries, indent=2) + '\n')
for name, row in entries.items():
    raw = (BASE / name).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], name
subprocess.run(['git', '-c', 'core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol', 'diff', '--check'], check=True)
subprocess.run(['git', 'add', 'DEVELOPMENT_CHECKPOINT.json', 'WORK_IN_PROGRESS.md', 'PROJECT_COMPLETED.md', 'BATCH_CONTINUOUS_P2.md', str(BASE)], check=True)
logs = [str(p) for p in BASE.rglob('*.log')]
if logs:
    subprocess.run(['git', 'add', '-f', *logs], check=True)
subprocess.run(['git', 'commit', '--quiet', '-m', '存档第85节Linux与Wine全量及4217条真实窗口检验'], check=True)
subprocess.run(['git', 'tag', 'p2-validation-085'], check=True)
print(json.dumps({'full_validation': 85, 'ui_attachments_archived': len(payloads), 'actual_ui_records': len(ui['checks']),
                  'readonly_audit_artifacts': 47 + sum(row['files'] for row in readonly_counts),
                  'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}))
