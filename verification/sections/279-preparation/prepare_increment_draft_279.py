"""Create cache-only source-bound increment draft/public packet; no native execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DRAFT = ROOT / '.cache/section279-draft'
DATA = DRAFT / 'research/p2-skill-sp-increments-279'
DATA.mkdir(parents=True, exist_ok=True)
sha = lambda raw: hashlib.sha256(raw).hexdigest()
proof_raw = (HERE / 'source-proof-preparation-279.json').read_bytes()
assert sha(proof_raw) == '6d0fe625c510701db798a3552c61847bcd3a38c5bc75d507de840d064fac0504'
proof = json.loads(proof_raw)
assert proof['method_count'] == 17 and proof['unique_instruction_count'] == 938 and proof['byte_span_count'] == 1670
assert not (DATA / 'source_manifest.json').exists(), 'preserve actual draft manifest before a new attempt'
(DATA / 'source-proof.json').write_bytes(proof_raw)
for name in ('SOURCE_GATE.md', 'SCHEMA.md'):
    shutil.copyfile(HERE / name, DATA / name)
shutil.copyfile(HERE.parent / 'p2-skill-data-modifiers-278/intel-arithmetic-source.json', DATA / 'intel-arithmetic-source.json')
readme = '''#279缓存准备：按类型技力增量与初始化

这组纯文件参数参照支持SpData.Init四槽、SkillData.InitIfNot、攻击/受击的单次增量请求。没有执行游戏DLL、读取内存、操作游戏或使用私人截图。来源为17个原方法、938独立指令、1670个fresh原件字节跨度；源包SHA不符则所有数值参照失效。

Blackboard指针是一次捕获后四槽共用；各lookup、mask和array字段快照独立。缺mask bit的槽默认Single1.0，但不会启用spType，攻击/受击仍需各自bit。BB成功先BTS写mask、后数组null/长度检查，因此短数组失败也保留已写mask。未知Single原bits/未知完整mask的正常direct write只留未知值前缀，不补成0或1。get_inited只证数组指针非空，不证明长度和内容。

SkillData先读duration、写m_inited=true，再做Single GE；失败不撤销flag。GE是inclusive >= rhs−Single epsilon，rhs0的−epsilon位型b727c5ac本身命中true；它不是固定点strict GE/EPS。first/second duration、first/second Blackboard分别资格，second BB可null传给SpData.Init。

攻击索引1、受击索引2来自raw helper1844dc660的mov eax,ecx/ret，metadata名字未知。Single转FP是MULSS(Q=2^32)+CVTTSS2SI，安全finite normal/zero signed64域才给toward-zero请求量；例如−1→−Q，Single epsilon→42949，−2^31→MIN64。越界/非有限/环境不明仍unknown；独立声明正常的调用可传opaque参数，不制造数值。

OnTick普通指令没有直接slot0数组读取/乘法。完整数组归属、实际SP、事件数量、自然时钟和技能完整周期一律unknown。这里只分析局外单次参数与调用前缀；没有实战收益统计、战斗站位或自动操作。

public-example.json含全部4kind、无bit默认1、独立lookup/mask/array、mask写后数组越界、负Single epsilon inclusive、flag早写后GE未知、正负请求、cancelled早return和未知转换opaque请求。准备不计279完成；root提升生产/必要验收/普通push后另记真实状态。

CPU指令资格：[Intel SDM Volume1 December2024](https://cdrdv2-public.intel.com/843827/253665-sdm-vol-1-dec-24.pdf)。它不证明游戏当前MXCSR或当前hotfix。
'''
(DATA / 'README.md').write_text(readme, encoding='utf8')
support = {name: sha((DATA / name).read_bytes()) for name in ('SOURCE_GATE.md', 'SCHEMA.md', 'README.md', 'intel-arithmetic-source.json')}
manifest = {'kind': 'skill-sp-increments-source-manifest-279', 'proof_sha256': sha(proof_raw),
            'dll_sha256': proof['dll_sha256'], 'metadata_sha256': proof['metadata_sha256'],
            'method_count': 17, 'unique_instruction_count': 938, 'byte_span_count': 1670,
            'support_files_sha256': support,
            'implemented_reference_scope': ['sp_data_init', 'skill_data_init', 'attack_gain', 'damage_gain'],
            'native_index_helper_identity_known': False, 'native_index_helper_address': '0x1844dc660',
            'captured_blackboard_pointer_count': 1, 'dynamic_keys_known': False,
            'single_ge_rule': 'ordered inclusive lhs>=Single(rhs-epsilon), exact rhs0 domain',
            'single_gain_rule': 'exact normal/zero Single power2 scaling and signed64 toward-zero conversion',
            'unknown_direct_value_writes_retained': True,
            'spdata_controller_array_alias_known': False, 'actual_array_or_sp_or_complete_cycle_known': False,
            'current_hotfix_or_live_window_validated': False,
            'official_cpu_source': proof['official_cpu_source']}
manifest_raw = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf8')
(DATA / 'source_manifest.json').write_bytes(manifest_raw)
core = DRAFT / 'rouge/skill_sp_increment_reference.py'
text = core.read_text(encoding='utf8').replace("MANIFEST_SHA256 = '__MANIFEST_SHA256__'",
                                            "MANIFEST_SHA256 = '" + sha(manifest_raw) + "'")
core.write_text(text, encoding='utf8')
spec = importlib.util.spec_from_file_location('skill_sp_increment_reference279cache', core)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.source_data()['valid'], module.source_data()
example = module.public_example()
reference = module.skill_sp_increment_reference(example)
(DATA / 'public-example.json').write_text(json.dumps(example, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
(DATA / 'public-example-reference.json').write_text(json.dumps(reference, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
assert {row['kind'] for row in reference['rows']} == {'sp_data_init', 'skill_data_init', 'attack_gain', 'damage_gain'}
print(json.dumps({'core_sha256': sha(core.read_bytes()), 'manifest_sha256': sha(manifest_raw),
                  'source': module.source_data(), 'public_rows': [(r['id'], r['normal'], r['status']) for r in reference['rows']]}, ensure_ascii=False))
