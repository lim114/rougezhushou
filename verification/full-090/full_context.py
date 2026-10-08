"""Freeze and verify one available Linux/Wine regression batch."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
OUT = Path('/workspace/.compat')
LOCAL = Path('/workspace/.continuation')
phase, number = sys.argv[1], int(sys.argv[2])
suffix = f'{number:03d}'
path = OUT / f'wine-validation-{suffix}-context.json'

def now():
    return datetime.now(timezone.utc).isoformat()

def hashes():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ('rouge', 'tests', 'scripts')
            for p in sorted((ROOT / folder).rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}

def last_json(log):
    for line in reversed(log.read_text(encoding='utf-8', errors='replace').splitlines()):
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and 'tests_run' in data:
            return data
    raise ValueError(f'No selected regression JSON in {log}')

if phase == 'start':
    assert not path.exists(), 'A previous receipt must not be overwritten.'
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    assert branch == 'codex/p2-development'
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()
    ctx = {'section': number, 'started_at': now(), 'branch': branch,
           'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
           'source_sha256': hashes(), 'source_snapshot_before_execution': True,
           'native_windows': False}
    path.write_text(json.dumps(ctx, ensure_ascii=False, indent=2) + '\n')
    print({'source_files': len(ctx['source_sha256']), 'commit': ctx['commit']})
elif phase == 'finish':
    ctx = json.loads(path.read_text())
    after = hashes()
    ctx['source_sha256_after'] = after
    ctx['source_drift'] = [n for n in sorted(set(after) | set(ctx['source_sha256']))
                           if after.get(n) != ctx['source_sha256'].get(n)]
    linux = json.loads((LOCAL / f'linux-full-{suffix}.json').read_text())
    wine = json.loads((OUT / f'wine-available-full-{suffix}.json').read_text())
    ui = json.loads((OUT / f'wine-ui-{suffix}.json').read_text())
    selected = last_json(OUT / f'wine-cloud-{suffix}.log')
    linux_selected = last_json(LOCAL / f'selected-{suffix}.log')
    (OUT / f'wine-cloud-{suffix}.json').write_text(json.dumps(selected, ensure_ascii=False, indent=2) + '\n')
    checks = {'full': f'wine-available-full-{suffix}.json', 'selected': f'wine-cloud-{suffix}.json',
              'pip': f'wine-pipcheck-{suffix}.log', 'ui': f'wine-ui-{suffix}.json',
              'linux_pip': str(LOCAL / f'linux-pipcheck-{suffix}.log')}
    ctx.update(completed_at=now(), checks=checks, ui_checks=len(ui['checks']),
               complete_repository_validation=linux['complete_repository_validation'] and wine['complete_repository_validation'],
               complete_ui_validation=ui.get('complete_ui_validation', False))
    valid = not ctx['source_drift'] and all(r['available_checks_passed'] and not r['source_drift'] and not r['failures'] and not r['errors'] for r in (linux, wine))
    valid = valid and ui['passed'] and not ui['source_drift'] and all(r['passed'] and not r['failures'] and not r['errors'] for r in (selected, linux_selected))
    valid = valid and all('No broken requirements found.' in p.read_text(encoding='utf-8', errors='replace') for p in (OUT / checks['pip'], Path(checks['linux_pip'])))
    ctx['available_checks_passed'] = valid
    ctx['outcome'] = 'Available Linux/Wine tests, dependencies and actual Qt controls passed' if valid else 'Available checks require diagnosis; see individual receipts'
    path.write_text(json.dumps(ctx, ensure_ascii=False, indent=2) + '\n')
    print({k: ctx[k] for k in ('section', 'available_checks_passed', 'source_drift', 'ui_checks', 'complete_ui_validation')})
    assert valid, ctx['outcome']
else:
    raise ValueError(phase)
