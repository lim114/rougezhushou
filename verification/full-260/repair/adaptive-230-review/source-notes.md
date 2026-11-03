# Adaptive OCR 230: read-only source notes

No production or test file was modified. No replacement sample was created or
run by this review. The original private `samples/native-client/operator-mechanist.png`
is unavailable. Both `verification/full-230/native.json` and
`native-after-repair.json`, in `failed_cases`, retain the original result:
`AssertionError: 2312604 not less than 2312604`.

The old test at `tests/test_adaptive_recognition.py:28–40` first accepts potential
6, clears `[400:590,1700:1920]`, verifies that current potential is absent and the
timestamp advances, then requires the second OCR `pixels` count to decrease.
That failure proves the pixel-count assertion failed. The receipts do not retain
the routing reason, prior completeness, domains, cache state or analysis geometry
needed to prove which branch caused it. Its later relocation assertions were not
reached and cannot be declared passed.

## Exact full-discovery conditions

`ScreenReader` prepares the current analysis frame on every read. At
`rouge/viewport.py:8–32`, client clipping, nearly black outer-padding removal and
resizing can change the analysis geometry even when raw screenshot shape stays
the same. Pixel metrics refer to that analysis frame, whereas the old test compares
against the source screenshot area.

| Path and source lines | Exact condition / consequence |
| --- | --- |
| `recognition.py:73–80` | Raw frame, shape, dtype, client rectangle and semantic run context all identical: reuse the whole result; no new OCR metrics are attached. A changed icon must fail this byte-equality check. |
| `recognition.py:135–147` | A single specialized visual page with a normalized domain and a supported PageOCR provider uses full current DET plus prioritized recognition batches; this is not DynamicOCR's dirty-crop path. |
| `recognition.py:148–153` | In the non-PageOCR path, disabled cache or a domain/identity not previously semantically verified forces discovery. The identity includes page, analysis shape, dtype and outward-quantized domain. |
| `recognition.py:154–157` | Semantic backoff chooses the unscoped reader but does not itself set `force_discovery`; page-route age >= 8 does force discovery. |
| `dynamic_ocr.py:24–28` | Dirty reuse requires no explicit force, a previous frame, equal analysis shape/dtype, equal domains or a full-to-domain seed, and age < 8. Any failed condition leaves `rects=None`. |
| `dynamic_ocr.py:29–38,94` | With a guarded page domain, any changed pixel outside it discards the domain and reads the current whole frame immediately. |
| `dynamic_ocr.py:41–62` | Changed pixels are max-pooled in 16-pixel blocks, expanded by 48 pixels, expanded to intersected prior OCR boxes with 12-pixel padding for three merge passes, and clipped to a page domain if present. More than 12 resulting regions, or their exact union area > 45% of the applicable domain/frame area, requests discovery. |
| `dynamic_ocr.py:63–80` | With `rects=None`, a full-to-domain seed is dropped. A missing domain calls the engine on the whole frame with `pixels=h*w`; a surviving explicitly supplied domain uses page discovery instead. |
| `recognition.py:175–181` | If a proposed page domain was dropped by DynamicOCR, routing changes to `page_outside_regions_changed` or `page_changed_area_full`. |
| `recognition.py:199–205` | A retained page-region result failing `specialized_observation_valid` is interpreted again after forced whole-frame discovery; this can perform crop OCR followed by whole-frame OCR. |
| `recognition.py:213–216` | Only semantically valid current observations retain `_page_verified_identity`. An incomplete first operator read can force `page_initial_discovery` again on the second frame. |

Unknown, incomplete, conflicting or damaged visual controls alone do **not**
guarantee a new full DynamicOCR pass: they leave `regions=None`, and the DynamicOCR
state decides whether unscoped dirty reuse is possible. However,
`recognition.py:165–173` deliberately clears its previous image and text after a
PageOCR read, so a PageOCR-to-DynamicOCR transition must start with discovery.

`page_features.py:112–143` rejects invalid/small frames, no descriptors, zero page
candidates or multiple candidates. Matching also rejects insufficient/ambiguous
features, bad affine fit/scale/rotation, insufficient control contrast or
correlation, absent support on either side, and clipped reference geometry
(`page_features.py:145–217`). Cached transforms require exact byte equality of
every control region plus equal frame shape/dtype (`81–99`).

## Two specific causal candidates exposed by the source

1. **A missing current potential makes the operator incomplete.**
   `operator_recognition.py:289–290` only adds potential after a current-pixel
   template match. Its required fields include potential at `344–349`; absence
   makes `complete=False`. `recognition.py:345–348` rejects an incomplete
   `operator_detail` region result. This can trigger the forced full retry or
   prevent verification for the next frame. Current potential remaining unknown
   is the correct value behavior; the extra full OCR is a separate cost decision.
   Source alone does not prove this was the original 230 route.

