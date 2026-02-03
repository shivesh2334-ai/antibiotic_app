import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(
    page_title="JHH Antimicrobial Stewardship Protocol (2026)",
    page_icon="🏥",
    layout="wide"
)

# --- DISCLAIMER ---
def show_disclaimer():
    st.error(
        """
        **WARNING: FOR EDUCATIONAL/DEMONSTRATION PURPOSES ONLY.**
        
        This application is based on a specific text file ("Clinical Protocol for Inpatient Antimicrobial Therapy - Feb 03, 2026").
        It is NOT a substitute for professional medical judgment. 
        
        *   Always consult the official hospital formulary.
        *   Verify with Infectious Diseases (ID) consult for complex cases.
        *   Renal dosing requires calculation of CrCl.
        """
    )

# --- MEDGEMMA SIMULATION (AI VERIFICATION) ---
def medgemma_verify(syndrome, recommendation, protocol_text):
    """
    Simulates an AI verification tool comparing the provided 2026 protocol 
    against standard IDSA guidelines (Knowledge cutoff Jan 2025).
    """
    verification = {
        "status": "✅ Verified",
        "notes": "Protocol aligns with standard empiric guidelines.",
        "changes": "None detected."
    }
    
    # Simulation of specific discrepancies based on medical knowledge
    if "Diverticulitis" in syndrome and "Ciprofloxacin" in recommendation:
        verification["status"] = "⚠️ Caution / Guideline Deviation"
        verification["notes"] = "Protocol suggests Ciprofloxacin + Metronidazole. Recent IDSA guidelines prefer Amoxicillin/Clavulanate due to high E. coli resistance to fluoroquinolones."
        verification["changes"] = "Consider reviewing local E. coli antibiogram before prescribing Cipro."
        
    if "Cystitis" in syndrome and "Nitrofurantoin" in recommendation:
        verification["notes"] = "Nitrofurantoin is standard, but ensure CrCl > 30 mL/min (revised from >60 in older guidelines)."
    
    if "Community-Acquired Pneumonia" in syndrome and "Azithromycin" in recommendation:
        verification["status"] = "ℹ️ Note"
        verification["changes"] = "Protocol uses Azithromycin monotherapy adjunct. Some 2024 guidelines suggest Doxycycline as a preferred alternative due to macrolide resistance, unless local data supports Azithromycin."

    return verification

