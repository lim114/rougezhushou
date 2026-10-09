import hashlib
import json
from pathlib import Path, PurePosixPath

BASE = Path('/workspace/.continuation')

def ref(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

previous = BASE / 'root-full095-public-continuation-supplements-v2.json'
assert ref(previous)['sha256'] == '2d2634dbce3e0abc93b663e033a42df7a64dc581a060f315898c0ecdddbc9084'
old = json.loads(previous.read_bytes())
assert old['full095_available_validation_passed'] is False
assert old['completed_section_increment'] == 0 and old['actual_files'] == 194
rows = list(old['rows'])
counts = dict(old['packet_file_counts'])
packets = (
    ('p2-runstate-reliability098-candidate-source-v1', 'public-artifacts-manifest.json', '70f4f88c958265b5c26bcca416040617a12e8e3ecf50926e18af01aeee82803a'),
    ('p2-runstate-reliability098-independent-source-review-v1', 'public-artifacts-manifest.json', '655f74ce5d33f64444e78e3b2493f3cba47376d0935390830310d4648822613b'),
    ('p2-condition096-root-execution-handoff-source-review-v1', 'public-artifacts-manifest-execution-handoff096.json', 'd0d5fa98639c9df3ef8f5d4400732f50350f9d3fcbb3738afec7a71382d52ef5'),
)
for name, manifest_name, manifest_sha in packets:
    packet = BASE / name
    manifest = packet / manifest_name
    assert ref(manifest)['sha256'] == manifest_sha
    contents = json.loads(manifest.read_bytes())['artifacts']
    expected = ({r['relative_path']: {'bytes': r['bytes'], 'sha256': r['sha256']} for r in contents}
                if isinstance(contents, list) else contents)
    files = sorted(p for p in packet.rglob('*') if p.is_file())
    assert {p.relative_to(packet).as_posix() for p in files} == set(expected) | {manifest_name}
    counts[name] = len(files)
    for path in files:
        rel = path.relative_to(packet).as_posix()
        full = ref(path)
        if rel != manifest_name:
            assert {'bytes': full['bytes'], 'sha256': full['sha256']} == expected[rel]
        assert '__pycache__' not in path.parts
        rows.append({'file': full, 'archive_path': 'continuation-public-preparation/' + name + '/' + rel,
                     'qualification': 'Sealed future Source preparation only; runtime admission, actual results and numbered completion remain absent.'})

names = ['root-full095-public-continuation-supplements-v2.json',
         'root-prepare095-public-continuation-supplements-v2.log',
         'root-prepare095-public-continuation-supplements-v2.exit-code']
for version, sequence in ((3, '03'), (4, '04')):
    names += ['ROOT_CURRENT_WORK_095_UI_CACHE_RETRY_PROGRESS_V%d.json' % version,
              'root-full095-ui-cache-progress-%s-native-index.json' % sequence,
              'root-record095-live-progress-v%d.py' % version,
              'root-record095-live-progress-v%d.log' % version,
              'root-record095-live-progress-v%d.exit-code' % version,
              'root-WORK_IN_PROGRESS-before095-ui-live-v%d.bin' % version]
for name in names:
    rows.append({'file': ref(BASE / name),
                 'archive_path': 'continuation-public-preparation/root-observations/' + name,
                 'qualification': 'Original Root public metadata preparation or running-process checkpoint; no full095 or future runtime PASS.'})
assert len(rows) == len({r['archive_path'] for r in rows})
for row in rows:
    assert ref(row['file']['path']) == row['file']
    name = PurePosixPath(row['archive_path'])
    assert not name.is_absolute() and '..' not in name.parts
    assert row['file']['bytes'] < 100 * 1024 * 1024
result = dict(old, packet_file_counts=counts, rows=rows,
              previous_selection=ref(previous),
              actual_files=len(rows), actual_total_bytes=sum(r['file']['bytes'] for r in rows))
out = BASE / 'root-full095-public-continuation-supplements-v3.json'
with out.open('x', encoding='utf-8') as handle:
    json.dump(result, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
print(json.dumps({'selection': ref(out), 'actual_files': len(rows),
                  'actual_total_bytes': result['actual_total_bytes'],
                  'fullPASS_or_commit_or_push': False, 'completed_section_increment': 0}))
