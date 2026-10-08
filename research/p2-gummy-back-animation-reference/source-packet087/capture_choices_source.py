import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASELINE = '9ef5a469673502754db3be320a8eece9a7fd18d4'
REL = 'rouge/animation_reference.py'
PROJECT = '/workspace/rougezhushou'
data = subprocess.check_output(['git', '-C', PROJECT, 'show', f'{BASELINE}:{REL}'])
blob = subprocess.check_output(['git', '-C', PROJECT, 'rev-parse', f'{BASELINE}:{REL}']).decode().strip()
assert hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest() == blob
dest = ROOT / 'history' / 'animation_reference.py'
dest.write_bytes(data)
receipt = {
    'version': 1, 'baseline_commit': BASELINE, 'repository_path': REL,
    'snapshot_path': str(dest), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'git_blob_sha1': blob,
    'source_read_only': True, 'choices_or_descriptor_helper_calls': 0,
    'finding': 'choices requires Attack prefix or a matching numbered Skill regex. The literal animation Skill has no numbered match and is not an available skill choice.',
    'scope': 'No choices function or UI was invoked and no UI option count is measured. The Back Attack source metadata may be a conventional optional reference only; native normal binding is unknown.',
    'application_calls_or_tests': 0,
}
(ROOT / 'choices-source-scope-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'source_read_only': True, 'helper_calls': 0}, indent=2))
