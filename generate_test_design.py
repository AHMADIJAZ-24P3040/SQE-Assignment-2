"""Generate test design sheets (ECP, BVA, Decision Table) in Excel format."""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Create workbook
wb = openpyxl.Workbook()
wb.remove(wb.active)

# ============================================================================
# ECP SHEET
# ============================================================================
ecp_sheet = wb.create_sheet("ECP")
ecp_headers = ["Req ID", "Class (Valid/Invalid)", "Representative Input", "Expected Output", "Test ID"]
for col, header in enumerate(ecp_headers, 1):
    cell = ecp_sheet.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

ecp_data = [
    # Dues-related ECP
    ("FR-04", "Valid: no dues", "student.outstanding_dues=0", "Proceeds to next check", "ECP-01"),
    ("FR-04", "Valid: positive dues", "student.outstanding_dues=100", "DUES_BLOCK", "ECP-02"),
    ("FR-15", "Invalid: negative dues", "student.outstanding_dues=-1", "ValueError('Invalid dues')", "ECP-03"),

    # Prerequisites ECP
    ("FR-03,FR-06", "Valid: all satisfied", "completed={'CS101'}, required={'CS101'}", "True", "ECP-04"),
    ("FR-03,FR-06", "Valid: partial satisfied", "completed={'CS101'}, required={'CS101','MATH101'}", "False", "ECP-05"),
    ("FR-03,FR-06", "Valid: none required", "completed={'CS101'}, required={}", "True", "ECP-06"),
    ("FR-03,FR-06", "Valid: none completed", "completed={}, required={'CS101'}", "False", "ECP-07"),

    # Already registered ECP
    ("FR-05", "Valid: not registered", "course not in registered_courses", "Proceeds to next check", "ECP-08"),
    ("FR-05", "Valid: already registered", "course in registered_courses", "ALREADY_REGISTERED", "ECP-09"),

    # Credit limit ECP
    ("FR-01,FR-07", "Valid: within limit", "current_credits=15, course_credits=3 (total=18)", "Proceeds to next check", "ECP-10"),
    ("FR-01,FR-07", "Valid: exactly at limit", "current_credits=18, course_credits=0", "N/A (credits 0 invalid)", "ECP-11"),
    ("FR-01,FR-07", "Invalid: exceed limit", "current_credits=16, course_credits=3 (total=19)", "CREDIT_LIMIT", "ECP-12"),

    # Seat availability ECP
    ("FR-08", "Valid: seat available", "enrolled=10, capacity=30", "REGISTERED", "ECP-13"),
    ("FR-08", "Valid: full (no seat)", "enrolled=30, capacity=30", "WAITLISTED", "ECP-14"),

    # Course credits validation ECP
    ("FR-02", "Valid: min credit", "course_credits=1", "Proceeds to next check", "ECP-15"),
    ("FR-02", "Valid: max credit", "course_credits=4", "Proceeds to next check", "ECP-16"),
    ("FR-02", "Invalid: too low", "course_credits=0", "ValueError('Invalid course credits')", "ECP-17"),
    ("FR-02", "Invalid: too high", "course_credits=5", "ValueError('Invalid course credits')", "ECP-18"),

    # Current credits validation ECP
    ("FR-02", "Valid: min current", "current_credits=0", "Proceeds to next check", "ECP-19"),
    ("FR-02", "Valid: max current", "current_credits=18", "Proceeds to next check", "ECP-20"),
    ("FR-02", "Invalid: below min", "current_credits=-1", "ValueError('Invalid current credits')", "ECP-21"),
    ("FR-02", "Invalid: above max", "current_credits=19", "ValueError('Invalid current credits')", "ECP-22"),

    # Capacity/Enrollment validation ECP
    ("FR-15", "Valid: normal", "capacity=30, enrolled=15", "Proceeds (no validation error)", "ECP-23"),
    ("FR-15", "Invalid: capacity < 1", "capacity=0, enrolled=0", "ValueError('Invalid capacity or enrollment')", "ECP-24"),
    ("FR-15", "Invalid: enrolled < 0", "capacity=30, enrolled=-1", "ValueError('Invalid capacity or enrollment')", "ECP-25"),
    ("FR-15", "Invalid: enrolled > capacity", "capacity=30, enrolled=31", "ValueError('Invalid capacity or enrollment')", "ECP-26"),
]

