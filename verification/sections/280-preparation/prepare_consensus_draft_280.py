"""Package new consensus reference only in cache; leave278 exact-only untouched."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DRAFT = ROOT / '.cache/section280-draft'
DATA = DRAFT / 'research/p2-cost-rounding-consensus-280'
DATA.mkdir(parents=True, exist_ok=True)
sha = lambda raw: hashlib.sha256(raw).hexdigest()
legacy = ROOT / 'rouge/skill_data_cost_reference.py'
legacy_sha = sha(legacy.read_bytes())
assert legacy_sha == '7cd8eee14c217c46419b5ac70bbcfe14f63e67a5687b7974d8718ae60618077a'
proof_raw = (HERE / 'source-proof-preparation-280.json').read_bytes()
assert sha(proof_raw) == '67455e993a068f538bda96bb45d6c5e6b33fb1357894c873bc73c39d691a5bc6'
proof = json.loads(proof_raw)
assert proof['method_count'] == 9 and proof['unique_instruction_count'] == 546 and proof['byte_span_count'] == 759
assert not (DATA / 'source_manifest.json').exists(), 'preserve earlier actual package'
(DATA / 'source-proof.json').write_bytes(proof_raw)
for name in ('SOURCE_GATE.md', 'SCHEMA.md', 'SOURCE_INSPECTION_CORRECTION.md', 'intel-rounding-source-inspection-v2-280.json'):
    shutil.copyfile(HERE / name, DATA / name)
readme = '''#280缓存准备：费用舍入共识

新API不改变278 exact-only接口。对三种成本数字前缀的Int32→Single转换四RC，再对Single加/乘四RC，共16组合；只有全部正常有限/零结果经原half-even规则成为同一有效signed32整数时才给共识。未知游戏MXCSR不以CPU默认nearest替代，未证同/异RC耦合不缩成4个对角线。

10×Single bits3e4ccccd约0.2的中间结果不精确，但全部最终整数为2；10×bits3d4ccccd约0.05仍为0/1未知。Single约1.05(bits3f866666)在费用20闭合21，费用30仍31/32。16777217转Single有16777216/16777218两个候选，乘0最后共识0、乘1继续未知。负数不夹成零，zero结果不猜实际符号位。

两步必须逐次舍入，不能直接对无限精度cost×modifier取整。每行decoder与modifier独立，public.independent_next_decode实际声明101，不继承前行整数。候选集只是源支持的条件正常结果，不是游戏取样或RC选择；normal指令/round资格未知时不把未来调用写成false。

nonfinite/subnormal/underflow/overflow或任何Int32域外候选使完整共识unknown。precision异常handler重写输入/结果不在引用域，不默认mask已开启。这里只给条件数字与可能下一encoder入参，没有encoder/store/update操作；actual cost、SP和完整周期始终unknown。

9源方法、546独立指令、759 fresh原文件跨度；Intel Volume1及Volume2abcd权威文档支持4RC和明确round控制。source SHA/support文件失效使全部引用失效。PDF下载失败及初次多匹配fused标题的更正完整保留，未采用错误标签。

准备不计280完成，不修改生产/tests/私人状态，不执行DLL/读取内存/操作游戏或聊天。root正式集成、必要验收与普通push后另记完成状态。
'''
(DATA / 'README.md').write_text(readme, encoding='utf8')
support = {name: sha((DATA / name).read_bytes()) for name in ('SOURCE_GATE.md', 'SCHEMA.md', 'README.md',
                                                            'SOURCE_INSPECTION_CORRECTION.md', 'intel-rounding-source-inspection-v2-280.json')}
manifest = {'kind': 'cost-rounding-consensus-source-manifest-280', 'proof_sha256': sha(proof_raw),
            'dll_sha256': proof['dll_sha256'], 'metadata_sha256': proof['metadata_sha256'],
            'method_count': 9, 'unique_instruction_count': 546, 'byte_span_count': 759,
            'support_files_sha256': support, 'rc_pair_scope': proof['rc_pair_scope'],
            'scalar_normal_qualifier': 'conditional ordinary hardware normal results without handler operand/result override',
            'game_rc_or_exception_masks_known': False, 'actual_cost_sp_cycle_known': False,
            'legacy_exact_api_modified': False, 'legacy_exact_core_sha256': legacy_sha,
            'public_kind_scope': ['rune_add', 'rune_mul', 'relic_mul'],
            'unmapped_round_helper_metadata_identity_known': False,
            'official_cpu_sources': proof['official_cpu_sources']}
manifest_raw = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf8')
(DATA / 'source_manifest.json').write_bytes(manifest_raw)
core = DRAFT / 'rouge/skill_cost_rounding_consensus.py'
text = core.read_text(encoding='utf8').replace("MANIFEST_SHA256 = '__MANIFEST_SHA256__'",
                                            "MANIFEST_SHA256 = '" + sha(manifest_raw) + "'")
core.write_text(text, encoding='utf8')
spec = importlib.util.spec_from_file_location('costConsensus280cache', core)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.source_data()['valid'], module.source_data()
payload = module.public_example()
result = module.skill_cost_rounding_consensus(payload)
(DATA / 'public-example.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
(DATA / 'public-example-reference.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
assert sha(legacy.read_bytes()) == legacy_sha
print(json.dumps({'core_sha256': sha(core.read_bytes()), 'manifest_sha256': sha(manifest_raw),
                  'source': module.source_data(), 'legacy_unchanged': True,
                  'public_rows': [(r['id'], r['encoder_argument_reference'], r['consensus_reference']['integer_candidates'],
                                   r['consensus_reference']['status']) for r in result['rows']]}, ensure_ascii=False))
