import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Page Configuration
st.set_page_config(
    page_title="Isango Engineering Intelligence Platform",
    page_icon="🏗️",
    layout="wide"
)

# Sidebar System Navigation
st.sidebar.title("🏗️ ISANGO PLATFORM")
st.sidebar.caption("CEMAC Engineering & Procurement Automation")

selected_module = st.sidebar.radio(
    "Select Operating Module:",
    [
        "🌊 Water Supply & Infrastructure Feasibility",
        "📑 Tender Engine & Bidding Dossier (DAO)",
        "🤝 Engineering AI Consulting Hub"
    ]
)

# ==============================================================================
# MODULE 1: WATER SUPPLY & INFRASTRUCTURE FEASIBILITY ENGINE
# ==============================================================================
if selected_module == "🌊 Water Supply & Infrastructure Feasibility":
    st.title("🌊 Infrastructure & Water Feasibility Engine")
    st.caption("Automated Hydraulic Assessment & System Sizing for CEMAC Regions")

    st.sidebar.header("1. Project Metadata")
    client_name = st.sidebar.text_input("Client / Municipality Name", "Kumba Urban Council")
    project_name = st.sidebar.text_input("Project Title", "Rural Water Supply Phase 1")
    currency_rate = st.sidebar.number_input("Pipe Unit Cost (XAF/meter)", value=3500, step=500)

    st.sidebar.header("2. Hydraulic Parameters")
    elevation_source = st.sidebar.number_input("Source Elevation (m)", value=450.0, step=1.0)
    elevation_target = st.sidebar.number_input("Storage Tank Elevation (m)", value=390.0, step=1.0)
    pipe_distance = st.sidebar.number_input("Pipeline Distance (m)", value=2500.0, step=100.0)
    pipe_diameter_mm = st.sidebar.selectbox("Pipe Inner Diameter (mm)", [50, 63, 75, 90, 110, 160], index=2)

    st.sidebar.header("3. Demand Parameters")
    population = st.sidebar.number_input("Target Population", value=3500, step=100)
    per_capita_demand = st.sidebar.number_input("Demand (L/person/day)", value=50, step=5)

    # Hydraulic Calculations Engine (Hazen-Williams Model)
    c_factor = 140.0
    daily_demand_m3 = (population * per_capita_demand) / 1000.0
    peak_flow_m3_s = (daily_demand_m3 * 2.0) / 86400.0
    pipe_diameter_m = pipe_diameter_mm / 1000.0
    available_head = elevation_source - elevation_target

    head_loss = (10.67 * pipe_distance * (peak_flow_m3_s ** 1.852)) / ((c_factor ** 1.852) * (pipe_diameter_m ** 4.87))
    net_head = available_head - head_loss
    is_gravity_feasible = net_head > 5.0

    if not is_gravity_feasible:
        required_lift_m = abs(net_head) + 10.0
        hydraulic_power_kw = (1000.0 * 9.81 * peak_flow_m3_s * required_lift_m) / (1000.0 * 0.65)
        solar_pv_kwp = hydraulic_power_kw * 1.65
    else:
        required_lift_m, hydraulic_power_kw, solar_pv_kwp = 0.0, 0.0, 0.0

    pipe_cost_xaf = pipe_distance * currency_rate
    fittings_contingency = pipe_cost_xaf * 0.15
    pump_solar_cost = (hydraulic_power_kw * 850000) + (solar_pv_kwp * 600000) if not is_gravity_feasible else 0
    civil_works_cost = 2500000
    total_estimated_xaf = pipe_cost_xaf + fittings_contingency + pump_solar_cost + civil_works_cost

    # Layout Output Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Daily Demand", f"{daily_demand_m3:.1f} m³/day")
    col2.metric("Available Head", f"{available_head:.1f} m")
    col3.metric("Friction Head Loss", f"{head_loss:.2f} m")
    col4.metric("Net Dynamic Pressure", f"{net_head:.2f} m")

    st.divider()
    c_left, c_right = st.columns([1, 1])

    with c_left:
        st.subheader("System Feasibility Evaluation")
        if is_gravity_feasible:
            st.success("✅ GRAVITY-FED SYSTEM IS FEASIBLE")
            st.write(f"Sufficient natural elevation drop (**{available_head:.1f} m**) overcomes pipe friction losses (**{head_loss:.2f} m**).")
        else:
            st.warning("⚡ POWERED / SOLAR PUMPING SYSTEM REQUIRED")
            st.write(f"* **Required Pump Power:** `{hydraulic_power_kw:.2f} kW`\n* **Solar PV Array Size:** `{solar_pv_kwp:.2f} kWp`")

        st.markdown(f"### **Estimated Budget:** `{total_estimated_xaf:,.0f} XAF`")

    with c_right:
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.plot([0, pipe_distance], [elevation_source, elevation_target], 'g-o', label='Ground Elevation Profile', linewidth=2)
        ax.plot([0, pipe_distance], [elevation_source, elevation_source - head_loss], 'r--', label='Hydraulic Grade Line', linewidth=2)
        ax.set_ylabel("Elevation (m)")
        ax.set_xlabel("Distance (m)")
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend()
        st.pyplot(fig)

    # PDF Report Generator
    def generate_pdf():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor("#0B3C5D"))
        story.append(Paragraph("ISANGO ENGINEERING SYSTEMS - FEASIBILITY REPORT", title_style))
        story.append(Paragraph(f"<b>Project:</b> {project_name} | <b>Client:</b> {client_name}", styles['Normal']))
        story.append(Spacer(1, 15))

        table_data = [
            ["Parameter", "Calculated Value"],
            ["Target Population", f"{population} Persons"],
            ["Daily Water Demand", f"{daily_demand_m3:.1f} m³/day"],
            ["Pipeline Length / Diameter", f"{pipe_distance} m / {pipe_diameter_mm} mm"],
            ["Available Static Head", f"{available_head:.1f} meters"],
            ["Calculated Friction Loss", f"{head_loss:.2f} meters"],
            ["System Recommendation", "GRAVITY-FED" if is_gravity_feasible else f"SOLAR PUMP ({solar_pv_kwp:.2f} kWp)"],
            ["Estimated Project Budget", f"{total_estimated_xaf:,.0f} XAF"]
        ]
        t = Table(table_data, colWidths=[200, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor("#0B3C5D")),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(t)
        story.append(Spacer(1, 15))
        story.append(Paragraph("<font size='8' color='gray'><b>DISCLAIMER:</b> Requires physical dry-season yield testing and RTK GPS topographic validation before detailed execution.</font>", styles['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer

    st.divider()
    st.download_button(
        label="📄 Download Official Feasibility Report (.PDF)",
        data=generate_pdf(),
        file_name=f"Feasibility_Study_{project_name.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

# ==============================================================================
# MODULE 2: TENDER ENGINE & BIDDING DOSSIER (DAO / COLEPS)
# ==============================================================================
elif selected_module == "📑 Tender Engine & Bidding Dossier (DAO)":
    st.title("📑 Tender Engine & Bidding Dossier (DAO)")
    st.caption("Automated Procurement Audit, Financial Sub-Details & BPU/DQE Generation")

    tender_tab1, tender_tab2, tender_tab3 = st.tabs([
        "📋 Administrative Audit (COLEPS / ARMP)",
        "💰 Financial Sub-Detail Engine (Sous-Détail des Prix)",
        "📄 Technical Methodology Generator"
    ])

    with tender_tab1:
        st.subheader("Administrative Document Compliance Tracker")
        col_a, col_b = st.columns(2)
        with col_a:
            tax_cert = st.date_input("Attestation de Non-Redevance (ANR) Date", datetime.date.today())
            cnps_cert = st.date_input("Attestation CNPS Date", datetime.date.today())
            rccm_num = st.text_input("RCCM Register Number", "RC/KBA/2025/B/012")
        with col_b:
            tender_bond = st.number_input("Tender Bond Amount (XAF)", value=500000, step=50000)
            submission_date = st.date_input("Tender Submission Deadline", datetime.date.today() + datetime.timedelta(days=14))

        tax_age_days = (submission_date - tax_cert).days
        cnps_age_days = (submission_date - cnps_cert).days

        st.subheader("Compliance Audit Status")
        if tax_age_days > 90:
            st.error(f"❌ **Tax Certificate Expired!** ANR age will be {tax_age_days} days on submission date (Limit: 90 days). Re-issue immediately.")
        else:
            st.success(f"✅ Tax Certificate Valid ({tax_age_days} days old on submission date).")

        if cnps_age_days > 90:
            st.error(f"❌ **CNPS Certificate Expired!** CNPS age will be {cnps_age_days} days on submission date (Limit: 90 days).")
        else:
            st.success(f"✅ CNPS Certificate Valid ({cnps_age_days} days old on submission date).")

    with tender_tab2:
        st.subheader("Financial Breakdown Engine (Sous-Détail des Prix)")
        col_f1, col_f2, col_f3 = st.columns(3)
        overhead_pct = col_f1.number_input("Overhead Expenses (Frais Généraux %)", value=15.0, step=1.0) / 100.0
        margin_pct = col_f2.number_input("Profit Margin (Bénéfice %)", value=12.0, step=1.0) / 100.0
        tva_pct = col_f3.number_input("TVA Tax Rate (%)", value=19.25, step=0.25) / 100.0

        default_items = pd.DataFrame([
            {"Code": "101", "Designation": "Site Clearance & Earthworks", "Unit": "m²", "Quantity": 1500.0, "Direct_Labor_XAF": 350.0, "Materials_XAF": 150.0, "Equipment_XAF": 200.0},
            {"Code": "201", "Designation": "Class 350 Concrete Foundations", "Unit": "m³", "Quantity": 120.0, "Direct_Labor_XAF": 15000.0, "Materials_XAF": 65000.0, "Equipment_XAF": 10000.0},
            {"Code": "202", "Designation": "High Yield Rebar Reinforcement", "Unit": "kg", "Quantity": 9500.0, "Direct_Labor_XAF": 120.0, "Materials_XAF": 620.0, "Equipment_XAF": 30.0},
            {"Code": "301", "Designation": "110mm HDPE Pipe Laying", "Unit": "m", "Quantity": 2500.0, "Direct_Labor_XAF": 800.0, "Materials_XAF": 3200.0, "Equipment_XAF": 300.0}
        ])

        edited_df = st.data_editor(default_items, num_rows="dynamic", use_container_width=True)

        # Mathematical Pricing Logic
        edited_df["Debourse_Sec_HT"] = edited_df["Direct_Labor_XAF"] + edited_df["Materials_XAF"] + edited_df["Equipment_XAF"]
        edited_df["Unit_Price_HT"] = edited_df["Debourse_Sec_HT"] * (1.0 + overhead_pct + margin_pct)
        edited_df["Total_Price_HT"] = edited_df["Unit_Price_HT"] * edited_df["Quantity"]

        total_ht = edited_df["Total_Price_HT"].sum()
        total_tva = total_ht * tva_pct
        total_ttc = total_ht + total_tva

        st.subheader("Detailed Quantity Estimate (DQE Output)")
        display_df = edited_df[["Code", "Designation", "Unit", "Quantity", "Debourse_Sec_HT", "Unit_Price_HT", "Total_Price_HT"]]
        st.dataframe(display_df.style.format({
            "Quantity": "{:,.2f}",
            "Debourse_Sec_HT": "{:,.0f} XAF",
            "Unit_Price_HT": "{:,.0f} XAF",
            "Total_Price_HT": "{:,.0f} XAF"
        }), use_container_width=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Bid Amount (HT)", f"{total_ht:,.0f} XAF")
        m2.metric(f"TVA Tax ({tva_pct*100:.2f}%)", f"{total_tva:,.0f} XAF")
        m3.metric("Total Bid Amount (TTC)", f"{total_ttc:,.0f} XAF")

    with tender_tab3:
        st.subheader("Technical Methodology Generator")
        work_type = st.selectbox("Project Category", ["Municipal Building / Public Structure", "Rural Water Supply Network", "Asphalted / Earth Road Rehabilitation"])
        contract_duration_months = st.number_input("Execution Timeline (Months)", value=6, step=1)

        if st.button("Generate Technical Methodology Plan"):
            st.markdown(f"""
            ### TECHNICAL METHODOLOGY NOTE
            **Project Domain:** {work_type} | **Execution Schedule:** {contract_duration_months} Months

            #### 1. Mobilization & Site Setup
            Site deployment begins within 10 days of receiving the official Service Order (*Ordre de Service*). Activities include setting up temporary site offices, installing security fencing, and carrying out initial RTK GNSS topographic verification.

            #### 2. Execution & Quality Assurance
            * **Phase 1 (Earthworks & Foundations):** Excavation, compaction testing, and concrete casting in accordance with Eurocode specifications.
            * **Phase 2 (Structural & Hydraulic Assembly):** Mandatory sampling and testing of rebar tensile strength and pipe hydro-testing prior to backfilling.
            * **Phase 3 (Testing & Handover):** System pressure testing at 1.5x nominal operating pressure followed by site restoration and provisional acceptance (*Réception Provisoire*).

            #### 3. Health, Safety & Environment (HSE)
            Mandatory Personal Protective Equipment (PPE) enforcement on site, zero-tolerance site safety guidelines, and waste disposal carried out in compliance with regional environmental norms.
            """)

# ==============================================================================
# MODULE 3: AI CONSULTING & DIAGNOSTIC HUB
# ==============================================================================
elif selected_module == "🤝 Engineering AI Consulting Hub":
    st.title("🤝 Civil Engineering AI & Digital Transformation Hub")
    st.caption("Client Diagnostic Audit & 30-Day Automation Sprint Intake")

    with st.form("consulting_intake_form"):
        firm_name = st.text_input("Engineering Firm / Company Name")
        firm_type = st.selectbox("Organization Type", ["Design Office (BET)", "General Contractor (BTP)", "Surveying Practice", "Municipal Council"])
        staff_count = st.number_input("Technical Staff Count (Engineers/Drafters)", value=5, step=1)

        hours_spent_calc = st.slider("Weekly hours spent manually writing Calculation Notes (Notes de Calcul)", 5, 80, 25)
        submitted = st.form_submit_button("Run Financial Savings Diagnostic")

        if submitted:
            weekly_cost_xaf = hours_spent_calc * 3500 * staff_count
            monthly_cost_xaf = weekly_cost_xaf * 4
            st.success("Diagnostic Audit Complete!")
            st.metric("Estimated Monthly Cost of Manual Typing", f"{monthly_cost_xaf:,.0f} XAF")
            st.write(f"By deploying Isango's automated calculation and tender engines, **{firm_name}** can save up to **{monthly_cost_xaf * 0.7:,.0f} XAF per month** in wasted engineering billable hours.")
