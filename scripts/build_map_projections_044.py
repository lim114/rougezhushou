"""Build fixed-bitmap geometry from independently recorded offline landmarks."""
import hashlib,json,math,sys
from pathlib import Path
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.battle_preview import battle_data,DATA
from rouge.map_projection import grid_digest


def main():
    base=ROOT/'.cache/research/map-projection-044'
    inputs=json.loads((base/'calibration-input.json').read_text(encoding='utf-8'))
    source=json.loads((base/'source-receipts.json').read_text(encoding='utf-8'))
    stages=battle_data()['stages'];records={};calibrations={};max_error=0
    for entry in inputs['calibrations']:
        if entry.get('enabled') is False:continue
        sid=entry['id'];stage=stages[sid]
        # The transform fits observed bitmap coordinates, not a guessed camera.
        src=np.array([[c,r] for r,c,x,y in entry['anchors']],dtype=np.float64)
        dst=np.array([[x,y] for r,c,x,y in entry['anchors']],dtype=np.float64)
        matrix,_=cv2.findHomography(src,dst,method=0)
        assert matrix is not None and np.isfinite(matrix).all(),sid
        inverse=np.linalg.inv(matrix);checks=[]
        for r,c,x,y,cue in entry['checks']:
            vector=matrix@np.array([c,r,1.0]);px,py=vector[:2]/vector[2]
            error=math.hypot(px-x,py-y);max_error=max(max_error,error)
            checks.append({'row':r,'col':c,'observed_pixel':[x,y],
                'projected_pixel':[float(px),float(py)],'error_px':error,'cue':cue})
        assert max(c['error_px'] for c in checks)<=inputs['pixel_tolerance'],(sid,checks)
        calibration={'anchors':entry['anchors'],'checks':checks,'matrix':matrix.ravel().tolist(),
            'inverse':inverse.ravel().tolist(),'tolerance_px':inputs['pixel_tolerance'],
            'bitmap_sha256':stage['image']['sha256'],'grid_sha256':grid_digest(stage),
            'width':stage['image']['width'],'height':stage['image']['height'],
            'rows':len(stage['map']),'cols':len(stage['map'][0]),'base_stage_id':sid}
        calibrations[sid]=calibration
        for alias in [sid,*entry['aliases']]:
            s=stages[alias]
            assert s['image']['sha256']==calibration['bitmap_sha256'],alias
            assert grid_digest(s)==calibration['grid_sha256'],alias
            assert hashlib.sha256((DATA/s['image']['file']).read_bytes()).hexdigest()==s['image']['sha256'],alias
            records[alias]={'calibration':sid,'level_sha256':s['level_source']['sha256'],
                'image_file':s['image']['file']}
    output={'version':'0.44.0','method':inputs['method'],'scope':inputs['scope'],
        'source':{'game_commit':battle_data()['source']['game_commit'],
            'resource_commit':battle_data()['source']['resource_commit'],
            'landmarks_sha256':hashlib.sha256((base/'calibration-input.json').read_bytes()).hexdigest(),
            'camera_reference':[r for r in source if r['file'] in ('resource-maps.json','resource-summary.json','resource-readme.md')]},
        'calibrations':calibrations,'stages':records}
    path=ROOT/'rouge/data/battle-map-projections.json'
    assert not path.exists(),'Do not overwrite a reviewed calibration.'
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'calibrated_bitmaps':len(calibrations),'bound_stages':len(records),
        'independent_check_landmarks':sum(len(c['checks']) for c in calibrations.values()),
        'max_independent_error_px':max_error,'tolerance_px':inputs['pixel_tolerance']}))


if __name__=='__main__':main()
