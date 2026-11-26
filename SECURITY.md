# Security policy

## Scope

Inventory Investigation Lab is a synthetic, read-only training project. It must not process real warehouse data, connect to an operational ERP or be exposed as an unauthenticated public API. The static site has no AI credentials and no live backend.

## Reporting a concern

Use GitHub's private vulnerability reporting if available. Otherwise contact the repository owner privately; do not put keys, personal information or exploit details in a public issue. Include the affected version, reproduction steps using synthetic data and impact. Rotate any exposed credential immediately.

## Controls

| Area | Implemented control |
| --- | --- |
| Dependencies | Exact version pins from successful Linux CI; pip check; pip-audit against PyPI advisories; weekly Dependabot configuration |
| CI | Read-only token permissions, actions pinned by commit, checkout credentials not persisted, job timeouts |
| Source | Bandit medium/high severity and confidence gate; focused tracked-text secret scanner with regression tests |
| REST | Localhost host allowlist; reject browser-origin POSTs; deterministic explanation only; no-store and defensive headers |
| AI | No commercial provider, optional browser worker, bounded prompt/output and timeout, synthetic input only |
| MCP | Local stdio, read-only tool annotations and identifier validation |
| Browser | Same-origin page CSP, text-node rendering, no credential storage; optional worker imports version-pinned public runtime |

Only bind the API to loopback. Model output remains untrusted. Only an exact permitted choice is accepted; the application constructs the explanation using canonical case and SOP text. No model prose is rendered and no stock adjustment is authorised.

## Audit procedure

Run the project tests, then run the following commands in a separate virtual environment with the scanner requirements installed:

```sh
python scripts/check_secrets.py
bandit -r inventory -ll -ii
pip-audit --no-deps --disable-pip -r requirements.txt -r requirements-web.txt
```

CI fails on reported vulnerabilities or scan failures; no vulnerability IDs are suppressed. Review CI logs for results rather than assuming that a configured scanner has passed.

## Known limitations

Version pins are based on Python 3.12 Linux CI, not cryptographic hashes or a universal platform lock. The browser binaries and scanner transitive dependencies are not fully locked. Advisory databases may be incomplete, and this is not a penetration test or a software supply-chain attestation. The focused secret scanner covers selected patterns in current tracked text only, not history or all credential types. Native GitHub secret scanning, push protection and branch protection require separate repository settings and plan eligibility; they are not enabled by this PR. The Bandit gate does not cover JavaScript or dependencies. The optional worker imports third-party assets without hash verification; its requests are not governed by the page meta CSP. See [AI.md](AI.md) for the release review boundary. Authentication, rate limiting, production deployment and model quality validation remain outside this release scope.

## Release history and asset checks

CI checks all reachable commit snapshots and commit messages in a full checkout for selected credential patterns, prohibited filenames, symlinks/submodules and unreviewed non-UTF-8 blobs. It distinguishes recognised service addresses from other author/committer metadata and reports affected abbreviated commit IDs and roles without exposing addresses. Owner review of remaining groups is required before publication. Unreachable objects, unreturned PR refs, external caches, old Actions logs and arbitrary personal or employer information require separate review. Public asset checks compare the npm archive and CDN entry, and the pinned model weight against upstream digests; this is not runtime SRI or a full transitive supply-chain audit. See [RELEASE.md](RELEASE.md).
