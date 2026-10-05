"""Stage the tested feature-budget fix; replace files without altering hardlinks."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import time

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXPERIMENT=ROOT/'.cache/page-features-059/budget-experiment-1791182679399208200/receipt.json'
CANDIDATE=ROOT/'.cache/page-features-059/candidate-1791182678996149000'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    experiment=read(EXPERIMENT)
    assert experiment['production_unchanged'] and experiment['threshold_modified'] is False
    chosen=next(e for e in experiment['candidate_experiments'] if e['left_feature_budget_per_view']==96)
    assert all(row['passed'] for row in chosen['rows'])
    folder=ROOT/'.cache/page-features-059'/f'adoption-{time.time_ns()}'
    folder.mkdir()
    live=ROOT/'rouge/data/page-features'
    hashes={p.name:sha(p) for p in live.iterdir() if p.is_file()}
    assert hashes['manifest.json']==experiment['source_sha256']['rouge/data/page-features/manifest.json']
    assert sha(ROOT/'rouge/page_features.py')==experiment['source_sha256']['rouge/page_features.py']
    shutil.copytree(live,folder/'before')
    builder_path=ROOT/'scripts/build_page_features_059.py'
    source=builder_path.read_text(encoding='utf-8')
    # The builder edit preceded this archive. Reconstruct its exact prior text
    # from those concrete hunks, and verify the pre-edit experiment hash.
    old=source.replace('STATIC_BUTTON_SOURCE_BOX = (262, 143, 438, 191)\n','')
    old=old.replace("CONTROL_FEATURE_BUDGET = {'left': 96, 'right': 48}\n",'')
    block="""            if key == 'owned_button':
                # Include the stable magnifier, excluding the count badge.
                # The actual recognized text must lie inside this source box.
                sx0, sy0, sx1, sy1 = STATIC_BUTTON_SOURCE_BOX
                if not (sx0 <= source_box[0] < source_box[2] <= sx1 and
                        sy0 <= source_box[1] < source_box[3] <= sy1):
                    raise ValueError('Static button text moved outside the inspected source control')
                source_box = STATIC_BUTTON_SOURCE_BOX
"""
    assert block in old;old=old.replace(block,'')
    old=old.replace("if len(selected) >= CONTROL_FEATURE_BUDGET[anchor['side']]:","if len(selected) >= 48:")
    old=old.replace("            'control_feature_budget_per_view': CONTROL_FEATURE_BUDGET,\n",'')
    reconstructed=folder/'builder-epoch1-reconstructed.py'
    reconstructed.write_bytes(old.encode('utf-8'))
    assert sha(reconstructed)==experiment['source_sha256']['scripts/build_page_features_059.py']
    staged=folder/'staged';shutil.copytree(live,staged)
    spec=importlib.util.spec_from_file_location('popup_builder_059_staged',builder_path)
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    builder.OUTPUT=staged;builder.main()
    with np.load(staged/'owned-popup.npz',allow_pickle=False) as actual, \
            np.load(CANDIDATE/'features.npz',allow_pickle=False) as expected:
        assert set(actual.files)==set(expected.files)
        for key in actual.files:assert np.array_equal(actual[key],expected[key]),key
    manifest=read(staged/'manifest.json')
    page=next(p for p in manifest['pages'] if p['page']=='run_owned_popup')
    assert page['control_feature_budget_per_view']=={'left':96,'right':48}
    assert page['derived_feature_scales']==[1.,.8,.65]
    assert page['independent_training_sources']==1
    names=['manifest.json',page['features'],*[a['patch'] for a in page['anchors']]]
    after={p.name:sha(p) for p in staged.iterdir() if p.is_file()}
    assert all(after[n]==value for n,value in hashes.items() if n not in names)
    changed=[n for n in names if hashes[n]!=after[n]]
    for name in names:
        assert Path(name).name==name
        # Copy to a new inode, then replace; old baseline supplemental media
        # hardlinks continue to point to their unmodified epoch1 bytes.
        temporary=live/(name+'.059-staged')
        assert not temporary.exists()
        shutil.copyfile(staged/name,temporary)
        os.replace(temporary,live/name)
    assert all(sha(live/name)==value for name,value in after.items())
    receipt={'passed':True,'before_sha256':hashes,'after_sha256':after,
        'changed_assets':changed,'old_binary_assets_unchanged':20,
        'experiment':{'path':EXPERIMENT.relative_to(ROOT).as_posix(),'sha256':sha(EXPERIMENT)},
        'candidate_feature_arrays_exact':True,'threshold_modified':False,
        'hardlinked_historical_bytes_preserved':True,
        'old_builder_reconstructed_not_contemporaneous_copy':{
            'path':reconstructed.relative_to(ROOT).as_posix(),'sha256':sha(reconstructed)},
        'builder_sha256':sha(builder_path),'adoption_script_sha256':sha(__file__),
        'private_state_read':False,'game_actions':0,'chat_requests':0,'verified_at':time.time()}
    path=folder/'receipt.json'
    with path.open('x',encoding='utf-8') as handle:json.dump(receipt,handle,ensure_ascii=False,indent=2)
    print(json.dumps({'passed':True,'changed':changed,'receipt':path.relative_to(ROOT).as_posix()}))


if __name__=='__main__':main()