2. **The old clearing rectangle may erase a static control too.**
   The public `rouge/data/page-features/manifest.json` operator-detail reference is
   1280 x 703; its elite control occupies `[1025,307,1084,331]`. At a 2052 x 1127
   canonical layout this becomes approximately
   `[1643.20,492.16,1737.79,530.64]`, overlapping the old test's clearing rectangle.
   That overlap can break exact-control reuse and visual matching. The numerical
   product 2312604 alone does not establish the old screenshot's width, height or
   affine transform; this is an independently verifiable public-layout condition,
   not proof about the unavailable sample. The old mask cannot safely be called
   an icon-only change.

## Public evidence that can distinguish the narrow mechanisms

- Build a clearly labelled **new public synthetic** panel from the checked-in
  static-control patches and `data/ui-icons/potential-6.png`, with independently
  drawn operator text. Record all fixture hashes and the actual visual plan;
  require an unambiguous identity and an initially complete current observation.
  First erase only the potential-icon ROI while leaving all control bytes intact.
  Then use a separate frame that erases both that icon and the elite control.
  Compare each changed frame against a fresh uncached whole-frame reader. Record
  current fields, missing fields, completeness, transform/domain, fallback reason,
  actual OCR call shapes, detector calls and recognition cache hits.
- The icon-only frame can establish a fresh-value/cache defect only if the
  warmed reader reports potential 6 after the independent current-pixel read
  cannot match it. `match_potential` itself is testable on those public pixels:
  ROI geometry/label height and exact pixels form the cache identity
  (`operator_recognition.py:191–223`; `recognition_cache.py:15–22`). A correct
  result is absent potential, regardless of whether cost is reduced.
- A crop-then-full trace with unchanged controls, complete current text coverage
  and a retry caused solely by `complete=False` can establish the narrower
  redundant-work mechanism on that public fixture. It does not by itself justify
  relaxing the semantic gate: a proposed optimization must still discover
  exterior changes and preserve unknown fields. Control-damage, exterior-change,
  geometry-change and over-45%-region cases are necessary guard comparisons.
- Existing `tests/test_page_ocr_056.py` already separates semantic rejection,
  forced full retry, geometry/domain identity, large changes and outside-domain
  guards using explicit controlled fixtures. Those cases prove protocol behavior
  when executed; they are not the original private OCR sample. No new mocked
  success should be reported as a replacement for the old 230 result.

## Metrics and cost interpretation

DynamicOCR `pixels` counts requested/covered image area, not measured provider
inference: `CachedOCR` can serve exact current crop bytes without invoking its
provider (`recognition_cache.py:15–22,48–49`). Its context includes OCR kwargs,
shape, dtype, hash and byte equality.

PageOCR intentionally detects the **whole current frame** on every ordinary call
and caches only exactly identical recognition batches. Its metrics expose
`detected_boxes`, `recognized_batches`, `reused_batches` and `recognized_boxes`,
not `pixels` (`page_ocr.py:121–164`). Its support contract is exact RapidOCR 1.4.4
with enabled DET/REC and a positive batch size (`49–58`). Configuration changes
invalidate the batch cache (`60–66,116–120`). A complete-text semantic rejection
can label routing `full_discovery` without repeating that same OCR
(`recognition.py:185–197`).

Therefore neither `routing=full_discovery` nor a source-area inequality alone is
an adequate proof of actual redundant inference. Keep the old result unresolved
until its actual fixture and trace are available; new public evidence may close
only the mechanism and scope it actually demonstrates.

## Read-only snapshot hashes

- `recognition.py`: `7f96fe7bf2f93cd6f954136d3d9b2e6cd58741f672ac1989303422ef9a9cb53b`
- `dynamic_ocr.py`: `0b2fbb9046540f3676ceb165efde007688099309cd649f223b858cef03ba28cc`
- `page_ocr.py`: `56ff0129e6c1f6848b4bb94b92545577d545525433d76c49ab2e2e951785e87e`
- `page_features.py`: `ab4cda4da8272ed35ad72269ad829ffb6ccb1ae711d82f24f6e6f530ca838c6e`
- `operator_recognition.py`: `1e79d32a69d6bbbf0e42ba8cdcb88c33a0ff3bc9932adbc6b0c19ef553705fb0`
- Original adaptive test: `188ecc89418b02d656f6807b2ecf6b0b6b139fdcdc8961331c9bdf935467fe4a`
- Public control manifest: `bd588445dfe35898d4b159211d2efe07f7c80ff2d013fcea7cb97aac7e5990b3`
