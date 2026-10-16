from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[1]
native = ROOT / 'verification/sections/294-window-attempt2/actual/window.json'
report = json.loads(native.read_bytes())
assert report['passed'] and report['qt_exit_code'] == 0
images = {str((native.parent / Path(row['screenshot']).name).relative_to(ROOT)).replace('\\', '/'):
          row['screenshot_sha256'] for row in report['stage_observations']}
assert len(images) == 4
assert all(sha256((ROOT/name).read_bytes()).hexdigest() == value for name, value in images.items())
review = {'section': 294, 'kind': 'root_archived_native_images_review',
          'at_utc': datetime.now(timezone.utc).isoformat(),
          'actual_images_opened_with_view_image': True, 'actual_image_count': len(images),
          'images': images,
          'observations': ['生存习性与湖中魇普通/紧急四张实际截图已打开核对，固定原图显示已核地面点，左侧格图保留原资料路线。',
                           '原图不连点成路线，点位与部分参考说明可见；仅四张末尺寸截图，不是十二张截图。',
                           '紧急关的技术资料由验收显式勾选；这不是默认玩家视图。',
                           '独立读数一致只说明近似参考，不证明本局实际出生位置、路线激活或整体坐标校准。']}
dest = ROOT / 'verification/sections/294-preparation/root-visual-review.json'
with dest.open('xb') as stream:
    stream.write((json.dumps(review, ensure_ascii=False, indent=2) + '\n').encode())
previous = (ROOT/'.cache/restart_window_293.py').read_bytes().decode()
current = previous.replace('293', '294').replace('294-window-attempt1/', '294-window-attempt2/').replace('294-necessary-first/', '294-necessary-final/')
assert current.count('assert len(expected_sources) == 21') == 1
current = current.replace('assert len(expected_sources) == 21', 'assert len(expected_sources) == 33')
assert current.count('handle, expected_pid = 4721974, 27964') == 1
current = current.replace('handle, expected_pid = 4721974, 27964', 'handle, expected_pid = 1183342, 40208')
with (ROOT/'.cache/restart_window_294.py').open('xb') as stream:
    stream.write(current.encode())
with (ROOT/'.cache/focus_window_294.py').open('xb') as stream:
    stream.write((ROOT/'.cache/focus_window_293.py').read_bytes().replace(b'293', b'294'))
print(json.dumps({'section': 294, 'visual_review_written': True, 'main_focus_tools_prepared_not_executed': True}))
