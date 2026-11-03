# Future102 registry increment — Source only

Only the literal NEW_MODULES tuple of scripts/verify_full_available.py is
expanded. Existing six selectors and all classifier/assertion/execution code
remain; AST equality outside that assignment was checked with standard library.
The proposed 15 new selectors are seven whole modules and eight exact methods,
covering 52 existing AST direct methods. This does not include the separate 15
new inventory-confirmation Source tests and is not any runtime PASS count.

Current ordered union200 becomes215 only if applied to this bound Source. Cloud
selected MODULES remains untouched.217 physical modules: coverage197 becomes207;
10 wholly omitted modules and four partial modules with10 omitted methods remain.
The complete_repository_validation flag of the old full runner must not be
interpreted as complete physical repository coverage. No assertion or skip rule
is relaxed. The exact increment and ordered unions are in increment-plan.json.

Import dependency audit is separate and has zero runtime execution:
/workspace/.continuation/section102-registry-import-audit-v1/README.md
Its40-project-module eager closures show cv2/numpy required even for RunState;
chat adds httpx. Current selected ScreenReader methods do not call delayed
RapidOCR or Qt/font drawing. Module-level imports still happen for every exact
method selector: successful actual loading is required. Existing AvailableResult
only treats its explicit environment whitelist as U; missing cv2/numpy/httpx,
DLL/shared-library ImportError/OSError or product JSON/icon files are true ERROR.
No Linux readiness or Windows native capture is claimed from this AST audit.

Before applying, Root must bind the actual completed101 Source, then actually
execute the original assertions, record errors/U/skips separately and check full
source drift. Any stale expectation or real defect requires source-backed
analysis, not deletion or fake success. This proposal was not applied or tested,
made no tracked edits and does not complete Section102.
