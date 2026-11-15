# Business Analyst skill associations — Member 1 / AQ2

This repository contains the cleaned cohort, preparation audit, pairwise association analysis and evidence supporting Sections 3 and 4.2 and Appendices C and D1. It does not contain the teammates’ AQ1, AQ3 or AQ4 analyses.

## Reproduce the report from the included data

Use Python 3 (tested with Python 3.12.14). From this folder run:

```sh
python -m pip install -r requirements.txt
python run_all.py
```

`run_all.py` regenerates numerical outputs, profile membership and both figures, then checks the headline results and SHA-256 hashes of all original numerical evidence files. It stops on failure. Figures are deterministic in content; font/rendering differences can affect image bytes across machines.

Alternatively, `python analyse_aq2.py` requires only NumPy and reproduces the association-rule results. The full binary matrix is constructed in memory. Pairwise enumeration is used, not an Apriori library implementation.

## Files and report mapping

| File | Purpose |
|---|---|
| data/ba_jobs_clean.csv | Included 1,929-posting cohort; input for AQ2 |
| data/prepare_data.py | Preparation from original postings CSV and skills ZIP |
| data/quality_audit.json | Preparation counts, aliases and original-source hashes |
| data/skill_normalization_audit.csv | Original normalized tokens and mapped skills |
| evidence/all_pair_rules.csv | All 70,490 directed evaluations |
| evidence/selected_rules.csv | 24 rules at working thresholds; Appendix C2 |
| evidence/threshold_sensitivity.csv | All 36 configurations; Section 4.2.2 |
| evidence/jaccard_pairs.csv | Jaccard ranking for pairs with support at least 5% |
| evidence/split_membership.csv | Discovery/checking membership; seed 20261114 |
| evidence/split_validation.csv | Internal robustness results; Section 4.2.3 |
| evidence/profile_membership.csv | Two overlapping provisional profile indicators |
| evidence/summary.json | Counts and headline results |
| evidence/selected_lift.png | Figure AQ2.1 |
| evidence/workflow.png | Redesigned Section 3.1 workflow |
| make_figures.py / make_profiles.py | Regenerate figures and profile indicators |
| verify_results.py | Verify reproduction against report evidence |

## Rebuild from the original sources (optional)

The original full files are NOT bundled. Obtain the same source versions used in Assignment 1:
- `linkedin_job_postings.csv`
- `job_skills.zip`, containing `job_skills.csv` at the ZIP root

Source: Asaniczka (2024), 1.3M LinkedIn Jobs & Skills (2024), Kaggle:
https://www.kaggle.com/datasets/asaniczka/1-3m-linkedin-jobs-and-skills-2024

The original files' hashes are in `data/quality_audit.json`. A different download or repackaged ZIP may have a different hash. Do not describe a different version as the exact original input.

```sh
python data/prepare_data.py raw/linkedin_job_postings.csv raw/job_skills.zip --out data
python run_all.py
```

Preparation also produces the long skills table, full binary matrix, frequencies, exclusions and grouping counts. These extra tables are not needed to rerun AQ2 from the included cleaned cohort. The full raw-to-clean pipeline has not been rerun as part of packaging because the original sources are not present here. The included cohort-to-results pipeline has been tested.

## Interpretation and scope

The cohort is not US-only. `search_country` counts are United States 1,480, United Kingdom 196, Canada 137 and Australia 116. This is a collection/search field, not independently verified workplace geography. The intended client can be US-based, but the pooled results must not be described as representative estimates of the US labour market.

The split is an internal robustness diagnostic, not independent validation. Thresholds are pragmatic; no significance or causal claim is made. The two profiles are analyst-defined and overlap. Employer review, an independent dataset and a broader time window are proposed future work and are not included or claimed as completed.

The old Assignment 1 implementation is unavailable. The A1 values quoted in Section 3.2 must be checked against the actual submitted plan before submission; they cannot be reconstructed merely by uploading this repository.

## Data attribution and sharing

This package does not grant a new licence to the source data. Preserve source attribution and check the dataset's distribution terms before making derived data public. A private course repository can be used for group collaboration; ensure markers have access if the report relies on a private URL. The report itself is not included because it contains the student's identity and is maintained separately.