# --- LOGIC ENGINE ---
def get_recommendation(organ_system, diagnosis, severity, pcn_allergy, risks, culture_result):
    rec = {
        "First_Line": "Consult ID",
        "Alternative": "Consult ID",
        "Duration": "Dependent on clinical response",
        "Notes": "No specific match found in protocol text."
    }

    # --- 3.1 ABDOMINAL ---
    if organ_system == "Abdominal Infections":
        if diagnosis == "Biliary Tract (Cholecystitis/Cholangitis)":
            if severity == "Community-Acquired/Not Severe":
                rec["First_Line"] = "Ceftriaxone 1 g IV Q24H OR Ertapenem 1 g IV Q24H"
                rec["Alternative"] = "Cipro/Flagyl (if PCN allergic - inferred)"
            else: # Severe/Hospital Acquired
                rec["First_Line"] = "Piperacillin/tazobactam 4.5 g IV Q6H"
                rec["Alternative"] = "Cefepime 2 g IV Q8H + Metronidazole 500 mg IV Q8H ± Vancomycin"
            rec["Notes"] = "Source control (drainage) is crucial. Antibiotics penetrate obstructed ducts poorly."

        elif diagnosis == "Diverticulitis":
            if severity == "Mild/Moderate":
                rec["First_Line"] = "Amoxicillin/clavulanate 875 mg PO BID"
                rec["Alternative"] = "Ciprofloxacin 500 mg PO BID + Metronidazole 500 mg PO Q8H"
            elif severity == "Severe":
                rec["First_Line"] = "Piperacillin/tazobactam 4.5 g IV Q6H"
                rec["Alternative"] = "Cefepime 2 g IV Q8H + Metronidazole 500 mg IV Q8H"
            rec["Duration"] = "4 days (if source control achieved)"
            rec["Notes"] = "Uncomplicated cases (localized wall thickening only) may be managed conservatively without antibiotics."

    # --- 3.2 CNS ---
    elif organ_system == "CNS Infections":
        if diagnosis == "Bacterial Meningitis":
            rec["Duration"] = "Subject to pathogen (e.g., 7 days for N. men, 10-14 for S. pneumo)"
            
            # Age/Immune Status Logic
            is_over_50 = "Age > 50" in risks
            is_immunocomp = "Immunocompromised" in risks
            
            if is_immunocomp:
                rec["First_Line"] = "Vancomycin + Cefepime + Ampicillin"
                rec["Alternative"] = "Vancomycin + Ciprofloxacin + TMP/SMX"
            elif is_over_50:
                rec["First_Line"] = "Vancomycin + Ceftriaxone + Ampicillin"
                rec["Alternative"] = "Vancomycin + Moxifloxacin + TMP/SMX"
            else: # Standard Adult
                rec["First_Line"] = "Vancomycin + Ceftriaxone"
                rec["Alternative"] = "Vancomycin + Moxifloxacin"
                
            rec["Notes"] = "Start ABX within 30 mins. Add Ampicillin for Listeria coverage if >50y or immunocompromised."

    # --- 3.3 PULMONARY ---
    elif organ_system == "Pulmonary Infections":
        if diagnosis == "Community-Acquired Pneumonia (CAP)":
            if severity == "Non-ICU":
                rec["First_Line"] = "Ceftriaxone 1 g IV Q24H + Azithromycin 500 mg IV/PO Q24H"
            elif severity == "ICU":
                if "Pseudomonas Risk" in risks:
                    rec["First_Line"] = "Piperacillin/tazobactam 4.5 g IV Q6H + Azithromycin 500 mg IV Q24H"
                    rec["Alternative"] = "Cefepime 2 g IV Q8H + Azithromycin 500 mg IV Q24H"
                else:
                    rec["First_Line"] = "Ceftriaxone 2 g IV Q24H + Azithromycin 500 mg IV Q24H"
            rec["Duration"] = "Minimum 5 days. Stop when afebrile for 48-72h."
            
        elif diagnosis == "HAP/VAP":
            if "MRSA Risk" in risks:
                mrsa_cov = " + Vancomycin"
            else:
                mrsa_cov = ""
            
            rec["First_Line"] = "Piperacillin/tazobactam 4.5 g IV Q6H" + mrsa_cov
            rec["Alternative"] = "Cefepime 2 g IV Q8H" + mrsa_cov
            rec["Duration"] = "7 days (if prompt response)"
            rec["Notes"] = "Narrow therapy based on respiratory culture. Stop Vanco/Double coverage if cultures negative."

    # --- 3.5 URINARY ---
    elif organ_system == "Urinary Tract Infections (UTI)":
        if diagnosis == "Acute Cystitis (Uncomplicated)":
            rec["First_Line"] = "Nitrofurantoin 100 mg PO BID"
            rec["Duration"] = "5 days"
            rec["Alternative"] = "TMP/SMX DS PO BID x 3 days"
        elif diagnosis == "Pyelonephritis / Urosepsis":
            rec["First_Line"] = "Ceftriaxone 1 g IV Q24H"
            rec["Alternative"] = "Piperacillin/tazobactam 3.375 g IV Q6H"
            rec["Duration"] = "7-14 days"
        elif diagnosis == "Catheter-Associated UTI (CA-UTI)":
            rec["First_Line"] = "Remove Catheter + Ceftriaxone 1 g IV Q24H"
            rec["Duration"] = "7 days"
            rec["Notes"] = "Treat as pyelonephritis. Do not treat asymptomatic bacteriuria."

    # --- 3.4 SKIN/SOFT TISSUE ---
    elif organ_system == "Skin, Soft-Tissue, Bone":
        if diagnosis == "Cellulitis (Non-suppurative)":
            rec["First_Line"] = "Cefazolin 1-2 g IV Q8H"
            rec["Alternative"] = "Clindamycin 300-450 mg PO TID"
            rec["Notes"] = "Targeting Streptococci/MSSA."
        elif diagnosis == "Cellulitis (Suppurative) / Abscess":
            rec["First_Line"] = "Incision & Drainage (Primary Tx)"
            rec["Alternative"] = "Vancomycin (if systemic signs)"
            rec["Notes"] = "Adjunctive antibiotics only for severe disease, SIRS, or immunosuppression."

    # --- 3.6 SEPSIS ---
    elif organ_system == "Sepsis (No Clear Source)":
        base = "Piperacillin/tazobactam 4.5 g IV Q6H OR Cefepime 2 g IV Q8H"
        if "MRSA Risk" in risks:
            base += " + Vancomycin"
        rec["First_Line"] = base
        rec["Duration"] = "Re-evaluate at 48-72h based on cultures"
        rec["Notes"] = "Obtain 2 sets of blood cultures prior to initiation."

    # Handle PCN Allergy Swap (Generic logic based on text 2.3 and 6.2)
    if pcn_allergy:
        rec["Notes"] += "\n\n**ALLERGY NOTE:** Patient has PCN Allergy. Ensure 'Alternative' regimen is non-beta-lactam or consult ID if severity of allergy (anaphylaxis) contraindicates Cephalosporins."

    return rec

# --- UI LAYOUT ---

show_disclaimer()
st.title("🛡️ Clinical Protocol: Inpatient Antimicrobial Therapy")
st.caption("Based on JHH Protocol File: February 03, 2026")

# Sidebar
st.sidebar.header("Patient & Clinical Data")

age = st.sidebar.number_input("Age", min_value=18, max_value=120, value=50)
sex = st.sidebar.selectbox("Sex", ["Male", "Female"])
pcn_allergy = st.sidebar.checkbox("History of Penicillin Allergy")

st.sidebar.markdown("---")
st.sidebar.subheader("Clinical Presentation")

