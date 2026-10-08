"""Prove the excluded public125 package is exact named root085 git blobs."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
freeze = json.loads((HERE / 'public-source-freeze-085.json').read_bytes())
source = json.loads((HERE / 'root-source-085-proof.json').read_bytes())
commit = freeze['base_commit']
assert commit == source['root_commit'] == '2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b'
assert len(source['files']) == source['maintenance_python_json_files'] == 723
index = {row['source_path']: row for row in source['files']}
names = sorted(freeze['source_sha256'])
assert len(names) == 125 and not freeze['patches']
batch = subprocess.check_output(
    ['git', 'cat-file', '--batch'], cwd=REPO,
    input=''.join(f'{commit}:{name}\n' for name in names).encode())
offset = 0
rows = []
for name in names:
    end = batch.index(b'\n', offset)
    blob, kind, length = batch[offset:end].decode().split()
    assert kind == 'blob'
    offset = end + 1
    raw = batch[offset:offset + int(length)]
    offset += int(length)
    assert batch[offset:offset + 1] == b'\n'
    offset += 1
    public = (HERE / 'public-schema-085' / name).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert raw == public == (REPO / name).read_bytes(), name
    assert digest == freeze['source_sha256'][name] == index[name]['sha256'], name
    assert len(raw) == index[name]['bytes'] and blob == index[name]['git_blob_sha1']
    rows.append({'path': name, 'bytes': len(raw), 'sha256': digest,
                 'git_blob_object_id': blob})
assert offset == len(batch)
receipt = {
    'status': 'PASS_PUBLIC125_EXACT_NAMED_ROOT085_GIT_BLOBS',
    'root_source_commit': commit, 'public_source_files': len(rows),
    'total_source_bytes': sum(row['bytes'] for row in rows),
    'all_bytes_equal': True, 'source_drift': [],
    'excluded_duplicate_directory': 'public-schema-085',
    'root723_source_proof_sha256': hashlib.sha256((HERE / 'root-source-085-proof.json').read_bytes()).hexdigest(),
    'rebuild_recipe': 'Read git show <root_source_commit>:<path> for each listed path; preserve bytes exactly, without overlay.',
    'files': rows, 'new_public_API_calls': 0, 'formatter_calls': 0,
    'gui_executed': False, 'wine_executed': False,
}
path = HERE / 'public-package-rebuild-proof085.json'
path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
compat = {'scope': 'Read-only125 public byte comparison with named root085; no repeated API/Qt/Wine',
          'root_commit': commit, 'public_file_count': len(rows), 'git_blob_mismatch': [],
          'source_sha256': freeze['source_sha256'], 'gui_executed': False, 'wine_executed': False}
(HERE / 'root-source-compatibility-085.json').write_text(json.dumps(compat, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'public_source_files': len(rows), 'exact_hash_bytes_and_git_object_proven': True,
                  'proof_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}))
