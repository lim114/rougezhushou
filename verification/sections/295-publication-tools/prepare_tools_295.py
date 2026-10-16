"""Cache-only adaptation. Never imports or executes output Git/publication tools."""
from pathlib import Path
from hashlib import sha256
import ast,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD=ROOT/'.cache/p3-294-publication-prep'
PARENT='e517095f388baad3aa7824dbd5b9dee6a68fb450'
OLD_PARENT='48eeb454e23fffee084fe7b6c7f9667b9216131d'
baseline={}
def read(name):
 p=OLD/name;raw=p.read_bytes();baseline[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
 return raw.decode('utf8').replace('294','295').replace(OLD_PARENT,PARENT)
def save(name,source):
 ast.parse(source,filename=name)
 with(HERE/name).open('xb')as f:f.write(source.encode('utf8'))
text=read('stage_section_294.py')
text=text.replace("'PROJECT_COMPLETED.md','PROJECT_PROGRESS.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/data/fixed-landmark-references.json'",
 "'PROJECT_COMPLETED.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/node_catalog_view.py','rouge/player_node_information.py'")
text=text.replace("'.stderr','.stdout'}","'.stderr','.stdout','.html'}")
text=text.replace("section['next_section']==295","section['next_section']==296")
text=text.replace("cp['next_section']==295","cp['next_section']==296")
text=text.replace("index['next_section']==295","index['next_section']==296")
text=text.replace("assert section['partial_scope_after']==[10,18,58] and section['whole_map_stage_image_gaps_unchanged']==[81,59]",
 "assert section['partial_direct_reference_scope_unchanged']==[10,18,58] and section['whole_map_gaps_unchanged']==[81,59]")
text=text.replace("assert section['only_existing_production_file_changed']=='rouge/data/fixed-landmark-references.json'",
"""assert section['only_existing_production_sources_changed']==['rouge/node_catalog_view.py','rouge/player_node_information.py']
assert section['typed_named_grant_count_unchanged']==17 and section['original_entry_gaps_unchanged']==[25,57]
progress=(ROOT/'PROJECT_PROGRESS.md').read_bytes()
assert sha256(progress).hexdigest()==section['PROJECT_PROGRESS_unchanged_sha256']
assert git(['show','HEAD:PROJECT_PROGRESS.md'])==progress""")
text=text.replace("assert section['first_failed_native_validation']['not_counted_as_final_passed_checks'] is True\n","")
text=text.replace("295-preparation/root-execution-tools/archive-manifest.json",
 "295-preparation/closeout-tools/archive-manifest.json")
save('stage_section_295.py',text)

text=read('push_section_294.py')
save('push_section_295.py',text)

text=read('verify_publication_294.py')
text=text.replace("'next_section':295","'next_section':296")
text=text.replace("cp['next_section']==295","cp['next_section']==296")
text=text.replace("idx=text.index('## 功能第293节')","idx=text.index('## 功能第294节')")
a=text.index(" 'scope':('Functional295 adds18")
b=text.index(" 'necessary_methods_actual':",a)
text=text[:a]+""" 'scope':('Functional295 adds one separate documented alpha-item reader through actual MainWindow entry; actual'+
 str(section['necessary_validation']['methods_run'])+' necessary and'+str(window['unique_checks'])+
 ' unique native checks, three PNGs. Old17 typed grants and38 full reward query outputs are unchanged. No quantity or original-entry gap is closed. Metadata adds no functional section.'),
"""+text[b:]
text=text.replace("'first_failed_native_validation_retained':True",
"""'old_typed_reward_contract_unchanged':True,'all38_old_reward_query_outputs_unchanged':True,
 'PROJECT_PROGRESS_unchanged':True,'original_entry_gaps_unchanged':[25,57]""")
save('verify_publication_295.py',text)

text=read('finish_publication_294.py')
text=text.replace("cp['next_section']==index['next_section']==295","cp['next_section']==index['next_section']==296")
text=text.replace("'next_section':295","'next_section':296")
text=text.replace('next295 only after','next296 only after')
text=text.replace("'prepare_tools_295.py','prepare_ready_295.py','first-preparation-tool-error.json','READY.json','RUN_PLAN.md','BASELINE.json'",
 "'prepare_tools_295.py','prepare_ready_295.py','READY.json','RUN_PLAN.md','BASELINE.json'")
save('finish_publication_295.py',text)
with(HERE/'BASELINE.json').open('xb')as f:
 f.write((json.dumps({'kind':'ADAPTED_FROM_ACTUAL294_STRICT_PUBLICATION_CHAIN','files':baseline,
 'old_tools_modified':False,'new_tools_executed':False},indent=2)+'\n').encode())
print(json.dumps({'cache_scripts_prepared':4,'AST_parse':True,'publication_or_Git_mutation_executed':False}))
