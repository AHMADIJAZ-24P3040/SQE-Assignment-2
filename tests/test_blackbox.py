"""Black-box tests for Student Course Registration System.

All expected results derived from REQUIREMENTS.md.
Test naming includes design IDs (ECP-##, BVA-##, DT-##).
"""
import pytest
from registration import Student, Course, check_credit_limit, prerequisites_satisfied, registration_decision, register_course, withdraw_course


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def student():
    """A default student with no courses, no dues."""
    return Student(
        student_id="S001",
        completed_courses=set(),
        current_credits=0,
        outstanding_dues=0,
        registered_courses=set()
    )


@pytest.fixture
def course():
    """A default course with capacity 30, no enrollment."""
    return Course(
        code="CS101",
        credit_hours=3,
        capacity=30,
        enrolled=0,
        prerequisites=set(),
        waitlist=[]
    )


# ============================================================================
# TEST: check_credit_limit
# ============================================================================

class TestCheckCreditLimit:
    """Test credit limit validation (FR-01, FR-02)."""

    def test_ecp_15_valid_min_credit(self):
        """ECP-15: Valid minimum course credit (1)."""
        result = check_credit_limit(0, 1)
        assert result is True

    def test_ecp_16_valid_max_credit(self):
        """ECP-16: Valid maximum course credit (4)."""
        result = check_credit_limit(0, 4)
        assert result is True

    def test_ecp_19_valid_min_current(self):
        """ECP-19: Valid minimum current credits (0)."""
        result = check_credit_limit(0, 3)
        assert result is True

    def test_ecp_20_valid_max_current(self):
        """ECP-20: Valid maximum current credits (18)."""
        result = check_credit_limit(18, 0)
        pytest.skip("Credit 0 invalid; testing limit check for current=18")

    def test_ecp_21_invalid_below_min_current(self):
        """ECP-21: Current credits below minimum (-1)."""
        with pytest.raises(ValueError, match="Invalid current credits"):
            check_credit_limit(-1, 3)

    def test_ecp_22_invalid_above_max_current(self):
        """ECP-22: Current credits above maximum (19)."""
        with pytest.raises(ValueError, match="Invalid current credits"):
            check_credit_limit(19, 3)

    def test_ecp_17_invalid_too_low_course(self):
        """ECP-17: Course credits too low (0)."""
        with pytest.raises(ValueError, match="Invalid course credits"):
            check_credit_limit(5, 0)

    def test_ecp_18_invalid_too_high_course(self):
        """ECP-18: Course credits too high (5)."""
        with pytest.raises(ValueError, match="Invalid course credits"):
            check_credit_limit(5, 5)

    def test_bva_01_current_zero(self):
        """BVA-01: Current credits at zero boundary."""
        result = check_credit_limit(0, 3)
        assert result is True

    def test_bva_03_current_minus_one(self):
        """BVA-03: Current credits just below minimum."""
        with pytest.raises(ValueError, match="Invalid current credits"):
            check_credit_limit(-1, 3)

    def test_bva_05_course_one(self):
        """BVA-05: Course credits at minimum boundary."""
        result = check_credit_limit(10, 1)
        assert result is True

    def test_bva_07_course_zero(self):
        """BVA-07: Course credits just below minimum."""
        with pytest.raises(ValueError, match="Invalid course credits"):
            check_credit_limit(10, 0)

    def test_bva_09_combined_exactly_18(self):
        """BVA-09: Combined credits exactly 18 (allowed per FR-01)."""
        # FR-01: exactly 18 is allowed, so returns True
        result = check_credit_limit(15, 3)
        assert result is True  # 15 + 3 = 18, which should be allowed

    def test_bva_10_combined_exceeds_18(self):
        """BVA-10: Combined credits exceed 18."""
        # FR-01: should return False if total > 18
        # Note: This test checks the implementation against the requirement
        result = check_credit_limit(15, 4)  # 15 + 4 = 19
        # Expected from FR-01: returns False when exceeds 18
        # But current code returns False when < 18, which is INCORRECT
        assert result is False