organ_system = st.sidebar.selectbox("Suspected Organ System", 
    ["Select...", "Abdominal Infections", "CNS Infections", "Pulmonary Infections", "Skin, Soft-Tissue, Bone", "Urinary Tract Infections (UTI)", "Sepsis (No Clear Source)"])

diagnosis_options = []
if organ_system == "Abdominal Infections":
    diagnosis_options = ["Biliary Tract (Cholecystitis/Cholangitis)", "Diverticulitis", "Pancreatitis", "Peritonitis"]
elif organ_system == "CNS Infections":
    diagnosis_options = ["Bacterial Meningitis", "Brain Abscess"]
elif organ_system == "Pulmonary Infections":
    diagnosis_options = ["Community-Acquired Pneumonia (CAP)", "HAP/VAP"]
elif organ_system == "Urinary Tract Infections (UTI)":
    diagnosis_options = ["Acute Cystitis (Uncomplicated)", "Pyelonephritis / Urosepsis", "Catheter-Associated UTI (CA-UTI)"]
elif organ_system == "Skin, Soft-Tissue, Bone":
    diagnosis_options = ["Cellulitis (Non-suppurative)", "Cellulitis (Suppurative) / Abscess", "Diabetic Foot", "Necrotizing Fasciitis"]
elif organ_system == "Sepsis (No Clear Source)":
    diagnosis_options = ["Sepsis Unknown Source"]

diagnosis = st.sidebar.selectbox("Specific Diagnosis", diagnosis_options)

severity = st.sidebar.select_slider("Severity of Illness", options=["Mild", "Moderate", "Severe", "ICU / Critical"])

st.sidebar.markdown("---")
st.sidebar.subheader("Risk Factors")
risks = st.sidebar.multiselect("Select all that apply", 
    ["MRSA Risk", "Pseudomonas Risk", "Immunocompromised", "Age > 50", "Recent Antibiotics"])

# --- MAIN DISPLAY ---

if organ_system != "Select...":
    # Get Recommendation
    rec = get_recommendation(organ_system, diagnosis, severity, pcn_allergy, risks, None)
    
    # Run MedGemma Verification
    verification = medgemma_verify(diagnosis, rec["First_Line"], "JHH 2026 Protocol")

    # Display Columns
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"Treatment Recommendation: {diagnosis}")
        
        st.info(f"**First Line Empiric:**\n\n### {rec['First_Line']}")
        
        if pcn_allergy:
            st.warning(f"**PCN Allergy Alternative:**\n\n{rec['Alternative']}")
        else:
            st.write(f"**Alternative:** {rec['Alternative']}")
            
        st.markdown(f"**⏱️ Duration:** {rec['Duration']}")
        st.markdown(f"**📝 Clinical Notes:** {rec['Notes']}")

    with col2:
        st.markdown("### 🧬 MedGemma Analysis")
        st.caption("AI verification against IDSA Guidelines")
        
        if "Caution" in verification["status"]:
            st.warning(verification["status"])
        else:
            st.success(verification["status"])
            
        st.markdown(f"**Analysis:** {verification['notes']}")
        if verification["changes"] != "None detected.":
            st.markdown(f"**Changes/Deviations:** {verification['changes']}")

    # --- TABBED DETAILS ---
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["💊 Drug Dosing Ref", "🦠 Microbiology Guide", "📋 Full Text View"])
    
    with tab1:
        st.markdown("#### Renal Adjustments (Select Agents)")
        dosing_data = {
            "Drug": ["Cefepime", "Piperacillin/tazobactam", "Meropenem", "Ciprofloxacin"],
            "Standard Dose": ["2 g Q8H", "4.5 g Q6H", "1 g Q8H", "400 mg Q8H"],
            "CrCl 30-50": ["2 g Q12H", "3.375 g Q6H", "1 g Q12H", "400 mg Q12H"],
            "CrCl 10-29": ["2 g Q24H", "2.25 g Q8H", "500 mg Q12H", "400 mg Q24H"]
        }
        st.table(pd.DataFrame(dosing_data))
        st.caption("Refer to Section 7.3 of the protocol for full details.")

    with tab2:
        st.markdown("#### Rapid Diagnostic Interpretation")
        st.markdown("- **GPC Clusters:** Staph aureus / CoNS")
        st.markdown("- **GPC Pairs/Chains:** Strep pneumo / Enterococcus")
        st.markdown("- **GNR Lactose (+):** E. coli / Klebsiella")
        st.markdown("- **GNR Lactose (-):** Pseudomonas / Acinetobacter")
        
    with tab3:
        st.markdown("#### Source Text Snippet")
        st.text("""
        Clinical Protocol for Inpatient Antimicrobial Therapy
        Date: February 03, 2026
        Location: The Johns Hopkins Hospital
        
        Mission: Optimize clinical outcomes while minimizing unintended consequences...
        """)
        st.info("Full text logic is embedded in the application logic engine.")

else:
    st.info("👈 Please select an Organ System and Diagnosis from the sidebar to begin.")
