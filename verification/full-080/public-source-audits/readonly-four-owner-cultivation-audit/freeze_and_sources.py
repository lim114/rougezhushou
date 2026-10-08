import hashlib, json, pathlib, subprocess

ROOT = pathlib.Path('/workspace/rougezhushou')
OUT = pathlib.Path(__file__).resolve().parent
HEAD = '225cb66'
owners = ['char_206_gnosis', 'char_437_mizuki', 'char_4087_ines', 'char_1035_wisdel']
head = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', HEAD], text=True).strip()
paths = subprocess.check_output(['git', '-C', str(ROOT), 'ls-tree', '-r', '--name-only', head], text=True).splitlines()
public = [p for p in paths if p.startswith('rouge/') and pathlib.PurePosixPath(p).suffix in ('.py', '.json')]
hashes = {}
for rel in public:
    data = subprocess.check_output(['git', '-C', str(ROOT), 'show', head + ':' + rel])
    dest = OUT / 'frozen75' / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    hashes[rel] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
notes = ['research/p2-gnosis-isw-a-reference/NOTE.md', 'research/p2-mizuki-amb-y/NOTE.md', 'research/p2-wisdel-secondary/RESEARCH.md', 'research/p2-wisdel-ghost-clock/RESEARCH.md']
for rel in notes:
    data = subprocess.check_output(['git', '-C', str(ROOT), 'show', head + ':' + rel])
    dest = OUT / 'baseline-notes' / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    hashes[rel] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
(OUT / 'freeze75-receipt.json').write_text(json.dumps({'baseline_head': head, 'source': 'immutable public git blobs only', 'files': hashes, 'working_tree_used': False, 'private_state_copied': False}, ensure_ascii=False, indent=2) + '\n')
originals = {
    'character_table': ('/workspace/rougezhushou/.cache/p2-s1-binding/character_table.json', '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
    'uniequip_table': ('/workspace/.continuation/p2-after-070-source-audit/originals/uniequip_table.json', 'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9'),
    'battle_equip_table': ('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json', '006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
}
tables, receipts = {}, {}
for kind, (name, expected) in originals.items():
    data = pathlib.Path(name).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == expected, (kind, digest)
    tables[kind] = json.loads(data)
    receipts[kind] = {'source_path': name, 'sha256': digest, 'bytes': len(data), 'game_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add', 'fresh_download': False, 'original_bytes_rehashed': True}
selectors = {}
for owner in owners:
    raw = tables['character_table'][owner]
    mods = {k: v for k, v in tables['uniequip_table']['equipDict'].items() if v['charId'] == owner}
    selectors[owner] = {'name': raw['name'], 'talents': raw['talents'], 'skills': raw['skills'], 'uniequip_originals': mods, 'battle_equip_originals': {k: tables['battle_equip_table'][k] for k in mods if k in tables['battle_equip_table']}}
(OUT / 'pinned-four-owner-selectors.json').write_text(json.dumps(selectors, ensure_ascii=False, indent=2) + '\n')
(OUT / 'source-reuse-receipt.json').write_text(json.dumps({'baseline_head': head, 'sources': receipts, 'selector_file': 'pinned-four-owner-selectors.json', 'not_native_binary_proof': True, 'source_only_readonly_audit': True}, ensure_ascii=False, indent=2) + '\n')
old = pathlib.Path('/workspace/.continuation/p2-summon-module-source-next-audit')
files = []
for name in ('source_inventory.py', 'source-inventory-receipt.json', 'pinned-owned-token-module-selectors.json'):
    data = (old / name).read_bytes()
    files.append({'source_path': str(old / name), 'archive_path': 'readonly-summon-module-audit/' + name, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
(old / 'public-artifacts-manifest-v1.json').write_text(json.dumps({'schema_version': 1, 'kind': 'readonly negative source audit; not a completed numbered section', 'files': files}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'baseline_head': head, 'frozen_public_package_files': len(public), 'originals_rehashed': list(receipts), 'selectors_bytes': (OUT / 'pinned-four-owner-selectors.json').stat().st_size, 'summon_audit_manifest_sha256': hashlib.sha256((old / 'public-artifacts-manifest-v1.json').read_bytes()).hexdigest()}))
