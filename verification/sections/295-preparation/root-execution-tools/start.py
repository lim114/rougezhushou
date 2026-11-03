from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, subprocess
ROOT=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
assert git('branch','--show-current')=='codex/p2-development'
assert not git('status','--porcelain')
parent=git('rev-parse','HEAD');assert parent=='e517095f388baad3aa7824dbd5b9dee6a68fb450'
remote=git('ls-remote','origin','refs/heads/codex/p2-development').split()[0];assert parent==remote
cp_path=ROOT/'DEVELOPMENT_CHECKPOINT.json';cp=json.loads(cp_path.read_bytes())
assert cp['completed_sections']==294 and cp['next_section']==295 and 'active_section' not in cp
dest=ROOT/'verification/sections/295-preparation';dest.mkdir(exist_ok=False)
before={}
for name in ('node_catalog.py','player_node_information.py','node_catalog_view.py'):
    raw=(ROOT/'rouge'/name).read_bytes();(dest/('before-'+name)).write_bytes(raw)
    before['rouge/'+name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
scope={'section':295,'status':'scope_defined_before_functional_changes',
    'at_utc':datetime.now(timezone.utc).isoformat(),'parent':parent,'actual_remote_parent':remote,
    'before_existing_sources':before,'remaining_item':'P3节点事件中的具名物品说明与图标',
    'new_capability':'线人完整选项明确记载的沙盘α，新增独立文献物品入口，可手动查看图标、用途与完整说明。',
    'acceptance':['原17条typed具名奖励契约与非目标事件输出保持，不借物品说明补原游戏入口。',
        '每次检查绑定的当前资料完整字节，篡改/缺失后清空旧图标和说明，恢复后不自动重选。',
        '独立弹窗默认未选，真实点击查看，刷新保留父页面及弹窗的选择、页签、选区与非零滚动。',
        '资料解锁说明不同于本局资格；数量、实际领取、已持有及效果激活仍未知，25/57缺口保留。',
        '隔离私态，验证不操作游戏/不发聊天；更新原测试窗口并保留私人五路径。'],
    'full_validation_due':305,'functional_complete':False}
(dest/'scope.json').write_bytes((json.dumps(scope,ensure_ascii=False,indent=2)+'\n').encode())
cp['active_section']={'section':295,'status':'documented_item_reader_preparation',
    'remaining_item':scope['remaining_item'],'new_capability':scope['new_capability'],
    'acceptance':scope['acceptance'],'preparation_receipt':'verification/sections/295-preparation/scope.json'}
cp_path.write_bytes((json.dumps(cp,ensure_ascii=False,indent=2)+'\n').encode())
wip=ROOT/'WORK_IN_PROGRESS.md'
wip.write_bytes(('## 第295节进行中 · 线人选项中的沙盘α图标与物品说明\n\n'
    '新增独立文献物品阅读入口，不放宽17条具名奖励契约，不补25/57原入口、数量或本局领取。'
    '默认未选，手动打开说明，保留阅读状态；失效清空旧内容。必要检查与真实窗口待验证，未完成、未发布；下一全量305。\n\n').encode()+wip.read_bytes())
print(json.dumps({'section':295,'scope_started':True,'parent_remote_equal':True,'complete':False}))
