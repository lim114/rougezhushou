from pathlib import Path
from hashlib import sha256
import ast,importlib.util,json,runpy,sys,subprocess
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
name='scripts/verify_full_available.py';p=ROOT/name;broken=p.read_bytes()
original=subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)
line=b"ADDITIONAL_MODULES += ('tests.test_choice_annotations_307', 'tests.test_choice_annotation_view_307', 'tests.test_annotation_presentation_pairs_307')"
assert line not in original
where=original.index(b'\n',original.index(b'ADDITIONAL_MODULES = '))+1
fixed=original[:where]+line+b'\r\n'+original[where:]
assert ast.dump(ast.parse(broken.replace(b'\r\r\n',b'\r\n')))==ast.dump(ast.parse(fixed))
p.write_bytes(fixed)
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('verified_registry307',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
after=m.maintained_selectors();assert len(after)==474
registration_path='verification/sections/307-preparation/maintained-registration.json';r=read(registration_path)
r['initial_pre_format_fix_sha256']=r['source_sha256'];r['source_sha256']=sha(name)
r['format_repair']={'cause':'Raw CRLF decoded then written in text mode doubled CR characters in preparation helper','original_HEAD_line_endings_preserved':True,'AST_after_normalizing_accidentally_doubled_CR_equal':True,'initial_guard_failed_before_mutation':'AST docstring differs because doubled CR creates extra blank lines; explicit CR normalization verifies intended complete source','only_new_registry_statement_added_to_original_source':True,'new_registry_count':474}
(ROOT/registration_path).write_bytes(enc(r))
# Preserve original LF-only todo layout; there is still exactly one substantive deletion.
p=ROOT/'PROJECT_PROGRESS.md';raw=p.read_bytes();p.write_bytes(raw.replace(b'\r\n',b'\n'))
p=ROOT/'DEVELOPMENT_CHECKPOINT.json';cp=read(p.relative_to(ROOT));cp['historical_before307_latest_functional_section']=cp['latest_functional_section'];cp['latest_functional_section']=307;p.write_bytes(enc(cp))
p=ROOT/'verification/sections/307.json';r=read(p.relative_to(ROOT));r['maintained_registry']['sha256']=sha(registration_path);p.write_bytes(enc(r))
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(ROOT/'verification/sections/307-preparation/execution-current-record-repair.py').write_bytes(Path(__file__).read_bytes())
publish=(ROOT/'.cache/publish306.py').read_text('utf8').replace('306','307')
publish=publish.replace("cp['next_section']==307","cp['next_section']==308").replace("'next_section':307","'next_section':308")
publish=publish.replace('603e1700c3ae4523ac2ff3d5495f127dc30556df','c45ffb00f1932a27919885440b98a52094b087e0')
(ROOT/'.cache/publish307.py').write_text(publish,encoding='utf8')
metadata=(ROOT/'.cache/metadata306.py').read_text('utf8').replace('306','307')
metadata=metadata.replace("cp['next_section']==307","cp['next_section']==308").replace("next_section=307","next_section=308").replace("['section']==305","['section']==306")
metadata=metadata.replace('本性难移伪装与现身资料、进度标题显示实际改动','事件附注区分出现前条件与选择后结果').replace('307未启动','308未启动')
start=metadata.index("p=ROOT/'PROJECT_REQUIREMENTS.md';s=p.read_text('utf8');old_pause=")
end=metadata.index("runpy.run_path",start)
metadata=metadata[:start]+metadata[end:]
(ROOT/'.cache/metadata307.py').write_text(metadata,encoding='utf8')
print(json.dumps({'section':307,'latest_functional_section':cp['latest_functional_section'],'registry_single_new_statement':True,'pending_publisher_parent':'c45ffb00f1932a27919885440b98a52094b087e0'},ensure_ascii=False))
