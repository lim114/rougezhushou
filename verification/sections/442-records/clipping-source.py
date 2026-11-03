from pathlib import Path
import sys,json,cv2,numpy as np
R=Path.cwd();sys.path.insert(0,str(R))
from rouge.recognition import ScreenReader
out=R/'verification/sections/442-capacity-clipping';out.mkdir(exist_ok=False)
im=cv2.imdecode(np.fromfile(R/'.cache/vlm-public-reference-frames/60.png',np.uint8),1)
reader=ScreenReader();rows=[]
for right in (1760,1740):
    result=reader.read(im[:,:right]);hope=(result.get('run')or{}).get('resources',{}).get('hope',{})
    row={'public_frame_seconds':60,'right_pixel':right,'hope_current_still_seven':hope.get('value')==7,'clipped_limit_not_claimed':'capacity'not in hope}
    rows.append(row);print(json.dumps(row),flush=True)
passed=all(r['hope_current_still_seven']and r['clipped_limit_not_claimed']for r in rows)
(out/'results.json').write_text(json.dumps({'passed':passed,'cases':rows,'scope':'Two clipped derivatives of the same public reference frame. Not independent sessions or arbitrary screen coverage.'},indent=2)+'\n','utf8')
(out/'source.py').write_bytes(Path(__file__).read_bytes())
raise SystemExit(0 if passed else 1)
