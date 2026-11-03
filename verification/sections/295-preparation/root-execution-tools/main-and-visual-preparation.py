from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json
ROOT=Path(__file__).resolve().parents[1]
native=ROOT/'verification/sections/295-window-attempt1/actual/window.json'
report=json.loads(native.read_bytes());assert report['passed'] and report['qt_exit_code']==0
images={(native.parent/Path(row['path']).name).relative_to(ROOT).as_posix():row['sha256'] for row in report['screenshots']}
assert len(images)==3 and all(sha256((ROOT/name).read_bytes()).hexdigest()==value for name,value in images.items())
review={'section':295,'kind':'root_archived_native_images_review','at_utc':datetime.now(timezone.utc).isoformat(),
    'actual_images_opened_with_view_image':True,'actual_image_count':3,'images':images,
    'observations':['实际1050×720主窗口“线人”资料页可见并可点击独立物品说明入口。',
        '实际850×650物品窗口显示沙盘α图标、中文用途、物品说明及解锁说明，部署费用+2与本局领取/出现资格明确区分。',
        '损坏临时公开资料的负例截图中选择、图标和旧说明均已清除；不是对当前游戏资料失效的断言。',
        '三张截图由隔离真实Windows窗口产生；没有游戏采样或聊天发送。']}
with(ROOT/'verification/sections/295-preparation/root-visual-review.json').open('xb') as stream:
    stream.write((json.dumps(review,ensure_ascii=False,indent=2)+'\n').encode())
previous=(ROOT/'.cache/restart_window_294.py').read_bytes().decode()
current=previous.replace('294','295').replace('295-window-attempt2/','295-window-attempt1/').replace('295-necessary-final/','295-necessary-first/')
assert current.count('assert len(expected_sources) == 33')==1
current=current.replace('assert len(expected_sources) == 33','assert len(expected_sources) == 34')
assert current.count('handle, expected_pid = 1183342, 40208')==1
current=current.replace('handle, expected_pid = 1183342, 40208','handle, expected_pid = 2297712, 35924')
with(ROOT/'.cache/restart_window_295.py').open('xb') as stream:stream.write(current.encode())
with(ROOT/'.cache/focus_window_295.py').open('xb') as stream:stream.write((ROOT/'.cache/focus_window_294.py').read_bytes().replace(b'294',b'295'))
print(json.dumps({'section':295,'actual_visual_review_written':True,'main_focus_tools_prepared_not_executed':True}))
