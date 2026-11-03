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
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(args.independent_final)==args.expected_independent_sha
independent=json.loads(args.independent_final.read_bytes())
assert independent.get('passed') is True or independent.get('status') in ('PASS_FINAL_FROZEN','FINAL_FROZEN_PASS')
ind_manifest=json.loads(args.independent_manifest.read_bytes())
readonly_path=Path('/workspace/.continuation/p2-after-082-readonly-consumer-boundaries/public-artifacts-manifest.json')
assert sha(readonly_path)=='fa83deaecd7c6ac3661a41e9e850ccc49609dc7e18a230ba6947935e89f68fac'
readonly=json.loads(readonly_path.read_bytes())
for manifest in (ind_manifest,readonly):
    assert manifest['format_version']==1
    for proof in manifest['files']:
        p=Path(proof['source_path'])
        assert sha(p)==proof['sha256'] and p.stat().st_size==proof['bytes']
assert len(readonly['files'])==4
assert any(Path(p['source_path'])==args.independent_final for p in ind_manifest['files'])
frozen=json.loads((OUT/'review-freeze84.json').read_bytes())
assert sha(OUT/'draft/rouge/damage.py')==frozen['damage_after_sha256']
assert sha(OUT/'draft/tests/test_haruka_repeat_text_input.py')==frozen['test_sha256']
assert sha(OUT/'section84.patch')==frozen['patch_sha256']
assert sha(OUT/'source-receipt84.json')==frozen['source_receipt_sha256']
freeze=json.loads((OUT/'freeze-receipt.json').read_bytes())
for rel,proof in freeze['files'].items():
    assert sha(OUT/'frozen'/rel)==proof['sha256']
    expected=frozen['damage_after_sha256'] if rel=='rouge/damage.py' else proof['sha256']
    assert sha(OUT/'draft'/rel)==expected
for proof in json.loads((OUT/'compression-receipt84.json').read_bytes())['files']:
    p=Path(proof['source_gzip']);assert sha(p)==proof['gzip_sha256']
    raw=gzip.decompress(p.read_bytes())
    assert hashlib.sha256(raw).hexdigest()==proof['raw_sha256'] and len(raw)==proof['raw_bytes']
    assert len(json.loads(raw))==proof['parsed_rows']
note=(OUT/'NOTE.draft.md').read_text()
note=note[:note.index('当前断点：')]+args.independent_note+'\n\n'+(
 '当前断点：作者source、两行guard、216矩阵、47项最终检查与正式独审均完成并冻结，全部公开证据明确列入v1清单。'
 'root在已完成的83 approved当前damage SHA上运行make-root-transport84.py生成并检查精确插入补丁，集成/注册后运行root-current-source-084.py及fresh回归，去两行必须严格恢复所有83 bytes。'
 '作者未执行83后运输或root当前源验证，不能覆盖旧整份damage源；无tracked/GUI/Wine操作。随后继续85并按cadence做全量检查。\n')
(OUT/'NOTE.md').write_text(note)
handoff={'format_version':1,'section':84,'status':'FINAL_SEALED',
         'baseline_commit':frozen['baseline_commit'],'baseline_public_files':720,'unchanged_old_files':719,
         'reference_patch':str(OUT/'section84.patch'),'reference_patch_sha256':frozen['patch_sha256'],
         'reference_only_damage_after_sha256':frozen['damage_after_sha256'],'test_sha256':frozen['test_sha256'],
         'reference_patch_numstat':frozen['patch_numstat'],'reference_root82_readonly_applycheck_exit':0,
         'guard_sha256':hashlib.sha256(json.loads((OUT/'draft-freeze84.json').read_bytes())['guard'].encode()).hexdigest(),
         'transport_helper':'make-root-transport84.py','root_current_source_script':'root-current-source-084.py',
         'requires_root83_approved_current_damage_sha':True,'root83_transport_executed_by_author':False,
         'root_current_source_executed_by_author':False,'whole_production_source_not_transportable':True,
         'author_unique_matrix_pairs':216,'author_fresh_matrix_calls':432,
         'author_comparison_counts':frozen['public_comparison']['counts'],
         'author_final_new_checks_passed':8,'author_related_checks_passed':39,'final_author_skips':0,
         'initial_test_run':'8 methods =7pass+1 test-expectation failure; original artifacts retained, source guard unchanged.',
         'transport_preparation':'One unresolved relative output path failed readonly numstat; original helper/log/valid initial patch retained; resolving paths passed.',
         'independent_final_path':str(args.independent_final),'independent_final_sha256':args.expected_independent_sha,
         'independent_manifest_path':str(args.independent_manifest),'independent_manifest_sha256':sha(args.independent_manifest),
         'independent_saved_pairs_reviewed':independent['saved_unique_native_typed_pairs_reviewed'],
         'independent_fresh_unique_inputs':independent.get('fresh_unique_inputs'),
         'independent_fresh_calculate_calls':independent.get('fresh_calculate_calls'),
         'independent_fresh_counts':independent.get('fresh_counts'),
         'independent_new_tests_passed':independent['new_test_methods_passed'],
         'readonly_4_files_manifest_sha256':sha(readonly_path),
         'registration':'tests.test_haruka_repeat_text_input in scripts/verify_cloud.py',
         'only_supported_change':'Actual public HarukaS2 raw repeat str becomes precise ValueError after old validations/report; all old nontext/inactive/earlier errors retained.',
         'mechanism_changes':False,'tracked_edits':False,'gui_executed':False,'wine_executed':False,
         'resume':'Root generate exact insertion from approved83 bytes, integrate/validate/commit84 then continue85 without waiting; full cadence after85.'}
(OUT/'handoff84.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n')
excluded={'baseline-public84.json','draft-public84.json','archivable-public-manifest84.json'}
public=[]
for p in sorted(OUT.iterdir()):
    if not p.is_file() or p.name in excluded:continue
    if p.suffix not in ('.py','.json','.md','.patch','.log','.gz'):continue
    public.append({'source_path':str(p),'archive_path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)})
for prefix,manifest,path in (('independent',ind_manifest,args.independent_manifest),
                             ('readonly-boundary',readonly,readonly_path)):
    for proof in manifest['files']:public.append({**proof,'archive_path':prefix+'/'+proof['archive_path']})
    public.append({'source_path':str(path),'archive_path':prefix+'/'+path.name,'bytes':path.stat().st_size,'sha256':sha(path)})
assert len({p['archive_path'] for p in public})==len(public)
manifest={'format_version':1,'section':84,'status':'FINAL_SEALED','files':public,
          'exclusions':'No captured source trees, whole old production source, raw matrix duplicates or bytecode; Git object and all file hashes preserved in freeze receipt.',
          'compressed_evidence':'Lossless two complete public typed matrices with raw hash/bytes/JSON verification; no calls repeated for compression or sealing.',
          'root_checkpoint':'83 current-byte surgical transport/current-source verification still root work; author has no tracked/GUI/Wine modifications.'}
p=OUT/'archivable-public-manifest84.json';p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'public_files':len(public),'readonly_4_plus_manifest':5,
                  'independent_files_plus_manifest':len(ind_manifest['files'])+1,
                  'handoff_sha256':sha(OUT/'handoff84.json'),'manifest_sha256':sha(p)}))
