"""Read-only bounded source inventory; no gameplay or calculation calls."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).parent
GAME = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
SOURCES = {
    'character_table': (ROOT / '.cache/p2-s1-binding/character_table.json', '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
    'char_patch_table': (Path('/workspace/.continuation/p2-after-076-condition-eligibility-audit/char_patch_table.json'), 'd1850d5aeec1a9246a0531e88c167e66745644957662c8272fc764f54904c57e'),
    'battle_equip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json'), '006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
    'uniequip_table': (Path('/workspace/.continuation/p2-after-070-source-audit/originals/uniequip_table.json'), 'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9'),
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

raw = {}
file_proofs = {}
for name, (path, expected) in SOURCES.items():
    data = path.read_bytes()
    assert sha(data) == expected, (name, sha(data))
    raw[name] = json.loads(data)
    file_proofs[name] = {'path': str(path), 'bytes': len(data), 'sha256': expected}

head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
assert branch == 'codex/p2-development'
public = {}
for name in ['rouge/data/catalog.json', 'rouge/operator_engine.py']:
    data = subprocess.check_output(['git', 'show', f'{head}:{name}'], cwd=ROOT)
    assert data == (ROOT / name).read_bytes(), name
    public[name] = {'bytes': len(data), 'sha256': sha(data)}
catalog = json.loads((ROOT / 'rouge/data/catalog.json').read_bytes())['operators']
assert len(catalog) == 32
all_chars = {**raw['character_table'], **raw['char_patch_table']['patchChars']}
incantation = {k: p for k, p in all_chars.items() if p.get('subProfessionId') == 'incantationmedic'}
implemented = sorted(set(incantation) & set(catalog))
assert implemented == ['char_1037_amiya3']
assert len(incantation) == 5
excluded = {}
for key in ['char_1046_sbell2', 'char_1041_angel2']:
    owner = all_chars[key]
    assert owner['subProfessionId'] != 'incantationmedic'
    excluded[key] = {'name': owner['name'], 'profession': owner['profession'],
                     'subProfessionId': owner['subProfessionId'],
                     'trait': owner['trait'],
                     'catalog_modules': [m['id'] for m in catalog[key]['modules']]}

records = []
for key, owner in sorted(incantation.items()):
    modules = []
    for module_id, module in raw['uniequip_table']['equipDict'].items():
        if module.get('tmplId') == key or (module.get('charId') == key and not module.get('tmplId')):
            if module.get('typeName1') == 'ORIGINAL':
                continue
            assert module_id in raw['battle_equip_table']
            modules.append({'id': module_id, 'uniequip_selector': module,
                            'battle_equip_source': raw['battle_equip_table'][module_id]})
    records.append({'id': key, 'name': owner['name'], 'profession': owner['profession'],
                    'subProfessionId': owner['subProfessionId'],
                    'source_table': 'char_patch_table.patchChars' if key in raw['char_patch_table']['patchChars'] else 'character_table',
                    'trait': owner['trait'], 'skill_selectors': owner['skills'],
                    'catalog_implemented': key in catalog, 'module_sources': modules})

receipt = {'status': 'bounded_negative_no_second_existing_incantation_consumer',
           'passed': True, 'source_commit': GAME, 'baseline_commit': head,
           'branch': branch, 'source_files': file_proofs, 'public_files': public,
           'catalog_owner_count': 32, 'raw_incantation_owner_count_including_patch': 5,
           'existing_incantation_catalog_owners': implemented,
           'incantation_sources': records, 'named_false_candidates': excluded,
           'prior_receipts_consulted': [
               '/workspace/.continuation/p2-ordinary-module-lead-after-075/bounded-module-lead-review.json',
               '/workspace/.continuation/p2-amiya-trait-scale-080/source-receipt80.json'],
           'new_public_api_calls': 0, 'gui_executed': False, 'wine_executed': False,
           'tracked_edits': False, 'section_number_assigned': False,
           'conclusion': 'Only medical Amiya is an existing incantationmedic model. Its scale consumer is already owned by section 80. The four other raw incantationmedic owners lack an explicit catalog skill model; no existing consumer fix can be copied to them. Holy Pramanix and Angel 2 are different original subprofessions and cannot inherit incantation healing.',
           'restart_conditions': [
               'A new supported incantationmedic catalog model is added with reviewed source and explicit skill behavior.',
               'An independently sourced defect is found in a different existing consumer without relying on a native script guess.'],
           'limits': ['Original data inventory proves class, form and selector identities only.',
                      'Module data does not prove hidden native attachment, tick clocks, layering or general stacking rules.',
                      'The previous 35-module static inventory is not repeated and is not counted as a new section.']}
destination = OUT / 'source-inventory-receipt.json'
with destination.open('x', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
manifest = {'format_version': 1, 'files': [
    {'source_path': str(path), 'archive_path': path.name, 'bytes': path.stat().st_size,
     'sha256': sha(path.read_bytes())}
    for path in [Path(__file__), destination]]}
with (OUT / 'archivable-public-manifest.json').open('x', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps({'passed': True, 'baseline_commit': head, 'catalog_incantation_owners': implemented,
                  'receipt_sha256': sha(destination.read_bytes()),
                  'manifest_sha256': sha((OUT / 'archivable-public-manifest.json').read_bytes())}))
