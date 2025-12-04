import math
import os
from io import BytesIO

import streamlit as st
from fpdf import FPDF

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Tube Bending Calculator",
    layout="wide"
)

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def safe_sidebar_image(path: str, caption: str):
    """Show image in sidebar if it exists, otherwise show a small note."""
    if os.path.exists(path):
        st.sidebar.image(path, caption=caption, use_container_width=True)
    else:
        st.sidebar.markdown(f"*Image not found: `{path}`*")


MATERIALS = {
    "Copper": {"E": 110_000.0, "yield": 200.0},        # MPa, rough typical values
    "Carbon Steel": {"E": 210_000.0, "yield": 250.0},
    "Aluminium": {"E": 70_000.0, "yield": 120.0},
}


def compute_bend_parameters(od_mm, wall_mm, angle_deg, straight_mm, d_of_bend, material_name):
    """Compute Wall Factor, CLR, arc length, total length, stress, etc."""
    props = MATERIALS[material_name]
    E = props["E"]
    sigma_y = props["yield"]

    wall_eff = max(wall_mm, 1e-6)
    clr = d_of_bend * od_mm                   # CLR = D * OD
    wf = od_mm / wall_eff                     # Wall Factor
    mbr = wf * od_mm                          # a common 'minimum bend radius' heuristic

    theta_rad = math.radians(angle_deg)
    arc_len = clr * theta_rad                 # bend arc length along neutral axis
    total_len = straight_mm + arc_len

    # very simplified outer-fibre bending stress: sigma = E * (epsilon),
    # epsilon ~ (t/2) / CLR  (outer fibre strain)
    stress = E * ((wall_mm / 2.0) / max(clr, 1e-6)) / 1000.0  # convert to MPa-ish scale
    fos = sigma_y / stress if stress > 0 else float("inf")

    return {
        "wf": wf,
        "clr": clr,
        "mbr": mbr,
        "arc_len": arc_len,
        "total_len": total_len,
        "stress": stress,
        "fos": fos,
    }


def generate_pdf_report(inputs, results):
    """Return a PDF report as bytes."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Tube Bending Report", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Material          : {inputs['material']}", ln=True)
    pdf.cell(0, 8, f"Tube O.D.         : {inputs['od']:.2f} mm", ln=True)
    pdf.cell(0, 8, f"Wall Thickness    : {inputs['wall']:.2f} mm", ln=True)
    pdf.cell(0, 8, f"Bend Angle        : {inputs['angle']:.2f} °", ln=True)
    pdf.cell(0, 8, f"Straight Length   : {inputs['straight']:.2f} mm", ln=True)
    pdf.cell(0, 8, f'"D" of Bend (CLR/OD): {inputs["d_of_bend"]:.2f}', ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Calculated Values", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Wall Factor (WF = OD / t)         : {results['wf']:.2f}", ln=True)
    pdf.cell(0, 8, f"Center-Line Radius (CLR)          : {results['clr']:.2f} mm", ln=True)
    pdf.cell(0, 8, f"Minimum Bend Radius (WF × OD)     : {results['mbr']:.2f} mm", ln=True)
    pdf.cell(0, 8, f"Bend Arc Length                   : {results['arc_len']:.2f} mm", ln=True)
    pdf.cell(0, 8, f"Approx. Total Tube Length         : {results['total_len']:.2f} mm", ln=True)
    pdf.cell(0, 8, f"Simplified Outer-Fibre Stress     : {results['stress']:.2f} MPa", ln=True)
    pdf.cell(0, 8, f"Factor of Safety vs Yield (FoS)   : {results['fos']:.2f}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Key Formulas (from Bend Manual concepts)", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        6,
        "Wall Factor (WF) = O.D. / Wall\n"
        '"D" of Bend      = CLR / O.D.\n'
        "CLR              = D × O.D.\n"
        "Bend Arc Length  = CLR × θ(rad)\n"
        "Total Length     = Straight Length + Bend Arc Length\n"
        "Outer-fibre strain ≈ (t/2) / CLR → Stress ≈ E × strain\n\n"
        "NOTE: Stress and FoS here are simplified estimates for study / comparison, "
        "not for final certification."
    )

    pdf_bytes = pdf.output(dest="S").encode("latin-1", "replace")
    return pdf_bytes


# -------------------------------------------------
# SIDEBAR – FIGURES FROM BEND MANUAL
# -------------------------------------------------
st.sidebar.title("Tube Bending Reference")

safe_sidebar_image("fig1_compression_bending.png", "Fig. 1 – Compression Bending")
safe_sidebar_image("fig2_press_bending.png", "Fig. 2 – Press Bending")
safe_sidebar_image("fig3_rotary_draw_bending.png", "Fig. 3 – Rotary Draw Bending")
st.sidebar.markdown("---")
safe_sidebar_image("fig4_reaction_tube.png", "Fig. 4 – Tube Reaction to Bending")
safe_sidebar_image("fig5_wall_factor_clr.png", "Fig. 5 – Wall Factor & CLR")
safe_sidebar_image("fig6_contoured_grooves.png", "Fig. 6 – Contoured Tube Grooves")
safe_sidebar_image("fig7_ram_wing_dies.png", "Fig. 7 – Ram & Wing Dies")

st.sidebar.markdown(
    """
These figures come from your **Bend Manual** and show how wall thinning,
neutral axis, tooling and bend type affect quality.
"""
)

# -------------------------------------------------
# MAIN UI
# -------------------------------------------------
st.title("Tube Bending Calculator (Based on Bend Manual Concepts)")

st.markdown(
    """
