"""Prepare two external product source files; do not import or execute them."""
import difflib
import hashlib
import json
from pathlib import Path

SOURCE = Path('/workspace/.continuation/future-deepcolor-s1-regeneration-note-source')
OUT = Path(__file__).resolve().parent
EXPECTED_MANIFEST = '706ed3f8242bed04909778ed15dc582b486e7479b96ae2cbf6c9a4074c012389'
manifest_bytes = (SOURCE / 'public-artifacts-manifest.json').read_bytes()
if hashlib.sha256(manifest_bytes).hexdigest() != EXPECTED_MANIFEST:
    raise RuntimeError('Source lead manifest drift')
manifest = json.loads(manifest_bytes)
changes = {
    'rouge/operator_engine.py': (
        '            if not normal and self.n==1:\n'
        '                self.notes.append(f\'触手数量 {count:g}；技能生命回复 {bb["hp_recovery_per_sec"]*duration*count:g}，生命回复不计直接治疗。\')\n',
        '            if not normal and self.n==1:\n'
        "                scope=(f'名义技能持续参数 {duration:g} 秒' if window is None else\n"
        "                    f'观察窗口中 {duration:g} 秒的名义技能覆盖假设')\n"
        '                self.notes.append(f\'触手数量 {count:g}（局外假设）；{scope}下，按基础每只 {bb["hp_recovery_per_sec"]:g} 生命/秒连续覆盖的回复参考 {bb["hp_recovery_per_sec"]*duration*count:g}（未计生命回复效果倍率）；实际触手在场、技能回复覆盖及时钟未核验，实际回复总量未知，生命回复不计直接治疗。\')\n'
    ),
    'rouge/reporting.py': (
        "        blocks.append(section('regeneration','生命回复',rows,['生命回复独立于直接治疗 HPS，不扣当前生命已满导致的无效回复。']))\n",
        "        notes=['生命回复独立于直接治疗 HPS，不扣当前生命已满导致的无效回复。']\n"
        "        if op=='char_110_deepcl' and number==1:\n"
        "            notes.append('以上为所选触手持续在场且技能回复持续覆盖时的速度参考，包含本次采用的生命回复效果倍率；实际在场、回复首跳和结束尚未核验，实际回复总量未知。')\n"
        "        blocks.append(section('regeneration','生命回复',rows,notes))\n"
    ),
}
diffs = []
inverse_diffs = []
outputs = []
for rel, (before, after) in changes.items():
    input_rel = 'git-snapshots/' + rel
    entry = next(a for a in manifest['artifacts'] if a['path'] == input_rel)
    raw = (SOURCE / input_rel).read_bytes()
    if len(raw) != entry['bytes'] or hashlib.sha256(raw).hexdigest() != entry['sha256']:
        raise RuntimeError('Frozen source leaf drift: ' + rel)
    newline = '\r\n' if b'\r\n' in raw else '\n'
    text = raw.decode('utf-8').replace('\r\n', '\n')
    if text.count(before) != 1:
        raise RuntimeError('Edit anchor not unique: ' + rel)
    drafted = text.replace(before, after)
    if drafted.count(after) != 1 or drafted.replace(after, before) != text:
        raise RuntimeError('Edit is not exactly invertible: ' + rel)
    baseline = OUT / 'baseline' / rel
    product = OUT / 'draft' / rel
    for p in (baseline, product):
        if p.exists():
            raise RuntimeError('Existing external product file: ' + str(p))
        p.parent.mkdir(parents=True, exist_ok=True)
    baseline.write_bytes(raw)
    output_raw = drafted.replace('\n', newline).encode('utf-8')
    product.write_bytes(output_raw)
    diff = ''.join(difflib.unified_diff(text.splitlines(True), drafted.splitlines(True), 'a/' + rel, 'b/' + rel))
    inverse = ''.join(difflib.unified_diff(drafted.splitlines(True), text.splitlines(True), 'a/' + rel, 'b/' + rel))
    diffs.append(diff)
    inverse_diffs.append(inverse)
    outputs.append({'repository_path': rel, 'source_packet_archive_path': input_rel,
                    'baseline_sha256': hashlib.sha256(raw).hexdigest(), 'baseline_bytes': len(raw),
                    'draft_sha256': hashlib.sha256(output_raw).hexdigest(), 'draft_bytes': len(output_raw),
                    'original_newlines_preserved': True, 'exact_text_inverse_checked': True})
for name, value in [('product-draft.patch', ''.join(diffs)), ('product-draft.inverse.patch', ''.join(inverse_diffs))]:
    p = OUT / name
    if p.exists():
        raise RuntimeError('Existing patch: ' + name)
    p.write_text(value, encoding='utf-8')
receipt = {'status': 'UNEXECUTED_EXTERNAL_SOURCE_DRAFT', 'merged_section': 91,
           'root_integrates_tracked_files_only': True,
           'source_baseline_commit': manifest['source_baseline_commit'],
           'actual_author_baseline_binding': 'PENDING_ROOT_FULL90_ACTUAL_TAG',
           'source_manifest_sha256': EXPECTED_MANIFEST, 'source_files': outputs,
           'root_tracked_mutations': 0, 'new_tests_created': 0,
           'project_execution': {'application_API': 0, 'helper': 0, 'formatter': 0, 'tests': 0,
                                 'Qt': 0, 'Wine': 0, 'game_source_parse_or_network': 0},
           'changes': ['qualify existing Deepcolor S1 base arithmetic totals by nominal/window scope, no-relic basis, declared count and continuous-coverage assumption',
                       'qualify existing post-finish conditional fixed-rate report without changing numeric outputs'],
           'no_native_clock_or_total_created': True}
(OUT / 'draft-preparation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': receipt['status'], 'product_source_paths': list(changes),
                  'product_execution': 0, 'future_author_entries': 'pending root authorization'}))
