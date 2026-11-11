"""Generate decision table in Excel format."""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Decision Table"

# Title
ws['A1'] = "Decision Table for registration_decision()"
ws['A1'].font = Font(bold=True, size=12)

# Conditions header
ws['A3'] = "CONDITIONS (in priority order per FR-09):"
ws['A3'].font = Font(bold=True, size=11)

conditions = [
    "1. Outstanding dues > 0 (FR-04, FR-15)",
    "2. Already registered in course (FR-05)",
    "3. Prerequisites not satisfied (FR-06)",
    "4. Credit limit exceeded (FR-07)",
    "5. Seat not available (enrolled == capacity) (FR-08)",
]
for idx, cond in enumerate(conditions, 4):
    ws[f'A{idx}'] = cond

# Decision table starts at row 10
row = 10
headers = ["Rule", "Dues\n(>0)", "Already\nReg", "Prereqs\nSat", "Credit\nLimit OK", "Seats\nAvail", "Expected Outcome", "Test ID"]
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=row, column=col, value=header)
    cell.font = Font(bold=True, color="FFFFFF", size=10)
    cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

# Decision table data (Y=True, N=False, - = don't care / short-circuit)
decisions = [
    # Format: Rule#, Dues, AlreadyReg, Prereqs, CreditLimit, Seats, Outcome, TestID
    (1, "Y", "-", "-", "-", "-", "DUES_BLOCK (short-circuit)", "DT-01"),
    (2, "N", "Y", "-", "-", "-", "ALREADY_REGISTERED (short-circuit)", "DT-02"),
    (3, "N", "N", "N", "-", "-", "PREREQUISITES_MISSING (short-circuit)", "DT-03"),
    (4, "N", "N", "Y", "N", "-", "CREDIT_LIMIT (short-circuit)", "DT-04"),
    (5, "N", "N", "Y", "Y", "N", "WAITLISTED (enrolled==capacity)", "DT-05"),
    (6, "N", "N", "Y", "Y", "Y", "REGISTERED (enrolled<capacity)", "DT-06"),
    # Edge cases and priority interactions
    (7, "Y", "Y", "N", "N", "N", "DUES_BLOCK (priority beats all)", "DT-07"),
    (8, "N", "Y", "N", "N", "Y", "ALREADY_REGISTERED (priority 2)", "DT-08"),
    (9, "N", "N", "N", "N", "Y", "PREREQUISITES_MISSING (priority 3)", "DT-09"),
    (10, "N", "N", "Y", "Y", "N (>cap)", "ValueError: Invalid capacity", "DT-10"),
]

for idx, data in enumerate(decisions, row + 1):
    for col, value in enumerate(data, 1):
        cell = ws.cell(row=idx, column=col, value=value)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        if col == 1:  # Rule number
            cell.font = Font(bold=True)
        # Highlight decision column
        if col == 7:
            cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")

# Set column widths
ws.column_dimensions['A'].width = 10
ws.column_dimensions['B'].width = 8
ws.column_dimensions['C'].width = 8
ws.column_dimensions['D'].width = 10
ws.column_dimensions['E'].width = 10
ws.column_dimensions['F'].width = 10
ws.column_dimensions['G'].width = 30
ws.column_dimensions['H'].width = 8

# Notes section
notes_row = row + len(decisions) + 3
ws[f'A{notes_row}'] = "NOTES:"
ws[f'A{notes_row}'].font = Font(bold=True)
ws[f'A{notes_row + 1}'] = "- Y = condition is True, N = condition is False, - = don't care (short-circuit)"
ws[f'A{notes_row + 2}'] = "- Each rule shows the first outcome that applies based on priority order (FR-09)"
ws[f'A{notes_row + 3}'] = "- Registration is non-mutating per FR-10; register_course applies the decision"
ws[f'A{notes_row + 4}'] = "- Invalid parameter validation per FR-15: dues first, then capacity/enrollment"

# Coverage notes
coverage_row = notes_row + 6
ws[f'A{coverage_row}'] = "TEST COVERAGE:"
ws[f'A{coverage_row}'].font = Font(bold=True)
ws[f'A{coverage_row + 1}'] = "✓ Every distinct outcome: REGISTERED, WAITLISTED, DUES_BLOCK, ALREADY_REGISTERED, PREREQUISITES_MISSING, CREDIT_LIMIT"
ws[f'A{coverage_row + 2}'] = "✓ Priority interactions: Rules 7-9 demonstrate condition priority enforcement"
ws[f'A{coverage_row + 3}'] = "✓ Boundary conditions covered in BVA sheet"
ws[f'A{coverage_row + 4}'] = "✓ Invalid inputs covered in ECP and BVA sheets"

wb.save(r"C:\Users\Ahmad Kazmi\Downloads\SQE_Assignment2_Student_Starter\SQE_Assignment2_Registration_Student\docs\decision_table.xlsx")
print("✓ Created: docs/decision_table.xlsx")
print(f"  - {len(decisions)} decision rules with comprehensive outcome coverage")
