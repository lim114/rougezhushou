"""Bind only the root-authorized, first-complete303 reader original bytes."""
from hashlib import sha256
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CANDIDATE = HERE / 'candidate'
PACK = CANDIDATE / 'research/p3-map-direct-ground-303'


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8')


def pin(path):
    raw = path.read_bytes()
    return {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}


def copy_exact(source, target, expected=None):
    if expected is not None:
        assert pin(source)['sha256'] == expected
    target.parent.mkdir(parents=True, exist_ok=True)
    assert not target.exists()
    shutil.copyfile(source, target)
    assert pin(source) == pin(target)


readers = {
    'A': ('a', 'ccef7dd5a1cf227945a29143dfd41eadc4b39deb412b970850d53f3aab8083e2'),
    'B': ('b', '03179421fe88573290a2fa342bd856eca8b9ba95d443d8a753ebd216c6701994'),
}
links = {
    '.cache/p3-303-map-candidates/logical-reader-requests-all-lowland.json':
        'research/p3-map-direct-ground-303/REQUEST_MANIFEST.json',
    '.cache/p3-303-map-candidates/reader-grid-ro6_b_6.json':
        'research/p3-map-direct-ground-303/reader-grid-ro6_b_6.json',
    '.cache/p3-303-map-candidates/reader-grid-ro6_n_2_3.json':
        'research/p3-map-direct-ground-303/reader-grid-ro6_n_2_3.json',
    'rouge/data/battle-maps/ro6_b_6.png': 'rouge/data/battle-maps/ro6_b_6.png',
    'rouge/data/battle-maps/ro6_n_2_3.png': 'rouge/data/battle-maps/ro6_n_2_3.png',
}
records = json.loads((PACK / 'source-records.template.json').read_bytes())
records['status'] = 'FIRST_COMPLETE_READINGS_FROZEN_ROOT_AUTHORIZED_COMPARISON'
records['both_first_complete_readings_frozen_before_comparison'] = True
records['reader_source_pin_links'] = {'A': links, 'B': links}
records['reader_originals'] = {}
for label, (suffix, digest) in readers.items():
    folder = ROOT / ('.cache/p3-303-reader-' + suffix)
    for original, public in [('READINGS.json', 'READER_' + label + '_ORIGINAL.json'),
                             ('READY.json', 'READER_' + label + '_READY_ORIGINAL.json')]:
        copy_exact(folder / original, PACK / public, digest if original == 'READINGS.json' else None)
    records['reader_originals'][label] = {
        'original_path': '.cache/p3-303-reader-' + suffix + '/READINGS.json',
        'public_copy': 'READER_' + label + '_ORIGINAL.json',
        **pin(PACK / ('READER_' + label + '_ORIGINAL.json')),
        'kind': 'independent isolated-context agent, not a human or game measurement',
    }
(PACK / 'source-records.json').write_bytes(encoded(records))
(PACK / 'README.md').write_bytes('''# 固定原图直接地格参考 · 第303节

固定原图为512×286，JSON地图数组行号就是显示行号，不能套用敌人路线的源行反转。
完整原level与原PNG复用已公开固定提交来源，所有字节由source-manifest绑定。

两名隔离上下文代理分别查看同两张原图和逻辑网格，首次完整读数各覆盖89个低地地板/道路请求，
在双方结果冻结后才逐格比较。它们不是两名真人或游戏内采样，也不证明绝对位置精度。
原READINGS与READY逐字节保存，内部.cache路径仅是历史输入路径；重建只使用本仓库公开映射。

全部89格都保留在构建比较回执。任一null或原像素欧氏距离超过4就拒绝，不调整坐标，
不重新读点，不平均、不拟合、不插值；通过格只保留A的原始像素并同时保存B的原始读数。
拒绝和缺读不是可映射点，不能从邻格推算。只接受LOWLAND tile_floor或显式tile_road。

旧58直接点、旧12图24关的规则投影全字典保持不变。两新图及本性难移的普通/紧急别名
分别绑定原level、原图、完整语义网格。部分直接点不等于整图校准：81关59图的完整核验缺口不减，
也不证明立体高台、格边界、反向定位或路径连线。

重建：python scripts/extend_direct_landmark_303.py 默认只读；
--output-dir必须是尚不存在的独立候选目录，不能写入当前生产数据或本来源包。
输出build-receipt记录实际计数与全部89条；source-manifest逐次重新核对全部来源字节。
prior-direct-references.json是294历史重放使用的原58完整快照，不是当前生产总量。
'''.encode('utf8'))

# Reuse complete fixed public objects. Do not duplicate large originals in the
# new source pack; create copies only in this isolated cache candidate root.
dependencies = {
    'rouge/data/battle-previews.json',
    'rouge/data/battle-map-projections.json',
}
for identity, row in records['stages'].items():
    dependencies.add('rouge/data/' + row['image']['file'])
    dependencies.add(row['level_file'])
for relative in sorted(dependencies):
    copy_exact(ROOT / relative, CANDIDATE / relative)
copy_exact(PACK / 'prior-direct-references.json', CANDIDATE / 'rouge/data/fixed-landmark-references.json')

source_names = ['REQUEST_MANIFEST.json', 'reader-grid-ro6_b_6.json', 'reader-grid-ro6_n_2_3.json',
                'READER_A_ORIGINAL.json', 'READER_B_ORIGINAL.json',
                'READER_A_READY_ORIGINAL.json', 'READER_B_READY_ORIGINAL.json',
                'prior-direct-references.json', 'prior-regular-projections.json',
                'source-records.json', 'README.md']
files = {str((PACK / name).relative_to(CANDIDATE)).replace('\\', '/'): pin(PACK / name) for name in source_names}
files.update({relative: pin(CANDIDATE / relative) for relative in sorted(dependencies)})
manifest = {'section': 303, 'kind': 'FROZEN_ORIGINAL_DIRECT_GROUND_SOURCES_NOT_FULL_MAP_CALIBRATION',
            'all_source_eligible_requests': 89, 'agreement_tolerance_px': 4,
            'reader_original_bytes_unchanged': True, 'source_adjustments': 0,
            'large_public_originals_reused_without_duplicate': True,
            'whole_map_gaps_unchanged': [81, 59], 'files': files}
(PACK / 'source-manifest.json').write_bytes(encoded(manifest))
digest = pin(PACK / 'source-manifest.json')['sha256']
builder = CANDIDATE / 'scripts/extend_direct_landmark_303.py'
raw = builder.read_bytes()
marker = b'AWAITING_ROOT_FROZEN_READER_SOURCE_MANIFEST'
assert raw.count(marker) == 1
builder.write_bytes(raw.replace(marker, digest.encode()))
result = {'kind': 'FROZEN_SOURCE_PREPARATION_ONLY_NOT_BUILD_OR_PRODUCT_ACCEPTANCE',
          'source_manifest': pin(PACK / 'source-manifest.json'), 'builder': pin(builder),
          'authoritative_files': len(files), 'reader_original_bytes_copied': True,
          'all89_retained': True, 'production_changes': False, 'Qt_or_tests_run': False}
(HERE / 'final-source-preparation-receipt.json').write_bytes(encoded(result))
print(json.dumps(result, ensure_ascii=False))
