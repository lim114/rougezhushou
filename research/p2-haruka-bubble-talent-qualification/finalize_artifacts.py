"""Copy sealed independent public proofs, update status once, then seal manifest."""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEPENDENT = ROOT.parent / 'p2-haruka-bubble-qualification-076-independent'
expected = {
    'final-review76-receipt.json': 'becb8b7f8520fac8b61e702872a81f0ca3d0e71655ed94abdef4f4f1385ff2b7',
    'FINAL76_REVIEW.md': 'd0c9e2703af08fee4daa4f051c4bcf4b3df10aa19a832ca852beab97c272ac64',
    'final-artifact-hashes76.json': 'a558136042b37bdd52dc3acc82981737ecb24fb4bbe8aa85228a06738b9ec167',
    'final-archive-list76.json': '9719ccd708ad7d6645d5666ee22286aea7f74275c819fbb73b23a7e3b5b4ccdb',
}
for name, sha in expected.items():
    assert hashlib.sha256((INDEPENDENT / name).read_bytes()).hexdigest() == sha
receipt = json.loads((INDEPENDENT / 'final-review76-receipt.json').read_text())
assert receipt['status'] == 'PASS_SEALED'
assert receipt['patch']['sha256'] == hashlib.sha256((ROOT / 'changes.patch').read_bytes()).hexdigest()
names = json.loads((INDEPENDENT / 'final-archive-list76.json').read_text())['relative_files']
names += ['final-archive-list76.json', 'final-artifact-hashes76.json']
assert len(names) == len(set(names))
hashes = json.loads((INDEPENDENT / 'final-artifact-hashes76.json').read_text())['files']
for name in names:
    source = (INDEPENDENT / name).resolve()
    source.relative_to(INDEPENDENT.resolve())
    assert '__pycache__' not in source.parts and source.suffix != '.pyc'
    raw = source.read_bytes()
    if name in hashes:
        assert len(raw) == hashes[name]['bytes']
        assert hashlib.sha256(raw).hexdigest() == hashes[name]['sha256']
    target = ROOT / 'independent' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    assert target.read_bytes() == raw

note = (ROOT / 'NOTE.md').read_text()
pending = '独立审阅：正在对最终冻结补丁做 source/code、窄 fresh 公共对照、新旧测试及已保存完整矩阵的独立严格复比；没有重复计算大矩阵。'
passed = ('独立审阅已封存 PASS：58 份 fresh 完整公共对照 / 148 次调用，16 份未解锁正声明与原零次数控制严格相同、34 份成功输出整份相同、8 个旧错误相同；补核 E2 S3 模块三级 × 两种模式的整份 typed JSON。'
          '独立选集 8 新 + 29 旧 = 37 个方法通过（与作者 39 个选集分开记），0 失败/错误/跳过。保存的 1788 份对照及 588 份双侧控制独立严格复比通过，没有重算大矩阵。'
          '独立再次核验 711 个基线 / 712 个草稿文件、4 份原表、710 个旧文件不变及 CRLF；只修改 engine 与新增测试。'
          '独立原件保持封存，可归档文件已逐字节复制到 `independent/`，见 `final-review76-receipt.json` 与 `FINAL76_REVIEW.md`。')
assert pending in note
(ROOT / 'NOTE.md').write_text(note.replace(pending, passed))
validation = json.loads((ROOT / 'validation.json').read_text())
validation['independent_review'] = 'PASS_SEALED'
validation['independent_fresh'] = receipt['fresh']
validation['independent_tests'] = receipt['tests']
validation['independent_saved_pairs'] = {
    'status': 'PASS', 'pairs': 1788, 'positive_countercontrols': 588,
    'new_calculate_calls': 0, 'counts': receipt['saved_author_evidence_independently_compared']['counts']}
(ROOT / 'validation.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n')
handoff = json.loads((ROOT / 'handoff.json').read_text())
handoff['status'] = 'READY_FINAL_SEALED_INDEPENDENT_PASS'
handoff['independent_review'] = {
    'status': 'PASS_SEALED', 'copied_public_files': len(names),
    'receipt': {'source_path': str(ROOT / 'independent' / 'final-review76-receipt.json'),
                'archive_path': 'independent/final-review76-receipt.json', 'sha256': expected['final-review76-receipt.json'],
                'bytes': (ROOT / 'independent' / 'final-review76-receipt.json').stat().st_size},
    'review': {'source_path': str(ROOT / 'independent' / 'FINAL76_REVIEW.md'),
               'archive_path': 'independent/FINAL76_REVIEW.md', 'sha256': expected['FINAL76_REVIEW.md'],
               'bytes': (ROOT / 'independent' / 'FINAL76_REVIEW.md').stat().st_size}}
handoff['author_evidence'] = {'public_pairs': 1788, 'fresh_public_calls': 4752,
    'locked_positive_corrected_matches_old_whole_zero_control': 588,
    'whole_accepted_unchanged': 1032, 'old_errors_unchanged': 168,
    'tests_new': 8, 'tests_related': 31, 'tests_total': 39}
handoff['source_and_patch_and_whole_public_evidence_frozen'] = True
(ROOT / 'handoff.json').write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n')
subprocess.run([sys.executable, str(ROOT / 'seal_public.py')], check=True)
manifest = json.loads((ROOT / 'public-artifacts-manifest.json').read_text())
for item in manifest['files']:
    raw = Path(item['source_path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item['sha256'] and len(raw) == item['bytes']
    assert not Path(item['archive_path']).is_absolute() and '..' not in Path(item['archive_path']).parts
print(json.dumps({'status': handoff['status'], 'public_payload_files': manifest['file_count'],
    'bytes': manifest['total_bytes'],
    'handoff_sha256': hashlib.sha256((ROOT / 'handoff.json').read_bytes()).hexdigest(),
    'manifest_sha256': hashlib.sha256((ROOT / 'public-artifacts-manifest.json').read_bytes()).hexdigest(),
    'all_listed_paths_hashes_bytes_verified': True}))
