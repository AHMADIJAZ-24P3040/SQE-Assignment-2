# Part B: White-Box Testing Analysis

**Assignment:** SQE Assignment 2 — Student Course Registration System  
**Date:** 2026-11-10  
**Function Under Analysis:** `registration_decision(student: Student, course: Course) -> str`  
**Lines:** 44–60 in registration.py

---

## B1: Control-Flow Graph and Cyclomatic Complexity

### 1.1 CFG Node Definitions

**Convention for Compound Conditions:**  
Every atomic condition is treated as its own decision node. Python's short-circuit evaluation (`and`/`or`) means compound expressions are evaluated left-to-right, stopping when the outcome is determined. Each decision node represents a point where execution can branch.

For line 48: `if not 0 <= course.enrolled <= course.capacity or course.capacity < 1:`
- This is a complex predicate, but for CFG purposes, treated as a single decision node (N4)
- The logic short-circuits: if enrolled is invalid, the capacity check may not evaluate
- For basis paths, we treat this as: "enrollment/capacity invalid" → T/F branches

| Node ID | Type | Line(s) | Description |
|---------|------|---------|-------------|
| N1 | START | — | Function entry point |
| N2 | DECISION | 46 | `if student.outstanding_dues < 0:` |
| N3 | PROCESS | 47 | `raise ValueError("Invalid dues")` |
| N4 | DECISION | 48 | `if not (0 <= course.enrolled ≤ capacity) or capacity < 1:` |
| N5 | PROCESS | 49 | `raise ValueError("Invalid capacity or enrollment")` |
| N6 | DECISION | 50 | `if student.outstanding_dues > 1000:` |
| N7 | RETURN | 51 | `return "DUES_BLOCK"` |
| N8 | DECISION | 52 | `if course.code in student.registered_courses:` |
| N9 | RETURN | 53 | `return "ALREADY_REGISTERED"` |
| N10 | DECISION | 54 | `if not prerequisites_satisfied(...):` |
| N11 | RETURN | 55 | `return "PREREQUISITES_MISSING"` |
| N12 | DECISION | 56 | `if not check_credit_limit(...):` |
| N13 | RETURN | 57 | `return "CREDIT_LIMIT"` |
| N14 | DECISION | 58 | `if course.enrolled > course.capacity:` |
| N15 | RETURN | 59 | `return "WAITLISTED"` |
| N16 | RETURN | 60 | `return "REGISTERED"` |
| N17 | EXIT | — | Function exit (all return paths converge) |

### 1.2 CFG Edges

**From→To (Label):**
- N1 → N2 (entry)
- N2 → N3 (True: dues < 0)
- N2 → N4 (False: dues ≥ 0, proceed)
- N3 → N17 (raise exception, exit)
- N4 → N5 (True: invalid enrollment/capacity)
- N4 → N6 (False: valid enrollment/capacity, proceed)
- N5 → N17 (raise exception, exit)
- N6 → N7 (True: dues > 1000)
- N6 → N8 (False: dues ≤ 1000, proceed)
- N7 → N17 (return DUES_BLOCK)
- N8 → N9 (True: already registered)
- N8 → N10 (False: not registered, proceed)
- N9 → N17 (return ALREADY_REGISTERED)
- N10 → N11 (True: prerequisites missing)
- N10 → N12 (False: prerequisites satisfied, proceed)
- N11 → N17 (return PREREQUISITES_MISSING)
- N12 → N13 (True: credit limit exceeded)
- N12 → N14 (False: within credit limit, proceed)
- N13 → N17 (return CREDIT_LIMIT)
- N14 → N15 (True: enrolled > capacity, WAITLISTED)
- N14 → N16 (False: enrolled ≤ capacity, REGISTERED)
- N15 → N17 (return WAITLISTED)
- N16 → N17 (return REGISTERED)

**Total Edges:** 23

### 1.3 Cyclomatic Complexity Calculation

**Method 1: V(G) = E - N + 2**
- Nodes (N): 17 (N1–N17)
- Edges (E): 23
- V(G) = 23 - 17 + 2 = **8**

**Method 2: V(G) = Decision Nodes + 1**
- Decision nodes: N2, N4, N6, N8, N10, N12, N14 = 7 decisions
- V(G) = 7 + 1 = **8**

**Confirmation:** Both methods agree. V(G) = **8**.

This means the function has **8 independent paths** (within the bounds of control flow).

---

## B2: Basis Paths

A basis path set is a set of V(G) linearly independent paths. Each new path must exercise at least one edge not covered by prior paths.