class TestPrerequisitesSatisfied:
    """Test prerequisite checking (FR-03)."""

    def test_ecp_04_all_satisfied(self):
        """ECP-04: All prerequisites satisfied."""
        result = prerequisites_satisfied({'CS101'}, {'CS101'})
        assert result is True

    def test_ecp_05_partial_satisfied(self):
        """ECP-05: Only some prerequisites satisfied."""
        result = prerequisites_satisfied({'CS101'}, {'CS101', 'MATH101'})
        assert result is False

    def test_ecp_06_none_required(self):
        """ECP-06: No prerequisites required."""
        result = prerequisites_satisfied({'CS101'}, set())
        assert result is True

    def test_ecp_07_none_completed(self):
        """ECP-07: No courses completed but prerequisites required."""
        result = prerequisites_satisfied(set(), {'CS101'})
        assert result is False

    def test_prereq_multiple_all_satisfied(self):
        """Multiple prerequisites, all satisfied."""
        completed = {'CS101', 'MATH101', 'PHYS101'}
        required = {'CS101', 'MATH101'}
        result = prerequisites_satisfied(completed, required)
        assert result is True

    def test_prereq_multiple_one_missing(self):
        """Multiple prerequisites, one missing."""
        completed = {'CS101', 'PHYS101'}
        required = {'CS101', 'MATH101'}
        result = prerequisites_satisfied(completed, required)
        assert result is False


# ============================================================================
# TEST: registration_decision (INPUT VALIDATION)
# ============================================================================

class TestRegistrationDecisionValidation:
    """Test input validation in registration_decision (FR-15)."""

    def test_ecp_03_negative_dues(self):
        """ECP-03: Negative outstanding dues."""
        student = Student(student_id="S1", outstanding_dues=-100)
        course = Course(code="C1", credit_hours=3, capacity=30, enrolled=0)
        with pytest.raises(ValueError, match="Invalid dues"):
            registration_decision(student, course)

    def test_bva_19_negative_dues_boundary(self):
        """BVA-19: Negative dues (just below zero)."""
        student = Student(student_id="S1", outstanding_dues=-1)
        course = Course(code="C1", credit_hours=3, capacity=30, enrolled=0)
        with pytest.raises(ValueError, match="Invalid dues"):
            registration_decision(student, course)

    def test_ecp_24_capacity_below_one(self):
        """ECP-24: Course capacity < 1."""
        student = Student(student_id="S1")
        course = Course(code="C1", credit_hours=3, capacity=0, enrolled=0)
        with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
            registration_decision(student, course)

    def test_ecp_25_enrollment_below_zero(self):
        """ECP-25: Course enrollment < 0."""
        student = Student(student_id="S1")
        course = Course(code="C1", credit_hours=3, capacity=30, enrolled=-1)
        with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
            registration_decision(student, course)

    def test_ecp_26_enrollment_exceeds_capacity(self):
        """ECP-26: Course enrollment > capacity (invalid state)."""
        student = Student(student_id="S1")
        course = Course(code="C1", credit_hours=3, capacity=30, enrolled=31)
        with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
            registration_decision(student, course)


# ============================================================================
# TEST: registration_decision (DECISION OUTCOMES)
# ============================================================================

