# Reviewer Guide: Part A (Black-Box) and Part B (White-Box)

This guide explains how a teammate can reproduce and check the testing work in this PR.

## 1. Set up
```
pip install -r requirements.txt
```

## 2. Run the tests
```
python -m pytest tests/test_blackbox.py -v
python -m pytest tests/test_whitebox.py -v
python -m pytest tests/ -v
```
Some tests are expected to fail. They show suspected defects in `registration.py` where the code disagrees with `REQUIREMENTS.md`. Please do not change expected values to make them pass.

## 3. Check coverage
```
python -m pytest tests/ --cov=registration --cov-branch --cov-report=term-missing
```
Compare the output with the saved files in `docs/evidence/` (`*coverage*.txt`).

## 4. Check that the implementation was not changed
```
git diff <starter-commit> -- registration.py
```
The output should be empty.

## 5. What to look at
| Area | File |
|---|---|
| ECP and BVA design | `docs/blackbox_test_design.xlsx` |
| Decision table | `docs/decision_table.xlsx` |
| Black-box tests | `tests/test_blackbox.py` |
| Control-flow graph | `docs/cfg.png` |
| Complexity, paths, MC/DC | `docs/whitebox_analysis.md` |
| White-box tests | `tests/test_whitebox.py` |
| Run evidence | `docs/evidence/` |

## 6. Review questions
- Does each expected value match the requirement ID it cites in `REQUIREMENTS.md`?
- Does each failing test point to a real disagreement between the SRS and the code?
- Does each white-box test name the branch, condition or path it targets?
- Do the coverage numbers in the report match the files in `docs/evidence/`?

## 7. Feedback
Leave comments on the PR. The author will respond to each one in the PR thread.