| Path ID | Node Sequence | Decision Outcomes | Representative Test Input | Expected Result (SRS Req) | Test ID |
|---------|---------------|-------------------|---------------------------|---------------------------|---------|
| **P1** | N1→N2→N3→N17 | dues<0 T | `Student(outstanding_dues=-1)` | `ValueError("Invalid dues")` FR-15 | test_wb_path_01 |
| **P2** | N1→N2→N4→N5→N17 | dues≥0 F, invalid enrollment T | `Course(enrolled=-1, capacity=10)` | `ValueError("Invalid capacity...")` FR-15 | test_wb_path_02 |
| **P3** | N1→N2→N4→N6→N7→N17 | Valid input, dues>1000 T | `Student(dues=1001), eligible` | `DUES_BLOCK` FR-04 | test_wb_path_03 |
| **P4** | N1→N2→N4→N6→N8→N9→N17 | Valid, dues≤1000, already reg T | `Student(registered_courses={'CS101'}), course CS101` | `ALREADY_REGISTERED` FR-05 | test_wb_path_04 |
| **P5** | N1→N2→N4→N6→N8→N10→N11→N17 | Valid, not duplicate, prereqs missing T | `Student(completed_courses={}), Course(prerequisites={'CS101'})` | `PREREQUISITES_MISSING` FR-06 | test_wb_path_05 |
| **P6** | N1→N2→N4→N6→N8→N10→N12→N13→N17 | Valid, prereqs OK, credit limit exceeded T | `Student(current_credits=16), Course(credit_hours=3)` | `CREDIT_LIMIT` FR-07 | test_wb_path_06 |
| **P7** | N1→N2→N4→N6→N8→N10→N12→N14→N15→N17 | Valid, credit OK, enrolled==capacity T | `Student(eligible), Course(enrolled=30, capacity=30)` | `WAITLISTED` FR-08 | test_wb_path_07 |
| **P8** | N1→N2→N4→N6→N8→N10→N12→N14→N16→N17 | All checks pass, seat available F | `Student(eligible), Course(enrolled=10, capacity=30)` | `REGISTERED` FR-08, FR-11 | test_wb_path_08 |

**Linearly Independence Justification:**
- P1: Introduces edge (N2→N3) — dues validation exception path, not covered by other paths
- P2: Introduces edge (N4→N5) — enrollment validation exception path, different from P1
- P3: Introduces edge (N6→N7) — dues > 1000 branch, different exception handling
- P4: Introduces edge (N8→N9) — already registered return, new decision branch
- P5: Introduces edge (N10→N11) — prerequisites missing return, extends path through N10
- P6: Introduces edge (N12→N13) — credit limit exceeded return, extends through N12
- P7: Introduces edge (N14→N15) — enrolled > capacity decision (True), seat waitlist path
- P8: Introduces edge (N14→N16) — enrolled ≤ capacity decision (False), final REGISTERED return

Each path adds at least one previously untouched edge. Together they cover all 23 edges.

---

## B3: Atomic Conditions and MC/DC Analysis

### 3.1 Atomic Conditions in registration_decision()

| Condition ID | Condition | Line | Decision | Type | Notes |
|--------------|-----------|------|----------|------|-------|
| **C1** | `student.outstanding_dues < 0` | 46 | N2 | Validation | Raises exception if True |
| **C2a** | `0 <= course.enrolled` | 48 | N4 | Compound (AND) | Part of range check |
| **C2b** | `course.enrolled <= course.capacity` | 48 | N4 | Compound (AND) | Part of range check |
| **C2c** | `course.capacity < 1` | 48 | N4 | Compound (OR) | After NOT of range |
| **C3** | `student.outstanding_dues > 1000` | 50 | N6 | Decision | Blocks registration if True |
| **C4** | `course.code in student.registered_courses` | 52 | N8 | Decision | Already registered if True |
| **C5** | `prerequisites_satisfied(...)` | 54 | N10 | Function call (negated) | Determines prerequisite pass/fail |
| **C6** | `check_credit_limit(...)` | 56 | N12 | Function call (negated) | Determines credit eligibility |
| **C7** | `course.enrolled > course.capacity` | 58 | N14 | Decision | Impossible in normal state (defect!) |

### 3.2 Truth Table for Most Complex Decision (N4)

**Line 48:** `if not (0 <= course.enrolled <= course.capacity) or course.capacity < 1:`

**Atomic components:**
- A: `0 <= course.enrolled`
- B: `course.enrolled <= course.capacity`
- C: `course.capacity < 1`

**Expression:** `NOT(A AND B) OR C` = `(NOT A OR NOT B) OR C`

**Truth Table (reachable rows only):**