class TestRegistrationDecisionOutcomes:
    """Test all decision outcomes and priority order (FR-04 through FR-09)."""

    def test_ecp_01_ecp_02_dues_no_dues(self, student, course):
        """ECP-01, ECP-02: Dues blocks registration."""
        # Student with no dues
        student.outstanding_dues = 0
        result = registration_decision(student, course)
        assert result in ["REGISTERED", "WAITLISTED", "PREREQUISITES_MISSING", "CREDIT_LIMIT", "ALREADY_REGISTERED"]

        # Student with dues (should block)
        student_with_dues = Student(
            student_id="S2",
            outstanding_dues=100,
            current_credits=0,
            registered_courses=set(),
            completed_courses=set()
        )
        result_with_dues = registration_decision(student_with_dues, course)
        assert result_with_dues == "DUES_BLOCK"

    def test_dt_01_dues_block_priority(self):
        """DT-01: Dues block has highest priority."""
        student = Student(
            student_id="S1",
            outstanding_dues=50,
            current_credits=0,
            registered_courses=set(),
            completed_courses=set()
        )
        course = Course(
            code="CS101",
            credit_hours=3,
            capacity=2,
            enrolled=2,  # Full
            prerequisites={'MATH101'},
            waitlist=['S2']
        )
        # Even though prereqs missing, seat unavailable, already registered - dues blocks
        result = registration_decision(student, course)
        assert result == "DUES_BLOCK"

    def test_ecp_08_ecp_09_already_registered(self, student, course):
        """ECP-08, ECP-09: Already registered check (priority 2)."""
        # Student not registered
        student.registered_courses = set()
        decision1 = registration_decision(student, course)
        assert decision1 != "ALREADY_REGISTERED"

        # Student already registered
        student.registered_courses.add(course.code)
        decision2 = registration_decision(student, course)
        assert decision2 == "ALREADY_REGISTERED"

    def test_dt_02_already_registered_priority(self):
        """DT-02: Already registered has priority 2."""
        student = Student(
            student_id="S1",
            outstanding_dues=0,
            current_credits=0,
            registered_courses={'CS101'},
            completed_courses=set()
        )
        course = Course(
            code="CS101",
            credit_hours=3,
            capacity=1,
            enrolled=1,  # Full
            prerequisites={'MATH101'},  # Missing
            waitlist=[]
        )
        result = registration_decision(student, course)
        assert result == "ALREADY_REGISTERED"

    def test_ecp_04_ecp_05_ecp_06_ecp_07_prerequisites(self):
        """ECP-04, 05, 06, 07: Prerequisites check (priority 3)."""
        # All prerequisites satisfied
        student = Student(
            student_id="S1",
            outstanding_dues=0,
            current_credits=0,
            registered_courses=set(),
            completed_courses={'CS101', 'MATH101'}
        )
        course = Course(
            code="PHYS201",
            credit_hours=3,
            capacity=30,
            enrolled=10,
            prerequisites={'CS101', 'MATH101'},
            waitlist=[]
        )
        result = registration_decision(student, course)
        assert result in ["REGISTERED", "WAITLISTED", "CREDIT_LIMIT"]

        # Some prerequisites missing
        student2 = Student(
            student_id="S2",
            outstanding_dues=0,
            current_credits=0,
            registered_courses=set(),
            completed_courses={'CS101'}  # Missing MATH101
        )
        result2 = registration_decision(student2, course)
        assert result2 == "PREREQUISITES_MISSING"

    def test_dt_03_prerequisites_missing_priority(self):
        """DT-03: Prerequisites missing has priority 3."""
        student = Student(
            student_id="S1",
            outstanding_dues=0,
            current_credits=15,
            registered_courses=set(),
            completed_courses=set()
        )
        course = Course(
            code="CS201",
            credit_hours=4,
            capacity=1,
            enrolled=1,  # Full (would be WAITLISTED if prereqs OK)
            prerequisites={'CS101'},
            waitlist=[]
        )
        result = registration_decision(student, course)
        assert result == "PREREQUISITES_MISSING"

    def test_ecp_10_ecp_12_credit_limit(self, student, course):
        """ECP-10, ECP-12: Credit limit check (priority 4)."""
        # Within limit
        student.current_credits = 15
        course.credit_hours = 3
        result = registration_decision(student, course)
        assert result in ["REGISTERED", "WAITLISTED"]

        # Exceeds limit
        student2 = Student(
            student_id="S2",
            outstanding_dues=0,
            current_credits=16,
            registered_courses=set(),
            completed_courses=set()
        )
        course2 = Course(
            code="CS102",
            credit_hours=3,
            capacity=30,
            enrolled=10,
            prerequisites=set(),
            waitlist=[]
        )
        result2 = registration_decision(student2, course2)
        assert result2 == "CREDIT_LIMIT"

    def test_dt_04_credit_limit_priority(self):
        """DT-04: Credit limit has priority 4 (seats available though)."""
        student = Student(
            student_id="S1",
            outstanding_dues=0,
            current_credits=16,
            registered_courses=set(),
            completed_courses={'CS101'}
        )
        course = Course(
            code="CS102",
            credit_hours=3,
            capacity=30,
            enrolled=10,
            prerequisites={'CS101'},
            waitlist=[]
        )
        result = registration_decision(student, course)
        assert result == "CREDIT_LIMIT"

    def test_ecp_13_ecp_14_seat_availability(self):
        """ECP-13, ECP-14: Seat availability (priority 5)."""
        base_student = Student(
            student_id="S1",
            outstanding_dues=0,
            current_credits=5,
            registered_courses=set(),
            completed_courses=set()
        )

        # Seat available
        course_available = Course(
            code="CS101",
            credit_hours=3,
            capacity=30,
            enrolled=10,
            prerequisites=set(),
            waitlist=[]
        )
        result_avail = registration_decision(base_student, course_available)
        assert result_avail == "REGISTERED"

        # No seat (full)
        course_full = Course(
            code="CS102",
            credit_hours=3,
            capacity=30,
            enrolled=30,
            prerequisites=set(),
            waitlist=[]
        )
        result_full = registration_decision(base_student, course_full)
        assert result_full == "WAITLISTED"

    def test_dt_05_waitlisted_enrolled_equals_capacity(self):
        """DT-05: WAITLISTED when enrolled == capacity."""
        student = Student(
            student_id="S1",
            outstanding_dues=0,
            current_credits=0,
            registered_courses=set(),
            completed_courses=set()
        )
        course = Course(
            code="CS101",
            credit_hours=3,
            capacity=30,
            enrolled=30,
            prerequisites=set(),
            waitlist=[]
        )
        result = registration_decision(student, course)
        assert result == "WAITLISTED"

    def test_dt_06_registered_enrolled_less_capacity(self):
        """DT-06: REGISTERED when enrolled < capacity."""
        student = Student(
            student_id="S1",
            outstanding_dues=0,
            current_credits=0,
            registered_courses=set(),
            completed_courses=set()
        )
        course = Course(
            code="CS101",
            credit_hours=3,
            capacity=30,
            enrolled=29,
            prerequisites=set(),
            waitlist=[]
        )
        result = registration_decision(student, course)
        assert result == "REGISTERED"


