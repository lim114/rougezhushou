"""One original pure unittest only; no Qt app, game, chat or private runtime use."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODULE = "tests.test_enemy_sp_inheritance_reference"
SELECTOR = MODULE + ".EnemySpInheritanceReferenceTests.test_invalid_source_level_reaches_preview_text_and_mechanism_source_query"
TARGET = "tests/test_enemy_sp_inheritance_reference.py"
ORIGINAL_SHA = "3523d3c99033412fd130994f9ab12e9e35faf663ed18eea35037a661cedda550"
FREEZE = "verification/full-290/source-freeze-repair.json"
FREEZE_SHA = "75cec266144a389b93aced04d150c4cf6e72a23403f250a9caab9915543e6ec0"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def worker(temporary):
    sys.path.insert(0, str(ROOT))
    safety = []
    private_paths = (ROOT / ".local", ROOT / "local-settings.json")

    def audit(event, args):
        if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            if any(path == item or path.is_relative_to(item) for item in private_paths):
                safety.append({"event": "original_private_open_blocked", "name": path.name})
                raise RuntimeError("Single pure-case runner forbids original private state")
        if event in ("socket.connect", "subprocess.Popen"):
            safety.append({"event": event + "_blocked"})
            raise RuntimeError("Single pure-case runner forbids network and subprocesses")
        if event == "import" and args and args[0] in (
            "rouge.app", "rouge.capture", "rouge.desktop_backend", "PySide6.QtWidgets"
        ):
            safety.append({"event": "GUI_game_chat_import_blocked", "name": args[0]})
            raise RuntimeError("This target must remain a pure public-data test")

    sys.addaudithook(audit)
    result = None
    error = None
    ids = []
    try:
        suite = unittest.defaultTestLoader.loadTestsFromName(SELECTOR)
        for sub in suite:
            if isinstance(sub, unittest.TestSuite):
                ids.extend(test.id() for test in sub)
            else:
                ids.append(sub.id())
        if ids != [SELECTOR] or suite.countTestCases() != 1:
            raise AssertionError("The exact original selector must load exactly one case")
        result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    except BaseException as exc:
        error = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
        traceback.print_exc(file=sys.stderr)
    record = {
        "kind": "SINGLE_ORIGINAL_PURE_CASE_ACTUAL_RESULT",
        "selector": SELECTOR,
        "loaded_test_ids": ids,
        "tests_run": None if result is None else result.testsRun,
        "failures": [] if result is None else [{"test": test.id(), "traceback": trace} for test, trace in result.failures],
        "errors": [] if result is None else [{"test": test.id(), "traceback": trace} for test, trace in result.errors],
        "skipped": [] if result is None else [{"test": test.id(), "reason": reason} for test, reason in result.skipped],
        "successful": bool(result and result.wasSuccessful() and not error and not safety),
        "exception": error,
        "safety_events": safety,
        "temporary_root": temporary,
        "qpa_environment": os.environ.get("QT_QPA_PLATFORM"),
        "qt_widgets_module_loaded": "PySide6.QtWidgets" in sys.modules,
        "game_sampling_calls": 0,
        "chat_requests": 0,
        "original_private_state_opened": False,
    }
    save(HERE / "worker-result.json", record)
    print(json.dumps({key: record[key] for key in ("selector", "tests_run", "successful", "safety_events", "exception")}, ensure_ascii=False))
    return 0 if record["successful"] else 1


def controller():
    if (HERE / "process.json").exists():
        raise FileExistsError("Do not overwrite the first real reproduction")
    target = ROOT / TARGET
    assert sha(target) == ORIGINAL_SHA, "Original test bytes changed; refusing reproduction"
    assert sha(ROOT / FREEZE) == FREEZE_SHA, "Expected same75 freeze changed"
    with (HERE / "originaltest.py").open("xb") as stream:
        stream.write(target.read_bytes())
    old = json.loads((ROOT / "verification/sections/290-necessary-repair/process.json").read_text(encoding="utf-8-sig"))
    names = sorted(set(old["source_sha256_before"]) | {TARGET})
    # Explicit module-to-path mapping avoids using the method name as a filename.
    assert TARGET == MODULE.replace(".", "/") + ".py"
    frozen = json.loads((ROOT / FREEZE).read_text(encoding="utf-8-sig"))
    expected = {**frozen["source_sha256"], **frozen["supplemental_public_inputs_sha256"]}
    before = {name: sha(ROOT / name) for name in names}
    mismatches = [name for name in names if expected.get(name) != before[name]]
    assert not mismatches, "Relevant sources differ from same75 freeze: " + str(mismatches)
    commit_before = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    started = datetime.now(timezone.utc).isoformat()
    timed_out = False
    with tempfile.TemporaryDirectory(prefix="rouge-290-single-original-display-") as directory:
        temporary = Path(directory)
        for child in ("appdata", "localappdata", "home"):
            (temporary / child).mkdir()
        env = dict(os.environ, QT_QPA_PLATFORM="offscreen", PYTHONDONTWRITEBYTECODE="1",
                   PYTHONPATH=str(ROOT), APPDATA=str(temporary / "appdata"),
                   LOCALAPPDATA=str(temporary / "localappdata"), HOME=str(temporary / "home"),
                   USERPROFILE=str(temporary / "home"))
        argv = [sys.executable, "-B", "-X", "utf8", str(Path(__file__).resolve()), "--worker", str(temporary)]
        with (HERE / "stdout.txt").open("xb") as stdout, (HERE / "stderr.txt").open("xb") as stderr:
            try:
                process = subprocess.run(argv, cwd=temporary, env=env, stdout=stdout, stderr=stderr, timeout=90)
                code = process.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                code = None
    after = {name: sha(ROOT / name) for name in names}
    child = json.loads((HERE / "worker-result.json").read_text(encoding="utf-8")) if (HERE / "worker-result.json").exists() else None
    report = {
        "kind": "necessary_change_related_tests_not_full_suite",
        "scope": "One original pure public-data test reproduction; not full suite, native UI or candidate validation.",
        "argv": argv,
        "modules": [MODULE],
        "selectors": [SELECTOR],
        "source_path_by_module": {MODULE: TARGET},
        "source_commit_before": commit_before,
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "exit_code": code,
        "timed_out": timed_out,
        "source_sha256_before": before,
        "source_sha256_after": after,
        "source_unchanged": before == after,
        "freeze_path": FREEZE,
        "freeze_sha256": FREEZE_SHA,
        "freeze_unchanged": sha(ROOT / FREEZE) == FREEZE_SHA,
        "relevant_source_map_matches_same75_freeze": not mismatches,
        "exact_original_test_sha256": ORIGINAL_SHA,
        "actual_tests_run": None if child is None else child["tests_run"],
        "actual_failures": None if child is None else child["failures"],
        "actual_errors": None if child is None else child["errors"],
        "safety_events": None if child is None else child["safety_events"],
        "worker_exception": None if child is None else child["exception"],
        "runner_sha256": sha(Path(__file__)),
        "originaltest_sha256": sha(HERE / "originaltest.py"),
        "stdout_sha256": sha(HERE / "stdout.txt"),
        "stderr_sha256": sha(HERE / "stderr.txt"),
        "game_sampling_verified": False,
        "chat_verified": False,
        "full_scope_reduced": False,
        "full_suite_rerun": False,
        "candidate_or_live_code_modified": False,
        "native_GUI_started": False,
        "original_private_state_opened": False,
    }
    save(HERE / "process.json", report)
    print(json.dumps({key: report[key] for key in ("exit_code", "source_unchanged", "actual_tests_run", "relevant_source_map_matches_same75_freeze", "freeze_unchanged", "safety_events")}, ensure_ascii=False))
    return 97 if not report["source_unchanged"] else (124 if timed_out else code)


if __name__ == "__main__":
    raise SystemExit(worker(sys.argv[2]) if sys.argv[1:] and sys.argv[1] == "--worker" else controller())
