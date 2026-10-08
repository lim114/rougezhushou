import argparse
import gzip
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).parent
parser=argparse.ArgumentParser()
parser.add_argument('--independent-manifest',type=Path,required=True)
parser.add_argument('--independent-final',type=Path,required=True)
parser.add_argument('--expected-independent-sha',required=True)
parser.add_argument('--independent-note',required=True)
args=parser.parse_args()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(args.independent_final)==args.expected_independent_sha
independent=json.loads(args.independent_final.read_bytes())
assert independent.get('passed') is True or independent.get('status') in ('FINAL_FROZEN_PASS','PASS_FINAL_FROZEN')
ind_manifest=json.loads(args.independent_manifest.read_bytes())
assert ind_manifest['format_version']==1
for row in ind_manifest['files']:
    path=Path(row['source_path'])
    assert sha(path)==row['sha256'] and path.stat().st_size==row['bytes']
assert any(Path(row['source_path'])==args.independent_final for row in ind_manifest['files'])
frozen=json.loads((OUT/'review-freeze82.json').read_bytes())
assert sha(OUT/'draft/rouge/operator_engine.py')==frozen['engine_after_sha256']
assert sha(OUT/'draft/tests/test_susuro_condition_text_input.py')==frozen['test_sha256']
assert sha(OUT/'section82.patch')==frozen['patch_sha256']
assert sha(OUT/'source-receipt82.json')==frozen['source_receipt_sha256']
freeze=json.loads((OUT/'freeze-receipt.json').read_bytes())
for rel,info in freeze['files'].items():
    assert sha(OUT/'frozen'/rel)==info['sha256']
    expected=frozen['engine_after_sha256'] if rel=='rouge/operator_engine.py' else info['sha256']
    assert sha(OUT/'draft'/rel)==expected
compression=json.loads((OUT/'compression-receipt82.json').read_bytes())
for proof in compression['files']:
    path=Path(proof['source_gzip'])
    assert sha(path)==proof['gzip_sha256']
    raw=gzip.decompress(path.read_bytes())
    assert hashlib.sha256(raw).hexdigest()==proof['raw_sha256'] and len(raw)==proof['raw_bytes']
    assert len(json.loads(raw))==proof['parsed_rows']
note=(OUT/'NOTE.draft.md').read_text()
note=note[:note.index('当前断点：')]+args.independent_note+'\n\n'+(
    '当前断点：外部来源、guard、426严格矩阵、54项作者检查与正式独立审查均已完成并冻结；公开证据全部由v1清单明确列出。'
    'root下一步应用两路径补丁并注册新测试，运行提供的 root-current-source-082.py 实际当前源复核及fresh回归。'
    '作者未执行root当前源检查，无tracked、GUI或Wine动作；Windows/Wine全量节奏由root统一执行。\n')
(OUT/'NOTE.md').write_text(note)
handoff={'format_version':1,'section':82,'status':'FINAL_SEALED',
         'baseline_commit':frozen['baseline_commit'],'baseline_public_files':718,'unchanged_old_files':717,
         'transport_patch':str(OUT/'section82.patch'),'patch_sha256':frozen['patch_sha256'],
         'engine_after_sha256':frozen['engine_after_sha256'],'test_sha256':frozen['test_sha256'],
         'patch_numstat':frozen['patch_numstat'],'root81_readonly_applycheck_exit':0,
         'root81_head_at_applycheck':frozen['root_head_at_applycheck'],'preserves_81_relic_warning_order':True,
         'author_discovery_calls':12,'author_fresh_matrix_calls':852,'author_unique_matrix_pairs':426,
         'author_comparison_counts':frozen['public_comparison']['counts'],
         'author_new_checks_passed':8,'author_related_checks_passed':46,'author_checks_skipped':0,
         'independent_final_path':str(args.independent_final),'independent_final_sha256':args.expected_independent_sha,
         'independent_manifest_path':str(args.independent_manifest),'independent_manifest_sha256':sha(args.independent_manifest),
         'independent_saved_pairs_reviewed':independent['native_typed_saved_pairs_reviewed'],
         'independent_fresh_unique_inputs':independent['fresh_unique_inputs'],
         'independent_fresh_calculate_calls':independent['fresh_calculate_calls'],
         'independent_fresh_counts':independent['fresh_counts'],
         'independent_new_tests_passed':independent['new_tests_passed'],
         'independent_new_tests_skipped':independent['new_tests_skipped'],
         'root_current_source_script':'root-current-source-082.py','root_current_source_executed_by_author':False,
         'registration':'tests.test_susuro_condition_text_input in scripts/verify_cloud.py',
         'only_behavior_change':'Actual selected 微创治疗 Susuro existing recipient consumer rejects raw str; every non-string, inactive source/owner and earlier old error preserved.',
         'mechanism_changes':False,'tracked_edits':False,'gui_executed':False,'wine_executed':False,
         'native_new_claims':False,'resume':'Root integrate on codex/p2-development, register, current source checks and fresh focused tests; checkpoint section82 then continue83 autonomously; next 5-section full cadence85.'}
(OUT/'handoff82.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n')
excluded={'baseline-public82.json','draft-public82.json','susuro-condition-public.json',
          'archivable-public-manifest82.json'}
public=[]
for path in sorted(OUT.iterdir()):
    if not path.is_file() or path.name in excluded:continue
    if path.suffix not in ('.py','.json','.log','.md','.patch','.gz'):continue
    public.append({'source_path':str(path),'archive_path':path.name,'bytes':path.stat().st_size,'sha256':sha(path)})
path=OUT/'draft/rouge/operator_engine.py'
public.append({'source_path':str(path),'archive_path':'draft-source/rouge/operator_engine.py',
               'bytes':path.stat().st_size,'sha256':sha(path)})
for row in ind_manifest['files']:
    public.append({**row,'archive_path':'independent/'+row['archive_path']})
public.append({'source_path':str(args.independent_manifest),'archive_path':'independent/'+args.independent_manifest.name,
               'bytes':args.independent_manifest.stat().st_size,'sha256':sha(args.independent_manifest)})
assert len({row['archive_path'] for row in public})==len(public)
manifest={'format_version':1,'section':82,'status':'FINAL_SEALED','files':public,
          'raw_public_outputs':'Lossless gzip with raw bytes/SHA and decode/JSON checks in compression-receipt82.json.',
          'exclusions':'Captured source trees, raw duplicate matrices and bytecode not transported; captured tracked Git object and every source hash in freeze receipt.',
          'checkpoint':'Root integration/current validation pending; no author tracked, GUI or Wine work.'}
path=OUT/'archivable-public-manifest82.json'
path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'public_files':len(public),'handoff_sha256':sha(OUT/'handoff82.json'),
                  'manifest_sha256':sha(path),'independent_final_sha256':args.expected_independent_sha}))