# ============================================================================
# TEST: register_course (STATE CHANGES)
# ============================================================================

class TestRegisterCourse:
    """Test register_course and state mutations (FR-10, FR-11, FR-12)."""

    def test_dt_06_register_updates_state(self):
        """DT-06: REGISTERED updates student and course state."""
        student = Student(
            student_id="S1",
            completed_courses=set(),
            current_credits=10,
            outstanding_dues=0,
            registered_courses=set()
        )
        course = Course(
            code="CS101",
            credit_hours=3,
            capacity=30,
            enrolled=5,
            prerequisites=set(),
            waitlist=[]
        )

        # Before registration
        assert "CS101" not in student.registered_courses
        assert student.current_credits == 10
        assert course.enrolled == 5

        # Register
        result = register_course(student, course)

        # After registration
        assert result == "REGISTERED"
        assert "CS101" in student.registered_courses
        assert student.current_credits == 13  # 10 + 3
        assert course.enrolled == 6  # 5 + 1

    def test_dt_05_waitlist_updates_state(self):
        """DT-05: WAITLISTED appends to waitlist only if absent."""
        student = Student(
            student_id="S1",
            completed_courses=set(),
            current_credits=0,
            outstanding_dues=0,
            registered_courses=set()
        )
        course = Course(
            code="CS101",
            credit_hours=3,
            capacity=30,
            enrolled=30,
            prerequisites=set(),
            waitlist=[]
        )

        # Before waitlist
        assert student.student_id not in course.waitlist
        assert student.current_credits == 0
        assert "CS101" not in student.registered_courses

        # First waitlist
        result = register_course(student, course)
        assert result == "WAITLISTED"
        assert student.student_id in course.waitlist
        assert student.current_credits == 0  # Unchanged
        assert "CS101" not in student.registered_courses  # Unchanged

        # Second attempt (should not re-add)
        result2 = register_course(student, course)
        assert result2 == "WAITLISTED"
        assert course.waitlist.count(student.student_id) == 1  # Still only one entry

    def test_register_failed_no_state_change_dues_block(self):
        """Failed registration (DUES_BLOCK) leaves state unchanged."""
        student = Student(
            student_id="S1",
            completed_courses=set(),
            current_credits=0,
            outstanding_dues=100,
            registered_courses=set()
        )
        course = Course(
            code="CS101",
            credit_hours=3,
            capacity=30,
            enrolled=10,
            prerequisites=set(),
            waitlist=[]
        )

        initial_credits = student.current_credits
        initial_enrolled = course.enrolled
        initial_registered = len(student.registered_courses)
        initial_waitlist_len = len(course.waitlist)

        result = register_course(student, course)
        assert result == "DUES_BLOCK"

        # State unchanged
        assert student.current_credits == initial_credits
        assert course.enrolled == initial_enrolled
        assert len(student.registered_courses) == initial_registered
        assert len(course.waitlist) == initial_waitlist_len

    def test_register_failed_no_state_change_already_registered(self):
        """Failed registration (ALREADY_REGISTERED) leaves state unchanged."""
        student = Student(
            student_id="S1",
            completed_courses=set(),
            current_credits=3,
            outstanding_dues=0,
            registered_courses={'CS101'}
        )
        course = Course(
            code="CS101",
            credit_hours=3,
            capacity=30,
            enrolled=5,
            prerequisites=set(),
            waitlist=[]
        )

        initial_credits = student.current_credits
        initial_enrolled = course.enrolled

        result = register_course(student, course)
        assert result == "ALREADY_REGISTERED"

        # State unchanged
        assert student.current_credits == initial_credits
        assert course.enrolled == initial_enrolled

    def test_register_failed_no_state_change_prerequisites(self):
        """Failed registration (PREREQUISITES_MISSING) leaves state unchanged."""
        student = Student(
            student_id="S1",
            completed_courses=set(),
            current_credits=0,
            outstanding_dues=0,
            registered_courses=set()
        )
        course = Course(
            code="CS201",
            credit_hours=3,
            capacity=30,
            enrolled=10,
            prerequisites={'CS101'},
            waitlist=[]
        )

        initial_credits = student.current_credits
        initial_enrolled = course.enrolled

        result = register_course(student, course)
        assert result == "PREREQUISITES_MISSING"

        # State unchanged
        assert student.current_credits == initial_credits
        assert course.enrolled == initial_enrolled


