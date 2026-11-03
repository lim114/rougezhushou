"""Exclusive, byte-preserving copy of four explicitly approved public evidence roots.

This script imports no project module and runs no product/test/window code.
Existing archive paths are never overwritten. Per-file hashes are checked before,
during and after copying. Source receipts retain their original bytes and claims.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "verification/sections/290-preparation/supplementary-public-evidence"
EXCLUDED_PARTS = {"__pycache__"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def digest(raw: bytes) -> dict:
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json_new(path: Path, payload: dict) -> None:
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with path.open("xb") as handle:
        handle.write(raw)


def inside(path: Path, parent: Path) -> Path:
    resolved = path.resolve(strict=True)
    resolved.relative_to(parent.resolve(strict=True))
    if path.is_symlink():
        raise ValueError(f"Symlink not permitted: {path}")
    return resolved


def inventory(source: Path, *, selected: tuple[str, ...] | None = None) -> dict[str, dict]:
    inside(source, ROOT / ".cache")
    candidates = []
    if selected is None:
        candidates = list(source.rglob("*"))
    else:
        for name in selected:
            selected_path = source / name
            if not selected_path.exists():
                raise FileNotFoundError(selected_path)
            candidates.extend(selected_path.rglob("*") if selected_path.is_dir() else [selected_path])
    result = {}
    for path in sorted(candidates):
        if not path.is_file():
            continue
        rel = path.relative_to(source)
        if EXCLUDED_PARTS.intersection(rel.parts) or path.suffix in EXCLUDED_SUFFIXES:
            continue
        inside(path, source)
        # Do not silently absorb a new clone, runtime state, or unrelated payload.
        if {".git", ".venv", "node_modules", "private", "runtime-state"}.intersection(rel.parts):
            raise ValueError(f"Unexpected non-public or dependency tree: {rel}")
        raw = path.read_bytes()
        result[rel.as_posix()] = digest(raw)
    if not result:
        raise ValueError(f"Empty evidence root: {source}")
    return result


def require_pins(source: Path, declared: dict, *, prefix: str = "") -> int:
    checked = 0
    for name, pin in declared.items():
        path = source / prefix / name
        inside(path, source)
        actual = digest(path.read_bytes())
        if actual["sha256"] != pin["sha256"] or (
            "bytes" in pin and actual["bytes"] != pin["bytes"]
        ):
            raise AssertionError(f"Original receipt pin mismatch: {path}")
        checked += 1
    return checked


def receipt_preflight() -> list[dict]:
    checks = []
    author = ROOT / ".cache/p3-290-author"
    receipt = read_json(author / "first-real-necessary/receipt.json")
    count = require_pins(author / "first-real-necessary", receipt["source_before"], prefix="source")
    checks.append({"kind": "author-first-source-pins", "files_checked": count})

    diagnostic = ROOT / ".cache/p3-full290-diagnostic"
    count = require_pins(diagnostic, read_json(diagnostic / "diagnostic-originals.json")["files"])
    checks.append({"kind": "diagnostic-original-pins", "files_checked": count})

    migration = ROOT / ".cache/p3-full290-presentation-migration"
    for attempt in (migration, migration / "attempt2"):
        controller = read_json(attempt / "first-controller.json")
        expected = {
            "run_bounded.py": {"sha256": controller["source_sha256"]},
            "verify_migration.py": {"sha256": controller["worker_source_sha256"]},
        }
        count = require_pins(attempt, expected)
        checks.append({"kind": "migration-executed-worker-pins", "attempt": attempt.relative_to(migration).as_posix(), "files_checked": count})
    ready = read_json(migration / "READY.json")
    count = require_pins(migration / "attempt2/after", {
        name: {"sha256": sha} for name, sha in ready["live_test_files_sha256"].items()
    })
    expected = {
        ready["first_controller_preflight_failure_retained"]["classification_file"]: {
            "sha256": ready["first_controller_preflight_failure_retained"]["classification_sha256"]
        },
        ready["actual_first_module_execution_receipt"]: {"sha256": ready["actual_first_module_execution_receipt_sha256"]},
        ready["AST_delta_file"]: {"sha256": ready["AST_delta_sha256"]},
        "attempt2/first-unittest.log": {"sha256": ready["unittest_log_sha256"]},
        "attempt2/root-maintained-runner.py": {"sha256": ready["root_runner_sha256"]},
    }
    count += require_pins(migration, expected)
    checks.append({"kind": "migration-ready-original-pins", "files_checked": count})

    query = ROOT / ".cache/p3-full290-query-opt"
    count = require_pins(query, read_json(query / "READY_HANDOFF.json")["files"])
    checks.append({"kind": "query-handoff-original-pins", "files_checked": count})
    return checks


GROUPS = (
    {
        "name": "author-first-module",
        "source": ".cache/p3-290-author",
        "selected": ("first-real-necessary", "IMPLEMENTATION_HANDOFF.json"),
        "classification": "First actual isolated new-module test run, not Windows or full-section acceptance.",
        "limits": ["Only explicitly approved first-real directory and handoff copied.", "No new tests executed during archiving."],
    },
    {
        "name": "diagnostic",
        "source": ".cache/p3-full290-diagnostic",
        "classification": "Exact offscreen search/diagnostic originals, including five actual presentation assertion failures; not full validation.",
        "limits": ["Loader search did not execute tests.", "Progress-marker positions are search clues; do not identify original A1 failures.", "Independent A1/A2 full/tool archives are not included."],
    },
    {
        "name": "presentation-migration",
        "source": ".cache/p3-full290-presentation-migration",
        "classification": "Original preflight contract mismatch (exit 1; zero tests), followed by separate 69-method offscreen display-contract validation.",
        "limits": ["First failure and attempt2 are preserved separately.", "Offscreen module checks are not native Windows or full acceptance.", "Review of changed assertions remains separate from archival integrity."],
    },
    {
        "name": "query-optimization",
        "source": ".cache/p3-full290-query-opt",
        "classification": "First reviewer SyntaxError before model execution and corrected public query equivalence/profile process; maintenance only.",
        "limits": ["38 events / 190 scenes / three contexts, 570 queries per module, plus 27 invalid inputs.", "Small-sample timing does not establish an A1 timeout cause, full-suite speed, OCR speed or sampling speed.", "Pending separate independent query review is not included."],
    },
)


def main() -> None:
    if DEST.exists():
        raise FileExistsError(f"Archive must be new; refusing overwrite: {DEST}")
    checks = receipt_preflight()
    # Freeze approved inventories before creating any archive output.
    snapshots = {}
    for group in GROUPS:
        snapshots[group["name"]] = inventory(ROOT / group["source"], selected=group.get("selected"))
    DEST.parent.resolve(strict=True)
    DEST.mkdir(exist_ok=False)
    group_summaries = []
    for group in GROUPS:
        source = ROOT / group["source"]
        target = DEST / group["name"]
        target.mkdir(exist_ok=False)
        before = snapshots[group["name"]]
        for name, expected in before.items():
            source_file = source / name
            inside(source_file, source)
            raw = source_file.read_bytes()
            if digest(raw) != expected:
                raise AssertionError(f"Original changed before copy: {source_file}")
            output = target / name
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("xb") as handle:
                handle.write(raw)
            if digest(output.read_bytes()) != expected:
                raise AssertionError(f"Copy mismatch: {output}")
        after = inventory(source, selected=group.get("selected"))
        if before != after:
            raise AssertionError(f"Source inventory changed during copy: {source}")
        manifest = {
            "kind": "PUBLIC_EVIDENCE_COPY_NOT_PRODUCT_ACCEPTANCE",
            "source_root": group["source"],
            "classification": group["classification"],
            "limits": group["limits"],
            "files": before,
            "file_count": len(before),
            "total_bytes": sum(pin["bytes"] for pin in before.values()),
            "source_unchanged_during_copy": True,
            "every_output_matches_original_bytes": True,
            "excluded": ["__pycache__", "*.pyc", "*.pyo"],
            "native_or_full_or_section_completion_claimed": False,
        }
        manifest_path = target / "ARCHIVE_MANIFEST.json"
        write_json_new(manifest_path, manifest)
        group_summaries.append({"group": group["name"], "manifest": manifest_path.relative_to(DEST).as_posix(), **digest(manifest_path.read_bytes()), "source_file_count": len(before), "source_bytes": manifest["total_bytes"]})

    # Recheck original declarations after all groups, not merely the first copy.
    after_checks = receipt_preflight()
    if after_checks != checks:
        raise AssertionError("Receipt verification set changed during archiving")
    script_path = DEST / "archive_public_evidence.py"
    raw_script = Path(__file__).read_bytes()
    with script_path.open("xb") as handle:
        handle.write(raw_script)
    summary = {
        "kind": "SECTION_290_SUPPLEMENTARY_PUBLIC_ARCHIVE_ONLY",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "archive_root": DEST.relative_to(ROOT).as_posix(),
        "groups": group_summaries,
        "copied_source_file_count": sum(row["source_file_count"] for row in group_summaries),
        "copied_source_bytes": sum(row["source_bytes"] for row in group_summaries),
        "receipt_pin_preflight_and_postflight": checks,
        "archive_script": {"path": script_path.name, **digest(raw_script)},
        "existing_archives_overwritten": False,
        "original_sources_modified": False,
        "project_code_imported": False,
        "new_tests_or_gui_or_full_run": False,
        "game_or_chat_or_private_operations": False,
        "section_290_completed_or_published_claimed": False,
        "separate_independent_query_review_copied": False,
        "full_A1_A2_tool_archives_copied": False,
    }
    write_json_new(DEST / "SUMMARY.json", summary)
    print(json.dumps({"status": "ARCHIVED_BYTE_VERIFIED_NOT_SECTION_COMPLETE", "root": summary["archive_root"], "groups": group_summaries, "source_files": summary["copied_source_file_count"], "source_bytes": summary["copied_source_bytes"], "summary": digest((DEST / "SUMMARY.json").read_bytes())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
