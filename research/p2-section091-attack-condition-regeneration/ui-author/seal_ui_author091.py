"""Seal only external source bytes and packaging metadata; zero project execution."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path("/workspace/rougezhushou")
ACTUAL = "2cbc45f03f99ed4f04b9c7e2612b58542f909168"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def put(name, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def row(path, source_path=None):
    raw = path.read_bytes()
    return {"source_path": str(source_path or path), "archive_path": path.relative_to(HERE).as_posix(),
            "bytes": len(raw), "sha256": sha(raw)}


assert subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, check=True, text=True, stdout=subprocess.PIPE).stdout.strip() == ACTUAL
assert subprocess.run(["git", "rev-parse", "p2-validation-090"], cwd=REPO, check=True, text=True, stdout=subprocess.PIPE).stdout.strip() == ACTUAL
assert not subprocess.run(["git", "status", "--short"], cwd=REPO, check=True, text=True, stdout=subprocess.PIPE).stdout
binding = json.loads((HERE / "actual-root-source-binding091.json").read_text())
for item in binding["sources"]:
    actual = subprocess.run(["git", "show", f"{ACTUAL}:{Path(item['source_path']).relative_to(REPO).as_posix()}"],
                            cwd=REPO, check=True, stdout=subprocess.PIPE).stdout
    assert sha(actual) == item["sha256"] and len(actual) == item["bytes"]
    assert Path(item["archive_path"]).read_bytes() == actual == Path(item["source_path"]).read_bytes()

historical = [
    ("historical-source34", Path("/workspace/.continuation/p2-continuous-attack-control-visibility091-source/manifest-source091.json"),
     "e085ece169ef52cfd97a4f656bd1cf370bdc29ae78abd13e7e14962e01435c78", 34),
    ("historical-design8", Path("/workspace/.continuation/p2-continuous-attack-control-visibility091-design/manifest-design091.json"),
     "9b7b26b1d281db116fe0b7a6768b00baa10ad2585f0e9acdc6ca215adc9fe45d", 8),
]
provenance = {}
dependencies = []
for prefix, manifest_path, expected_sha, expected_count in historical:
    raw = manifest_path.read_bytes()
    assert sha(raw) == expected_sha
    manifest = json.loads(raw)
    assert manifest["file_count"] == expected_count == len(manifest["files"])
    copied = []
    for item in manifest["files"]:
        source = Path(item["source_path"])
        content = source.read_bytes()
        assert len(content) == item["bytes"] and sha(content) == item["sha256"]
        destination = HERE / prefix / item["archive_path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        assert destination.read_bytes() == content
        provenance[destination.relative_to(HERE).as_posix()] = source
        copied.append(row(destination, source))
    copied_manifest = HERE / prefix / manifest_path.name
    shutil.copyfile(manifest_path, copied_manifest)
    provenance[copied_manifest.relative_to(HERE).as_posix()] = manifest_path
    dependencies.append({"kind": "HISTORICAL_IMMUTABLE_PACKET_NOT_NEW_RUN", "original_manifest": str(manifest_path),
                         "original_manifest_sha256": expected_sha, "original_files": len(copied),
                         "original_bytes": sum(r["bytes"] for r in copied), "copied_manifest": str(copied_manifest),
                         "each_copy_bytes_hash_verified": True,
                         "source_calls_rerun": False, "old_design_no_toggle_scope_superseded_not_rewritten": prefix == "historical-design8"})
put("historical-packet-transport091.json", {"format_version": 1, "packets": dependencies,
                                          "new_project_API_helper_formatter_tests_Qt_Wine_calls": 0})

app = HERE / "candidate/rouge/app.py"
runner = HERE / "candidate/scripts/verify_damage_ui.py"
assert sha(app.read_bytes()) == "fa27d6eceaf88f8caf1bc4e994641c6d110884ee9fbf673ab7d46a355cc41143"
assert sha(runner.read_bytes()) == "0b0dcbcade07f0ff11b2bdcba7c7598a696ff4ece3418bc296312ce97c2a2d54"
assert app.read_bytes().count(b"\n") == app.read_bytes().count(b"\r\n")
assert b"\r\n" not in runner.read_bytes()
freeze_names = ["candidate/rouge/app.py", "candidate/scripts/verify_damage_ui.py", "candidate-ui091.patch",
                "actual-root-source-binding091.json", "static-candidate-proof091.json", "static-runner-contract-migration091.json",
                "GROUPED-DESIGN091.md", "focused-MainWindow-plan091.json", "problem-evidence091.json"]
freeze = {"format_version": 1, "status": "FINAL_FROZEN_UI_AUTHOR_SOURCE_ONLY_STOPWRITE_PENDING_FORMAL_ROOT_WINDOW",
          "actual_full90_commit": ACTUAL, "actual_full90_tag": "p2-validation-090",
          "source_files": binding["sources"], "frozen_items": [row(HERE / name) for name in freeze_names],
          "unchanged_backend_and_calculate_AST": True, "CRLF_app_LF_existing_runner_preserved": True,
          "new_test_module": None, "registry_change": None,
          "author_calls": {"API": 0, "helper": 0, "formatter": 0, "constructor": 0, "tests": 0, "Qt": 0, "Wine": 0},
          "only_verification": "One external stdlib byte/AST preparation plus external sealing metadata checks; no project import/execution",
          "sole_formal_reviewer": "/root/source_080_resume", "actual_window_owner": "/root",
          "pending": ["independent source-only formal", "root sole tracked integration/source checks", "root meaningful focused actual MainWindow behavior acceptance", "root grouped91 archive/commit"],
          "historical_dependencies": dependencies,
          "shared_deepcolor": "Separate author source23/finalengine-reporting packet; no overlap with UI two targets"}
put("ui-review-freeze091.json", freeze)
freeze_raw = (HERE / "ui-review-freeze091.json").read_bytes()
put("ui-author-handoff091.json", {
    "format_version": 1, "status": "EXPLICIT_FINAL_FROZEN_UI_AUTHOR_STOPWRITE_PENDING_SOLE_FORMAL_ROOT_INTEGRATION_WINDOW",
    "directory": str(HERE), "actual_base_commit": ACTUAL, "actual_base_tag": "p2-validation-090",
    "freeze": {"path": str(HERE / "ui-review-freeze091.json"), "sha256": sha(freeze_raw), "bytes": len(freeze_raw)},
    "app": row(app), "existing_runner": row(runner), "combined_patch": row(HERE / "candidate-ui091.patch"),
    "public_manifest": str(HERE / "ui-author-public-manifest091.json"),
    "design": str(HERE / "GROUPED-DESIGN091.md"), "focused_window_plan": str(HERE / "focused-MainWindow-plan091.json"),
    "problem_evidence": str(HERE / "problem-evidence091.json"),
    "source_checked": "Actual2cbc Git object + current target bytes + all external original packet transport hashes; app3 blocks / existing runner1 expression inverse and AST source parse passed",
    "runtime_test_saved": "NONE; meaningful root actual MainWindow behavior validation remains pending, not static-approved runtime",
    "author_calls": {"API": 0, "helper": 0, "formatter": 0, "constructor": 0, "tests": 0, "Qt": 0, "Wine": 0},
    "failures": {"source_preparation_failures": 0, "product_failures_observed": 0, "old_Attack_assertion_failure_run": False},
    "source_baseline_old_hashes": {"rouge/app.py": "6a107fa37d2c21b9160131aa8c901fc2342ef7a422c3134dc0579ea24f4b56a2",
                                  "scripts/verify_damage_ui.py": "3b8ff41400002ff8616cb99690e47dcea9793b32bcdaa3ceb2bea20150fa396b"},
    "sole_formal_reviewer": "/root/source_080_resume", "root_sole_tracked_apply_stage_commit": True,
    "formal_scope": "Only app/scripts source/qualification/bool/default/hidden values/signal pattern/label-tooltip/one assertion inverse; no new API/tests/Qt/Wine, no duplicate old source probes",
    "shared_grouped_section91": "Deepcolor engine/reporting separate author/formal. Root merges both scopes and performs one grouped acceptance/archive.",
    "unknowns": ["Native target acquisition/SP release/attachment/full clocks", "Received/event remains reference_only", "Actual Qt initialization/emissions/automatic calls/rendering not observed by author"],
    "historical_dependencies_copied_unchanged": dependencies,
    "original_source34_design8_full90_not_modified": True,
})

files = []
for path in sorted(HERE.rglob("*")):
    if path.is_file() and path.name != "ui-author-public-manifest091.json":
        files.append(row(path, provenance.get(path.relative_to(HERE).as_posix())))
manifest = {"format_version": 1, "status": "EXPLICIT_FINAL_UI_AUTHOR_FROZEN_SOURCE_ONLY_PENDING_FORMAL_ROOT_WINDOW",
            "scope": "Section91 grouped continuous-attack UI author app/scripts plus immutable source34/design8 copies, not Deepcolor formal/results",
            "files": files, "file_count": len(files), "total_bytes": sum(r["bytes"] for r in files),
            "manifest_itself_not_in_files": True, "author_new_API_helper_formatter_ctor_tests_Qt_Wine_calls": 0,
            "root_tracked_changed": False, "stopwrite": True}
put("ui-author-public-manifest091.json", manifest)
for item in files:
    raw = (HERE / item["archive_path"]).read_bytes()
    assert len(raw) == item["bytes"] and sha(raw) == item["sha256"]
print(json.dumps({"status": "EXPLICIT_FINAL_STOPWRITE", "file_count": manifest["file_count"], "total_bytes": manifest["total_bytes"],
                  "manifest_sha256": sha((HERE / "ui-author-public-manifest091.json").read_bytes()),
                  "handoff_sha256": sha((HERE / "ui-author-handoff091.json").read_bytes()),
                  "freeze_sha256": sha(freeze_raw), "product_app_sha256": sha(app.read_bytes()),
                  "runner_sha256": sha(runner.read_bytes()), "patch_sha256": sha((HERE / "candidate-ui091.patch").read_bytes()),
                  "new_calls": 0}, ensure_ascii=False))