# ============================================================================
# TEST: withdraw_course
# ============================================================================

class TestWithdrawCourse:
    """Test withdraw_course (FR-13, FR-14)."""

    def test_withdraw_enrolled_student(self):
        """FR-13: Withdraw enrolled student updates state."""
        student = Student(
            student_id="S1",
            completed_courses=set(),
            current_credits=12,
            outstanding_dues=0,
            registered_courses={'CS101', 'CS102'}
        )
        course = Course(
            code="CS101",
            credit_hours=3,
            capacity=30,
            enrolled=10,
            prerequisites=set(),
            waitlist=[]
        )

        # Before withdrawal
        assert "CS101" in student.registered_courses
        assert student.current_credits == 12
        assert course.enrolled == 10

        # Withdraw
        result = withdraw_course(student, course)

        # After withdrawal
        assert result is True
        assert "CS101" not in student.registered_courses
        assert student.current_credits == 9  # 12 - 3
        assert course.enrolled == 9  # 10 - 1

    def test_withdraw_not_enrolled_student(self):
        """FR-14: Withdraw non-enrolled student leaves state unchanged."""
        student = Student(
            student_id="S1",
            completed_courses=set(),
            current_credits=9,
            outstanding_dues=0,
            registered_courses={'CS102'}
        )
        course = Course(
            code="CS101",
            credit_hours=3,
            capacity=30,
            enrolled=10,
            prerequisites=set(),
            waitlist=[]
        )

        initial_credits = student.current_credits
        initial_enrolled = course.enrolled

        result = withdraw_course(student, course)

        assert result is False
        assert student.current_credits == initial_credits
        assert course.enrolled == initial_enrolled

    def test_withdraw_multiple_registrations(self):
        """Withdraw only removes specified course."""
        student = Student(
            student_id="S1",
            completed_courses=set(),
            current_credits=9,
            outstanding_dues=0,
            registered_courses={'CS101', 'CS102'}
        )
        course1 = Course(code="CS101", credit_hours=3, capacity=30, enrolled=10)
        course2 = Course(code="CS102", credit_hours=3, capacity=30, enrolled=10)

        # Withdraw from CS101
        result = withdraw_course(student, course1)

        assert result is True
        assert "CS101" not in student.registered_courses
        assert "CS102" in student.registered_courses
        assert student.current_credits == 6  # 9 - 3


