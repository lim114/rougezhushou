"""Reproduce the original unread-row fault using public synthetic text only.

Exit0 means that the old defect was observed, never that the product passed.
The preserved old source, not the later repaired function, is exercised.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys,types
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R))
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
assert not args.output.exists()
manifest=json.loads((R/'verification/full-425/repair-source-baseline-attempt1/manifest.json').read_bytes())
row=next(r for r in manifest['files']if r['original_public_path']=='rouge/player_shop_hover.py')
raw=(R/row['preserved_public_copy']).read_bytes();assert sha256(raw).hexdigest()==row['original_sha256']
module=types.ModuleType('rouge._preserved_shop_before_425_repair');module.__package__='rouge'
exec(compile(raw,row['preserved_public_copy'],'exec'),module.__dict__)
def text(name,x,y,w=100):return [[[x,y],[x+w,y],[x+w,y+20],[x,y+20]],name,.99]
records=[text('购买',600,10),text('当前余额',30,40),text('第一法则',100,120),text('活玫瑰',300,120),
    text('白模鱼',100,580),text('支援补给站',300,580),text('编队',600,810)]
for x in(240,440):
    for y in(250,480,710):records.append(text('价格',x,y,40))
names={'第一法则':['row1-a'],'活玫瑰':['row1-b'],'白模鱼':['row3-a'],'支援补给站':['row3-b']}
item,shop=module.shop_target(records,names,(245,410),(850,800,3))
assert shop and item and item['id']=='row1-a','The expected original defect was not reproduced.'
report={'section':425,'kind':'PUBLIC_SYNTHETIC_REPRODUCTION_OF_ORIGINAL_DEFECT_NOT_PRODUCT_PASS',
    'original_public_source':row,'original_behavior_correct':False,'defect_reproduced':True,
    'expected_item':None,'actual_wrong_item_id':item['id'],'cursor':[245,410],
    'synthetic_current_text_records':records,'name_ids':names,'frame_shape':[850,800,3],
    'reason':'Middle-row names are unread; price labels locate all three rows. The original algorithm ignores those labels and stretches a known first-row name across the unread row.',
    'game_capture_or_input_performed':False,'private_data_used_or_copied':False,
    'repaired_product_or_full_validation_pass_claimed':False}
args.output.parent.mkdir(parents=True,exist_ok=True)
with args.output.open('x',encoding='utf8')as f:f.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'original_defect_reproduced':True,'original_product_correct':False,'public_synthetic_input_only':True}))
