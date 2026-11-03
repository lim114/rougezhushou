import difflib
import hashlib
import json
import subprocess
from pathlib import Path

OUT=Path(__file__).parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
freeze=json.loads((OUT/'freeze-receipt.json').read_bytes())
draft=json.loads((OUT/'draft-freeze84.json').read_bytes())
for rel,info in freeze['files'].items():
    assert sha(OUT/'frozen'/rel)==info['sha256']
    expected=draft['damage_after_sha256'] if rel=='rouge/damage.py' else info['sha256']
    assert sha(OUT/'draft'/rel)==expected
test='tests/test_haruka_repeat_text_input.py'
assert sha(OUT/'draft'/test)==draft['test_sha256']
engine='rouge/damage.py'
before=(OUT/'frozen'/engine).read_bytes().decode()
after=(OUT/'draft'/engine).read_bytes().decode()
test_text=(OUT/'draft'/test).read_bytes().decode()
patch=('diff --git a/'+engine+' b/'+engine+'\n'+
       ''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),
                                  fromfile='a/'+engine,tofile='b/'+engine))+ 
       'diff --git a/'+test+' b/'+test+'\nnew file mode 100644\n'+
       ''.join(difflib.unified_diff([],test_text.splitlines(True),fromfile='/dev/null',tofile='b/'+test)))
p=OUT/'section84.patch'
with p.open('xb') as f:f.write(patch.encode())
repo=Path('/workspace/rougezhushou')
numstat=subprocess.run(['git','apply','--numstat',str(p)],cwd=repo,check=True,capture_output=True,text=True).stdout
assert numstat.splitlines()==['2\t0\t'+engine,str(len(test_text.splitlines()))+'\t0\t'+test],numstat
applied=subprocess.run(['git','apply','--check',str(p)],cwd=repo,capture_output=True,text=True)
assert applied.returncode==0,applied.stderr
head=subprocess.run(['git','rev-parse','HEAD'],cwd=repo,check=True,capture_output=True,text=True).stdout.strip()
current_relic=subprocess.run(['git','show','HEAD:rouge/relics.py'],cwd=repo,check=True,capture_output=True).stdout
baseline_relic=(OUT/'frozen/rouge/relics.py').read_bytes()
new_log=(OUT/'new-tests84.log').read_text()
assert 'Ran 8 tests' in new_log and new_log.endswith('OK\n')
(OUT/'new-tests84.json').write_text(json.dumps({'passed':True,'run':8,'passed_count':8,'failures':0,'errors':0,'skipped':0,
    'actual_command':'PYTHONHASHSEED=0 /workspace/rougezhushou/.venv/bin/python -m unittest discover -s tests -p test_haruka_repeat_text_input.py -v',
    'working_directory':str(OUT/'draft'),'log_sha256':sha(OUT/'new-tests84.log'),'test_sha256':draft['test_sha256']},ensure_ascii=False,indent=2)+'\n')
receipt={'passed':True,'status':'FINAL_AUTHOR_SOURCE_AND_MATRIX_FROZEN_FOR_REVIEW',
         'baseline_commit':freeze['baseline_commit'],'baseline_public_files':720,'unchanged_old_files':719,
         'added_new_test':test,'damage_before_sha256':draft['damage_before_sha256'],
         'damage_after_sha256':draft['damage_after_sha256'],'test_sha256':draft['test_sha256'],
         'patch_sha256':sha(p),'patch_numstat':numstat,'root_readonly_applycheck_exit':applied.returncode,
         'root_head_at_applycheck':head,'root_current_81_relics_sha256':hashlib.sha256(current_relic).hexdigest(),
         'author_baseline_relics_sha256':hashlib.sha256(baseline_relic).hexdigest(),
         'root81_preservation':'Reference patch only exact two-line insertion in damage and new test; no whole damage.py copy. Root adapts insertion after83 approved guards; no relics or engine transport.',
         'source_receipt_sha256':sha(OUT/'source-receipt84.json'),
         'public_comparison':json.loads((OUT/'public-comparison84.json').read_bytes()),
         'new_tests':8,'related_tests':json.loads((OUT/'related-tests84.json').read_bytes()),
         'new_calculate_calls_in_this_preparation':0,'tracked_edits':False,'gui_executed':False,'wine_executed':False}
(OUT/'review-freeze84.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'freeze_sha256':sha(OUT/'review-freeze84.json'),'patch_sha256':sha(p),'numstat':numstat,'root_head':head}))
