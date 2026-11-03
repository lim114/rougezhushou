import hashlib, json, pathlib, subprocess

OUT = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path('/workspace/rougezhushou')
HEAD = 'a52a4bf9217aee3c11617135b7fc9cc6c38fd0f2'
paths = subprocess.check_output(['git', '-C', str(ROOT), 'ls-tree', '-r', '--name-only', HEAD], text=True).splitlines()
public = [p for p in paths if p.startswith('rouge/') and pathlib.PurePosixPath(p).suffix in ('.py', '.json')]
docs = ['PROJECT_PROGRESS.md', 'research/p2-mei-airborne-module-reference/prior-readonly-audit/NOTE.md', 'research/p2-mei-airborne-module-reference/prior-readonly-audit/common-skill-public-contract.json', 'research/p2-mei-airborne-module-reference/prior-readonly-audit/lead-audit-receipt.json', 'research/p2-training-input-types/rebuild-receipt.json']
hashes = {}
for rel in public + docs:
    blob = subprocess.check_output(['git', '-C', str(ROOT), 'show', HEAD + ':' + rel])
    destination = OUT / ('frozen75' if rel in public else 'prior-receipts') / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(blob)
    hashes[rel] = {'sha256': hashlib.sha256(blob).hexdigest(), 'bytes': len(blob)}
receipt = {'baseline_head': HEAD, 'source': 'immutable public git blobs only', 'public_package_files': len(public), 'files': hashes, 'root_working_tree_used': False, 'private_state_copied': False, 'source_only_readonly_audit': True}
(OUT / 'freeze75-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'baseline_head': HEAD, 'files': len(hashes), 'freeze_sha256': hashlib.sha256((OUT / 'freeze75-receipt.json').read_bytes()).hexdigest()}))
