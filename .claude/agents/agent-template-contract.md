# agent-template-contract.md
## Purpose
Standard contract for all sub-agent `.md` files.

## Standard inputs
- task
- repo_root
- phase
- selected_agents
- updated_files_scope (optional)
- constraints (optional)
- artifact_map
- prior_agent_outputs

## Standard outputs
1) Changes (unified diffs preferred)
2) Updated artifacts list (created/modified/unchanged)
3) Gate report (pass/fail + evidence + remediation)
4) Notes (assumptions/limitations/follow-ups)

## Required output headings
## Agent
## Inputs
## Work performed
## Changes
## Updated artifacts
## Gates
## Notes

## Canonical gate names
- no_secrets_in_code
- config_separation
- example_env_present
- docstrings_complete
- readme_updated_if_needed
- expected_results_updated
- prompt_log_updated
- tests_present
- edge_cases_covered
- coverage_target
- packaging_valid
- imports_valid
- init_exports_valid
- versioning_present
- final_checklist_pass
- ui_docs_present
- usability_review_done
- notebook_present
- figures_present
- sensitivity_analysis_present
- parallelism_strategy_defined
- thread_safety_checked
- extension_points_documented
- iso25010_mapping_present
