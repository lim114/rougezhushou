"""Build only this independent cache package; production remains root-owned."""
from pathlib import Path
import hashlib
import json
import shutil

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
PACKET = BASE / 'research/p2-panel-native-finalization-283'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
files = {}


def copy(src, relative):
    target = BASE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != target.resolve():
        shutil.copyfile(src, target)
    files[relative] = sha(target.read_bytes())


for name in ('mechanist_explosion_math.py', 'catalog.py', 'shield_source_inventory.py'):
    copy(ROOT / 'rouge' / name, 'rouge/' + name)
copy(ROOT / '.cache/section283-numeric/rouge/panel_native_precision.py', 'rouge/panel_native_precision.py')
assert files['rouge/panel_native_precision.py'] == '878347f7f5d69d09535f1bf0aec409068c68a3cdcf54812091c7deb96be838fc'
for relative in ('research/p2-recovery-attributes-273/source-proof.json',
                 'research/p2-skill-sp-increments-279/source-proof.json',
                 'research/p2-cost-rounding-consensus-280/source-proof.json'):
    copy(ROOT / relative, relative)
for name in ('source-proof.json', 'field-custom-attributes.json', 'routing-metadata.json', 'preparation-correction.md', 'SCHEMA.md'):
    copy(PACKET / name, 'research/p2-panel-native-finalization-283/' + name)
for source, name in (
    ('section283-numeric/intel-primary-inspection-283.json', 'intel-primary-inspection.json'),
    ('section283-numeric/fp-asfloat-primary-readback-283.json', 'fp-asfloat-primary-readback.json'),
    ('section283-numeric/NUMERIC_SCHEMA.md', 'NUMERIC_SCHEMA.md'),
    ('section283-source-review/source-gates-283.json', 'manager-range-round-source-gates.json'),
):
    copy(ROOT / '.cache' / source, 'research/p2-panel-native-finalization-283/' + name)

manifest = {
    'schema_version': 1, 'kind': 'conditional native panel finalization integrated with nominal model snapshots',
    'dll_sha256': '583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5',
    'metadata_sha256': 'd3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f',
    'files': files,
    'scope': ['five fixed field/type/range identities', 'distinct cultivation/rune/ordinary/skill numeric pipelines',
              'conditional all-RC typed writer parameters', 'independent read/write/manager flow normality'],
    'actual_runtime_inventory_hotfix_or_rc_proven': False,
    'protected_encode_decode_roundtrip_proven': False,
    'whole_dynamic_callgraph_closed': False,
    'source_guard_is_fresh_each_invocation': True,
    'reused_proofs_are_not_new_fresh_native_mechanism_credit': True,
    'main_model_qualification': 'nominal_model_snapshot; no execution facts supplied by model',
}
manifest_path = PACKET / 'source-manifest.json'
manifest_path.write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
core = (BASE / 'core_template.py').read_bytes().replace(b'@@SOURCE_SHA256@@', sha(manifest_path.read_bytes()).encode('ascii'))
target = BASE / 'rouge/panel_native_finalization.py'
target.write_bytes(core)
(BASE / 'rouge/__init__.py').write_bytes(b'')
compile(core, str(target), 'exec')
report = {'status': 'cache_candidate_only', 'core_sha256': sha(core),
          'source_manifest_sha256': sha(manifest_path.read_bytes()),
          'source_proof_sha256': sha((PACKET / 'source-proof.json').read_bytes()),
          'fresh_guard_file_count': len(files), 'production_modified': False,
          'actual_native_value_or_complete_section_claimed': False}
(BASE / 'draft-build-283.json').write_bytes((json.dumps(report, indent=2) + '\n').encode('utf8'))
print(json.dumps(report))