for row, data in enumerate(ecp_data, 2):
    for col, value in enumerate(data, 1):
        cell = ecp_sheet.cell(row=row, column=col, value=value)
        cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

# Set column widths
ecp_sheet.column_dimensions['A'].width = 12
ecp_sheet.column_dimensions['B'].width = 20
ecp_sheet.column_dimensions['C'].width = 40
ecp_sheet.column_dimensions['D'].width = 35
ecp_sheet.column_dimensions['E'].width = 12

# ============================================================================
# BVA SHEET
# ============================================================================
bva_sheet = wb.create_sheet("BVA")
bva_headers = ["Req ID", "Variable", "Boundary Value", "Valid/Invalid", "Expected Output", "Test ID"]
for col, header in enumerate(bva_headers, 1):
    cell = bva_sheet.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

bva_data = [
    # Current credits boundary
    ("FR-02", "current_credits", 0, "Valid", "Min boundary (no validation error)", "BVA-01"),
    ("FR-02", "current_credits", 18, "Valid", "Max boundary (no validation error)", "BVA-02"),
    ("FR-02", "current_credits", -1, "Invalid", "Just below min: ValueError", "BVA-03"),
    ("FR-02", "current_credits", 19, "Invalid", "Just above max: ValueError", "BVA-04"),

    # Course credits boundary
    ("FR-02", "course_credits", 1, "Valid", "Min boundary (no validation error)", "BVA-05"),
    ("FR-02", "course_credits", 4, "Valid", "Max boundary (no validation error)", "BVA-06"),
    ("FR-02", "course_credits", 0, "Invalid", "Just below min: ValueError", "BVA-07"),
    ("FR-02", "course_credits", 5, "Invalid", "Just above max: ValueError", "BVA-08"),

    # Combined credit limit (18 total)
    ("FR-01,FR-07", "current+course", "15+3=18", "Valid", "Exactly at limit: Proceeds", "BVA-09"),
    ("FR-01,FR-07", "current+course", "15+4=19", "Invalid", "Exceeds limit: CREDIT_LIMIT", "BVA-10"),
    ("FR-01,FR-07", "current+course", "0+18", "Invalid", "18 credits in single course: N/A", "BVA-11"),
    ("FR-01,FR-07", "current+course", "18+1=19", "Invalid", "Already at max, any course: CREDIT_LIMIT", "BVA-12"),

    # Seat availability (capacity boundary)
    ("FR-08", "enrolled vs capacity", "enrolled=0, capacity=1", "Valid", "Below capacity: REGISTERED", "BVA-13"),
    ("FR-08", "enrolled vs capacity", "enrolled=1, capacity=1", "Valid", "At capacity: WAITLISTED", "BVA-14"),
    ("FR-08", "enrolled vs capacity", "enrolled=29, capacity=30", "Valid", "One seat left: REGISTERED", "BVA-15"),
    ("FR-08", "enrolled vs capacity", "enrolled=30, capacity=30", "Valid", "Exactly full: WAITLISTED", "BVA-16"),

    # Dues boundary (positive threshold)
    ("FR-04", "outstanding_dues", 0, "Valid", "Zero dues: Proceeds", "BVA-17"),
    ("FR-04", "outstanding_dues", 1, "Valid", "Just above zero: DUES_BLOCK", "BVA-18"),
    ("FR-15", "outstanding_dues", -1, "Invalid", "Negative: ValueError", "BVA-19"),
]

for row, data in enumerate(bva_data, 2):
    for col, value in enumerate(data, 1):
        cell = bva_sheet.cell(row=row, column=col, value=value)
        cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

