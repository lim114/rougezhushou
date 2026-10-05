"""Exact before/after replays and public semantics for immutable reference reuse."""
import copy,hashlib,importlib.util,json,statistics,sys,time,unittest
from pathlib import Path
from unittest.mock import patch
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from rouge import relic_recognition as current,run_recognition
from rouge.recognition import ScreenReader
from rouge.damage import calculate_damage
from verify_projection_recognition_029 import variants


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def baseline():
    path=ROOT/'.cache/batch-043-before/rouge/relic_recognition.py'
    spec=importlib.util.spec_from_file_location('rouge._icons_before_043',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.__file__=str(ROOT/'rouge/relic_recognition.py')
    return module


def clear(module,raw=True):
    for name in ('templates','prepared_templates','_reference_image','_refined_template','artwork_families'):
        getattr(module,name).cache_clear()
    if raw:
        for name in ('reference_entries','_artwork'):
            if hasattr(module,name):getattr(module,name).cache_clear()


def main():
    started=time.perf_counter();folder=ROOT/'.cache/recognition-043';old=baseline()
    prior=read('PREVIEW_0.42_VERIFICATION.json');names=prior['test_modules']
    with (folder/'tests.log').open('w',encoding='utf-8') as log:
        tests=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    assert tests.wasSuccessful() and tests.testsRun-len(tests.skipped)==403 and len(tests.skipped)==70
    for row in read('.cache/recognition-043/before-public-results.json'):
        assert calculate_damage(row['scenario'])==row['result'],row['scenario']
    fixtures=read('.cache/relic-recognition-fixtures-022.json');rows=[];benchmarks=[]
    for fixture in fixtures:
        path=ROOT/'samples/native-client'/fixture['file'];assert digest(str(path.relative_to(ROOT)))==fixture['sample_sha256']
        image=cv2.imdecode(np.fromfile(path,np.uint8),1)
        for case,im,anchor in variants(fixture,image):
            timings={};outputs={}
            for label,module in (('before',old),('after',current)):
                clear(module);start=time.perf_counter()
                outputs[label]=module.match_held_icons(im,anchor,fixture['count'])
                timings[label+'_cold_ms']=(time.perf_counter()-start)*1000
            assert outputs['before']==outputs['after'],case
            rows.append({'case':case,'sample_sha256':fixture['sample_sha256'],'size':list(im.shape[:2]),
                'exact_scores_candidates_centers':True,'records':outputs['after'],**timings})
            if case.endswith(':native') and fixture['file'] in ('run-relic-multicard-closed.png','run-relic-multicard.png'):
                times={'before':[],'after':[]}
                # Alternating order; templates warm, current image matching recomputed.
                for repeat in range(7):
                    order=(('before',old),('after',current)) if repeat%2==0 else (('after',current),('before',old))
                    for label,module in order:
                        start=time.perf_counter();found=module.match_held_icons(im,anchor,fixture['count'])
                        times[label].append((time.perf_counter()-start)*1000)
                        assert found==outputs['after'],case
                before=statistics.median(times['before']);after=statistics.median(times['after'])
                benchmarks.append({'case':case,'before_warm_ms':times['before'],'after_warm_ms':times['after'],
                    'before_median_ms':before,'after_median_ms':after,'speedup':before/after})
            print(json.dumps({'case':case,'exact':True,**timings}),flush=True)
    assert len(rows)==14
    # Four changing scales exceed the existing scaled-template cache. Raw art
    # still belongs to immutable reference files, not a previous observed frame.
    prep={}
    for label,module in (('before',old),('after',current)):
        clear(module);original=cv2.imdecode;calls=[0]
        def decoded(*args,**kwargs):
            calls[0]+=1
            return original(*args,**kwargs)
        start=time.perf_counter()
        with patch.object(cv2,'imdecode',decoded):
            for height in (900,777,649,810):module.prepared_templates(height)
        prep[label]={'png_decode_calls':calls[0],'four_scale_preparation_ms':(time.perf_counter()-start)*1000}
    entries=current.reference_entries();files={e['file'] for e in entries}
    assert len(files)<=256 and prep['after']['png_decode_calls']==len(files)
    assert prep['before']['png_decode_calls']==len(entries)*4
    raw_bytes=sum(current._artwork(f).nbytes for f in files)
    assert all(not current._artwork(f).flags.writeable for f in files)
    assert current._artwork.cache_info().currsize<=256 and current.prepared_templates.cache_info().currsize<=3
    projection_bytes=sum(row[-1][0].nbytes for row in current.prepared_templates(900))
    public=[];reader=ScreenReader(cache_enabled=False)
    for fixture in fixtures:
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client'/fixture['file'],np.uint8),1)
        with patch.object(run_recognition,'match_held_icons',old.match_held_icons):before=reader.read(image)
        after=reader.read(image)
        for field in ('page','run','operator','map','stage','nodes','node_content','texts','viewport','limitations'):
            assert before[field]==after[field],(fixture['file'],field)
        public.append({'sample':fixture['file'],'exact_public_observation_fields':True,'observation':after,
            'before_total_ms':before['performance']['total_ms'],'after_total_ms':after['performance']['total_ms']})
        print(json.dumps({'public_sample':fixture['file'],'exact':True}),flush=True)
    assert len(public)==5
    (folder/'paired-replay.json').write_text(json.dumps({'rows':rows,'public':public,'benchmarks':benchmarks,
        'scale_preparation':prep},ensure_ascii=False,indent=2),encoding='utf-8')
    previous=read('FINAL_0.42_VERIFICATION.json')
    changed={n for n,sha in previous['source_sha256'].items() if digest(n)!=sha}
    assert changed=={'rouge/app.py','rouge/relic_recognition.py','AGENTS.md','pyproject.toml'},changed
    manifest=read('.cache/batch-043-before/manifest.json')
    assert manifest==read('.cache/recognition-043/baseline.json')['source_hashes'] and len(manifest)==8
    for name,sha in manifest.items():assert digest('.cache/batch-043-before/'+name)==sha
    files=('rouge/relic_recognition.py','rouge/recognition.py','rouge/run_recognition.py',
        'rouge/visual_recognition.py','rouge/app.py','AGENTS.md','pyproject.toml',
        'scripts/verify_recognition_043.py','scripts/capture_recognition_baseline_043.py')
    receipt={'version':'0.43.0','passed':True,'verified_at':time.time(),'current_tests_passed':403,
        'new_unit_tests':0,'tests_run':tests.testsRun,'historical_combat_tests_skipped':len(tests.skipped),
        'test_modules':names,'failures':len(tests.failures),'errors':len(tests.errors),
        'exact_public_output_cases':732,'public_baseline_outputs_unchanged':True,
        'paired_visual_cases':14,'public_reader_cases':5,'exact_records_scores_centers_preserved':True,
        'exact_public_observation_fields_preserved':True,'benchmarks':benchmarks,'warm_repeats_per_version':7,
        'scale_preparation':prep,'immutable_raw_art_cache_bytes':raw_bytes,
        'projection_template_bytes_at_height_900':projection_bytes,'raw_art_cache_max_entries':256,
        'scaled_template_cache_max_entries':3,'recognition_identity_thresholds_unchanged':True,
        'no_previous_frame_approximate_reuse':True,'current_frame_terms_recomputed':True,
        'changed_existing_source_files':sorted(changed),'source_hashes':{n:digest(n) for n in files},
        'test_log':'.cache/recognition-043/tests.log','test_log_sha256':digest('.cache/recognition-043/tests.log'),
        'replay':'.cache/recognition-043/paired-replay.json','replay_sha256':digest('.cache/recognition-043/paired-replay.json'),
        'elapsed_seconds':time.perf_counter()-started,'private_state_used':False,'chat_requests':0,'game_actions':0,
        'limits':['Timing is local replay, not live or all-inventory accuracy.',
            'Only immutable reference terms/artwork are reused; current pixels and dynamic anchors remain current.',
            'Public OCR-reader timings are ordered single reads, not an end-to-end speed benchmark.',
            'Relic-specific cost rounding/card lifecycle remains unknown; no numerical model added.',
            'P1-P3 remain incomplete.']}
    (ROOT/'RECOGNITION_0.43_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','paired_visual_cases','public_reader_cases',
        'scale_preparation','immutable_raw_art_cache_bytes','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
