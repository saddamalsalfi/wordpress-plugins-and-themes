# Verification, installable ZIPs, and distribution

Validate the archive and the actual target environments. Directory checks, repository releases, and application updates are separate operations.

## Validate meaningful behavior and release contents

Use isolated environments and synthetic data. Select checks proportional to the change; do not create implementation-mirroring tests for superficial coverage.

| Area | Appropriate verification |
| --- | --- |
| PHP standards/compatibility | PHP lint, WordPress Coding Standards/PHPCS, configured PHP compatibility/static analysis |
| Plugin distribution | Official Plugin Check plus manual security/lifecycle review |
| Theme distribution | Official Theme Check plus applicable theme review requirements |
| Logic/integration | PHPUnit with supported WordPress test fixtures, including `WP_UnitTestCase` where appropriate |
| JS/editor | Repository lint/build, unit/component tests, and saved-block regressions |
| Browser journeys | Branch-compatible Playwright or project E2E tooling, multiple roles and viewport/RTL checks |
| Lifecycle/data | Clean package install, activation, upgrade, deactivation, uninstall/retention, dependency failure |
| Permissions/privacy | Unauthorized objects, REST/AJAX, CSRF, private files, export/erasure, cross-site isolation |
| Matrix | Minimum and target WordPress/PHP, supported databases, single-site/Multisite, declared integrations |

- Use official `@wordpress/env`, WordPress development test tooling, or an equivalent configured isolated environment. Verify commands and dependency versions before running them; never point automated test setup at production databases.
- Run package checks against the built artifact, not only source. Include runtime Composer dependencies and compiled JS/CSS/metadata; exclude dev-only packages and verify dependency licenses.
- Distinguish tool configuration, checks actually run, and results. Plugin Check/Theme Check do not guarantee acceptance, security, legal compliance, or universal compatibility.
- Build an installable ZIP with one correct slug directory. Exclude credentials, `wp-config.php`, production uploads, dumps, logs, caches, tests/fixtures not needed at runtime, and irrelevant repository files.
- Distinguish GitHub source/releases from WordPress.org's plugin SVN distribution and theme submission/update process. Do not assume a Git tag or GitHub ZIP automatically updates directory users.
- Keep immutable versioned releases, accurate requirements/readme/license/changelog, publicly available readable source as required, and verified update-channel metadata. Recheck current directory rules, GPL-compatible distribution requirements, trademarks, external-service disclosure, and monetization requirements before submission.
- Obtain only approvals required for actual publication/deployment; the task to prepare a package does not itself authorize publishing externally. Report concrete changes, actual tests, remaining limits, and manual migration/deployment steps.

## Scoped completion checklist

Use only the rows relevant to the scoped change. When reporting results, name the host/application version, PHP/runtime, installation or upgrade source, exact check, result, and any untested variant. For preparations, keep the proposed archive and metadata reviewable; an external publish or a production deploy is a separate action.

- [ ] Correct plugin deployment type or theme model, identity, and paths.
- [ ] Headers, runtime checks, dependency behavior, and compatibility matrix aligned.
- [ ] Safe lifecycle/migrations and explicit content/retention ownership.
- [ ] Capabilities, nonces, object access, REST/AJAX, input validation, and output escaping verified.
- [ ] Personal data, integrations, private files, and Multisite isolation addressed.
- [ ] Blocks/theme templates preserve content, customization precedence, localization, and accessibility.
- [ ] Relevant checks and clean-package tests passed; untested scope recorded.
- [ ] Artifact, sources, licensing, documentation, and intended update channel consistent.

## Upstream sources

Match these docs and the installed source to the target version; these links are not a support matrix.

- [WPCS tooling](https://github.com/WordPress/WordPress-Coding-Standards)
- [WordPress development source and tests](https://github.com/WordPress/wordpress-develop)
- [Plugin Check](https://github.com/WordPress/plugin-check)
- [Theme Check](https://github.com/WordPress/theme-check)
- [Isolated wp-env environments](https://developer.wordpress.org/block-editor/reference-guides/packages/packages-env/)
- [Plugin Directory guidelines](https://developer.wordpress.org/plugins/wordpress-org/detailed-plugin-guidelines/)
- [Theme Directory guidelines](https://developer.wordpress.org/themes/releasing-your-theme/theme-review-guidelines/)
