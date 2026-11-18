# Reproduction guide

This guide accompanies *Auditing Owner Preservation and Scope in Review Policy Migration*. Use the [paper](CSCWD2027-frozen.pdf) for the reported results and the [supplement](CSCWD2027_S1.pdf) for sampling and audit details.

## Setup

Extract the artifact ZIP or check out the repository at the commit you want to cite. Open a terminal in the directory that contains `README.md`. Use Python 3.10 or later. The two checks below use saved inputs and bundled dependencies without a GitHub token or network access.

## Verify the saved results

| Command | Inputs and checks | Expected result |
| --- | --- | --- |
| `python new_cohorts/verify_new.py` | Recomputes PR additions from saved pre/post CODEOWNERS files and changed paths. Recomputes declared owner sets and omissions for saved policy snapshots. | 25 PR comparisons, 7 with raw additions and 2 after author exclusion. Also verifies 788 context–policy rows across 13 additional repositories. |
| `python check_strata.py` | Compares historical owner declarations with applicable bot reviewers and checks the omission sets for both tools. | Original common cohort: 24 exposed repositories and 5 with an owner/reviewer conflict. New cohort: 2 exposed repositories and 0 conflicts, with equal owner/reviewer sets in all 42 and 5 tested bot contexts, respectively. |

The checks recompute from archived inputs and outputs. Tool reruns and live hosting data are outside these commands. The original execution and sampling procedures are described in the paper and supplement. The [new-cohort protocol](new_cohorts/protocol.txt) records the frozen selection conditions and windows.

## Follow a claim back to its inputs

- **Historical omissions:** Find H01–H11 in the [case index](reviewer_entry/case_index.csv). Each row points to the repository, source PR, frozen revisions and evaluated paths. PR passages provide source context. AI-assisted categories have no independent author coding.
- **Author exclusion:** Read the [original PR matrix](reviewer_entry/pr_matrix_19.json) or the [new PR table](new_cohorts/B_pr.csv). Owner additions are declaration changes. Public request events are recorded separately from declarations.
- **Whole-tree preview:** Join the [attempt index](reviewer_entry/preview_attempt_crosswalk.csv) to the [probe and rule rows](reviewer_entry/preview_probe_rules.csv) on `attempt_id`. The attempt index identifies 25 starting policies and the off-probe count for each. The probe rows show winning rules, missing declarations and actual appends. Appends are rule-level edits and can be repeated across probe rows. Use one row per attempt when totaling counts. The [path-level differences](audit_revision/semantics_preview_20261109/preview_scope_detail/all_path_differences.jsonl) record the affected paths. Table V reports 13 affected attempts and 4,915 off-probe path–attempt pairs.

Project acceptance requires explicit actor-specific targets. The reported conditional previews describe possible edits and their scope.
