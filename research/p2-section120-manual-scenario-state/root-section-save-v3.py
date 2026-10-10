"""Root-only archive/checkpoint preparation; Git publication is separate."""
import argparse
import datetime
import hashlib
import json
import pathlib
import shutil
import subprocess


def digest(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec")
    args = parser.parse_args()
    spec_path = pathlib.Path(args.spec).resolve()
    spec = json.loads(spec_path.read_text())
    repo = pathlib.Path("/workspace/rougezhushou")
    n = spec["section"]
    guard = json.loads(pathlib.Path(spec["source_guard"]).read_text())
    expected = guard["source_sha256"]
    assert guard["section"] == n
    for relative, sha in expected.items():
        assert digest(repo / relative)["sha256"] == sha, relative
    for relative, sha in guard.get("source_additional_sha256", {}).items():
        assert digest(repo / relative)["sha256"] == sha, relative
    for check in spec["exit_files"]:
        assert pathlib.Path(check).read_text().strip() == "0", check
    for path in spec["pass_receipts"]:
        receipt = json.loads(pathlib.Path(path).read_text())
        assert receipt["passed"] is True and receipt["workflow_complete"] is True, path
        assert receipt.get("source_drift", []) == [], path
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    archive = repo / spec["archive"]
    archive.mkdir(parents=True, exist_ok=False)
    rows = []
    # Only caller-listed public evidence; no runtime directories are inferred.
    entries = list(spec["public_evidence"])
    entries.extend([
        {"source": str(spec_path), "destination": "root-save-spec.json"},
        {"source": str(pathlib.Path(__file__).resolve()), "destination": "root-section-save-v3.py"},
    ])
    for entry in entries:
        src = pathlib.Path(entry["source"]).resolve()
        dst = pathlib.Path(entry["destination"])
        assert not dst.is_absolute() and ".." not in dst.parts
        files = sorted(p for p in src.rglob("*") if p.is_file()) if src.is_dir() else [src]
        for leaf in files:
            assert not leaf.is_symlink()
            assert all(part not in (".local", ".venv", ".git", "__pycache__") for part in leaf.parts)
            relative = dst / leaf.relative_to(src) if src.is_dir() else dst
            target = archive / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            assert not target.exists(), relative
            original = digest(leaf)
            shutil.copyfile(leaf, target)
            copied = digest(target)
            assert original == copied, relative
            rows.append({"path": relative.as_posix(), "original": str(leaf), **copied})
    manifest = {"kind": "ROOT_ACTUAL_PUBLIC_ARCHIVE_BYTE_VERIFIED", "section": n,
                "prepared_at_Beijing": stamp, "root_prior_HEAD": head,
                "files": rows, "file_count": len(rows),
                "total_bytes": sum(row["bytes"] for row in rows),
                "native_windows_verified": False, "private_state_included": False}
    (archive / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (archive / "README.md").write_text(spec["archive_readme"] + "\n")
    section = {**spec["section_receipt"], "section": n, "branch": "codex/p2-development",
               "validated_at_Beijing": stamp, "root_prior_commit": head,
               "passed": True, "workflow_complete": True,
               "research_archive": spec["archive"], "maintained_source_files": len(expected),
               "source_after_checks_unchanged": True,
               "commit_status": "VALIDATED_ARCHIVED_READY_FOR_REAL_COMMIT_PUSH",
               "commit_policy": "Every completed section commit and push; every five sections full validation and summary",
               "native_windows_verified": False, "game_chat_executed": False,
               "complete_repository_validation": False}
    (repo / "verification/sections" / f"{n:03d}.json").write_text(json.dumps(section, ensure_ascii=False, indent=2) + "\n")
    cp_path = repo / "DEVELOPMENT_CHECKPOINT.json"
    cp = json.loads(cp_path.read_text())
    assert cp["completed_sections"] == n - 1
    cp["completed_sections"] = n
    cp["next_section"] = n + 1
    cp["next_action"] = spec["next_action"]
    cp["full_validation_due"] = (n % cp["policy"]["full_validation_interval"] == 0)
    cp["pending_batch_sections"] = []
    cp["sections"].append({"number": n, "topic": spec["topic"],
                           "verification": f"verification/sections/{n:03d}.json",
                           "commit_status": "VALIDATED_READY_FOR_PER_SECTION_SAVE"})
    cp["current_section_save"] = {"section": n, "prepared_at_Beijing": stamp,
                                  "status": "READY_FOR_REAL_COMMIT_AND_PUSH",
                                  "prior_actual_HEAD": head,
                                  "archive_manifest": spec["archive"] + "/manifest.json",
                                  "full_validation_due": cp["full_validation_due"]}
    if spec.get("previous_publication"):
        proof_path = pathlib.Path(spec["previous_publication"])
        proof = json.loads(proof_path.read_text())
        assert proof["local_HEAD"] == head == proof["remote_HEAD"]
        assert proof["push_primary_exit"] == 0 and proof["clean"] is True
        cp["last_verified_cloud_save"] = {"section": n - 1, "commit": head,
                                          "remote": "origin codex/p2-development",
                                          "proof": spec["archive"] + "/prior-publication.json"}
    cp_path.write_text(json.dumps(cp, ensure_ascii=False, indent=2) + "\n")
    for name, paragraph in (("PROJECT_COMPLETED.md", spec["completed_paragraph"]),
                            ("WORK_IN_PROGRESS.md", spec["work_paragraph"])):
        p = repo / name
        p.write_text(f"## 当前连续开发进度 · 第{n}节\n\n{stamp}（北京时间）。{paragraph}\n\n以下记录为历史断点，当前以上述安排为准。\n\n---\n\n" + p.read_text())
    for relative, sha in expected.items():
        assert digest(repo / relative)["sha256"] == sha, relative
    for relative, sha in guard.get("source_additional_sha256", {}).items():
        assert digest(repo / relative)["sha256"] == sha, relative
    print(json.dumps({"section": n, "archive_files": len(rows),
                      "archive_bytes": manifest["total_bytes"],
                      "root_prior_HEAD": head, "source_files": len(expected),
                      "status": "ARCHIVED_CHECKPOINT_READY_NOT_YET_COMMITTED"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
