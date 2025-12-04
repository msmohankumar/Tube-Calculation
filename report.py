# report.py
from fpdf import FPDF

def generate_pdf(diameter, angle, bend_radius, total_length, filename="Tube_Bending_Report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Tube Bending Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, f"Tube Diameter: {diameter} mm")
    pdf.multi_cell(0, 10, f"Bend Angle: {angle}°")
    pdf.multi_cell(0, 10, f"Recommended Bend Radius: {bend_radius:.2f} mm")
    pdf.multi_cell(0, 10, f"Total Tube Length: {total_length:.2f} mm")
    pdf.output(filename)
