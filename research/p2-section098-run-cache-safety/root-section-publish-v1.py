"""Root-only real commit, normal push and remote equality observation."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('spec')
    args = parser.parse_args()
    spec = json.loads(Path(args.spec).read_text())
    repo = Path('/workspace/rougezhushou')
    external = Path('/workspace/.continuation')
    n = spec['section']
    archive = spec['archive']
    guard = json.loads(Path(spec['source_guard']).read_text())
    for path, sha in guard['source_sha256'].items():
        assert hashlib.sha256((repo / path).read_bytes()).hexdigest() == sha, path
    output = external / f'section{n:03d}-publication-v1.json'
    assert not output.exists()
    subprocess.run(['git', 'add', '--update', '--', '.'], cwd=repo, check=True)
    new = [path for path in guard['changed_paths'] if path in guard['source_sha256']]
    subprocess.run(['git', 'add', '--', *new, f'verification/sections/{n:03d}.json'], cwd=repo, check=True)
    subprocess.run(['git', 'add', '-f', '--', archive], cwd=repo, check=True)
    subprocess.run(['git', '-c', 'core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol',
                    'diff', '--cached', '--check', '--', '.', ':(exclude)' + archive], cwd=repo, check=True)
    manifest = json.loads((repo / archive / 'manifest.json').read_text())
    indexed = set(subprocess.check_output(['git', 'ls-files', archive], cwd=repo, text=True).splitlines())
    for row in manifest['files']:
        relative = archive + '/' + row['path']
        assert relative in indexed, relative
        assert hashlib.sha256((repo / relative).read_bytes()).hexdigest() == row['sha256']
    command = ['git', 'commit', '-m', f'完成第{n}节{spec["topic"]}及实际验证']
    commit = subprocess.run(command, cwd=repo, capture_output=True, text=True)
    commit_log = external / f'section{n:03d}-commit-v1.log'
    with commit_log.open('x') as handle:
        handle.write(commit.stdout + commit.stderr)
    with (external / f'section{n:03d}-commit-v1.exit-code').open('x') as handle:
        handle.write(str(commit.returncode) + '\n')
    commit.check_returncode()
    push = subprocess.run(['git', 'push', '-u', 'origin', 'HEAD:refs/heads/codex/p2-development'],
                          cwd=repo, capture_output=True, text=True)
    push_log = external / f'section{n:03d}-push-v1.log'
    with push_log.open('x') as handle:
        handle.write(push.stdout + push.stderr)
    with (external / f'section{n:03d}-push-v1.exit-code').open('x') as handle:
        handle.write(str(push.returncode) + '\n')
    push.check_returncode()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
    remote = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/codex/p2-development'],
                                     cwd=repo, text=True).strip().split()[0]
    clean = not subprocess.check_output(['git', 'status', '--porcelain'], cwd=repo, text=True).strip()
    assert head == remote and clean
    proof = {'section': n, 'kind': 'ACTUAL_COMMIT_PUSH_REMOTE_EQUAL_CLEAN',
             'verified_at_Beijing': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
             'local_HEAD': head, 'remote_HEAD': remote, 'commit_primary_exit': commit.returncode,
             'push_primary_exit': push.returncode, 'clean': clean,
             'archive_files_verified_before_commit': len(manifest['files']),
             'source_files': len(guard['source_sha256']),
             'full095_pass': False, 'next_section': n + 1,
             'native_windows_verified': False}
    with output.open('x') as handle:
        json.dump(proof, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(json.dumps(proof, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
