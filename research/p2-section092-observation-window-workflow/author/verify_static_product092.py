"""Read-only product verification; stdlib/Git reads, no project imports or calls."""
import ast
import copy
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
COMMIT = '59961ec3d633ac91b01014fb06b357d45e5979f7'
PROOF = ROOT / 'static-product-proof092.json'


def fingerprint(path, raw=None):
    data = path.read_bytes() if raw is None else raw
    return {'path': str(path), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}


def one_replace(raw, old, new):
    assert raw.count(old) == 1, ('expected exactly one block', old[:90])
    return raw.replace(old, new, 1)


def mask_body(tree, names):
    tree = copy.deepcopy(tree)
    found = []
    def walk(node, scope=''):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                qualified = scope + child.name
                if qualified in names:
                    assert isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                    child.body = [ast.Pass()]
                    found.append(qualified)
                else:
                    walk(child, qualified + '.')
            else:
                walk(child, scope)
    walk(tree)
    assert sorted(found) == sorted(names), found
    return ast.dump(tree, include_attributes=False)


def main():
    assert not PROOF.exists(), 'Do not overwrite an earlier proof.'
    freeze_path = ROOT / 'pre-public-freeze092.json'
    transport_path = ROOT / 'actual91-transport-proof092.json'
    patch_path = ROOT / 'candidate-flow092.patch'
    freeze_raw = freeze_path.read_bytes()
    transport_raw = transport_path.read_bytes()
    patch_raw = patch_path.read_bytes()
    freeze = json.loads(freeze_raw)
    transport = json.loads(transport_raw)
    assert freeze['actual_root_commit'] == transport['actual_root_commit'] == COMMIT
    frozen = {item['archive_path']: item for item in freeze['files']}
    products = {item['path']: item for item in transport['products']}
    files = {}
    for name in ('app.py', 'reporting.py'):
        relative = 'rouge/' + name
        baseline_path = ROOT / 'actual91-leaves' / relative
        candidate_path = ROOT / 'candidate' / relative
        old, new = baseline_path.read_bytes(), candidate_path.read_bytes()
        git_raw = subprocess.run(['git', 'show', COMMIT + ':' + relative],
            cwd=REPO, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        assert old == git_raw, relative + ' baseline is not exact fixed Git.'
        before, after = fingerprint(baseline_path, old), fingerprint(candidate_path, new)
        item = products[relative]
        assert (before['bytes'], before['sha256']) == (item['old_bytes'], item['old_sha256'])
        assert (after['bytes'], after['sha256']) == (item['new_bytes'], item['new_sha256'])
        item = frozen['candidate/' + relative]
        assert (after['bytes'], after['sha256']) == (item['bytes'], item['sha256'])
        files[name] = {'relative': relative, 'old_path': baseline_path,
            'new_path': candidate_path, 'old': old, 'new': new,
            'baseline': before, 'candidate': after}

    app = files['app.py']
    for data in (app['old'], app['new']):
        assert data.count(b'\n') == data.count(b'\r\n')
        assert data.replace(b'\r\n', b'').count(b'\r') == 0
    report = files['reporting.py']
    assert b'\r' not in report['old'] and b'\r' not in report['new']

    app_old = "        self.limit_window = QCheckBox('使用指定输出窗口（秒）')\r\n".encode()
    window_tip = '只改变当前技能模型的观察范围，不把输入秒数当作技能持续时间；实际已计窗口见报告。已计窗口为0秒时不计算窗口平均DPS/HPS，未定位来源与未知回转仍保持原说明。'
    app_new = ("        self.limit_window = QCheckBox('使用指定观察窗口（秒）')\r\n"
        + f"        self.limit_window.setToolTip('{window_tip}')\r\n"
        + f"        self.window_seconds.setToolTip('{window_tip}')\r\n"
        + "        self.limit_window.toggled.connect(lambda:self.calculate())\r\n"
        + "        self.window_seconds.valueChanged.connect(lambda:self.calculate())\r\n").encode()
    tip_old = '秒数以技能开启为0；初动使用initial_target_windows等独立部署时间轴。此处为测试情景，当前尚未从战斗画面自动跟踪。动画参考值会自动加载；不要在这里填写培养属性。'
    tip_new = tip_old + '区间按30Hz模拟帧换算，换算后结束须晚于开始。关闭逐帧时，常规连续攻击参考不按供靶/移动/中断区间逐帧调度；目标消失声明和友方潜在治疗仍按已有范围处理，未知时钟不补算。'
    app_tip_old = f"        self.timing_scenario.setToolTip('{tip_old}')\r\n".encode()
    app_tip_new = f"        self.timing_scenario.setToolTip('{tip_new}')\r\n".encode()
    expected_app = one_replace(one_replace(app['old'], app_old, app_new), app_tip_old, app_tip_new)
    assert expected_app == app['new'], 'App contains changes outside the two authorized blocks.'
    inverse_app = one_replace(one_replace(app['new'], app_new, app_old), app_tip_new, app_tip_old)
    assert inverse_app == app['old']

    damage_row = "                rows.append(metric('window_seconds','伤害观察窗口',skill['window_seconds'],'秒'))\n"
    damage_old = ("            if skill.get('window_seconds'):\n" + damage_row
        + "                rows.append(metric('window_dps','情景平均伤害参考' if result.get('charge_reference') else '窗口平均 DPS',\n"
        + "                    window_damage/skill['window_seconds'] if window_damage is not None else None,'伤害/秒'))\n").encode()
    damage_new = ("            if skill.get('window_seconds') is not None:\n" + damage_row
        + "            if skill.get('window_seconds'):\n"
        + "                rows.append(metric('window_dps','情景平均伤害参考' if result.get('charge_reference') else '窗口平均 DPS',\n"
        + "                    window_damage/skill['window_seconds'] if window_damage is not None else None,'伤害/秒'))\n").encode()
    healing_old = ("            if skill.get('window_seconds'):\n"
        + "                rows.append(metric('window_hps','窗口平均 HPS',window_healing/skill['window_seconds'] if window_healing is not None else None,'治疗/秒'))\n").encode()
    healing_new = ("            if skill.get('window_seconds') is not None:\n"
        + "                rows.append(metric('window_seconds','治疗观察窗口',skill['window_seconds'],'秒'))\n").encode() + healing_old
    expected_report = one_replace(one_replace(report['old'], damage_old, damage_new), healing_old, healing_new)
    assert expected_report == report['new'], 'Report contains changes outside the two authorized blocks.'
    # Remove the newly placed duration guard/rows and restore the old positive
    # damage duration row; preserve both original truthy average branches.
    inverse_report = one_replace(one_replace(report['new'], damage_new, damage_old), healing_new, healing_old)
    assert inverse_report == report['old']
    assert healing_old in report['new']
    assert damage_old.split(damage_row.encode(), 1)[1] in report['new']

    ast_checks = {}
    for name, allowed in [('app.py', ['MainWindow.make_damage_tab']), ('reporting.py', ['build_report'])]:
        item = files[name]
        old_tree = ast.parse(item['old'].decode('utf-8'), filename=str(item['old_path']))
        new_tree = ast.parse(item['new'].decode('utf-8'), filename=str(item['new_path']))
        assert mask_body(old_tree, allowed) == mask_body(new_tree, allowed), name
        ast_checks[name] = {'only_changed_body': allowed[0],
            'all_other_AST_including_signatures_equal': True}

    regenerated_patch = ''.join(''.join(difflib.unified_diff(
        files[name]['old'].decode('utf-8').splitlines(keepends=True),
        files[name]['new'].decode('utf-8').splitlines(keepends=True),
        fromfile='a/' + files[name]['relative'], tofile='b/' + files[name]['relative']))
        for name in ('app.py', 'reporting.py')).encode('utf-8')
    assert regenerated_patch == patch_raw, 'Frozen patch is not the exact two-file baseline diff.'
    item = frozen['candidate-flow092.patch']
    assert (len(patch_raw), hashlib.sha256(patch_raw).hexdigest()) == (item['bytes'], item['sha256'])
    assert sum(line.startswith(b'@@ ') for line in patch_raw.splitlines()) == 4
    for item in files.values():
        assert item['old_path'].read_bytes() == item['old']
        assert item['new_path'].read_bytes() == item['new']
    assert freeze_path.read_bytes() == freeze_raw
    assert transport_path.read_bytes() == transport_raw
    assert patch_path.read_bytes() == patch_raw

    proof = {'format_version': 1, 'status': 'PASS_STATIC_ONLY_NOT_FORMAL_REVIEW',
        'fixed_git_commit': COMMIT,
        'files': {name: {'baseline': item['baseline'], 'candidate': item['candidate']}
                  for name, item in files.items()},
        'bindings': {'freeze': fingerprint(freeze_path, freeze_raw),
                     'transport': fingerprint(transport_path, transport_raw),
                     'patch': fingerprint(patch_path, patch_raw),
                     'checker': fingerprint(Path(__file__).resolve())},
        'checks': {'fixed_git_leaf_bytes_equal': True, 'frozen_candidate_and_patch_hashes_equal': True,
            'AST': ast_checks, 'exact_app_authorized_blocks': 2, 'exact_report_authorized_blocks': 2,
            'app_inverse_bytes_equal': True, 'report_inverse_bytes_equal': True,
            'damage_old_positive_average_branch_preserved': True,
            'healing_old_average_branch_preserved': True,
            'app_newlines': 'CRLF only', 'report_newlines': 'LF only',
            'patch_exactly_regenerated_from_baseline': True, 'patch_hunks': 4,
            'all_input_bytes_unchanged_after_check': True},
        'scope': 'Only two frozen product leaves, freeze metadata, transport metadata and patch; no old49/730 recheck.',
        'project_calls': dict.fromkeys(('API', 'helper', 'formatter', 'tests', 'Qt', 'Wine'), 0),
        'runtime_limits': 'AST/text/bytes evidence only; no signal delivery or numerical/report runtime claim.'}
    encoded = (json.dumps(proof, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    assert len(encoded) <= 6 * 1024
    with PROOF.open('xb') as output:
        output.write(encoded)
    print(json.dumps({'status': proof['status'], 'proof': fingerprint(PROOF),
        'project_calls': proof['project_calls']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
