"""Compare a frozen external public package with a named clean root commit."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
label, revision = sys.argv[1:]
commit = subprocess.check_output(['git', 'rev-parse', revision], cwd=REPO, text=True).strip()
freeze = json.loads((HERE / f'public-source-freeze-{label}.json').read_text())
package = HERE / f'public-schema-{label}'
mismatch = []
for name, digest in freeze['source_sha256'].items():
    raw = (package / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest, name
    committed = subprocess.check_output(['git', 'show', f'{commit}:{name}'], cwd=REPO)
    if raw != committed:
        mismatch.append(name)
receipt = {
    'scope': 'Read-only byte comparison of previously tested external public package with root committed source; no repeated API/Qt/Wine run',
    'root_commit': commit,
    'public_file_count': len(freeze['source_sha256']),
    'git_blob_mismatch': mismatch,
    'source_sha256': freeze['source_sha256'],
    'gui_executed': False,
    'wine_executed': False,
}
(HERE / f'root-source-compatibility-{label}.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
assert not mismatch, mismatch
print({'public_files': receipt['public_file_count'], 'strict_same': True, 'root_commit': commit})
