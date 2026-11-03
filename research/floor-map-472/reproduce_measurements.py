"""Reproduce offline proposals from the retained first-pass source regions."""
from hashlib import sha256
from pathlib import Path
import json
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
observations=json.loads((Path(__file__).parent/'observations.json').read_bytes())['observations']
checked=[]
for row in observations:
    raw=(ROOT/'rouge/data/battle-maps'/(row['stage']+'.png')).read_bytes()
    assert sha256(raw).hexdigest()==row['image_sha256']
    image=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
    hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    mask=(cv2.inRange(hsv,(90,80,90),(125,255,255))if row['color']=='blue'else
          cv2.bitwise_or(cv2.inRange(hsv,(0,90,90),(12,255,255)),cv2.inRange(hsv,(168,90,90),(179,255,255))))
    x0,y0,x1,y1=row['manual_roi']
    count,labels,stats,centroids=cv2.connectedComponentsWithStats(mask[y0:y1,x0:x1],connectivity=8)
    index=max(range(1,count),key=lambda i:int(stats[i,cv2.CC_STAT_AREA]))
    x,y,w,h,area=map(int,stats[index]);box=[x0+x,y0+y,w,h]
    point=[box[0]+(w-1)/2,box[1]+(h-1)/2]
    assert box==row['largest_component_box']and point==row['pixel']and area==row['component_pixels']
    checked.append({'stage':row['stage'],'cell':[row['row'],row['col']],'pixel':point})
print(json.dumps({'passed':True,'opencv_version':cv2.__version__,'observations_checked':len(checked),'records':checked}))
