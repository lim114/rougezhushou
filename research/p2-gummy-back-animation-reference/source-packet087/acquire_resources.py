"""Reacquire only two pinned public resources via Git metadata, with TLS."""
import hashlib
import json
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent
COMMIT = 'd0b5af0b004b044d322397ce5ae79632b6d9fcdd'
API = 'https://api.github.com/repos/fexli/ArknightsResource/contents/'
FOLDER = 'spine/char_196_sunbr/char_196_sunbr'
OUT.mkdir(parents=True, exist_ok=True)


def fetch(url, destination):
    assert url.startswith('https://')
    request = urllib.request.Request(url, headers={'User-Agent': 'Codex-public-source-audit',
        'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(request, timeout=30) as response:
        content = response.read()
        status = response.status
        final_url = response.geturl()
        headers = dict(response.headers)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return {'requested_url': url, 'final_url': final_url, 'status': status,
        'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest(),
        'response_headers': {name: value for name, value in headers.items()
                             if name.lower() in ('etag', 'last-modified', 'content-type', 'content-length')},
        'TLS_certificate_verification': 'Python default verified TLS; no unverified context or bypass'}


directory_url = API + FOLDER + '?ref=' + COMMIT
directory_path = OUT / 'metadata/resource-directory.json'
directory_receipt = fetch(directory_url, directory_path)
directory = json.loads(directory_path.read_bytes())
assert isinstance(directory, list)
folders = {entry['name']: entry for entry in directory}
assert all(folders[face]['type'] == 'dir' for face in ('Front', 'Back'))
records = []
for face in ('Front', 'Back'):
    path = folders[face]['path'] + '/char_196_sunbr.skel'
    metadata_url = API + path + '?ref=' + COMMIT
    metadata_path = OUT / ('metadata/' + face + '-resource.json')
    metadata_receipt = fetch(metadata_url, metadata_path)
    metadata = json.loads(metadata_path.read_bytes())
    assert metadata['type'] == 'file' and metadata['path'] == path
    assert metadata['name'] == 'char_196_sunbr.skel'
    url = metadata['download_url']
    assert url == 'https://raw.githubusercontent.com/fexli/ArknightsResource/' + COMMIT + '/' + path
    destination = OUT / ('reacquired/' + face + '/char_196_sunbr.skel')
    download = fetch(url, destination)
    data = destination.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    assert len(data) == metadata['size'] and blob == metadata['sha']
    if face == 'Front':
        assert len(data) == 90939
        assert hashlib.sha256(data).hexdigest() == '7bf9d7e014bf3402043639d4c348ca2409e89c7ab4cb0d794c52f4278d5c9d04'
        assert blob == 'cc171af6926392621c192c1dc5ba4f036d1b9b00'
    records.append({'orientation': face, 'source_commit': COMMIT,
        'source_path': path, 'metadata_url': metadata_url,
        'metadata_receipt': metadata_receipt, 'download': download,
        'git_blob_expected': metadata['sha'], 'git_blob_computed': blob,
        'metadata_size': metadata['size'], 'resource_archive_path': destination.relative_to(OUT).as_posix(),
        'newly_reacquired': True, 'historical_cache_reconstructed': False})
(OUT / 'resource-acquisition.json').write_text(json.dumps({'passed': True,
    'source_commit': COMMIT, 'directory_receipt': directory_receipt,
    'resource_files': records, 'resource_file_count': 2,
    'application_calls': 0, 'animation_parse_attempts': 0}, indent=2) + '\n')
print(json.dumps({'passed': True, 'resource_file_count': 2, 'animation_parse_attempts': 0,
                  'resources': [{'orientation': row['orientation'],
                    'bytes': row['download']['bytes'], 'sha256': row['download']['sha256'],
                    'git_blob': row['git_blob_computed']} for row in records]}))
