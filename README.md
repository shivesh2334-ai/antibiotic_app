# ABX Steward

A responsive, static antimicrobial stewardship decision-support application. It helps qualified healthcare professionals explore infections, review historical baseline regimens, inspect selected antimicrobial monographs, and complete a safety time-out.

## Clinical scope and warning

The disease pathways are derived from and paraphrase the attached **ICMR Treatment Guidelines for Antimicrobial Use in Common Syndromes, 2nd edition (2019)**. This India-focused guideline remains a dated baseline and must not be treated as current prescribing authority. Recommendations require confirmation against current national/local guidance, institutional policy, the local antibiogram, microbiology, patient-specific factors and specialist advice.

The application intentionally does not automate a prescription or calculate patient-specific doses.

## Run locally

Serve this directory with any static web server, for example:

```bash
npx serve .
```

## Deploy to Vercel

Import the repository into Vercel. No build command or environment variables are required; the project is plain static HTML/CSS/JavaScript.
