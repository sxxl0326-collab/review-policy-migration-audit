# Review policy migration audit

Replication materials for *Auditing Owner Preservation and Scope in Review Policy Migration*. Read [Supplementary Information](CSCWD2027_S1.pdf) or download the [versioned artifact](https://github.com/sxxl0326-collab/review-policy-migration-audit/releases/tag/v1.0.1).

From the extracted archive or repository root, run:

```sh
python new_cohorts/verify_new.py
```

Tested with Python 3.10. The check reads saved CODEOWNERS snapshots and path lists and recomputes 25 PR comparisons and 788 context-policy rows. Configuration records and public PR links identify software histories. Project targets, team membership and notification delivery can remain unknown.

| Question | Evidence |
|---|---|
| Which original histories and pull requests? | [H01–H11 mapping, source passages, paths and SHAs](reviewer_entry/case_index.csv), [19-PR matrix](reviewer_entry/pr_matrix_19.json) |
| Did the original tools agree? | [24 paired inputs](reviewer_entry/common24_repository_breakdown.csv), [original per-repository checks](previous_tables/repository_checks.csv) |
| Which paths changed beyond the probes? | [Attempt denominators](audit_revision/semantics_preview_20261109/preview_scope_detail/attempts.csv), [path-level differences](audit_revision/semantics_preview_20261109/preview_scope_detail/all_path_differences.jsonl) |
| What did the matcher checks cover? | [24 matcher cases](audit_revision/semantics_preview_20261109/semantic_tests/cases_and_results.json) |
| How were the new cohorts selected? | [Frozen rules](new_cohorts/protocol.txt), [later pool](new_cohorts/selection_frame_later.json), [archive pool](new_cohorts/selection_frame_archive.json), [screening ledger](new_cohorts/wave/screening_ledger.json) |
| What changed in the additional experiments? | [13 paired repositories by tool](new_cohorts/A_repositories.csv), [25 user-account PRs](new_cohorts/B_pr.csv), [including empty PR windows](new_cohorts/B_repositories.csv) |

Figures 2 and 4 visualize the original cohorts. The later and archive strata contribute respectively 2 and 0 repositories with nonempty owners on a tested path. Figure 3 distinguishes actual merged policies from counterfactual tool replay. The five source descriptions are available with their evidence and review status in the history index. No itemwise human adjudication or agreement statistic is inferred.
