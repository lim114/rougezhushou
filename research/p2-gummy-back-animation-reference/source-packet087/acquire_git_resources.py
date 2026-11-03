import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT / 'git-metadata'
COMMIT = 'd0b5af0b004b044d322397ce5ae79632b6d9fcdd'
REMOTE = 'https://github.com/fexli/ArknightsResource.git'
PREFIX = 'spine/char_196_sunbr/char_196_sunbr'
receipt = {
    'version': 1, 'started_at': datetime.now(timezone.utc).isoformat(),
    'remote': REMOTE, 'commit': COMMIT, 'transport': 'standard Git HTTPS; inherited proxy and CA; TLS verification unchanged',
    'newly_reacquired': True, 'historical_cache_reconstructed': False,
    'resource_limit': 2, 'operations': [], 'resources': [], 'application_calls': 0, 'parser_calls': 0,
}

def save():
    (ROOT / 'git-acquisition-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')

def run(args, *, capture=True):
    start = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    out, err = result.stdout, result.stderr.decode('utf-8', 'replace')
    receipt['operations'].append({'command': args, 'started_at': start, 'finished_at': datetime.now(timezone.utc).isoformat(), 'exit_code': result.returncode, 'stdout_bytes': len(out), 'stderr': err})
    save()
    if result.returncode:
        raise RuntimeError(f'Git operation failed with exit {result.returncode}: {err}')
    if 'filtering not recognized' in err.lower() or 'filtering is not supported' in err.lower():
        raise RuntimeError('Partial filter not supported; stop without further resource operations')
    return out

if REPO.exists():
    raise RuntimeError('Use a new metadata directory; do not silently reuse partial state')
run(['git', 'init', '--bare', str(REPO)])
run(['git', '-C', str(REPO), 'remote', 'add', 'origin', REMOTE])
run(['git', '-C', str(REPO), 'config', 'remote.origin.promisor', 'true'])
run(['git', '-C', str(REPO), 'config', 'remote.origin.partialclonefilter', 'blob:none'])
run(['git', '-C', str(REPO), '-c', 'protocol.version=2', 'fetch', '--no-tags', '--depth=1', '--filter=blob:none', 'origin', COMMIT])
actual_commit = run(['git', '-C', str(REPO), 'rev-parse', 'FETCH_HEAD']).decode().strip()
assert actual_commit == COMMIT, (actual_commit, COMMIT)
commit_object = run(['git', '-C', str(REPO), 'cat-file', 'commit', COMMIT])
(ROOT / 'fixed-commit-object.txt').write_bytes(commit_object)
receipt['commit_object_sha256'] = hashlib.sha256(commit_object).hexdigest()
receipt['metadata_object_inventory_before_resource_reads'] = run(['git', '-C', str(REPO), 'count-objects', '-v']).decode()
tree_paths = [f'{PREFIX}/{orientation}/char_196_sunbr.skel' for orientation in ('Front', 'Back')]
tree_listing = run(['git', '-C', str(REPO), 'ls-tree', COMMIT, '--', *tree_paths]).decode()
(ROOT / 'fixed-two-paths-ls-tree.txt').write_text(tree_listing)
entries = {}
for line in tree_listing.splitlines():
    left, path = line.split('\t', 1)
    mode, kind, blob = left.split()
    assert mode == '100644' and kind == 'blob', (mode, kind, path)
    entries[path] = blob
assert set(entries) == set(tree_paths), entries
for orientation, path in zip(('Front', 'Back'), tree_paths):
    blob = entries[path]
    data = run(['git', '-C', str(REPO), 'cat-file', 'blob', blob])
    git_blob = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
    assert git_blob == blob, (orientation, git_blob, blob)
    git_size = int(run(['git', '-C', str(REPO), 'cat-file', '-s', blob]).decode().strip())
    assert git_size == len(data)
    sha = hashlib.sha256(data).hexdigest()
    if orientation == 'Front':
        assert len(data) == 90939 and blob == 'cc171af6926392621c192c1dc5ba4f036d1b9b00'
        assert sha == '7bf9d7e014bf3402043639d4c348ca2409e89c7ab4cb0d794c52f4278d5c9d04'
    dest = ROOT / 'reacquired' / orientation / 'char_196_sunbr.skel'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    receipt['resources'].append({'orientation': orientation, 'path': path, 'source_url': f'https://raw.githubusercontent.com/fexli/ArknightsResource/{COMMIT}/{path}', 'git_transport_url': REMOTE, 'source_path': str(dest), 'bytes': len(data), 'sha256': sha, 'git_blob_sha1': blob, 'git_cat_file_size': git_size, 'acquired_at': datetime.now(timezone.utc).isoformat()})
    save()
receipt['metadata_object_inventory_after_resource_reads'] = run(['git', '-C', str(REPO), 'count-objects', '-v']).decode()
receipt['finished_at'] = datetime.now(timezone.utc).isoformat()
receipt['completed'] = True
save()
print(json.dumps({'resources': receipt['resources'], 'completed': True}, ensure_ascii=False, indent=2))
