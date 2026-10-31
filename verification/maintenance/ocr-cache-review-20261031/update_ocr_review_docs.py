from pathlib import Path
import difflib
R=Path.cwd()
def save(name,s):
 p=R/name;a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=s.splitlines(keepends=True)
 for x,y,n in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in a],[v.rstrip('\r\n')for v in b],autojunk=False).get_matching_blocks():b[y:y+n]=a[x:x+n]
 p.write_bytes(''.join(b).encode('utf8'))
n='PROGRAM_REVIEW.md';s=(R/n).read_text('utf8');s=s.replace('本轮未优化识别。','已回顾页面OCR与图像精确缓存，移除双重摘要/像素核对并验证实际引擎结果保持；整页识别尚未提速。',1);s=s.replace('识别替换/优化仍最后，不因扫描完成而销项。','OCR覆盖、适配、准确率与耗时同步优化，不因局部缓存提速或扫描完成而销项。',1);save(n,s)
n='IMPLEMENTATION_STRATEGY.md';s=(R/n).read_text('utf8');s=s.replace('新页面识别准确率、分辨率及耗时优化仍统一放在最后','新页面识别准确率、分辨率及耗时优化同步推进',1);s=s.replace('保留“页面特征分流→专门读取”的已有两条路线，最后补新页面、跨分辨率、转场、滚动和短暂停留覆盖。','保留“页面特征分流→专门读取”的已有两条路线，同步补新页面、跨分辨率、转场、滚动和短暂停留覆盖。',1);save(n,s)
n='VIDEO_PARITY.md';s=(R/n).read_text('utf8');s=s.replace('识别优化按既定要求最后统一验收。','识别覆盖、适配、准确率与耗时按最新要求同步改进和验收。',1);s=s.replace('再补完整数据和覆盖层，最后统一识别验收。','同步补完整数据、覆盖层和识别覆盖/准确率/耗时验收。',1);save(n,s)
n='PROJECT_REQUIREMENTS.md';s=(R/n).read_text('utf8');marker='## 代码实现约束（新增与已有代码均适用）';s=s.replace(marker,'## OCR同步优化（2026-10-31最新更正）\n\nOCR及识别覆盖、适配、准确率与耗时不再置于最后，与功能和全程序回顾同步推进；新增与已有实现均适用。下文旧回执中的“识别最后”仅记录历史，不覆盖本要求。保留原输入与对照结果，分别报告局部缓存、完整页面、连续帧和真实游戏的范围，不能把单函数或缓存命中提速当作全流程提速。\n\n'+marker,1);save(n,s)
print('Updated active recognition direction; historical receipts remain original.')