| A | B | C | A∧B | ¬(A∧B) | ¬(A∧B)∨C | Outcome |
|---|---|---|-----|--------|----------|---------|
| T | T | T | T | F | T | Raises (invalid) |
| T | T | F | T | F | F | Proceeds (valid) |
| T | F | T | F | T | T | Raises (invalid) |
| T | F | F | F | T | T | Raises (invalid) |
| F | T | T | F | T | T | Raises (invalid) |
| F | T | F | F | T | T | Raises (invalid) |
| F | F | T | F | T | T | Raises (invalid) |
| F | F | F | F | T | T | Raises (invalid) |

Note: Row (T,T,F) is the only "Proceeds" outcome. All other rows raise an exception.

### 3.3 MC/DC Analysis for Decision N4

**Rationale for choosing N4:** 
- Has 3 atomic conditions (C2a, C2b, C2c)
- Complex boolean logic with short-circuit evaluation
- Directly affects program behavior (exception vs proceed)
- This is the enrollment/capacity validation gate

**MC/DC Test Pairs for N4:**

For each condition, show a minimal pair where:
- Condition X changes from T→F or F→T
- Other conditions remain fixed (or are "not evaluated" per short-circuit)
- Decision outcome flips

**Pair for C2a (0 ≤ enrolled):**
- Test WB-MCDC-01a: enrolled=0, capacity=10, result=T → Proceeds (valid)
- Test WB-MCDC-01b: enrolled=-1, capacity=10, result=T → Raises (invalid)
- Effect: C2a=T→F flips outcome from "Proceeds" to "Raises"

**Pair for C2b (enrolled ≤ capacity):**
- Test WB-MCDC-02a: enrolled=5, capacity=10, result=F → Proceeds (valid)
- Test WB-MCDC-02b: enrolled=15, capacity=10, result=T → Raises (invalid)
- Effect: C2b=T→F flips outcome from "Proceeds" to "Raises"

**Pair for C2c (capacity < 1):**
- Test WB-MCDC-03a: capacity=1, enrolled=0, result=F → Proceeds (valid)
- Test WB-MCDC-03b: capacity=0, enrolled=0, result=T → Raises (invalid)
- Effect: C2c=T→F flips outcome from "Raises" to "Proceeds"

**MC/DC Test Set (minimal: 4 tests):**
1. WB-MCDC-01: enrolled=0, capacity=10 → Proceeds (C2a=T, C2b=T, C2c=F)
2. WB-MCDC-02: enrolled=-1, capacity=10 → Raises (C2a=F, triggers ¬A=T, short-circuit)
3. WB-MCDC-03: enrolled=15, capacity=10 → Raises (C2a=T, C2b=F, triggers ¬B=T)
4. WB-MCDC-04: enrolled=0, capacity=0 → Raises (C2c=T)

**Note:** pytest-cov reports statement and branch coverage only. Condition and MC/DC coverage are computed manually above.

---

## B4: Statement and Branch Coverage Analysis

### 4.1 Initial Coverage (Part A baseline)

From `docs/evidence/blackbox_initial_coverage.txt`:
```
Name              Stmts   Miss   Branch   BrPart   Cover   Missing
registration.py      53      3        26        3       92%    51, 59, 71
```

**Missing coverage in registration_decision():**
- Line 51: `return "DUES_BLOCK"` — Never reached (dues > 1000 but SRS requires > 0)
- Line 59: `return "WAITLISTED"` — Never reached (enrolled > capacity impossible condition)

**Uncovered branches:**
- Line 50 (N6): `True` branch never taken (wrong threshold masks high-dues scenarios)
- Line 58 (N14): `True` branch never taken (wrong comparison, condition never true)

### 4.2 Coverage Gaps Requiring White-Box Tests

| Line | Branch | Condition | Coverage Gap | Test Name | Fix Required |
|------|--------|-----------|--------------|-----------|--------------|
| 51 | True | `dues > 1000` | Never executed (should be `> 0`) | test_wb_cov_01_dues_block_correct | Fix: Change > 1000 to > 0 |
| 59 | True | `enrolled > capacity` | Structurally impossible in normal state | test_wb_cov_02_waitlisted_at_capacity | Fix: Change > to == |

**Note:** These are not bugs in the tests; they expose genuine defects in registration.py.

---

## Summary Table

| Metric | Value |
|--------|-------|
| **Cyclomatic Complexity V(G)** | 8 |
| **Decision Nodes** | 7 |
| **Basis Paths** | 8 (P1–P8) |
| **Atomic Conditions** | 7 (C1–C7) |
| **Initial Statement Coverage** | 92% (51, 59, 71 uncovered) |
| **Initial Branch Coverage** | ~65% (2 branches uncovered) |
| **MC/DC Tests** | 4 (for N4) |
| **Defects Exposing Coverage Gaps** | 2 (lines 51, 59) |

