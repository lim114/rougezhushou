"""Select explicit public Source and recovery metadata, never live runtime trees."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/workspace/.continuation')
PRIOR = BASE / 'root-full095-public-continuation-supplements-v3.json'
OUTPUT = BASE / 'root-full095-public-continuation-supplements-v4.json'
PACKETS = (
    'full095-ui-identity-retry-source-v1',
    'full095-ui-identity-independent-review-v1',
    'full095-saved-validator-ui-identity-source-v1',
    'full095-saved-validator-ui-identity-independent-review-v1',
    'full095-regression-ui-identity-resume-source-v1',
    'full095-ui-identity-root-spec-source-preparation-v1',
    'full095-ui-identity-recovery-independent-source-review-v1',
    'full095-identity-recovery-helper-independent-scope-review-v1',
    'full095-ui-identity-recovery-final-independent-source-review-v1',
    'full095-identity-final-handoff-count-erratum-v1',
    'full095-regression-ui-identity-resume-final-v1',
    'full095-saved-control-ui-identity-source-v1',
    'full095-actual-acceptance-ui-identity-source-v1',
    'full095-archive-ui-identity-spec-source-v1',
    'full095-archive-ui-identity-spec-source-v2',
    'full095-ui-identity-archive-final-review-source-v1',
    'full095-ui-identity-evidence-sealer-source-v1',
    'full095-ui-identity-evidence-sealer-source-v2',
    'full095-third-ui-identity-saved-and-archive-handoff-v1',
    'full095-identity-evidence-helpers-independent-source-review-v1',
    'full095-ui-identity-evidence-final-v1',
    'full095-ui-identity-evidence-final-independent-source-review-v1',
    'full095-ui-identity-actual-observer-source-v1',
    'full095-ui-identity-actual-observer-binding-source-v1',
    'full095-ui-identity-actual-observer-independent-source-review-v1',
    'p2-condition096-final-admission-source-preparation-v1',
)
LOOSE_FILES = (
    'root-full095-public-continuation-supplements-v3.json',
    'root-prepare095-public-continuation-supplements-v3.py',
    'root-prepare095-public-continuation-supplements-v3.log',
    'root-prepare095-public-continuation-supplements-v3.exit-code',
    'ROOT_CURRENT_WORK_095_UI_CACHE_SESSION_LOST_PRIMARY_UNAVAILABLE.json',
    'root-full095-ui-cache-session-lost-v1-native-index.json',
    'root-record095-ui-cache-session-lost-v1.py',
    'root-record095-ui-cache-session-lost-v1.log',
    'root-record095-ui-cache-session-lost-v1.exit-code',
    'root-WORK_IN_PROGRESS-before095-ui-cache-session-lost-v1.bin',
    'root-full095-ui-identity-retry-v1-prelaunch.json',
    'root-full095-ui-identity-retry-v1-actual-spec.json',
    'root-assemble095-ui-identity-actual-spec-v1.log',
    'root-assemble095-ui-identity-actual-spec-v1.exit-code',
    'root-seal095-ui-identity-context-v1.log',
    'root-seal095-ui-identity-context-v1.exit-code',
    'root-seal095-ui-identity-evidence-v1.log',
    'root-seal095-ui-identity-evidence-v1.exit-code',
    'root-resume095-ui-identity-v1.log',
    'root-resume095-ui-identity-v1.exit-code',
    'root-full095-wine_ui-identity-retry-v1-actual-launch.json',
    'root-recovery-progress-report095-draft-v1.md',
)

def ref(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    assert str(path.resolve()) == str(path) and path.is_relative_to(BASE)
    raw = path.read_bytes()
    assert len(raw) < 100 * 1024 * 1024
    return {'path': str(path), 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest()}

def main():
    assert not OUTPUT.exists()
    prior_ref = ref(PRIOR)
    assert prior_ref['sha256'] == 'a83e6afc45f239098a54fb165916fbd3f23b0dd6cc4f1dd947b06a284ecaadf7'
    prior = json.loads(PRIOR.read_bytes())
    rows = list(prior['rows'])
    assert len(rows) == 249
    for row in rows:
        assert ref(row['file']['path']) == row['file']
    selected = {row['file']['path'] for row in rows}
    archive_names = {row['archive_path'] for row in rows}
    counts = dict(prior['packet_file_counts'])
    qualification = ('Explicit public Source/recovery metadata preparation, not an additional '
                     'runtime, numbered section completion, or full95 PASS. Source statuses '
                     'remain historical at their author/sealing times. Two lost UI attempts '
                     'retain unknown primary exits. Sections96 onward are paused.')
    def add(path):
        full = ref(path)
        if full['path'] in selected:
            return
        archive = 'continuation-public-preparation/' + path.relative_to(BASE).as_posix()
        assert archive not in archive_names
        rows.append({'file': full, 'archive_path': archive, 'qualification': qualification})
        selected.add(full['path'])
        archive_names.add(archive)
    for name in PACKETS:
        folder = BASE / name
        assert folder.is_dir() and not folder.is_symlink()
        files = sorted(p for p in folder.rglob('*') if p.is_file())
        assert files and all('__pycache__' not in p.parts for p in files)
        counts[name] = len(files)
        for path in files:
            add(path)
    for name in LOOSE_FILES:
        add(BASE / name)
    value = {'status': 'EXPLICIT_PUBLIC_RECOVERY_SUPPLEMENTS_PREPARED_NOT_ARCHIVED_OR_FULLPASS',
             'prepared_at_UTC': datetime.now(timezone.utc).isoformat(),
             'prior_selection': prior_ref, 'packet_file_counts': counts, 'rows': rows,
             'full095_available_validation_passed': False,
             'commit_or_push_performed': False, 'completed_section_increment': 0,
             'future_actual096_097_098_guards': None,
             'scope': 'Explicit named public Source packets and Root recovery metadata only; '
                      'no live native directory, private state, DLL or binary discovery.'}
    with OUTPUT.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'output': ref(OUTPUT), 'files': len(rows),
                      'total_bytes': sum(row['file']['bytes'] for row in rows),
                      'runtime_or_project_executions': 0}))

if __name__ == '__main__':
    main()
