"""Prepare concrete archive inputs after actual full100 closure."""
import hashlib
import json
from pathlib import Path


def main():
    base = Path('/workspace/.continuation')
    root = Path('/workspace/rougezhushou')
    rows = []
    for catalog in ('public-files-source-plan.json', 'optional-sealed-Source-packets.json'):
        rows.extend(json.loads((base/'full100-archive-plan-source-v2'/catalog).read_bytes())['files'])
    def add(path, destination):
        raw = path.read_bytes()
        rows.append({'source_path':str(path), 'archive_path':destination,
                     'bytes':len(raw), 'sha256':hashlib.sha256(raw).hexdigest()})
    def folder(path, destination):
        for leaf in sorted(path.rglob('*')):
            if leaf.is_file():
                add(leaf, str(Path(destination)/leaf.relative_to(path)))
    for name in ('full100-wine-selected-v3.json', 'full100-wine-selected-v3.log', 'full100-wine-selected-v3.stdout.log', 'full100-wine-selected-v3.exit-code'):
        add(base/name, 'wine/selected/'+name)
    folder(base/'full100-window-actual-v3', 'GUI-third-attempt')
    for name in ('full100-window-supervisor-v3.json', 'full100-window-supervisor-v3.json.stdout.log', 'full100-window-supervisor-v3.json.stderr.log', 'full100-window-primary-v3.log', 'full100-window-primary-v3.exit-code'):
        add(base/name, 'GUI-third-attempt/supervision/'+name)
    for folder_name in ('full100-cpython-fileio-source-diagnosis-v1', 'full100-linux-proc-stat-source-v1', 'section096-100-progress-source-v1', 'full100-archive-facts-source-v1', 'full100-archive-plan-source-v2'):
        folder(base/folder_name, 'source-and-scope/'+folder_name)
    for number in range(96,100):
        path=base/f'section{number:03d}-publication-v1.json'
        add(path, 'prior-section-publications/'+path.name)
    for name in ('root-full100-saved-audit-v1.py', 'root-full100-saved-audit-v1.json', 'root-full100-saved-audit-v1.log', 'root-full100-saved-audit-v1.exit-code', 'root-full100-visual-audit-v1.json', 'root-full100-spec-builder-v1.py'):
        add(base/name, 'Root-audit/'+name)
    gui=json.loads((base/'full100-window-actual-v3/wine-ui-100.json').read_bytes())
    assert gui['passed'] is True
    todo = (root/'PROJECT_PROGRESS.md').read_text()
    remaining='\n'.join(line for line in todo.splitlines() if line.startswith('|'))
    report = '''# 第96–100节进度和未完成项目

五节专项已逐节实际检验、归档、提交并推送到 `codex/p2-development`，完成编号为100。此次补充保存只归档五节检查，不增加小节编号。下一节101处理缓存消费者安全，102处理库存确认资格和遗漏回归登记；P2机制尚未完成。

| 小节 | 已编入并专项检验的成果 | 实际GitHub提交 |
| --- | --- | --- |
| 96 | 条件控件的培养资格、来源和预览说明；保留原数值及全文对照 | [8283b07](https://github.com/lim114/rougezhushou/commit/8283b07e6af43e0535b70c0a6f700b69c050ac45) |
| 97 | 账号保存失败保留旧文件与临时证据，合法新观察可供内存使用；Unicode与告警边界 | [4c98e59](https://github.com/lim114/rougezhushou/commit/4c98e595efef2eb1fd03f0d08422ee432be86765) |
| 98 | 本局缓存加载前的消费者容器保护；不凭布尔库存或未知观察清除可信事实 | [8037683](https://github.com/lim114/rougezhushou/commit/8037683f115ff481446bcefe2e07455fcc777578) |
| 99 | 区分缓存读取保护与保存失败；旧目标、临时证据及内存保留，失败会话不自动重试 | [27fa675](https://github.com/lim114/rougezhushou/commit/27fa675dcccbf50b757e89e1ac0a0a04f1355ccf) |
| 100 | 培养数据只读安全显示；坏培养不丢失独立招募/个人强化事实，保留手动等级与Qt数值边界 | [8436f90](https://github.com/lim114/rougezhushou/commit/8436f906842cd45b7553d8f54f2b0efc0619f097) |

本次五节检查的实际结果：Linux维护并集运行2036项，实际通过1876项，84条历史/声明跳过，126条不可用记录涉及87个父测试；Wine维护并集运行2100项，实际通过1947项，87条跳过，123条不可用记录涉及84个父测试。两者失败/错误均0。Wine跳过包含3个因精确符号链接能力限制而未运行原测试体的项，不能重复相加或算通过。Linux与Wine依赖检查均真实退出0。

精选回归Linux运行1216项/1跳过，Wine运行1216项/4跳过，均无失败/错误；此处按真实运行和跳过记录报告，不从减法编造单独通过计数。Linux full回执自身登记350个生产源码文件；Root另用完整743个维护源码加CORE登记前后检查，二者区别保留。

第三次完整Wine Qt窗口验证完成4283条检查和52个保存状态，4张真实PNG已由Root查看，保存的字节/SHA、显式公共数值投影、原生类型标签/字典顺序/浮点hex和三份全文已复核。这个旧保存编码没有容器别名表示，显式投影也不证明旧Gold全部返回对象相同；96–100专项的更严格证据单独归档。旧95全函数调用向量未重测，旧95三次未完成记录继续搁置。前两次full100窗口失败、第一轮Wine失败及能力probe原失败都按原字节保存，没有改写为通过。

范围为当前200个维护选择器（196个整模块+4个方法），覆盖217个物理模块中的197个；20个模块和另一个截图方法未登记，未找到明确退役依据，列入后续核查。历史截图/缓存和缺失依赖不可用，未重造私人样本。因此不是全库发现，也不是原生Windows、实际游戏或聊天认证。窗口为当前100上的有界功能套件，加上96–100各节独立专项证据。

以下18组为实际PROJECT_PROGRESS.md原待办。P1保持断点，当前先P2，完成后P3；识别优化仍最后。不确定的时钟、层、来源和机制需有资料后才编写。

''' + remaining + '\n'
    spec={'guard':str(base/'full100-completed-source-guard-v1.json'),
          'successful_primary_files':[str(base/x) for x in ('full100-linux-v1.exit-code','full100-linux-pip-v1.exit-code','resume100-selected-v1.exit-code','full100-wine-full-v3.exit-code','full100-wine-selected-v3.exit-code','full100-wine-pip-v1.exit-code','root-full100-saved-audit-v1.exit-code')],
          'linux_full':str(base/'full100-linux-v1/receipt.json'), 'wine_full':str(base/'full100-wine-full-v3.json'),
          'wine_selected':str(base/'full100-wine-selected-v3.json'), 'gui_receipt':str(base/'full100-window-actual-v3/wine-ui-100.json'),
          'gui_supervisor':str(base/'full100-window-supervisor-v3.json'), 'gui_primary':str(base/'full100-window-primary-v3.exit-code'),
          'saved_audit':str(base/'root-full100-saved-audit-v1.json'), 'visual_audit':str(base/'root-full100-visual-audit-v1.json'),
          'actual_gui_attempts':3, 'gui_deferred_after_three':False, 'files':rows,
          'report_zh':report, 'readme':'# 第96–100节五节检查档案\n\n实际结果见 closure.json 和 REPORT_ZH.md；manifest.json逐文件记录原件与SHA。Source-only目录是检验器来源和审阅，运行结果由相应原始日志/退出码/回执承担。当前仍完成100，下一节101；私人内容未纳入。'}
    path=base/'root-full100-archive-spec-v1.json'
    with path.open('x',encoding='utf-8') as handle:
        json.dump(spec,handle,ensure_ascii=False,indent=2);handle.write('\n')
    print(json.dumps({'spec':str(path),'files':len(rows),'ready_for_actual_archive_gate':True}))


if __name__ == '__main__':
    main()
