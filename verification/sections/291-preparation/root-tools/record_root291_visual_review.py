from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'verification/sections/291-window-attempt5/actual'
receipt=json.loads((base/'window.json').read_bytes())
assert receipt['passed'] and receipt['screenshot_count']==7
notes={
 'layout-1':'1050x720实际窗口：事件树、玩家说明及两个横排引用入口可见；默认未选择，位置与实际目的地的区别有中文说明。',
 'layout-2':'1280x800实际窗口：中文正文、原选项入口及两个独立引用控件分开，未见重叠。',
 'layout-3':'1440x930实际窗口：阅读区与引用区域完整，较大窗口利用额外正文高度。',
 'bound-current':'当前记录：文本选区、非零滚动及所选位置/关卡可见；单向完成例外和实际目标未知分开。',
 'bound-history':'历史记录：位置标签明确历史，提示不能借历史证明完成或本次目的地；原阅读选区保留。',
 'fixed-ro6_t_10':'枯枝：已打开固定战斗预览，网格图与原图、出怪资料和敌人资料可见；原图未校准的限制仍显示。',
 'fixed-ro6_t_11':'败叶：已打开其不同固定战斗预览，网格、原图与多条出怪资料可见；实际出场时刻/面板未知未伪造。'}
images=[]
for row in receipt['screenshots']:
 p=base/Path(row['path']).name
 assert sha256(p.read_bytes()).hexdigest()==row['sha256'] and row['name'] in notes
 images.append({'relative_path':p.relative_to(ROOT).as_posix(),'sha256':row['sha256'],
                'actually_viewed_by_root':True,'acceptable':True,'review':notes[row['name']]})
assert set(notes)=={row['name'] for row in receipt['screenshots']}
review={'section':291,'kind':'root_manual_visual_review_not_new_test_execution',
 'actual_window_attempt':5,'receipt':'verification/sections/291-window-attempt5/actual/window.json',
 'receipt_sha256':sha256((base/'window.json').read_bytes()).hexdigest(),
 'all_images_actually_viewed_and_accepted':True,'images':images,
 'mechanism_game_state_or_numerical_accuracy_certified_by_visual_review':False}
p=ROOT/'verification/sections/291-preparation/root-final-window-visual-review.json'
with p.open('xb') as f:f.write((json.dumps(review,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'actual_images_reviewed':len(images),'review_saved':True,'new_tests_counted':False}))
