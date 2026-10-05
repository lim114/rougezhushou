"""Append reviewed landmarks without rewriting the prior calibration records."""
import copy,hashlib,json,math,sys
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.battle_preview import battle_data,DATA
from rouge.map_projection import grid_digest


def main():
    base=ROOT/'.cache/research/map-projection-045'
    prior=ROOT/'.cache/batch-045-before/rouge/data/battle-map-projections.json'
    path=ROOT/'rouge/data/battle-map-projections.json'
    assert path.read_bytes()==prior.read_bytes()
    old=json.loads(prior.read_text(encoding='utf-8'));output=copy.deepcopy(old)
    original=json.loads((ROOT/'.cache/research/map-projection-044/calibration-input.json').read_text(encoding='utf-8'))
    rejected=next(e for e in original['calibrations'] if e['id']=='ro6_n_1_3')
    recorded=json.loads((base/'acute-six-anchor-fit.json').read_text(encoding='utf-8'))
    assert recorded['accepted'] and recorded['tolerance_px']==4
    entry={'id':'ro6_n_1_3','aliases':['ro6_e_1_3'],'anchors':recorded['anchors'],
           'checks':rejected['checks'],'enabled':True}
    inputs={'pixel_tolerance':4,'method':old['method'],'scope':old['scope'],
            'notes':'Checks copied unchanged from the rejected 0.44 candidate. Six clear junctions span three image heights. Never fit check coordinates.',
            'calibrations':[entry]}
    input_path=base/'calibration-input.json';assert not input_path.exists()
    input_path.write_text(json.dumps(inputs,ensure_ascii=False,indent=2),encoding='utf-8')
    anchors=entry['anchors'];sid=entry['id'];s=battle_data()['stages'][sid]
    matrix,_=cv2.findHomography(np.array([[c,r] for r,c,x,y in anchors],float),
                               np.array([[x,y] for r,c,x,y in anchors],float),method=0)
    assert matrix is not None and np.isfinite(matrix).all()
    checks=[]
    for r,c,x,y,cue in entry['checks']:
        vec=matrix@np.array([c,r,1.]);px,py=vec[:2]/vec[2]
        error=math.hypot(px-x,py-y);assert error<=4,(cue,error)
        checks.append({'row':r,'col':c,'observed_pixel':[x,y],'projected_pixel':[float(px),float(py)],
                       'error_px':error,'cue':cue})
    output['calibrations'][sid]={'anchors':anchors,'checks':checks,'matrix':matrix.ravel().tolist(),
        'inverse':np.linalg.inv(matrix).ravel().tolist(),'tolerance_px':4,
        'bitmap_sha256':s['image']['sha256'],'grid_sha256':grid_digest(s),
        'width':s['image']['width'],'height':s['image']['height'],'rows':len(s['map']),
        'cols':len(s['map'][0]),'base_stage_id':sid,
        'landmarks_sha256':hashlib.sha256(input_path.read_bytes()).hexdigest()}
    c=output['calibrations'][sid]
    for alias in [sid,*entry['aliases']]:
        stage=battle_data()['stages'][alias]
        assert grid_digest(stage)==c['grid_sha256']
        assert stage['image']['sha256']==c['bitmap_sha256']
        assert hashlib.sha256((DATA/stage['image']['file']).read_bytes()).hexdigest()==c['bitmap_sha256']
        assert alias not in output['stages']
        output['stages'][alias]={'calibration':sid,'level_sha256':stage['level_source']['sha256'],
                               'image_file':stage['image']['file']}
    assert all(output['calibrations'][k]==v for k,v in old['calibrations'].items())
    assert all(output['stages'][k]==v for k,v in old['stages'].items())
    output['version']='0.45.0'
    output['source']['added_landmarks_045']={'file':str(input_path.relative_to(ROOT)),
        'sha256':hashlib.sha256(input_path.read_bytes()).hexdigest(),
        'original_rejected_readings':'.cache/research/map-projection-044/calibration-input.json'}
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'new_calibrations':1,'total_calibrations':4,'bound_stages':8,
        'new_independent_checks':len(checks),'new_max_error_px':max(p['error_px'] for p in checks),
        'prior_records_unchanged':True}))


if __name__=='__main__':main()
