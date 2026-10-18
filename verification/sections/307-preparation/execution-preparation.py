from pathlib import Path
from hashlib import sha256
import importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
out=ROOT/'verification/sections/307-preparation'
def enc(v):return json.dumps(v,ensure_ascii=False,indent=2)+'\n'
def sha(p):return sha256(p.read_bytes()).hexdigest()
native=json.loads((ROOT/'verification/sections/307-window-attempt2/actual/window.json').read_bytes())
assert native['passed'] and len(native['screenshots'])==5
images=[]
for r in native['screenshots']:
 p=Path(r['path']);assert p.is_relative_to(ROOT) and sha(p)==r['sha256']
 images.append({'file':p.relative_to(ROOT).as_posix(),'sha256':r['sha256'],'root_viewed':True,'review':'Actual source-backed player labels, true prior conditions, result notes and failed-source neutral wording are legible; supplied original screenshots viewed at high detail.'})
(ROOT/'verification/sections/307-root-visual.json').write_text(enc({'section':307,'all_reviewed':True,'images':images,'native_receipt':'verification/sections/307-window-attempt2/actual/window.json','native_receipt_sha256':sha(ROOT/'verification/sections/307-window-attempt2/actual/window.json')}),encoding='utf8')
p=ROOT/'scripts/verify_full_available.py';raw=p.read_bytes()
spec=importlib.util.spec_from_file_location('registry_before307',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
before=module.maintained_selectors();assert len(before)==471
(out/'before/scripts').mkdir(parents=True,exist_ok=True);(out/'before/scripts/verify_full_available.py').write_bytes(raw)
s=raw.decode('utf8');end=s.index('\n',s.index('ADDITIONAL_MODULES = '));s=s[:end]+"\nADDITIONAL_MODULES += ('tests.test_choice_annotations_307', 'tests.test_choice_annotation_view_307', 'tests.test_annotation_presentation_pairs_307')"+s[end:];p.write_text(s,encoding='utf8')
spec=importlib.util.spec_from_file_location('registry_after307',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
after=module.maintained_selectors();assert len(after)==474 and after[:471]==before
(out/'maintained-registration.json').write_text(enc({'section':307,'before_count':471,'after_count':474,'original_ordered_prefix_unchanged':True,'appended':after[471:],'source_sha256':sha(p),'full_rerun':False,'next_full':320,'actual_exit':0}),encoding='utf8')
s=(ROOT/'.cache/open_test_window_306.py').read_text('utf8')
s=s.replace("old=load('verification/sections/305-main-window.json')","old=load('verification/sections/306-main-window.json')")
s=s.replace('306','307').replace("old=load('verification/sections/307-main-window.json')","old=load('verification/sections/306-main-window.json')")
s=s.replace('307-window-attempt1','307-window-attempt2').replace('307-necessary-attempt1','307-necessary-attempt2').replace("necessary['methods_ran']==75","necessary['methods_ran']==87")
(ROOT/'.cache/open_test_window_307.py').write_text(s,encoding='utf8')
(out/'failure-and-repair-history.json').write_text(enc({'section':307,'first_necessary_receipt':'verification/sections/307-necessary-attempt1/process.json','first_necessary_failure':'test03 tried to pop new annotation metadata from unrelated, correctly unchanged choices; original error KeyError annotation_reference; test fixture now asserts unrelated rows exact and only normalizes source-bound metadata','first_necessary_original_test':'verification/sections/307-preparation/before/tests/test_choice_annotations_307.py','production_changed_to_fix_assertion':False,'corrected_necessary_receipt':'verification/sections/307-necessary-attempt2/process.json','preliminary_ad_hoc_pair_check':{'observed_exit':1,'cause':'Test called keyword-only context argument positionally; fixed caller to context=context, production untouched','full_original_stdout_retained':False,'scope_limit':'No full-log evidence invented; final complete paired test is in actual necessary attempt2'},'native_failure_and_repair':'verification/sections/307-preparation/native-fixture-repair.json','all_original_retained_failure_directories_preserved':True}),encoding='utf8')
print(enc({'registration':len(after),'visuals_actually_reviewed':len(images),'main_helper_ready':True}))
