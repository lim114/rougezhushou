"""Seal author085 after independent final receipt, without rerunning calculations."""
from pathlib import Path, PurePosixPath
import hashlib
import json

OUT=Path(__file__).parent
REVIEW=OUT.with_name('p2-orchid-near-text-085-independent')
def sha(data):
    return hashlib.sha256(data).hexdigest()
def read_checked(path, expected_sha, expected_size=None):
    data=path.read_bytes()
    assert sha(data)==expected_sha, str(path)
    if expected_size is not None:assert len(data)==expected_size, str(path)
    return data
def write_new(path, data):
    assert not path.exists(), str(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)
def dump_new(path, value):
    write_new(path,(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())
def relative(row):
    path=PurePosixPath(row['archive_path'])
    assert not path.is_absolute() and '..' not in path.parts
    return str(path)
def row_for(path, archive_path):
    data=path.read_bytes()
    return {'source_path':str(path),'archive_path':archive_path,
            'bytes':len(data),'sha256':sha(data)}

pending_path=OUT/'public-artifacts-manifest-author-pending.json'
pending_bytes=read_checked(pending_path,'bd86b9b3b5b0641c79e0be86990e4c93465875245a5eb1186a7a57c2ee8ace8b')
pending=json.loads(pending_bytes)
assert pending['format_version']==1 and len(pending['files'])==47
for row in pending['files']:
    assert Path(row['source_path'])==OUT/relative(row)
    read_checked(Path(row['source_path']),row['sha256'],row['bytes'])

review_path=REVIEW/'independent-review-final085.json'
review_bytes=read_checked(review_path,'0a41656fa7245ca3094efe0807053de8a093992e84b0457a99b3aa1fdc00b34c')
formal=json.loads(review_bytes)
assert formal['status']=='PASS_FINAL_FROZEN'
assert formal['saved_counts']=={'text_rejected':94,'same_success':79,'same_error':24}
assert formal['fresh_counts']=={'active_text_rejected':4,'whole_success_same':5,'old_errors_exact':3}
assert formal['new_tests_passed']==9 and formal['new_tests_skipped']==0
review_manifest_path=REVIEW/'independent-public-manifest085.json'
review_manifest_bytes=read_checked(review_manifest_path,'03405e18e29ee08a44319dfb550ca13cc71cec7083797b65f9dce0e7d8c1e727')
review_manifest=json.loads(review_manifest_bytes)
assert review_manifest['format_version']==1 and review_manifest['file_count']==44
assert len(review_manifest['files'])==44
review_data=[]
review_names=set()
for row in review_manifest['files']:
    name=relative(row)
    assert name not in review_names
    review_names.add(name)
    data=read_checked(Path(row['source_path']),row['sha256'],row['bytes'])
    review_data.append((name,data))
assert sum(len(data) for _,data in review_data)==743842
assert 'independent-review-final085.json' in review_names

# Recheck the frozen author source packages; no executable helper or API call.
baseline=json.loads((OUT/'baseline-freeze085.json').read_bytes())
assert len(baseline['public_source_files'])==720
unchanged=0
for name,row in baseline['public_source_files'].items():
    read_checked(OUT/'baseline'/name,row['sha256'],row['bytes'])
    if name!='rouge/damage.py':
        read_checked(OUT/'draft'/name,row['sha256'],row['bytes'])
        unchanged+=1
assert unchanged==719
read_checked(OUT/'draft/rouge/damage.py','29ecf0a145c620e1a96af76019288e7e24dbc02c1ca6695a475931a65a1e285e')
read_checked(OUT/'draft/tests/test_orchid_near_text_input.py','8fd8cdaf383ab54945404ad33c5f610c2fc2e4bb018800b1a8bed3193a0dce86')
read_checked(OUT/'EVIDENCE_BOUNDARY.md',formal['author_EVIDENCE_BOUNDARY_sha256'])
transport=json.loads(read_checked(OUT/'transport-root84-receipt085.json','bd5af68991fd52001ee53fce045c9231762fa5b8f8390d2ee09ad2cefd5a9b05'))
guard=read_checked(OUT/'guard085-crlf.txt',transport['guard_sha256'],transport['guard_bytes'])
assert len(guard.splitlines())==6 and all(line.endswith(b'\r\n') for line in guard.splitlines(keepends=True))
assert guard in (OUT/'draft/rouge/damage.py').read_bytes()
read_checked(OUT/'section85-root84-surgical.patch',transport['surgical_patch_sha256'])

# All source hashes must pass before any independent evidence is copied.
assert not (OUT/'independent').exists()
for name,data in review_data:write_new(OUT/'independent'/name,data)
write_new(OUT/'independent/independent-public-manifest085.json',review_manifest_bytes)

note='''# 085作者最终封存

正式独立审查为 PASS_FINAL_FROZEN。已选翔虫机动的梓兰 near_previous_deployment 文本条件在每次核心报告完成后明确报错；实际 selected_talents 决定资格。E0、其他干员、所有非文本别名及原 double_charge 行为保留。

作者197组保存记录只证明完整严格JSON值类型与三个报告文本：94文本拒绝、79完整相同、24原错误相同。它们没有编码前native类型树。正式审查未重算作者394次矩阵调用，另用12个不同输入执行24次 public calculate_damage，保存编码前native类型树并完整比较：4拒绝、5完整相同、3原错误相同。合法level43的E0S2与E1专精准确保留技能资格错误；第三例为late windup旧错误。原作者两个level90例仅证明等级错误优先，EVIDENCE_BOUNDARY.md解释这一边界。

作者9新增+40相关测试通过；独立审查9新增测试通过，未重复40旧测试或作者1328次旧测试API调用。新增测试内部API调用未计数，因此不宣称作者或正式审查的全部API总数。独审测试外纯helper调用34次（source9、saved资格cache11、fresh来源选择14），不算calculate_damage调用。

最终包逐件核验旧pending47与独立44件后原字节导入44件及其manifest。作者720baseline与719未改draft旧文件再次核hash；冻结源码、测试、矩阵和NOTE未改。纯执行副本仍按各自manifest明确排除，只存可审的原表选择、结果、脚本与回执。全部封存附件属于公开工程证据。

root84的实际7044518运输补丁仅插入原批准的6行CRLF，441字节，放在既有83/84 guards后、return前；不得用b5整文件覆盖root。根需新增并注册精确test，再独立做当前源、相关66实际测试、精选和第85节全量Linux/Wine/MainWindow检查。作者没有root-current-source-085脚本或执行结论，root负责当前8 source/4原件/30rank/实helper/registry/去6line等于批准d02b全字节检查。

guard位置证实既有每次核心准备、引擎、finisher、报告错误优先；不推断所有未知外层分支错误都有同样顺序。30秒原参数、位置覆盖、原生时钟、箭矢实际资源及叠加仍是已有范围与明确未知。作者与审查均未运行GUI、Wine、native Windows或真实游戏；本包不是第85节已集成或完整平台验证结论。
'''
write_new(OUT/'FINAL_REVIEW_NOTE.md',note.encode())
handoff={
    'status':'AUTHOR_FINAL_FROZEN_FORMAL_PASS_READY_FOR_ROOT_SURGICAL_INTEGRATION',
    'section':85,'fixed_author_baseline':'b5a40f30683bfc0945decaabbd4db5914c28427f',
    'fixed_root84_transport_commit':transport['fixed_root84_commit'],
    'independent_final_path':str(OUT/'independent/independent-review-final085.json'),
    'independent_final_sha256':sha(review_bytes),
    'independent_manifest_path':str(OUT/'independent/independent-public-manifest085.json'),
    'independent_manifest_sha256':sha(review_manifest_bytes),
    'independent_files_imported':44,'independent_manifest_also_imported':True,
    'source_subreview_final_handoff_sha256':formal['source_subreview_final_handoff_sha256'],
    'source_subreview_final_manifest_sha256':formal['source_subreview_final_manifest_sha256'],
    'pending47_preserved_verified':True,'pending_manifest_sha256':sha(pending_bytes),
    'baseline720_checked':True,'unchanged_old_draft719_checked':True,
    'author_freeze_sha256':'96fa448ec78f4021122520a96e6e580289a3e4f113ed3835af2f803204169026',
    'frozen_author_hashes':formal['frozen_author_hashes'],
    'root84_surgical_patch_path':str(OUT/'section85-root84-surgical.patch'),
    'root84_surgical_patch_sha256':transport['surgical_patch_sha256'],
    'guard_path':str(OUT/'guard085-crlf.txt'),'guard_bytes':len(guard),
    'guard_sha256':sha(guard),'guard_lines':6,
    'new_test_path':str(OUT/'draft/tests/test_orchid_near_text_input.py'),
    'new_test_sha256':formal['frozen_author_hashes']['new_test_sha256'],
    'new_test_registry_module':'tests.test_orchid_near_text_input',
    'old_author_related_modules':transport['original_author_related_modules'],
    'current_root_overlap_modules':transport['root_overlap_regression_modules'],
    'saved_pairs':197,'saved_counts':formal['saved_counts'],
    'saved_evidence_scope':'Whole strict JSON value types plus estimate/default/technical text; no pre-encoding native type tree.',
    'author_matrix_calculate_calls':394,'author_related_test_calculate_calls':1328,
    'author_new_test_methods':9,'author_old_test_methods':40,
    'author_new_test_internal_API_call_count':'Not instrumented; no grand total claimed.',
    'formal_fresh_inputs':12,'formal_fresh_calculate_calls':24,
    'formal_fresh_counts':formal['fresh_counts'],
    'formal_fresh_evidence_scope':'Different inputs; complete native types before encoding, public values/source selections and three texts.',
    'formal_new_tests':9,'formal_new_tests_skipped':0,
    'formal_new_test_internal_API_call_count':formal['new_test_internal_calculate_or_helper_calls'],
    'formal_pure_source_helper_calls_outside_tests':formal['pure_source_helper_calls_outside_tests'],
    'olderror_priority_scope':formal['scope_of_old_error_priority'],
    'no_accepted_nontext_double_charge_clock_or_numeric_formula_change':True,
    'root_current_source_check_script_provided':False,
    'root_current_checks_owner':'root independently verifies fixed source/raw30ranks/actualhelper/registry/remove6line==root84 approved complete damage bytes.',
    'root_current_tests_and_full_section85_verification_pending':True,
    'GUI_Wine_native_Windows_game_validation':False,'tracked_edits':False,
    'unknowns_retained':formal['unknowns_retained'],
    'restart_conditions':'Mechanic expansion needs matched-version native attachment, actual placementcoverage, clock and composition evidence. Continue existing input-type scope independently.',
    'manifest_is_external_and_excludes_itself':True,
}
dump_new(OUT/'handoff-author-final085.json',handoff)

rows=list(pending['files'])
names={relative(row) for row in rows}
extras=['public-artifacts-manifest-author-pending.json','EVIDENCE_BOUNDARY.md',
        'guard085-crlf.txt','section85-root84-surgical.patch','transport-root84-receipt085.json',
        'finalize_author085.py','FINAL_REVIEW_NOTE.md','handoff-author-final085.json']
extras+=['independent/'+name for name,_ in review_data]
extras+=['independent/independent-public-manifest085.json']
for name in extras:
    assert name not in names, name
    names.add(name);rows.append(row_for(OUT/name,name))
rows.sort(key=lambda row:row['archive_path'])
manifest={'format_version':1,'status':'FINAL_SEALED','section':85,
          'files':rows,'file_count':len(rows),'total_bytes':sum(row['bytes'] for row in rows),
          'manifest_self_excluded':True,'public_artifacts_only':True,
          'archival_scope':'Frozen pending47 plus immutable pendingmanifest, added evidence-boundary/transport/final metadata and independent44+manifest. Complete unchanged execution source copies remain excluded and reproducible from fixed git hashes.',
          'whole_source_execution_copies_excluded':['baseline/ except manifest-listed files','draft/ except manifest-listed files','independent/source-subreview/fixed-helper-package/','independent/source-subreview/readonly-apply-target/']}
dump_new(OUT/'public-artifacts-manifest-author-final085.json',manifest)
for row in rows:read_checked(Path(row['source_path']),row['sha256'],row['bytes'])
print(json.dumps({'status':handoff['status'],'handoff_path':str(OUT/'handoff-author-final085.json'),
      'handoff_sha256':sha((OUT/'handoff-author-final085.json').read_bytes()),
      'manifest_path':str(OUT/'public-artifacts-manifest-author-final085.json'),
      'manifest_sha256':sha((OUT/'public-artifacts-manifest-author-final085.json').read_bytes()),
      'file_count':len(rows),'total_bytes':manifest['total_bytes']},ensure_ascii=False))
