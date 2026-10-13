# New public operator fixtures: genuine before-change evidence

These are explicitly new synthetic panels, not recovered private screenshots.
All pixels come from declared text/layout, checked-in static controls and the
checked-in potential-6 icon. No fixture was written to `samples/native-client`.
Production, tests, thresholds and historical assertions were not changed.

`fixture-manifest.json` identifies the sources, hashes, drawn font and declared
Fang values: level 40, elite 0, potential 6, trust 100%, skill rank 3, selected
skill 1. The fixed catalog has one skill and no modules. Real RapidOCR 1.4.4 and
the unmodified ScreenReader recognize a **complete** baseline in every run.
The image visibly says `PUBLIC SYNTHETIC FIXTURE`.

## Four independently paired scenarios

`frames.json` supplies PNG paths/hashes, pixel hashes, shapes and dtype for:

- Icon removed: only `[1100,240,1190,330]` is cleared; actual visual-control reuse
  remains `exact_controls` and current potential becomes unknown.
- Control damaged: `[1048,307,1084,331]` clears part of the elite control; current
  identity and potential remain readable. Current selected skill becomes unknown,
  matching an independent fresh full read.
- Exterior overlay: newly drawn `PUBLIC OVERLAY 261` lies outside the scheduled
  page domains and is actually returned by default, legacy and fresh readers.
- Geometry changed: the fixture's prepared image is placed at `[500,100]` in a
  3200 x 1800 non-black canvas; complete current fields are recovered after full
  discovery.

Each scenario starts with its own fresh reader and complete Fang baseline.
Both default and explicit legacy (`page_ocr_enabled=False`) strategies are tested,
followed by a separate uncached, unrouted full-frame oracle. All **eight** changed
operator projections exactly match their fresh oracle: identity, scope, fields,
skill ranks, missing fields and completeness. This is stronger than checking a
single previously observed value.

| Changed scenario | Default before behavior | Legacy before behavior |
| --- | --- | --- |
| Icon removed | PageOCR full current detection; absent potential; no duplicate full retry | Dirty crop followed by semantic forced full retry; 2 DET + 3 REC calls |
| Control damaged | PageOCR-to-Dynamic transition loses its baseline and requests 2,312,604 pixels | Current dirty region requests 40,572 pixels; same fresh fields |
| Exterior overlay | Full current DET discovers the actual new exterior text | Guard forces full discovery and returns that text |
| Geometry changed | Full discovery of 5,760,000 current pixels | Full discovery of 5,760,000 current pixels |

For the control-damage case, actual ONNX work was default DET 1 / REC 2 versus
legacy DET 1 / REC 1. Recorded inference times were 863.3 ms and 168.8 ms in this
run; these times are observations under the current shared workload, not a general
speed guarantee. The corresponding pixels ratio is 40,572 / 2,312,604 = 1.75%.
The default transition is a concrete target for verified PageOCR-to-Dynamic
baseline transfer without weakening semantic gates or thresholds.

Actual `OrtInferSession` calls are observed by a wrapper that calls the original
method and returns its actual output unchanged. Provider types and cache
configuration remain intact. `before-scenarios.json` retains full observations,
raw OCR texts, current metrics, model-call shapes/counts/times and before/after
source hashes. `before-summary.json` provides the compact comparison.

## Three-frame current-owner guard

`owner-sequence-frames.json` supplies three genuine public frames:
Fang -> Vanilla -> Vanilla with elite control damage. Vanilla is fixed catalog
`char_240_wyvern`, one skill, no modules, E0 max 40 and E1 max 55; the declared
Lv40/E0 and `/40` remain legal. No maximum of 50 was invented.

Real default inference returns complete Fang on frame 1, complete Vanilla with
PageOCR and `exact_controls` on frame 2, then **Vanilla** with potential 6 and
current unknown selected skill on frame 3. Every frame matches its independently
uncached full oracle. The third frame currently requests full 2,312,604 pixels.
An after-change run must keep the current Vanilla owner when transferring the
most recent verified baseline; preserving the older Fang raw records would fail
this sequence. Details are in `before-owner-sequence.json` and its log.

## Seals and limits

`before-seal.json` seals the original four-scenario fixtures, scripts and receipts.
`owner-sequence-seal.json` seals the additional owner sequence. `validation.json`
confirms unchanged production hashes, complete baselines, eight fresh comparisons,
three current-owner/fresh comparisons and actual exterior-text detection.

These are Linux real-OCR before-change receipts. No production fix or after-change
pass is claimed here. Native Windows is not verified. The unavailable original
230 `operator-mechanist` pixel-count assertion remains unresolved and is never
declared passed from these different public images.
