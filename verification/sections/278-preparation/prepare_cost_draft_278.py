"""Package cost-only278 draft, preserving original preparation evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DRAFT = ROOT / '.cache/section278-draft'
DATA = DRAFT / 'research/p2-skill-data-cost-278'
DATA.mkdir(parents=True, exist_ok=True)
sha = lambda raw: hashlib.sha256(raw).hexdigest()
proof_raw = (HERE / 'source-proof-preparation-278.json').read_bytes()
assert sha(proof_raw) == '823f5e9fca98291bba30336b2836f9167bbc4242c774c1fb93695cd0d17c7f30'
proof = json.loads(proof_raw)
manifest = {
    'kind': 'skill-data-cost-source-manifest-278', 'proof_sha256': sha(proof_raw),
    'dll_sha256': proof['dll_sha256'], 'metadata_sha256': proof['metadata_sha256'],
    'method_count': 32, 'unique_instruction_count': 3145, 'byte_span_count': 4034,
    'implemented_scope': 'three Single cost changes, low32 signed scaling, replacement and independently qualified update call arguments',
    'deferred_scope': 'four-slot SpData/SkillData initialization remains future preparation; included original source records are not completion claims',
    'single_eligibility': 'exact Int32-to-Single and exact finite normal/zero operation, valid Int32 half-even range; no default MXCSR',
    'unmapped_round_helper_address': '0x18059e290', 'round_helper_metadata_identity_proven': False,
    'encoding_roundtrip_and_actual_cost_proven': False, 'actual_sp_or_clock_or_full_cycle_proven': False,
    'integer_scale_rule': 'signed reinterpretation of low32 imul; no clamp or Single percentage conversion',
    'scale_update_onlycost': True, 'replacement_update_onlycost': 'not independent modifySpType value',
    'official_cpu_source': json.loads((HERE / 'intel-arithmetic-source.json').read_bytes()),
    'independent_reviews': {
        'cost_review_sha256': sha((ROOT / '.cache/section278-independent-cost-source/cost-source-review.json').read_bytes()),
        'init_review_readback_sha256': sha((ROOT / '.cache/section278-independent-source/independent-init-source-readback.json').read_bytes()),
    },
}
raw = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf8')
(DATA / 'source_manifest.json').write_bytes(raw)
(DATA / 'source-proof.json').write_bytes(proof_raw)
for name in ('SOURCE_GATE.md', 'SCHEMA.md', 'preliminary-label-corrections.md', 'intel-arithmetic-source.json'):
    shutil.copyfile(HERE / name, DATA / name)
core = DRAFT / 'rouge/skill_data_cost_reference.py'
text = core.read_text(encoding='utf8').replace("MANIFEST_SHA256 = '__MANIFEST_SHA256__'", "MANIFEST_SHA256 = '" + sha(raw) + "'")
core.write_text(text, encoding='utf8')
spec = importlib.util.spec_from_file_location('skill_data_cost_reference278cache', core)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.source_data()['valid'], module.source_data()
example = module.public_example()
output = module.skill_data_cost_reference(example)
(DATA / 'public-example.json').write_text(json.dumps(example, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
(DATA / 'public-example-reference.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
readme = '''#278缓存准备：技能费用的逐次数据修饰与更新

主API skill_data_cost_reference(payload)严格绑定原32方法3145独立指令4034fresh byte spans及manifest。仅成本5kind进入此次草案；四槽初始化原件保留为后继，不冒称已实现。

CSkillCdMul/Add的名称不是实际回复率计算：源中改变的是spCost，按每个独立decoded读点先Int32转Single，再mul/add、half-even round、编码及20byte写。root当前游戏RC/FTZ/DAZ/exception masks未证，草案仅exact Single安全域给数字。10×0x3d4ccccd以及16777217转换例保留unknown。25×0.5→12、23×0.5→12、−23×0.5→−12；没有夹成零。

SpScale为独立Int32 m_scale的low32乘法，MIN32×−1仍MIN32，并在正常写之后独立owner/data2读取，再调用UpdateSpData(onlycost=true)。replacement先编码后firstSpData-null检查；modifySpType=true会写type并使onlycost=false；三个data、两个owner快照不能复用。

public.independent_next_decode声明101，该读点不会继承前一步编码入参12。所有写入只保留opaque20byte payload和编码入参，不输出修改后实际decoded费用。当前SP、真实完整技能周期和时钟一律unknown；void update没有虚构Boolean返回。

普通分支、对象存在、读点normal和值分别资格。unknown未来called=null，只有源支路证明不调用才false。null deferred owner仍先执行后续data getter，不提前漏掉前缀。原始准备错误标签与修证并存；原件、独立审计和当前草案不互相覆盖。

CPU Single/RC原证：[Intel SDM Volume1 December2024](https://cdrdv2-public.intel.com/843827/253665-sdm-vol-1-dec-24.pdf)。它证明指令资格，不证明游戏当前环境。raw round helper地址0x18059e290的metadata身份未闭合；不得称为另一码表地址上的Mathf.RoundToInt。
'''
(DATA / 'README.md').write_text(readme, encoding='utf8')
print(json.dumps({'core_sha256': sha(core.read_bytes()), 'manifest_sha256': sha(raw), 'source': module.source_data(),
                  'public_rows': [(row['id'], row['normal'], row['encoder_argument_reference'], row['status']) for row in output['rows']]}, ensure_ascii=False))
