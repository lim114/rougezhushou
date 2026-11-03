"""Bind reused public evidence by exact SHA and stage mapping; no new native audit count."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
DATA = HERE / 'research/p2-skill-data-cost-consensus-281'
DATA.mkdir(parents=True, exist_ok=True)
sha = lambda raw: hashlib.sha256(raw).hexdigest()
legacy_dir = HERE / 'research/p2-skill-data-cost-278'
consensus_dir = HERE / 'research/p2-cost-rounding-consensus-280'
legacy = json.loads((legacy_dir / 'source-proof.json').read_bytes())
consensus = json.loads((consensus_dir / 'source-proof.json').read_bytes())
assert sha((legacy_dir / 'source-proof.json').read_bytes()) == '823f5e9fca98291bba30336b2836f9167bbc4242c774c1fb93695cd0d17c7f30'
assert sha((consensus_dir / 'source-proof.json').read_bytes()) == '67455e993a068f538bda96bb45d6c5e6b33fb1357894c873bc73c39d691a5bc6'
assert legacy['dll_sha256'] == consensus['dll_sha256'] and legacy['metadata_sha256'] == consensus['metadata_sha256']
methods = {(r['method']['Address'], r['method'].get('metadata_method_index')): r for r in legacy['methods']}
assert all(methods[(r['method']['Address'], r['method'].get('metadata_method_index'))]['reachable_bytes_sha256'] == r['reachable_bytes_sha256']
           for r in consensus['methods'])
by_index = {row['method'].get('metadata_method_index'): row for row in legacy['methods'] if row['method'].get('metadata_method_index') is not None}
stage_map = {
    'rune_mul': (85326, {'owner_read': '0x180cf701f', 'character_data_read': '0x180cf702d', 'skill_data_read': '0x180cf703b',
                         'blackboard_read': '0x180cf7050', 'modifier_read': '0x180cf7070', 'sp_data_read': '0x180cf707d',
                         'cost_copy': '0x180cf7091', 'cost_decode': '0x180cf70bb', 'single_conversion': '0x180cf70c6',
                         'single_arithmetic': '0x180cf70c9', 'round': '0x180cf70cf', 'encode': '0x180cf70de', 'store': '0x180cf70ee'}),
    'rune_add': (85329, {'owner_read': '0x180cf6dee', 'character_data_read': '0x180cf6dfc', 'skill_data_read': '0x180cf6e0a',
                         'blackboard_read': '0x180cf6e1f', 'modifier_read': '0x180cf6e3f', 'sp_data_read': '0x180cf6e4c',
                         'cost_copy': '0x180cf6e60', 'cost_decode': '0x180cf6e8a', 'single_conversion': '0x180cf6e95',
                         'single_arithmetic': '0x180cf6e98', 'round': '0x180cf6e9e', 'encode': '0x180cf6ead', 'store': '0x180cf6ebd'}),
    'relic_mul': (85835, {'owner_read': '0x180d0f203', 'character_data_read': '0x180d0f212', 'skill_data_read': '0x180d0f220',
                          'blackboard_read': '0x180d0f235', 'modifier_read': '0x180d0f250', 'sp_data_read': '0x180d0f255',
                          'cost_copy': '0x180d0f26c', 'cost_decode': '0x180d0f296', 'single_conversion': '0x180d0f2a6',
                          'single_arithmetic': '0x180d0f2a9', 'round': '0x180d0f2d7', 'encode': '0x180d0f376', 'store': '0x180d0f386'}),
}
mapping = {}
for kind, (index, stages) in stage_map.items():
    row = by_index[index]
    instructions = {i['address']: i for i in row['instructions']}
    assert all(address in instructions for address in stages.values())
    assert not any(i.get('target') == '0x18070b0b0' for i in row['instructions'])
    mapping[kind] = {'metadata_method_index': index, 'method_name': row['method']['Name'],
                     'reachable_bytes_sha256': row['reachable_bytes_sha256'],
                     'stage_instruction_addresses': stages,
                     'stage_instruction_bytes': {stage: instructions[address]['bytes'] for stage, address in stages.items()},
                     'normal_after_cost_store': 'return; no owner reread or UpdateSpData appended'}
for kind, index in (('scale_cost', 84998), ('replace_cost', 84880)):
    row = by_index[index]
    mapping[kind] = {'metadata_method_index': index, 'method_name': row['method']['Name'],
                     'reachable_bytes_sha256': row['reachable_bytes_sha256'],
                     'reuse': 'unchanged public278 complete result including deferred owner/data and UpdateSpData arguments',
                     'new_numeric_evaluator_used': False}
components = {}
for key, filename, directory in (('legacy', 'skill_data_cost_reference.py', legacy_dir),
                                  ('consensus', 'skill_cost_rounding_consensus.py', consensus_dir)):
    proof = legacy if key == 'legacy' else consensus
    components[key] = {'core_sha256': sha((HERE / 'rouge' / filename).read_bytes()), 'source_directory': directory.name,
                       'proof_sha256': sha((directory / 'source-proof.json').read_bytes()),
                       'source_files_sha256': {p.name: sha(p.read_bytes()) for p in directory.iterdir() if p.is_file()},
                       'existing_method_count': proof['method_count'], 'existing_byte_span_count': proof['byte_span_count']}
links = {'kind': 'SECTION281_REUSED_PUBLIC_SOURCE_BINDING_NOT_NEW_NATIVE_FRESH_AUDIT',
         'components': components, 'source_method_mapping': mapping,
         'unique_native_method_count': 32, 'original_byte_span_count': 4034,
         'consensus9_methods_are_subset_of_legacy32': True,
         'fresh_native_method_count_this_preparation': 0, 'fresh_native_span_count_this_preparation': 0,
         'original_file_hashes': {'dll_sha256': legacy['dll_sha256'], 'metadata_sha256': legacy['metadata_sha256']},
         'public_evaluator_or_source_injection': False, 'production_monkeypatch': False,
         'actual_cost_sp_complete_cycle_proven': False,
         'source_scope_correction': 'Single store-return is separate from scale/replace owner-Update workflow'}
links_raw = (json.dumps(links, ensure_ascii=False, indent=2) + '\n').encode('utf8')
assert not (DATA / 'source-links.json').exists(), 'preserve earlier packet'
(DATA / 'source-links.json').write_bytes(links_raw)
for name in ('DESIGN.md', 'SCHEMA.md'):
    shutil.copyfile(HERE / name, DATA / name)
readme = '''#281缓存准备：完整费用流程的舍入共识

新API独立组合278完整source-qualified前缀与280条件整数共识。三Single只写费用后return，不自行追加owner/Update；后两kind原样保留278已有update路径。旧两个模块/默认接口不改，没有公共source/evaluator参数或monkeypatch。

在pointer/BB/found/copy/decode前缀已资格后，Single完整转换/运算/round正常时才取得integer reference；候选分歧或输入/环境未知且后续round/encode/store正常事实独立明确时，可以保存opaque20byte写入前缀。正常调用不代表整数已证或protected roundtrip，actual费用/SP/完整周期仍unknown。

每行decoded cost独立；不合并百分比、不继承前行encoder参数。normal未知未来called=null，failed未来false；prelude失败/正常早return不越过。scale/replace的old fields与278公开返回逐项相同，包括owner-null后先data、独立身份及onlycost。

来源复用32方法/4034原跨度，280九方法已核是子集，不相加成41或宣称新增fresh源审。source-links记录精确stage地址/bytes、两core和来源包SHA。准备仅自有缓存；root正式集成/必要验收/推送后另记进度。
'''
(DATA / 'README.md').write_text(readme, encoding='utf8')
manifest = {'kind': 'skill-data-cost-consensus-source-manifest-281', 'source_links_sha256': sha(links_raw),
            'support_files_sha256': {name: sha((DATA / name).read_bytes()) for name in ('DESIGN.md', 'SCHEMA.md', 'README.md')},
            'unique_native_method_count': 32, 'original_byte_span_count': 4034,
            'prior_native_source_reused_without_new_fresh_count': True,
            'legacy_default_api_and_results_preserved': True, 'actual_cost_sp_cycle_proven': False}
manifest_raw = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf8')
(DATA / 'source_manifest.json').write_bytes(manifest_raw)
core = HERE / 'rouge/skill_data_cost_consensus_reference.py'
text = core.read_text(encoding='utf8').replace("LINKS_SHA256 = '__LINKS_SHA256__'", "LINKS_SHA256 = '" + sha(links_raw) + "'")
text = text.replace("MANIFEST_SHA256 = '__MANIFEST_SHA256__'", "MANIFEST_SHA256 = '" + sha(manifest_raw) + "'")
core.write_text(text, encoding='utf8')
spec = importlib.util.spec_from_file_location('costConsensusWorkflow281cache', core)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.source_data()['valid'], module.source_data()
payload = module.public_example()
result = module.skill_data_cost_consensus_reference(payload)
(DATA / 'public-example.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
(DATA / 'public-example-reference.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'core_sha256': sha(core.read_bytes()), 'links_sha256': sha(links_raw), 'manifest_sha256': sha(manifest_raw),
                  'source': module.source_data(), 'public_rows': [(r['id'], r['normal'], r['encoder_argument_reference'],
                                                                 len(r['stored_prefixes'])) for r in result['rows']]}, ensure_ascii=False))