Use this tool to calculate **basic bend geometry** and see the
relationships used in the bending manuals: **Wall Factor, “D” of bend,
Center-Line Radius (CLR), arc length, total length and a simplified stress check.**
"""
)

# ---------------- INPUTS ----------------
st.header("1️⃣ Input Parameters")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    material = st.selectbox("Material", list(MATERIALS.keys()), index=0)

with col2:
    od = st.number_input("Tube O.D. (mm)", min_value=1.0, value=10.0, step=0.1)

with col3:
    wall = st.number_input("Wall Thickness (mm)", min_value=0.1, value=1.0, step=0.1)

with col4:
    angle = st.number_input("Bend Angle (°)", min_value=1.0, max_value=180.0, value=90.0, step=1.0)

with col5:
    straight_len = st.number_input("Straight Length before Bend (mm)", min_value=1.0, value=500.0, step=1.0)

st.markdown(
    """
From **Figure 5**:  
- **Wall Factor (WF)** = O.D. ÷ Wall  
- **“D” of Bend** = CLR ÷ O.D.  
"""
)

d_of_bend = st.selectbox(
    '"D" of Bend (CLR / O.D.)',
    [2.0, 2.5, 3.0, 4.0, 5.0],
    index=2,
    help="Tighter bends → lower D (e.g. 2×D); gentler bends → higher D (e.g. 4–5×D).",
)

# ---------------- CALCULATIONS ----------------
st.header("2️⃣ Calculated Values")

results = compute_bend_parameters(od, wall, angle, straight_len, d_of_bend, material)

colA, colB, colC = st.columns(3)
with colA:
    st.metric("Wall Factor WF = OD / t", f"{results['wf']:.2f}")
with colB:
    st.metric("Center-Line Radius CLR (mm)", f"{results['clr']:.2f}")
with colC:
    st.metric("Minimum Bend Radius (WF × OD)", f"{results['mbr']:.2f}")

colD, colE = st.columns(2)
with colD:
    st.metric("Bend Arc Length (mm)", f"{results['arc_len']:.2f}")
with colE:
    st.metric("Approx. Total Tube Length (mm)", f"{results['total_len']:.2f}")

st.metric("Simplified Outer-Fibre Stress (MPa)", f"{results['stress']:.2f}")
st.metric("Factor of Safety vs Yield", f"{results['fos']:.2f}")

# ---------------- FORMULA REFERENCE ----------------
st.header("3️⃣ Formula & Concept Reference")

with st.expander("Wall Factor & “D” of Bend (Figure 5)", expanded=True):
    st.latex(r"WF = \frac{OD}{t}")
    st.latex(r"D = \frac{CLR}{OD}")
    st.markdown(
        """
- Higher **WF** → thinner wall → more risk of flattening, wrinkling, buckling.  
- For a chosen **“D of bend”**, center-line radius is:

\\[
CLR = D \\times OD
\\]

Smaller **D** → tighter bend (harder, needs better tooling).  
Larger **D** → easier bend, less distortion.
"""
    )

with st.expander("Bend Geometry & Neutral Axis (Figure 4)"):
    st.latex(r"L_{bend} = CLR \times \theta_{rad}")
    st.latex(r"L_{total} \approx L_{straight} + L_{bend}")
    st.markdown(
        """
During bending:

- Outer wall is in **tension** → *thins out*.  
- Inner wall is in **compression** → *builds up*.  
- Between them lies the **neutral axis** where length does not change.

For length calculations we follow the **center line** (using CLR).
"""
    )

with st.expander("Bending Stress (very simplified)"):
    st.latex(r"\epsilon_{outer} \approx \frac{t/2}{CLR}")
    st.latex(r"\sigma_{outer} \approx E \times \epsilon_{outer}")
    st.markdown(
        """
This is a **teaching-level approximation**:

- It ignores ovalisation, local buckling, mandrel support, etc.
- Always validate final designs with detailed analysis, tooling supplier data,
  and physical try-out.
"""
    )

with st.expander("Bending Methods (Figures 1–3, 6–7)"):
    st.markdown(
        """
**Compression Bending (Fig. 1)**  
- Tube is pushed around a bending form.  
- Simple and cheap, but more cross-section distortion.

**Press Bending (Fig. 2)**  
- A matching die presses the tube into a radius.  
- Good for simple, large-radius bends.

**Rotary Draw Bending (Fig. 3)**  
- Tube is clamped to a **bend die** and drawn around it.  
- Best precision for CLR, D of bend, and low ovality.  
- Often used with mandrel, wiper die, pressure die (see Figs. 6–7).

**Contoured Grooves & Ram/Wing Dies (Figs. 6–7)**  
- Groove shape must suit the O.D. and CLR.  
- Correct die selection reduces marking, flattening and slipping.
"""
    )

# ---------------- PDF REPORT ----------------
st.header("4️⃣ Download Report")

inputs_dict = {
    "material": material,
    "od": od,
    "wall": wall,
    "angle": angle,
    "straight": straight_len,
    "d_of_bend": d_of_bend,
}

pdf_bytes = generate_pdf_report(inputs_dict, results)

st.download_button(
    label="📄 Download Tube Bending PDF Report",
    data=pdf_bytes,
    file_name="tube_bending_report.pdf",
    mime="application/pdf",
)
