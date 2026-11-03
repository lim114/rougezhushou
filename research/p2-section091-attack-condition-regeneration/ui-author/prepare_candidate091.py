"""External, stdlib-only source candidate. Never imports or executes project code."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE / "baseline/rouge/app.py"
DEST = HERE / "candidate/rouge/app.py"
TOOLTIP = (
    "声明估算时是否持续普攻；自然回复技能也可能通过适用的天赋或藏品使用此条件。"
    "显示此项不表示必有额外技力。未核验的技力来源仅作资料参考，未知回转保持未知。"
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def put_json(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


old = BASE.read_bytes()
assert digest(old) == "6a107fa37d2c21b9160131aa8c901fc2342ef7a422c3134dc0579ea24f4b56a2"
assert old.count(b"\r\n") == old.count(b"\n")
changes = [
    (
        "ui-meaning-and-refresh",
        "        self.continuous_attacks.setChecked(True)\r\n"
        "        form.addRow('攻击回复条件',self.continuous_attacks)\r\n",
        "        self.continuous_attacks.setChecked(True)\r\n"
        f"        self.continuous_attacks.setToolTip('{TOOLTIP}')\r\n"
        "        self.continuous_attacks.toggled.connect(lambda:self.calculate())\r\n"
        "        form.addRow('普攻回技力条件',self.continuous_attacks)\r\n",
    ),
    (
        "implemented-owner-qualification",
        "        healer=op in catalog()['operators'] and has_healing(op,skill)\r\n",
        "        implemented=op in catalog()['operators']\r\n"
        "        healer=implemented and has_healing(op,skill)\r\n",
    ),
    (
        "attack-or-natural-row-visibility",
        "                    (self.continuous_attacks,current.get('sp_type')=='INCREASE_WHEN_ATTACK'),\r\n",
        "                    (self.continuous_attacks,implemented and current.get('sp_type') in ('INCREASE_WHEN_ATTACK','INCREASE_WITH_TIME')),\r\n",
    ),
]
candidate = old
receipts = []
for problem, before, after in changes:
    before = before.encode()
    after = after.encode()
    assert candidate.count(before) == 1, problem
    candidate = candidate.replace(before, after, 1)
    receipts.append({"id": problem, "before_sha256": digest(before), "after_sha256": digest(after),
                     "before": before.decode(), "after": after.decode()})
inverse = candidate
for _, before, after in reversed(changes):
    assert inverse.count(after.encode()) == 1
    inverse = inverse.replace(after.encode(), before.encode(), 1)
assert inverse == old
assert candidate.count(b"\r\n") == candidate.count(b"\n")
old_ast = ast.parse(old.decode(), filename="fixed-actual90-app.py")
new_ast = ast.parse(candidate.decode(), filename="candidate-app.py")
assert ast.dump(ast.parse(inverse.decode()), include_attributes=False) == ast.dump(old_ast, include_attributes=False)


def methods(tree):
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "MainWindow")
    return {n.name: n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


old_methods, new_methods = methods(old_ast), methods(new_ast)
assert old_methods.keys() == new_methods.keys()
changed_methods = [name for name in old_methods if ast.dump(old_methods[name], include_attributes=False)
                   != ast.dump(new_methods[name], include_attributes=False)]
assert changed_methods == ["make_damage_tab", "update_skill_options"]
assert old.count(b"self.continuous_attacks.setChecked(") == candidate.count(b"self.continuous_attacks.setChecked(") == 1
assert old.count(b"self.continuous_attacks.isChecked()") == candidate.count(b"self.continuous_attacks.isChecked()") == 1
assert old.count(b"'continuous_attacks':self.continuous_attacks.isChecked()") == 1
assert candidate.count(b"'continuous_attacks':self.continuous_attacks.isChecked()") == 1
DEST.write_bytes(candidate)
patch = "".join(difflib.unified_diff(old.decode().splitlines(keepends=True), candidate.decode().splitlines(keepends=True),
                                    fromfile="a/rouge/app.py", tofile="b/rouge/app.py"))
(HERE / "candidate-app091.patch").write_bytes(patch.encode())
put_json("static-candidate-proof091.json", {
    "status": "SOURCE_BYTE_AST_ONLY_PASS_NOT_PRODUCT_RUNTIME_VERIFICATION",
    "candidate_base_commit": "2cbc45f03f99ed4f04b9c7e2612b58542f909168",
    "baseline": {"path": str(BASE), "sha256": digest(old), "bytes": len(old), "crlf": old.count(b"\r\n")},
    "candidate": {"path": str(DEST), "sha256": digest(candidate), "bytes": len(candidate), "crlf": candidate.count(b"\r\n"), "lone_lf": 0},
    "patch": {"path": str(HERE / "candidate-app091.patch"), "sha256": digest(patch.encode()), "bytes": len(patch.encode())},
    "exact_byte_inverse": True,
    "exact_whole_ast_inverse": True,
    "changed_MainWindow_methods": changed_methods,
    "unchanged_calculate_AST": True,
    "unchanged_update_operator_AST": True,
    "continuous_default_setter_count_old_new": [1, 1],
    "continuous_native_bool_serialization_count_old_new": [1, 1],
    "changes": receipts,
    "signal_claim": "Connection text matches existing OPTIONS bool pattern; setter precedes new connection in source. No actual Qt emission, initialization, calculation-count, rendering, or exception behavior has been observed.",
    "old_test_contract_migration": "scripts/verify_damage_ui.py:39 Attack-only predicate is migrated below to Attack/Natural at the actually selected rank. Existing implemented-owner iteration, all other assertions, and runner body remain byte-exact.",
    "new_calls": {"project_api": 0, "helper": 0, "formatter": 0, "constructor": 0, "Qt": 0, "Wine": 0, "tests": 0},
    "formal_dependency": "Root full90 actual2cbc/tag is bound; independent formal review, root integration/checks and actual MainWindow acceptance remain pending",
})

runner_base = HERE / "baseline/scripts/verify_damage_ui.py"
runner_old = runner_base.read_bytes()
assert digest(runner_old) == "3b8ff41400002ff8616cb99690e47dcea9793b32bcdaa3ceb2bea20150fa396b"
runner_before = "app_module.catalog()['operators'][op]['skills'][skill-1]['levels'][-1]['sp_type']=='INCREASE_WHEN_ATTACK'".encode()
runner_after = "app_module.catalog()['operators'][op]['skills'][skill-1]['levels'][window.skill_rank_value()-1]['sp_type'] in ('INCREASE_WHEN_ATTACK','INCREASE_WITH_TIME')".encode()
assert runner_old.count(runner_before) == 1
runner_new = runner_old.replace(runner_before, runner_after, 1)
assert runner_new.replace(runner_after, runner_before, 1) == runner_old
assert runner_new.count(b"\r\n") == 0
ast.parse(runner_new.decode(), filename="candidate-verify-damage-ui.py")
runner_dest = HERE / "candidate/scripts/verify_damage_ui.py"
runner_dest.parent.mkdir(parents=True, exist_ok=True)
runner_dest.write_bytes(runner_new)
runner_patch = "".join(difflib.unified_diff(runner_old.decode().splitlines(keepends=True), runner_new.decode().splitlines(keepends=True),
                                           fromfile="a/scripts/verify_damage_ui.py", tofile="b/scripts/verify_damage_ui.py"))
(HERE / "candidate-ui091.patch").write_bytes((patch + runner_patch).encode())
put_json("static-runner-contract-migration091.json", {
    "status": "SOURCE_ONLY_SINGLE_ASSERTION_CONTRACT_MIGRATION_PASS_NOT_RUNNER_RUNTIME",
    "baseline": {"path": str(runner_base), "sha256": digest(runner_old), "bytes": len(runner_old)},
    "candidate": {"path": str(runner_dest), "sha256": digest(runner_new), "bytes": len(runner_new), "LF_only": True},
    "before_expression": runner_before.decode(), "after_expression": runner_after.decode(),
    "single_expression_byte_inverse": True, "AST_parse": "PASS",
    "existing_implemented_owner_filter_unchanged": True,
    "all_other_runner_bytes_unchanged": True,
    "qualified_rank_source": "app.update_skill_options reads current selected skill level using skill_rank_value()-1. catalog.operator_profiles overlays implemented catalog profiles; runner already skips unimplemented owner. Expected SP type now uses the same selected rank rather than the former final-rank fixture assumption.",
    "old_Attack_only_assertion_failure_classification": "Expected contract migration, no product failure was run or observed",
    "no_mirror_text_test_added": True,
    "calls": {"project_api": 0, "helper": 0, "Qt": 0, "Wine": 0, "tests": 0},
    "root_sole_actual_MainWindow_acceptance": True,
})
print(json.dumps({"status": "EXTERNAL_CANDIDATE_BYTE_AST_PASS", "candidate_sha256": digest(candidate),
                  "runner_sha256": digest(runner_new), "combined_patch_sha256": digest((patch + runner_patch).encode()), "calls": 0}))
