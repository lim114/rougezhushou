"""Independent real-OCR page-routing replay. Never captures or reads private state.

Stages are bounded and resumable: inventory -> baseline -> paired -> summary.
Every stage writes a new epoch directory; old failures and source seals survive.
Fake OCR, exact-frame hits and pixel-only work estimates cannot prove speedup.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import inspect
import json
import os
from pathlib import Path
import shutil
import statistics
import sys
import time

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / ".cache/research/page-routing-056"
FIELDS = ("page", "run", "operator", "map", "stage", "nodes", "node_content", "viewport")
REPRESENTATIVE_IDS = {"exploration-map", "map-template-node-detail", "module-mechanist",
                      "operator-kaltsit", "operator-mechanist", "operator-silverash",
                      "run-emergency-mechanist", "run-mechanist-selected", "run-relic-multicard",
                      "kaltsit_owned", "chen_owned", "leizi_owned", "myrtle_owned"}
# Confidence/geometry remain in the strict equality receipt. They are not facts.
EVIDENCE = {"box", "title_box", "center", "card_position", "confidence", "score",
            "description_evidence", "name_evidence", "local_ocr_calls", "elapsed_ms"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def public_sources():
    return (sorted((ROOT / "rouge").rglob("*.py")) + sorted((ROOT / "rouge/data").rglob("*.json"))
            + sorted(path for path in (ROOT / "rouge/data/page-features").rglob("*")
                     if path.is_file() and path.suffix != ".json"))


def seal_sources():
    return {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path) for path in public_sources()}


def samples():
    result = []
    for path in sorted((ROOT / "samples/native-client").glob("*.png")):
        result.append({"id": path.stem, "image": path.relative_to(ROOT).as_posix(),
                       "client_rect": None, "role": "existing_public_development_sample",
                       "independent_holdout": False})
    receipt_root = ROOT / ".cache/research/p1-live-recipient-055"
    for name, receipt_name in (
        ("kaltsit_owned", "receipt-1791126961478703800.json"),
        ("chen_owned", "receipt-1791127302045231200.json"),
        ("leizi_owned", "cached-pair-1791129741668048800-receipt.json"),
        ("myrtle_owned", "cached-pair-1791132335648665700-receipt.json"),
    ):
        receipt = read(receipt_root / receipt_name)
        frame = receipt["frames"][0] if "frames" in receipt else receipt
        image_path = ROOT / Path(frame["image"])
        assert sha(image_path) == frame["image_sha256"]
        row = {"id": name, "image": image_path.relative_to(ROOT).as_posix(),
               "client_rect": frame["client_rect"], "role": "actual_owned_popup_positive",
               "independent_holdout": False, "origin_receipt": (receipt_root / receipt_name).relative_to(ROOT).as_posix()}
        if "frames" in receipt:
            second = receipt["frames"][1]
            assert sha(ROOT / second["image"]) == second["image_sha256"]
            row["animation_image"] = Path(second["image"]).as_posix()
            row["animation_sha256"] = second["image_sha256"]
        result.append(row)
    assert len(result) == 24
    for row in result:
        image = cv2.imdecode(np.fromfile(ROOT / row["image"], np.uint8), 1)
        assert image is not None
        row.update(sha256=sha(ROOT / row["image"]), size=[image.shape[1], image.shape[0]])
    return result


def inventory():
    folder = RESEARCH / ("epoch-" + str(time.time_ns()))
    folder.mkdir(parents=True, exist_ok=False)
    before = seal_sources()
    frozen = folder / "baseline-source/rouge"
    frozen.mkdir(parents=True)
    for path in (ROOT / "rouge").rglob("*.py"):
        destination = frozen / path.relative_to(ROOT / "rouge")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    # All data is public reference content. JSON is copied; immutable images are
    # linked only to avoid needless duplication. No .local or runtime is used.
    for path in (ROOT / "rouge/data").rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        destination = frozen / "data" / path.relative_to(ROOT / "rouge/data")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".json":
            shutil.copyfile(path, destination)
        else:
            try:
                os.link(path, destination)
            except OSError:
                shutil.copyfile(path, destination)
    after = seal_sources()
    assert before == after, "source changed while creating 0.55 baseline seal"
    manifest = {"epoch": folder.name, "created_at": time.time(), "samples": samples(),
                "original_source_sha256": before, "semantic_fields": list(FIELDS),
                "all_samples_preexisting_development_material": True,
                "private_state_read": False, "game_actions": 0, "chat_requests": 0,
                "limits": ["Not an independent classifier holdout; all sources already existed.",
                           "Derived resize/translation/animation variants are not independent samples."]}
    write(folder / "inventory.json", manifest)
    print(json.dumps({"epoch": folder.name, "samples": len(manifest["samples"]),
                      "source_files": len(before)}), flush=True)


def load_reader(folder, frozen=False):
    sys.path.insert(0, str(folder / "baseline-source" if frozen else ROOT))
    from rouge.recognition import ScreenReader
    return ScreenReader


def reader_factory(cls, routed):
    parameters = inspect.signature(cls).parameters
    options = {"cache_enabled": True}
    if "page_routing_enabled" in parameters:
        options["page_routing_enabled"] = routed
    elif routed:
        raise AssertionError("ScreenReader needs page_routing_enabled=True/False for strict paired replay")
    return cls(**options)


def image_for(sample, variant="native"):
    path = sample.get("animation_image") if variant == "animation" else sample["image"]
    image = cv2.imdecode(np.fromfile(ROOT / path, np.uint8), 1)
    assert image is not None
    expected = sample.get("animation_sha256") if variant == "animation" else sample["sha256"]
    assert sha(ROOT / path) == expected
    rect = deepcopy(sample["client_rect"])
    if variant == "scaled_translated":
        factor = .83
        height, width = image.shape[:2]
        new_width, new_height = round(width * factor), round(height * factor)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        image = cv2.copyMakeBorder(image, 31, 17, 43, 19, cv2.BORDER_CONSTANT, value=(170, 170, 170))
        if rect is None:
            rect = [43, 31, new_width + 43, new_height + 31]
        else:
            rect = [round(rect[0]*new_width/width)+43, round(rect[1]*new_height/height)+31,
                    round(rect[2]*new_width/width)+43, round(rect[3]*new_height/height)+31]
    return image, rect


def public_observation(result):
    # The historical reference is a JSON public payload. Apply that same wire
    # serialization to both readers: skill_ranks integer keys become strings,
    # tuples become arrays, with no fact/score/coordinate rounding or deletion.
    return json.loads(json.dumps({key: result.get(key) for key in FIELDS}, ensure_ascii=False))


def strict_semantics(value):
    """Exclude only an embedded diagnostic timer, keeping all fact evidence."""
    if isinstance(value, dict):
        return {key: strict_semantics(item) for key, item in value.items() if key != "elapsed_ms"}
    if isinstance(value, list):
        return [strict_semantics(item) for item in value]
    return value


def strict_differences(expected, actual, path="", limit=80):
    if expected == actual:
        return []
    rows = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        for key in sorted(set(expected) | set(actual)):
            rows += strict_differences(expected.get(key), actual.get(key), path+"/"+str(key), limit-len(rows))
            if len(rows) >= limit:
                break
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            rows.append({"path": path+"/length", "baseline": len(expected), "routed": len(actual)})
        for i, (old, new) in enumerate(zip(expected, actual)):
            rows += strict_differences(old, new, path+"/"+str(i), limit-len(rows))
            if len(rows) >= limit:
                break
    elif limit > 0:
        def small(value):
            return value if not isinstance(value, (dict, list)) else str(type(value).__name__)
        rows.append({"path": path, "baseline": small(expected), "routed": small(actual)})
    return rows[:limit]


def facts(value):
    if isinstance(value, dict):
        return {key: facts(item) for key, item in value.items() if key not in EVIDENCE}
    if isinstance(value, list):
        return [facts(item) for item in value]
    return value


def retained(expected, actual, path=""):
    """Every observed baseline fact must survive. Unknowns may become known."""
    if expected is None:
        return []
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [path]
        result = []
        for key, value in expected.items():
            result.extend(retained(value, actual.get(key), path + "/" + str(key)))
        return result
    if isinstance(expected, list):
        if not isinstance(actual, list):
            return [path]
        # Matched elements are consumed once so multiplicity cannot disappear.
        available = list(actual)
        result = []
        for index, value in enumerate(expected):
            match = next((i for i, item in enumerate(available) if not retained(value, item)), None)
            if match is None:
                result.append(path + "/" + str(index))
            else:
                available.pop(match)
        return result
    return [] if expected == actual else [path]


def selected_samples(inventory_data, all_samples=False):
    return [sample for sample in inventory_data["samples"]
            if all_samples or sample["id"] in REPRESENTATIVE_IDS]


def baseline(folder, budget, all_samples=False):
    inventory_data = read(folder / "inventory.json")
    cls = load_reader(folder, frozen=True)
    started = time.perf_counter()
    completed = 0
    selected = selected_samples(inventory_data, all_samples)
    for sample in selected:
        target = folder / "baseline" / (sample["id"] + ".json")
        if target.exists():
            continue
        if completed and time.perf_counter() - started >= budget:
            break
        image, rect = image_for(sample)
        reader = reader_factory(cls, False)
        result = reader.read(image, client_rect=rect)
        value = {"id": sample["id"], "sha256": sample["sha256"],
                 "original_source_sha256": inventory_data["original_source_sha256"],
                 "observation": public_observation(result), "performance": result["performance"]}
        write(target, value)
        completed += 1
        print(json.dumps({"baseline": sample["id"], "page": result["page"],
                          "ms": result["performance"]["total_ms"]}), flush=True)
    present = sum((folder / "baseline" / (sample["id"] + ".json")).exists() for sample in selected)
    print(json.dumps({"baseline_complete": present == len(selected), "samples_done": present,
                      "samples_selected": len(selected),
                      "segment_seconds": time.perf_counter() - started}), flush=True)


def planned_cases(inventory_data, variants=False, all_samples=False, focus=None):
    selected = selected_samples(inventory_data, all_samples)
    base = deepcopy(next(sample for sample in inventory_data["samples"] if sample["id"] == "operator-kaltsit"))
    animated = next(sample for sample in inventory_data["samples"] if sample["id"] == "operator-kaltsit-animated")
    base.update(animation_image=animated["image"], animation_sha256=animated["sha256"],
                animation_source_id=animated["id"],
                animation_provenance="preexisting_operator_frame_pair_capture_time_order_not_verified")
    myrtle = next(sample for sample in selected if sample["id"] == "myrtle_owned")
    warm = [(base, "animation"), (myrtle, "animation")]
    if focus == "operator-animation":
        return [(base, "animation")]
    if focus == "pilot":
        return ([(sample, "native") for sample in selected if sample["id"] in
                 {"operator-kaltsit", "operator-mechanist", "operator-silverash"}]
                + warm)
    cases = [(sample, "native") for sample in selected]
    if variants:
        ids = {"operator-kaltsit", "run-mechanist-selected", "map-template-node-detail", "myrtle_owned"}
        cases += [(sample, "scaled_translated") for sample in selected if sample["id"] in ids]
        cases += warm
    return cases


def pairs(folder, budget, variants=False, all_samples=False, stop_on_first_failure=False, focus=None):
    inventory_data = read(folder / "inventory.json")
    cls = load_reader(folder)
    start_seal = seal_sources()
    verifier_sha256 = sha(__file__)
    stage = folder / ("paired-" + str(time.time_ns()))
    stage.mkdir(exist_ok=False)
    prior_rows = []
    for previous in folder.glob("paired-*/rows/*.json"):
        value = read(previous)
        if value.get("source_sha256") == start_seal and receipt_verifier_valid(folder, previous, value):
            prior_rows.append(value["case"])
    started = time.perf_counter()
    completed = 0
    selected = selected_samples(inventory_data, all_samples)
    cases = planned_cases(inventory_data, variants, all_samples, focus)
    for case_index, (sample, variant) in enumerate(cases):
        case = sample["id"] + ":" + variant
        if case in prior_rows:
            continue
        if completed and time.perf_counter() - started >= budget:
            break
        image, rect = image_for(sample, variant)
        readers = {label: reader_factory(cls, label == "routed") for label in ("baseline", "routed")}
        outputs = {}
        # Alternate first model to reduce consistent thermal/order bias.
        order = ("baseline", "routed") if case_index % 2 == 0 else ("routed", "baseline")
        for label in order:
            if variant == "animation":
                original, original_rect = image_for(sample)
                readers[label].read(original, client_rect=original_rect)
            outputs[label] = readers[label].read(image, client_rect=rect)
            assert outputs[label]["performance"]["reuse"] != "exact_frame", case
            engine = readers[label]._engine
            engine = getattr(engine, "engine", engine)
            assert type(engine).__module__.startswith("rapidocr_onnxruntime"), type(engine)
        before, after = map(public_observation, (outputs["baseline"], outputs["routed"]))
        regressions = retained(facts(before), facts(after))
        original_regressions = []
        strict_original = None
        if variant == "native":
            original = read(folder / "baseline" / (sample["id"] + ".json"))["observation"]
            original_regressions = retained(facts(original), facts(before))
            strict_original = strict_semantics(original) == strict_semantics(before)
        row = {"case": case, "sha256": sample["sha256"], "variant": variant,
               "source_sha256": start_seal, "order": list(order),
               "verifier_sha256": verifier_sha256,
               "strict_public_equal": strict_semantics(before) == strict_semantics(after),
               "strict_original_055_equal": strict_original,
               "original_055_fact_regressions": original_regressions,
               "routing_fact_regressions": regressions,
               "strict_semantic_differences": strict_differences(strict_semantics(before), strict_semantics(after)),
               "passed": strict_semantics(before) == strict_semantics(after) and (strict_original is not False),
               "observations": {"baseline": before, "routed": after},
               "performance": {label: outputs[label]["performance"] for label in outputs},
               "actual_rapidocr_engine": True, "exact_frame_excluded": True,
               "derived_case_not_independent_sample": variant != "native"}
        if variant == "animation":
            row["animation_image"] = sample["animation_image"]
            row["animation_sha256"] = sample["animation_sha256"]
            row["animation_provenance"] = sample.get("animation_provenance", "previous_real_capture_pair_ordered")
        write(stage / "rows" / (sample["id"] + "-" + variant + ".json"), row)
        completed += 1
        print(json.dumps({"case": case, "passed": row["passed"],
                          "strict_equal": row["strict_public_equal"],
                          "regressions": regressions,
                          "strict_differences": row["strict_semantic_differences"][:6],
                          "baseline_ms": outputs["baseline"]["performance"]["total_ms"],
                          "routed_ms": outputs["routed"]["performance"]["total_ms"]}), flush=True)
        if stop_on_first_failure and not row["passed"]:
            break
    end_seal = seal_sources()
    verifier_unchanged = verifier_sha256 == sha(__file__)
    write(stage / "segment.json", {"source_sha256": start_seal, "source_unchanged": start_seal == end_seal,
                                  "verifier_sha256": verifier_sha256, "verifier_unchanged": verifier_unchanged,
                                  "completed": completed, "elapsed_seconds": time.perf_counter()-started,
                                  "variants_enabled": variants, "all_samples_enabled": all_samples,
                                  "stop_on_first_failure": stop_on_first_failure,
                                  "focus": focus,
                                  "selected_sample_ids": [sample["id"] for sample in selected],
                                  "private_state_read": False,
                                  "game_actions": 0, "chat_requests": 0})
    assert start_seal == end_seal, "source changed during paired verification"
    assert verifier_unchanged, "independent verifier changed during paired verification"


def percentile(values, fraction):
    if not values:
        return None
    values = sorted(values)
    pos = (len(values)-1)*fraction
    low = int(pos)
    high = min(len(values)-1, low+1)
    return values[low] + (values[high]-values[low])*(pos-low)


def receipt_verifier_valid(folder, path, value):
    if value.get("verifier_sha256") == sha(__file__):
        return True
    history = folder / "verifier-history.json"
    if not history.exists():
        return False
    entry = read(history).get(value.get("verifier_sha256"))
    if not entry or sha(ROOT / entry["file"]) != value.get("verifier_sha256"):
        return False
    sealed = next((row for row in entry["saved_rows"] if Path(row["receipt"]) == path.relative_to(ROOT)), None)
    if not sealed or sha(path) != sealed["sha256"] or not value.get("passed"):
        return False
    before = value["observations"]["baseline"]
    after = value["observations"]["routed"]
    original = read(folder / "baseline" / (value["case"].split(":")[0]+".json"))["observation"]
    # Recheck the actual saved public payloads with this verifier, never just a
    # historical pass flag. No OCR rerun is needed for a diagnostic key fix.
    return (strict_semantics(before) == strict_semantics(after) and
            strict_semantics(original) == strict_semantics(before))


def summary(folder, all_samples=False, variants=False, focus=None):
    current = seal_sources()
    selected = {}
    for path in sorted(folder.glob("paired-*/rows/*.json")):
        value = read(path)
        if value["source_sha256"] == current and receipt_verifier_valid(folder, path, value):
            selected[value["case"]] = (path, value)
    expected = planned_cases(read(folder / "inventory.json"), variants, all_samples, focus)
    expected_ids = {sample["id"] for sample, variant in expected}
    expected_cases = {sample["id"]+":"+variant for sample, variant in expected}
    selected = {case: pair for case, pair in selected.items() if case in expected_cases}
    rows = [value for path, value in selected.values()]
    metrics = {}
    for group, accepted in (("cold", {"native", "scaled_translated"}), ("continuous_animation", {"animation"})):
        metrics[group] = {}
        for label in ("baseline", "routed"):
            times = [row["performance"][label]["total_ms"] for row in rows if row["variant"] in accepted]
            metrics[group][label] = {"count": len(times), "p50_ms": percentile(times, .5),
                                     "p95_ms": percentile(times, .95), "times_ms": times}
    routing = [row["performance"]["routed"].get("routing", {}) for row in rows]
    visual_times = [record["visual_ms"] for record in routing if isinstance(record.get("visual_ms"), (int, float))]
    fallbacks = {}
    strategies = {}
    for record in routing:
        reason = str(record.get("fallback_reason") or "none")
        fallbacks[reason] = fallbacks.get(reason, 0)+1
        strategy = str(record.get("strategy", "unreported"))
        strategies[strategy] = strategies.get(strategy, 0)+1
    native_count = sum(row["variant"] == "native" for row in rows)
    receipt = {"passed": expected_cases.issubset(selected) and all(row["passed"] for row in rows),
               "source_sha256": current, "samples_native": native_count, "all_cases": len(rows),
               "verifier_sha256": sha(__file__),
               "selected_sample_ids": sorted(expected_ids), "inventory_samples": 24,
               "focus": focus,
               "expected_cases": sorted(expected_cases), "missing_cases": sorted(expected_cases-set(selected)),
               "strict_equal_cases": sum(row["strict_public_equal"] for row in rows),
               "regression_cases": [row["case"] for row in rows if not row["passed"]],
               "metrics": metrics, "routing_metrics": routing,
               "visual_preclassification": {"count": len(visual_times), "p50_ms": percentile(visual_times, .5),
                                             "p95_ms": percentile(visual_times, .95)},
               "fallback_counts": fallbacks, "strategy_counts": strategies,
               "replay_receipts": {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
                                   for path, row in selected.values()},
               "actual_rapidocr_engine": True, "exact_frame_excluded": True,
               "private_state_read": False, "game_actions": 0, "chat_requests": 0,
               "limits": ["Development corpus only; not independent classifier accuracy.",
                          "Single cold pair per case; P95 is descriptive local replay, not live capture.",
                          "Continuous results use two existing animation pairs, not synthetic pixel speedup.",
                          "texts can differ; all eight public semantic fields including evidence must match.",
                          "Only nested elapsed_ms diagnostic timers are excluded from semantic equality.",
                          "Observations use the existing public JSON wire format, including stringified numeric map keys.",
                          "Fact retention projection is diagnostic only and never relaxes the strict gate.",
                          "Source-wide hashes must remain fixed within each stage."]}
    path = folder / ("summary-" + str(time.time_ns()) + ".json")
    write(path, receipt)
    print(json.dumps({"receipt": str(path.relative_to(ROOT)), "passed": receipt["passed"],
                      "samples_native": native_count, "cases": len(rows), "metrics": metrics,
                      "regressions": receipt["regression_cases"]}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("inventory", "baseline", "paired", "summary"))
    parser.add_argument("--epoch")
    parser.add_argument("--budget-seconds", type=float, default=145)
    parser.add_argument("--variants", action="store_true")
    parser.add_argument("--all-samples", action="store_true")
    parser.add_argument("--stop-on-first-failure", action="store_true")
    parser.add_argument("--focus", choices=("pilot", "operator-animation"))
    options = parser.parse_args()
    if options.mode == "inventory":
        inventory()
        return
    assert options.epoch and Path(options.epoch).name == options.epoch
    folder = RESEARCH / options.epoch
    if options.mode == "baseline":
        baseline(folder, options.budget_seconds, options.all_samples)
    elif options.mode == "paired":
        pairs(folder, options.budget_seconds, options.variants, options.all_samples, options.stop_on_first_failure, options.focus)
    else:
        summary(folder, options.all_samples, options.variants, options.focus)


if __name__ == "__main__":
    main()