bva_sheet.column_dimensions['A'].width = 12
bva_sheet.column_dimensions['B'].width = 18
bva_sheet.column_dimensions['C'].width = 25
bva_sheet.column_dimensions['D'].width = 12
bva_sheet.column_dimensions['E'].width = 35
bva_sheet.column_dimensions['F'].width = 10

# ============================================================================
# DECISION TABLE SHEET
# ============================================================================
dt_sheet = wb.create_sheet("Decision Table")
dt_headers = ["Rule", "Dues", "Already Reg", "Prerequisites", "Credit Limit", "Seat Available", "Expected Outcome", "Test ID"]
for col, header in enumerate(dt_headers, 1):
    cell = dt_sheet.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

dt_data = [
    # Priority: dues, already reg, prerequisites, credit limit, availability (FR-09)
    (1, "Y (>0)", "N", "Y", "Y", "Y", "DUES_BLOCK", "DT-01"),
    (2, "Y (>0)", "Y", "Y", "Y", "Y", "DUES_BLOCK (stops at due)", "DT-02"),
    (3, "N", "Y", "Y", "Y", "Y", "ALREADY_REGISTERED", "DT-03"),
    (4, "N", "N", "N", "Y", "Y", "PREREQUISITES_MISSING", "DT-04"),
    (5, "N", "N", "Y", "N", "Y", "CREDIT_LIMIT", "DT-05"),
    (6, "N", "N", "Y", "Y", "N (enrolled=cap)", "WAITLISTED", "DT-06"),
    (7, "N", "N", "Y", "Y", "Y (enrolled<cap)", "REGISTERED", "DT-07"),
    # Edge cases
    (8, "N", "N", "Y", "Y", "Y (enrolled>cap invalid)", "ValueError", "DT-08"),
    (9, "Y", "N", "N", "N", "N", "DUES_BLOCK (priority 1)", "DT-09"),
    (10, "N", "Y", "N", "N", "N", "ALREADY_REGISTERED (priority 2)", "DT-10"),
]

for row, data in enumerate(dt_data, 2):
    for col, value in enumerate(data, 1):
        cell = dt_sheet.cell(row=row, column=col, value=value)
        cell.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)

for col in range(1, len(dt_headers) + 1):
    dt_sheet.column_dimensions[get_column_letter(col)].width = 14

# ============================================================================
# SUMMARY SHEET
# ============================================================================
summary_sheet = wb.create_sheet("Summary", 0)
summary_sheet['A1'] = "Test Design Summary"
summary_sheet['A1'].font = Font(bold=True, size=14)

summary_sheet['A3'] = "ECP Cases:"
summary_sheet['B3'] = f"{len(ecp_data)} cases (ECP-01 through ECP-{len(ecp_data):02d})"

summary_sheet['A4'] = "BVA Cases:"
summary_sheet['B4'] = f"{len(bva_data)} cases (BVA-01 through BVA-{len(bva_data):02d})"

summary_sheet['A5'] = "Decision Table Rules:"
summary_sheet['B5'] = f"{len(dt_data)} rules (DT-01 through DT-{len(dt_data):02d})"

summary_sheet['A7'] = "Total Unique Test Cases:"
summary_sheet['B7'] = len(ecp_data) + len(bva_data) + len(dt_data)

summary_sheet.column_dimensions['A'].width = 25
summary_sheet.column_dimensions['B'].width = 40

# Save
output_file = r"C:\Users\Ahmad Kazmi\Downloads\SQE_Assignment2_Student_Starter\SQE_Assignment2_Registration_Student\docs\blackbox_test_design.xlsx"
wb.save(output_file)
print(f"✓ Created: {output_file}")
print(f"  - ECP: {len(ecp_data)} cases")
print(f"  - BVA: {len(bva_data)} cases")
print(f"  - Decision Table: {len(dt_data)} rules")
