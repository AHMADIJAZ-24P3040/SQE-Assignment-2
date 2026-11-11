# Part A and Part B Testing Summary

## Overview

Part A covers black-box testing in `tests/test_blackbox.py` using equivalence class partitioning (ECP), boundary value analysis (BVA), and a decision table. Part B covers white-box testing in `tests/test_whitebox.py`, including the control-flow graph (CFG), cyclomatic complexity V(G), basis paths, statement and branch coverage, and MC/DC.

## Deliverable file map

### Tests
- `tests/conftest.py`
- `tests/test_blackbox.py`
- `tests/test_whitebox.py`

### Docs
- `docs/blackbox_test_design.xlsx`
- `docs/cfg.png`
- `docs/decision_table.xlsx`
- `docs/whitebox_analysis.md`
- `docs/evidence/HANDOFF_PartA.md`
- `docs/evidence/HANDOFF_PartB.md`
- `docs/evidence/blackbox_initial_coverage.txt`
- `docs/evidence/blackbox_initial_run.txt`
- `docs/evidence/whitebox_final_coverage.txt`
- `docs/evidence/whitebox_full_run.txt`
- `docs/evidence/whitebox_initial_coverage.txt`

## Test results

The requested pytest commands could not run in this environment: PowerShell reported that Python was not found, and `.venv\Scripts\python.exe` does not exist. Therefore, this run produced no passed, failed, or skipped counts and no statement or branch coverage percentages. No numeric test results are reported here. Existing handoff artifacts describe earlier runs but are not substituted for the requested real run.

Failing tests, when produced by a real run, are legitimate evidence of defects. `registration.py` was not changed.

## Known defects

As listed in `docs/evidence/HANDOFF_PartA.md` and confirmed in `docs/evidence/HANDOFF_PartB.md`:

1. `check_credit_limit()` uses an off-by-one boundary at the combined credit limit (`< 18` instead of allowing `<= 18`).
2. `prerequisites_satisfied()` checks for any intersection instead of requiring every prerequisite (subset).
3. `registration_decision()` uses the wrong dues threshold (`> 1000` rather than blocking any positive dues).
4. `registration_decision()` checks `enrolled > capacity` rather than recognizing a full course at capacity.
5. `withdraw_course()` does not decrement `course.enrolled` when a course is withdrawn.

`registration.py` remains unchanged.
