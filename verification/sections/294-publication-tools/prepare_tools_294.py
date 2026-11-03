"""Cache-only adaptation producer. Does not import or execute its output tools."""
from pathlib import Path
from hashlib import sha256
import ast
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT='48eeb454e23fffee084fe7b6c7f9667b9216131d'
sources={}
def original(name):
    raw=(ROOT/'.cache'/name).read_bytes()
    sources[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    return raw.decode('utf8')
def save(name,text):
    ast.parse(text,filename=name)
    with(HERE/name).open('xb')as f:f.write(text.encode('utf8'))

text=original('stage_section_293.py')
a=text.index('original=(ROOT/')
b=text.index("tracked=['AGENTS.md'")
text=text[:a]+text[b:]
text=text.replace("parents[1]","parents[2]",1).replace('293','294')
text=text.replace('78b43ec3c4f69f410f7f290eb1048b755ad57b0e',PARENT)
text=text.replace("'rouge/node_catalog_view.py'","'rouge/data/fixed-landmark-references.json'")
text=text.replace("294-preparation/promotion/application.json","294-preparation/promotion.json")
text=text.replace("promotion['files_promoted']","promotion['promoted']")
text=text.replace("row={'section':294,","row={'section':294,'prior_commit':'"+PARENT+"',")
text=text.replace("section=json.loads((ROOT/'verification/sections/294.json').read_bytes())",
"""section=json.loads((ROOT/'verification/sections/294.json').read_bytes())
assert section['section']==294 and section['prior_commit']=='48eeb454e23fffee084fe7b6c7f9667b9216131d'
assert section['cloud_published'] is False and section['next_section']==295
assert section['partial_scope_after']==[10,18,58] and section['whole_map_stage_image_gaps_unchanged']==[81,59]
assert section['only_existing_production_file_changed']=='rouge/data/fixed-landmark-references.json'
assert section['full_validation']['after_section']==290 and section['full_validation']['full_suite_rerun'] is False
assert section['first_failed_native_validation']['not_counted_as_final_passed_checks'] is True
assert (ROOT/'verification/sections/294-preparation/root-execution-tools/archive-manifest.json').is_file()
for label in ('necessary_validation','native_windows_validation'):
    source=section[label]
    assert sha256((ROOT/source['receipt']).read_bytes()).hexdigest()==source['sha256']
    actual=json.loads((ROOT/source['receipt']).read_bytes())
    assert actual['source_sha256_before']==actual['source_sha256_after']
    for name,value in actual['source_sha256_after'].items():
        assert not name.startswith(('.cache/','.local/')) and name!='local-settings.json'
        assert sha256((ROOT/name).read_bytes()).hexdigest()==value,name
cp=json.loads((ROOT/'DEVELOPMENT_CHECKPOINT.json').read_bytes())
assert cp['completed_sections']==294 and cp['next_section']==295 and 'active_section'not in cp
assert cp['policy']['current_user_batch_target_section'] is None and cp['next_full_validation_after']==305
index=json.loads((ROOT/'CLOUD_INDEX.json').read_bytes())
assert index['completed_sections']==294 and index['next_section']==295
assert index['requirements']['sha256']==sha256((ROOT/'PROJECT_REQUIREMENTS.md').read_bytes()).hexdigest()
for name,value in index['public_pointers'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==value
assert not(ROOT/'.cache/section294-stage-readback.json').exists()
assert not(ROOT/'.cache/section294-stage-allowlist.txt').exists()""")
save('stage_section_294.py',text)

original('push_section_293.py')
save('push_section_294.py',"""from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def git(args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def load(name):return json.loads((ROOT/name).read_bytes())
kind=sys.argv[1];assert kind in ('functional','metadata')
assert git(['branch','--show-current'])=='codex/p2-development'
assert not git(['status','--porcelain'])
head=git(['rev-parse','HEAD']);parent=git(['rev-parse','HEAD^'])
if kind=='functional':
    stage=load('.cache/section294-stage-readback.json')
    assert parent==stage['prior_commit']=='48eeb454e23fffee084fe7b6c7f9667b9216131d'
    assert set(git(['diff-tree','--no-commit-id','--name-only','-r',head]).splitlines())==set(stage['staged_and_disk_sha256'])
    expected=stage['staged_and_disk_sha256']
else:
    proof=load('verification/sections/294-publication.json')
    assert proof['passed']is True and parent==proof['functional_commit']==proof['commit']
    assert set(git(['diff-tree','--no-commit-id','--name-only','-r',head]).splitlines())==set(load('.cache/section294-metadata-stage.json')['exact_staged_and_disk'])
    expected=load('.cache/section294-metadata-stage.json')['exact_staged_and_disk']
names=sorted(expected)
blobs=subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=(''.join(head+':'+p+'\\n'for p in names)).encode('utf8'))
offset=0
for name in names:
    end=blobs.index(b'\\n',offset);header=blobs[offset:end].split();assert header[1]==b'blob'
    size=int(header[2]);offset=end+1;raw=blobs[offset:offset+size];offset+=size
    assert blobs[offset:offset+1]==b'\\n';offset+=1
    assert sha256(raw).hexdigest()==expected[name] and raw==(ROOT/name).read_bytes(),name
assert offset==len(blobs)
dest=ROOT/f'.cache/section294-{kind}-push.json';assert not dest.exists()
argv=['git','push','origin','HEAD:refs/heads/codex/p2-development']
started=datetime.now(timezone.utc).isoformat()
try:
    actual=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
    code=actual.returncode;stdout=actual.stdout;stderr=actual.stderr;timed_out=False
except subprocess.TimeoutExpired as exc:
    code=124;stdout=exc.stdout or b'';stderr=exc.stderr or b'';timed_out=True
row={'section':294,'kind':kind,'commit':head,'prior_commit':parent,'argv':argv,'exit_code':code,
 'stdout':stdout.decode('utf8',errors='replace'),'stderr':stderr.decode('utf8',errors='replace'),
 'started_utc':started,'at_utc':datetime.now(timezone.utc).isoformat(),'ordinary_push':True,
 'timed_out':timed_out,'remote_ref_verified_by_this_push_only':False}
with dest.open('xb')as f:f.write((json.dumps(row,ensure_ascii=False,indent=2)+'\\n').encode('utf8'))
print(json.dumps({'section':294,'kind':kind,'commit':head,'actual_push_exit':code,'timed_out':timed_out}))
raise SystemExit(code)
""")

text=original('verify_publication_293.py').replace("parents[1]","parents[2]",1).replace('293','294')
text=text.replace("assert head=='6b59ad14e30226fab12d1f3447da96b80208ff63'",
"""stage=load('.cache/section294-stage-readback.json')
assert git(['rev-parse','HEAD^']).decode().strip()==stage['prior_commit']=='48eeb454e23fffee084fe7b6c7f9667b9216131d'""")
text=text.replace("assert push['exit_code']==0 and push['commit']==head and push['ordinary_push'] is True",
"assert push['section']==294 and push['kind']=='functional' and push['exit_code']==0 and push['commit']==head and push['ordinary_push'] is True and push['timed_out'] is False")
text=text.replace("'scope':'Functional294 one-hop future result and scene reader, actual80 necessary and54 unique native checks; both source-builder failures retained. Metadata adds no functional section.'",
"""'scope':('Functional294 adds18 directly compared points on2 original images/4 stage IDs, total10 images/18 IDs/58 points; actual'+str(section['necessary_validation']['methods_run'])+
 ' necessary and'+str(window['unique_checks'])+' unique native checks. First failed native attempt retained. Metadata adds no functional section.'),
 'necessary_methods_actual':section['necessary_validation']['methods_run'],
 'native_unique_checks_actual':window['unique_checks'],'native_assertion_count_actual':window['successful_assertion_executions_including_repeated_guards'],
 'current_source_full_validation_claimed':False,
 'first_failed_native_validation_retained':True""")
text=text.replace("idx=text.index('## 功能第292节')","idx=text.index('## 功能第293节')")
text=text.replace("'next_section':294","'next_section':295")
text=text.replace("cp=load('DEVELOPMENT_CHECKPOINT.json');cp['historical_before294_publication']=cp['last_verified_cloud_save']",
"""cp=load('DEVELOPMENT_CHECKPOINT.json')
assert cp['completed_sections']==294 and cp['next_section']==295 and 'historical_before294_publication'not in cp
cp['historical_before294_publication']=cp['last_verified_cloud_save']""")
save('verify_publication_294.py',text)

text=original('finish_publication_293.py').replace("parents[1]","parents[2]",1).replace('293','294')
text=text.replace("functional='6b59ad14e30226fab12d1f3447da96b80208ff63'",
"""functional=load('verification/sections/294-publication.json')['functional_commit']
assert git(['rev-parse',functional+'^']).decode().strip()=='48eeb454e23fffee084fe7b6c7f9667b9216131d'""")
text=text.replace("cp['next_section']==index['next_section']==294","cp['next_section']==index['next_section']==295")
text=text.replace("raw=(ROOT/'.cache'/name).read_bytes()","raw=(Path(__file__).resolve().parent/name).read_bytes()")
a=text.index("    correction=ROOT/")
b=text.index("    (archive/'archive-manifest.json')",a)
text=text[:a]+"""    for name in ('prepare_tools_294.py','prepare_ready_294.py','first-preparation-tool-error.json','READY.json','RUN_PLAN.md','BASELINE.json'):
        raw=(Path(__file__).resolve().parent/name).read_bytes()
        (archive/name).write_bytes(raw)
        manifest['files'][name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
"""+text[b:]
text=text.replace("'next_section':294","'next_section':295")
text=text.replace("draft only .cache/p3-next-map-research/NEXT_FUNCTION_PROPOSAL.md. Do not restart completed294 tests.",
"next295 only after explicit new functional scope. Do not restart completed294 tests.")
text=text.replace("pushed['commit']==head and pushed['exit_code']==0",
"pushed['section']==294 and pushed['kind']=='metadata' and pushed['ordinary_push']is True and pushed['timed_out']is False and pushed['commit']==head and pushed['exit_code']==0")
text=text.replace("write('.cache/section294-metadata-stage.json',",
"assert not(ROOT/'.cache/section294-metadata-stage.json').exists()\n    write('.cache/section294-metadata-stage.json',")
text=text.replace("write('.cache/current294-checkpoint.json',row)",
"assert not(ROOT/'.cache/current294-checkpoint.json').exists()\n    write('.cache/current294-checkpoint.json',row)")
save('finish_publication_294.py',text)
with(HERE/'BASELINE.json').open('xb')as f:
    f.write((json.dumps({'kind':'ADAPTED_FROM_ACTUAL_SECTION293_PUBLICATION_TOOLS','files':sources,
        'old_files_modified':False,'source_preparation_only':True},indent=2)+'\n').encode('utf8'))
print(json.dumps({'cache_scripts_prepared':4,'all_four_AST_parse':True,'publication_tools_executed':False,'Git_mutations':False}))