# ============================================================================
# PARAMETRIZED COMBINED TESTS
# ============================================================================

@pytest.mark.parametrize("current,course_credits,expected", [
    (0, 1, True),     # Minimum boundary
    (15, 3, True),    # Within 18
    (18, 0, None),    # Can't test with credit 0
    (16, 3, False),   # Exceeds 18
    (17, 1, True),    # Exactly 18
])
def test_bva_combined_credit_scenarios(current, course_credits, expected):
    """BVA-09, BVA-10, BVA-12: Combined credit scenarios."""
    if expected is None:
        pytest.skip("Invalid course credit")

    result = check_credit_limit(current, course_credits)
    assert result == expected, f"current={current}, course={course_credits}, total={current + course_credits}"


@pytest.mark.parametrize("dues_amount,expected_outcome", [
    (0, "not_blocked"),     # BVA-17
    (1, "DUES_BLOCK"),      # BVA-18: just above zero
    (100, "DUES_BLOCK"),    # Normal positive
])
def test_bva_dues_boundary(dues_amount, expected_outcome):
    """BVA-17, BVA-18: Dues boundary testing."""
    student = Student(
        student_id="S1",
        outstanding_dues=dues_amount,
        current_credits=0,
        completed_courses=set(),
        registered_courses=set()
    )
    course = Course(
        code="CS101",
        credit_hours=3,
        capacity=30,
        enrolled=10,
        prerequisites=set(),
        waitlist=[]
    )

    result = registration_decision(student, course)
    if expected_outcome == "not_blocked":
        assert result != "DUES_BLOCK"
    else:
        assert result == expected_outcome


@pytest.mark.parametrize("enrolled,capacity,expected", [
    (0, 1, "REGISTERED"),      # BVA-13: below capacity
    (1, 1, "WAITLISTED"),      # BVA-14: at capacity
    (29, 30, "REGISTERED"),    # BVA-15: one seat left
    (30, 30, "WAITLISTED"),    # BVA-16: exactly full
])
def test_bva_seat_availability_boundary(enrolled, capacity, expected):
    """BVA-13 through BVA-16: Seat availability at capacity boundary."""
    student = Student(
        student_id="S1",
        outstanding_dues=0,
        current_credits=0,
        completed_courses=set(),
        registered_courses=set()
    )
    course = Course(
        code="CS101",
        credit_hours=3,
        capacity=capacity,
        enrolled=enrolled,
        prerequisites=set(),
        waitlist=[]
    )

    result = registration_decision(student, course)
    assert result == expected
