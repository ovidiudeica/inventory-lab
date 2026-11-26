# Release 1.0.0

Version 1.0.0 is prepared for the first public release. Publication requires passing CI on main and a successful privacy review; deployment and release status are recorded in GitHub.

## Acceptance checklist

- CI passes for the exact reviewed head: Python, real MCP round trip, export, Chromium, security.
- History scan runs with a full checkout across reachable branch/tag refs; no matching credentials or unreviewed binary blobs. Review non-noreply commit metadata, historical pull request content and logs separately before disclosure. A clean focused scan is not proof of absence of secrets or private information.
- Review all six real-model selections and independently verified canonical explanations in CI. Check invalid-output rejection and unchanged reports. A valid selection is not proof that it is the most useful focus.
- Check upstream licence and asset integrity results; assess remaining browser runtime supply-chain limitations. No third-party assets are committed.
- Owner approved the MIT licence for original project code on 26 November 2026.
- Review all open Dependabot proposals. Checkout and Setup Python are pinned to exact SHAs. MCP 2.x is a major change deferred until compatibility is separately validated; retain the tested MCP 1.x pin.
- Confirm GitHub Free, zero additional-spend budgets and standard runners. No paid provider or external compute.
- Confirm repository owner approves visibility change and publication separately.

## Release notes

Inventory metrics and reports use a deterministic Python engine; REST and MCP share it. The static dashboard works without AI. Optional model inference runs in the visitor's browser and is explicitly unverified. No real employer data, ERP connection, commercial inference or stock mutation is included.

## Model review rubric

For each SKU, review the validated explanation against the canonical case:

| SKU | Expected variance | Permitted possible explanation | SOPs |
| --- | ---: | --- | --- |
| SKU-101 | -4 | Unreconciled transfer may explain shortage | 01, 02, 03 |
| SKU-102 | 0 | No discrepancy observed | 01 |
| SKU-103 | +4 | Receipt posting mismatch may explain surplus | 01, 02, 03 |
| SKU-104 | -6 | Open pick may explain shortage | 01, 02, 03 |
| SKU-105 | 0 | No discrepancy observed | 01 |
| SKU-106 | -4 | Cause unknown | 01, 02, 03 |

Development CI demonstrated free-form model quality failures in all six cases (missing variance, repeated or invented procedures). The remediation uses constrained selection and canonical rendering. Review the new CI results before approval; no arbitrary model text may be shown.

## Publication runbook

After approved release PR merge, repeat the final checks against main. Inspect public-facing repository metadata, history and Actions logs; confirm owner consent to disclosure (MIT licence already approved). Change visibility only with explicit approval. Configure GitHub Pages from main /docs, with HTTPS, then test the deployed URL, subpath routing, model opt-in and report download. Create the final tag/release only after approval and successful verification. If a critical issue is found, stop publication or disable Pages; making a repository private again does not erase copies already obtained.


## Privacy gate

Do not expose non-noreply author or committer addresses without reviewing the reported metadata groups. The scanner distinguishes exact recognised service addresses from other addresses and reports abbreviated commit IDs and roles, never raw addresses. This is a privacy review, not a secret finding. If other addresses remain, obtain owner review of the actual metadata before publication. Do not publish if any unrecognised author or committer metadata remains. This repository uses a fresh source snapshot rather than the previous Git history. GitHub email settings do not retrospectively remove historical metadata.
