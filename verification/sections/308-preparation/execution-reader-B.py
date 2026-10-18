from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'.cache/p3-308-reader-inputs';OUT=ROOT/'.cache/p3-308-reader-b'
def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def sha(p):return sha256(p.read_bytes()).hexdigest()
pins=json.loads((SOURCE/'SOURCE_PINS.json').read_bytes());assert sha(SOURCE/'SOURCE_PINS.json')=='f5b0a26d68aa29b6dd5e5d67dfc96fdfc87e6c662c50f46da598bcb894077d49'
for name,pin in pins['files'].items():assert (SOURCE/name).stat().st_size==pin['bytes'] and sha(SOURCE/name)==pin['sha256']
request=json.loads((SOURCE/'REQUESTS.json').read_bytes())
# Each literal is an independent visual reading in the unchanged original PNG.
# There is no coordinate formula, fit, interpolation or post-comparison update.
measured={
 'ro6_n_5_1':{
  (3,1):[129,113],(3,3):[184,113],(3,5):[242,114],(3,7):[302,114],(3,9):[360,113],
  (4,1):[122,140],(4,3):[179,140],(4,5):[241,140],(4,7):[304,140],(4,9):[366,140],
  (5,1):[115,167],(5,2):[148,167],
  (6,2):[139,198],(6,3):[172,198],(6,4):[205,198],(6,5):[238,198],(6,6):[272,198],(6,7):[305,198],(6,8):[339,198]},
 'ro6_n_5_5':{
  (1,1):[120,79],(1,2):[145,79],(1,9):[333,76],(1,10):[360,76],
  (2,1):[112,102],(2,2):[138,102],
  (3,1):[104,126],(3,4):[197,119],(3,7):[284,120],(3,8):[312,120],(3,9):[341,120],(3,10):[370,120],(3,11):[400,120],
  (4,1):[96,149],(4,4):[195,145],(4,7):[287,145],(4,8):[316,145],(4,9):[347,145],(4,10):[377,145],(4,11):[408,145],
  (5,1):[87,175],(5,4):[192,173],
  (6,1):[79,204],(6,4):[189,202],(6,5):[231,201],(6,6):[265,201],(6,7):[300,201],(6,8):[335,201],(6,9):[369,201],(6,10):[404,201],(6,11):[439,201]}}
images=[]
for group in request['groups']:
 sid=group['stage_id'];readings=[]
 for row in group['all_requests']:
  key=(row['row'],row['col']);pixel=measured[sid].get(key)
  readings.append({'request_id':row['request_id'],'row':row['row'],'col':row['col'],'tile_key':row['tile_key'],'pixel':pixel,
   'reason':'原图可见地面及格边界，按逻辑格逐格目视读取近似中心；未拟合或插值。' if pixel is not None else '树根、立面或邻接遮挡使本格完整地面对应不够清楚；保留未知，不从邻格推算。'})
 assert len(readings)==len(group['all_requests'])
 images.append({'stage_id':sid,'rows':group['rows'],'cols':group['cols'],'width':group['image']['width'],'height':group['image']['height'],'image_sha256':group['image']['sha256'],'readings':readings})
assert sum(len(i['readings'])for i in images)==67
target=OUT/'READER_B_ORIGINAL.json';assert not target.exists()
record={'schema':'section308-independent-fixed-image-readings-v1','reader':'B','declarations':{'scope':'Only the two requested new target images and their target coordinates; historical unrelated maps/source code do not supply a target measurement','other_reader_seen':False,'old_projection_or_landmarks_seen':False,'fit_or_interpolation_used':False,'original_images_modified':False,'coordinates_frozen_in_first_formal_record':True},'source_pins':{'files':[{'path':(SOURCE/n).relative_to(ROOT).as_posix(),**p}for n,p in pins['files'].items()]},'coordinate_rule':'零基显示row,col直接索引原map数组；原PNG像素；不套用敌人路线行反转。','reading_method':'Root B independently viewed both exact512×286 original PNGs and both exact logical grids. Separate4x nearest-neighbor views only enlarged the original pixels for visual reading; they contain no fitted point or grid annotation. Original files unchanged. Every literal first reading frozen before comparing with A. Unclear cells null. Two agent contexts are not two human measurements and do not prove absolute accuracy.','images':images,'frozen_utc':datetime.now(timezone.utc).isoformat()}
target.write_bytes(encoded(record))
ready={'reader':'B','file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'bytes':target.stat().st_size,'request_count':67,'nonnull_readings':sum(r['pixel']is not None for i in images for r in i['readings']),'other_reader_seen_before_freeze':False,'not_acceptance_or_absolute_accuracy':True,'source_pins_manifest_sha256':sha(SOURCE/'SOURCE_PINS.json')}
(OUT/'READY_B_ORIGINAL.json').write_bytes(encoded(ready));print(json.dumps(ready,ensure_ascii=False))
