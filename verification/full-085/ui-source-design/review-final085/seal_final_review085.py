"""Copy retained diagnostics, prove release-only delta, seal files; zero product calls."""
import ast
import difflib
import gzip
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
AUTHOR=HERE.parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def json_raw(value):return (json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
def write(name,value):
    raw=json_raw(value)
    with (HERE/name).open('xb')as out:out.write(raw)
    return sha(raw)
def copy(source,relative):
    raw=source.read_bytes();target=HERE/relative;target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb')as out:out.write(raw)
    assert source.read_bytes()==target.read_bytes()==raw
    return {'source_path':str(source),'archive_path':relative,'bytes':len(raw),'sha256':sha(raw)}

review=json.loads((HERE/'final-static-and-saved1154-review085.json').read_bytes())
assert review['status']=='PASS_FINAL_STATIC_AND_ALL_SAVED1154_0_NEW_PRODUCT_CALLS'
preserved=[]
for directory in sorted(AUTHOR.iterdir()):
    if not directory.is_dir()or not (directory.name.startswith('preparation')or
        directory.name in ('review-prep','review-design','source-boundaries-083084')):continue
    for path in sorted(directory.rglob('*')):
        if path.is_file()and '__pycache__'not in path.parts:
            preserved.append(copy(path,'author-retained-history/'+path.relative_to(AUTHOR).as_posix()))
for name in ['preparation-diagnostics085.json','remaining-contract-field-audit085.json',
    'source85-module-candidate-schema.json','root-source-compatibility-085.json',
    'runner-static-review.json','runner-085.patch','final-source-085-ready.json',
    'public-package-rebuild-proof085.json','artifact-mapping-and-old3063-proof085.json',
    'public-schema-final-085.log','public-schema-final-085-failure-summary.json',
    'public-schema-resume085.log','public-schema-remaining573085.log','CHECKPOINT.md']:
    preserved.append(copy(AUTHOR/name,'author-retained-history/'+name))
guard=HERE/'author-retained-history/preparation085-final-guarded-source-and-api'
manifest=json.loads((guard/'manifest.json').read_bytes())
assert len(manifest['files'])==8
for row in manifest['files']:
    raw=(guard/row['archive_path']).read_bytes()
    assert len(raw)==row['bytes']and sha(raw)==row['sha256']
final=HERE/'final-source-and-result-snapshot'
guarded=(guard/'wine-ui-smoke-085.py').read_bytes()
runner=(final/'wine-ui-smoke-085.py').read_bytes()
assert sha(guarded)=='9551471ba5fbf27fd1c4171e8e01a679a3845d034535856a207c60a3c2cfa998'
assert sha(runner)==review['final_runner_sha256']
expected=guarded.replace(b"if __name__ == '__main__' and True:",b"if __name__ == '__main__' and False:",1)
expected=expected.replace(b"receipt['sections83_85_final_checks_pending']=True",b"receipt['sections83_85_final_checks_pending']=False",1)
assert runner==expected and len(runner)==len(guarded)+2
fragment=(guard/'supplemental-checks.py.fragment').read_bytes()
assert (final/'supplemental-checks.py.fragment').read_bytes()==fragment.replace(
    b"receipt['sections83_85_final_checks_pending']=True",b"receipt['sections83_85_final_checks_pending']=False",1)
for name in ['public_contracts.py','cases085.py']:
    assert (guard/name).read_bytes()==(final/name).read_bytes()
before=ast.parse((guard/'build_runner.py').read_bytes())
after=ast.parse((final/'build_runner.py').read_bytes())
assert isinstance(before.body[0],ast.Expr)and isinstance(after.body[0],ast.Expr)
before.body=before.body[1:];after.body=after.body[1:]
def scope_value(tree):
    receipt=next(n for n in tree.body if isinstance(n,ast.Assign)
        and any(isinstance(t,ast.Name)and t.id=='receipt'for t in n.targets))
    assert isinstance(receipt.value,ast.Dict)
    return receipt.value,next(i for i,k in enumerate(receipt.value.keys)if isinstance(k,ast.Constant)and k.value=='scope')
old_dict,index=scope_value(before);new_dict,new_index=scope_value(after)
assert ast.literal_eval(old_dict.values[index])=='Static-only pending085 design; no API/Qt/Wine proof'
assert isinstance(new_dict.values[new_index],ast.IfExp)
new_dict.values[new_index]=old_dict.values[index]
assert ast.dump(before,include_attributes=False)==ast.dump(after,include_attributes=False)
payload=json.loads(gzip.decompress((final/'public-schema-final-085.json.gz').read_bytes()))
assert payload['corrected_pending_runner_sha256']==sha(guarded)
static=json.loads((HERE/'author-retained-history/runner-static-review.json').read_bytes())
assert static['runner_sha256']==sha(runner)and static['ready_for_actual_execution']is True
assert static['sections83_85_pending']is False and static['total_case_design_count']==4217
ready=json.loads((HERE/'author-retained-history/final-source-085-ready.json').read_bytes())
assert ready['runner_sha256']=='e3242a4e255bdbc208a57759b444df346e36c771e168e6e4b1ffabb85124df41'
rebuild=json.loads((HERE/'author-retained-history/public-package-rebuild-proof085.json').read_bytes())
assert rebuild['root_source_commit']==review['root_commit']and rebuild['public_source_files']==125
assert rebuild['all_bytes_equal']is True and rebuild['source_drift']==[]
source_expected=json.loads((HERE/'initial-static-review085.json').read_bytes())['source723_hashes']
assert {r['path']:{'bytes':r['bytes'],'sha256':r['sha256']}for r in rebuild['files']}=={
    name:value for name,value in source_expected.items()if name.startswith('rouge/')}
mapping=json.loads((HERE/'author-retained-history/artifact-mapping-and-old3063-proof085.json').read_bytes())
assert mapping['runner_sha256']==sha(runner)and mapping['planned_total_actual_checks']==4217
assert len(mapping['output_mappings'])==7
runner_tree=ast.parse(runner);old=(HERE/'actual080-preserved.py').read_bytes()
for row in mapping['output_mappings']:
    old_name,new_name=row['original080_name'],row['final085_name']
    assert new_name==old_name.replace('-080','-085')
    assert runner.count(new_name.encode())==old.count(old_name.encode())==row['original_and_final_literal_occurrences_including_metadata']
    sinks=[n for n in ast.walk(runner_tree)if isinstance(n,ast.BinOp)and isinstance(n.op,ast.Div)
        and isinstance(n.left,ast.Name)and n.left.id=='OUT'and isinstance(n.right,ast.Constant)and n.right.value==new_name]
    assert len(sinks)==row['static_OUT_path_sink_occurrences']==1
    assert row['actual_linux_destination']=='/workspace/.compat/'+new_name
    assert row['runner_windows_OUT']=='Z:\\workspace\\.compat'
assert mapping['GUI_executed']is False and mapping['Wine_executed']is False
transport={'status':'PASS_GUARD_RELEASE_ONLY_AND_HISTORY_RETAINED',
    'guarded_after_API_runner_sha256':sha(guarded),'released_final_runner_sha256':sha(runner),
    'exact_runner_changes':['entry guard True to False','sections83_85_final_checks_pending True to False'],
    'runner_byte_delta':2,'cases_and_all_contract_helpers_byte_identical_to_API_candidate':True,
    'builder_changes_only_docstring_and_static_scope_description':True,
    'historical_first_API_ready_file_retained_unmodified':True,
    'historical_ready_file_is_original_e324_preflight_gate_not_current_runner_identity':True,
    'current_runner_identity_authority':'Final source-and-result snapshot plus runner-static-review/final handoff exact SHA',
    'guarded8_manifest_files_all_hash_verified':True,'author_preparation_files_retained':preserved,
    'independent_public125_rebuild_receipt_values_bound_to_723_source_proof':True,
    'all_seven_actual_OUT_sinks_unique_and_inherited_literal_counts_preserved':True,
    'application_API_calls':0,'formatter_calls':0,'production_helper_calls':0,'Qt_calls':0,'Wine_calls':0,
    'scope':'Release follows approved source plus successful saved1154 proof; root actual UI result remains pending.'}
transport_sha=write('final-release-and-diagnostics-review085.json',transport)
note='''# UI085 最终独立复核

固定root产品源码2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b。正式审查已PASS：最终runner b6976652eb50e06909cca68490b0b9d3e11ea81fbc9a73ca87efcbb10354e306，saved gzip 7334c691de4c918898898bb2d0d3480fdd50fa268410343f92cb83645fd6674a。全部723份命名gitblob、125公共源码、完整旧3063正文逐字节一致；旧源码tree可用命名commit和125哈希精确重建，未拷贝运行公共tree。

新增1154个不同界面状态设计对应1086组不同计算输入；81节68组technical False/True设计共享计算参数。作者实际1154次API为69+512+573，未重算旧3063或两段已完成结果。1130成功、24个精确既有ValueError；三文本3390个请求，instrumented公开格式化函数入口4520=1130estimate+2260default+1130technical，estimate内部delegate包含在default中。作者原请求source qualification helper480、saved581重断言216另列，共696；不混入API或formatter。

本独审0应用API、0格式化器、0生产selected_talents、0Qt/Wine、0tracked改动。先保存结果581审查采用216次本地JSON候选投影，最终1154审查采用480次本地JSON投影；它们不调用生产helper。所有None/False原义保留，无get默认值放宽未知。独立还核报告指标对应实际保存结果、8组固定BOSS身份覆写全JSON相等及68technical pairs的全JSON/三文本相等。

两项不同检查合同错误各一次：69条旧机械师S3零窗口缺顶层total_healing，只核确切estimate零治疗；581条processed enemy使用target.enemy_id/stage_id/level，目录record才有id。原反例gzip、初稿、trace、来源修正和全部准备诊断均原字节保留。全部剩余83/84/85 receiver在继续前已按实际producer及资格闭合。历史final-source-ready是初始e324预核门槛，仍按历史原件保存；当前最终runner身份以正式封包SHA为准。

最终guarded955→releasedb697只含两处True→False，helper/cases完全相同，builder只改文档和静态scope。完整旧正文逆向、all1154保存记录审查各一次成功后没有重跑。当前可供root一次实际Qt/Wine验证；本回执不是GUI通过，也不证明原生Windows、游戏状态、30秒能力附着、叠加规则或native时钟。

最终断点：独审已封存，交root实际4217计划窗口测试；任何新的任务须明确授权，取消的浮点历史审计不自动启动。旧83/85source sealed文件不改。
'''
with (HERE/'NOTE.md').open('x')as out:out.write(note)
handoff={'status':'FINAL_SEALED_PASS_UI085_STATIC_AND_SAVED_ONLY',
    'format_version':1,'directory':str(HERE),
    'root_commit':review['root_commit'],'final_runner_sha256':review['final_runner_sha256'],
    'saved_gzip_sha256':review['saved_result_gzip_sha256'],
    'final_review_receipt':{'path':'final-static-and-saved1154-review085.json','sha256':sha((HERE/'final-static-and-saved1154-review085.json').read_bytes())},
    'release_history_receipt':{'path':'final-release-and-diagnostics-review085.json','sha256':transport_sha},
    'saved581_source_receipt':{'path':'remaining-receiver-source-and-saved581-review085.json','sha256':sha((HERE/'remaining-receiver-source-and-saved581-review085.json').read_bytes())},
    'reviewer_calls':{'application_API':0,'formatter':0,'production_helper':0,'Qt':0,'Wine':0},
    'actual_UI_validation_passed_by_this_reviewer':False,
    'next_action':'root exact-byte preflight then single actual Qt/Wine suite; no API matrix repeat',
    'all_native_game_and_native_Windows_assertions_excluded':True,
    'manifest':'final-public-artifacts-manifest085.json'}
handoff_sha=write('final-handoff085.json',handoff)
rows=[]
for path in sorted(HERE.rglob('*')):
    if not path.is_file()or '__pycache__'in path.parts:continue
    relative=path.relative_to(HERE).as_posix()
    if relative in ('final-public-artifacts-manifest085.json','seal-final-review085.log'):continue
    raw=path.read_bytes()
    rows.append({'source_path':str(path),'archive_path':relative,'bytes':len(raw),'sha256':sha(raw)})
manifest_value={'format_version':1,'status':'FINAL_SEALED_PASS',
    'scope':'Complete independent UI085 static/saved review plus retained original preparation evidence; no executable public tree',
    'files':rows,'file_count':len(rows),'total_bytes':sum(r['bytes']for r in rows),
    'handoff_sha256':handoff_sha,'reviewer_product_calls':0,
    'exclusions':['seal-final-review085.log live during seal','__pycache__','author public-schema-085 executable tree']}
manifest_sha=write('final-public-artifacts-manifest085.json',manifest_value)
for row in rows:
    raw=(HERE/row['archive_path']).read_bytes();assert len(raw)==row['bytes']and sha(raw)==row['sha256']
assert sha((HERE/'final-handoff085.json').read_bytes())==handoff_sha
assert sha((HERE/'final-public-artifacts-manifest085.json').read_bytes())==manifest_sha
print(json.dumps({'status':handoff['status'],'manifest':'final-public-artifacts-manifest085.json',
    'manifest_sha256':manifest_sha,'handoff_sha256':handoff_sha,'files':len(rows),
    'bytes':manifest_value['total_bytes'],'release_receipt_sha256':transport_sha},ensure_ascii=False))
