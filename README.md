# JHH Antimicrobial Stewardship App (2026 Protocol)

This is a Streamlit-based Clinical Decision Support System (CDSS) prototype based on the "Clinical Protocol for Inpatient Antimicrobial Therapy" (Feb 03, 2026).

## Features
*   **Syndrome-Based Logic:** Inputs for Abdominal, CNS, Pulmonary, UTI, Skin/Soft Tissue, and Sepsis.
*   **Risk Stratification:** Adjusts recommendations based on ICU status, MRSA/Pseudomonas risk, and Penicillin allergy.
*   **MedGemma Verification:** A simulated AI agent that compares the 2026 protocol recommendations against standard IDSA guidelines to highlight potential deviations or new resistance patterns.
*   **Dosing References:** Integrated renal adjustment tables.

## Installation

1.  Ensure you have Python installed.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```
2.  Open your browser to the local URL provided (usually `http://localhost:8501`).
3.  Use the Sidebar to input patient demographics and clinical presentation.

## Disclaimer
**For Educational Use Only.** This tool utilizes a specific text file for its logic and does not replace live clinical judgment or official hospital formularies.
