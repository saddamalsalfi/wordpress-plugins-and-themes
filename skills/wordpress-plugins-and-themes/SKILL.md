---
name: wordpress-plugins-and-themes
description: "Develop, review, and package WordPress plugins, blocks, and themes. Use for classic, block or child themes, MU plugins, plugin headers and upgrades, REST/AJAX permissions, Multisite, theme.json, and installable ZIPs."
license: MIT
---

# WordPress Plugins and Themes

Use this skill for a WordPress plugin, block, or theme code change, including distribution readiness. Do not invoke it just to edit a page, adjust WordPress settings, or move persistent content types into a theme.

## Start with the deployed contract

- Inspect plugin/theme headers, manifests, lockfiles, editor/build tooling, and tests. Record WordPress and PHP minimums, single-site versus Multisite, active parent theme, optional dependencies, and update channel. Verify APIs at the declared minimum rather than assuming current Gutenberg features are in core.
- Choose a standard, network, MU, or drop-in plugin lifecycle; or a classic, block, hybrid, or child theme model. Preserve slug, text domain, basename, block names, options/meta, and REST routes. A skill repository name is not a runtime WordPress slug.
- In a review, report findings and evidence without editing unless asked. Prefer supported hooks and APIs to core or parent modifications.

## Choose what to read

- [Plugin deployment, theme models, identity, and headers](references/extension-contract.md) — Read before choosing type, slug, layout, minimum versions, or update channel.
- [Upgrades, Multisite, and scheduled work](references/lifecycle-and-operations.md) — Read for schema changes, activation/uninstall, scheduler behavior, or bulk work.
- [Object-level access, REST/AJAX, and personal data](references/rest-security-and-privacy.md) — Read for endpoints, forms, files, integrations, or privacy flows.
- [Blocks, templates, and editor behavior](references/blocks-and-themes.md) — Read for block assets, saved markup, Site Editor overrides, and theme inheritance.
- [Localization and site/network boundaries](references/locales-and-multisite.md) — Read for PHP/JS locale handling, RTL, and per-site versus network scope.
- [Verification, installable ZIPs, and distribution](references/testing-and-release.md) — Read for checks on the built artifact, directory rules, and tested support.

## Implement the affected contract

1. **Lifecycle and data:** MU plugins are auto-loaded via root PHP files and do not use normal activation hooks. Standard plugin updates do not generally re-run activation. Separate explicit, guarded upgrades from deactivation and uninstall. On Multisite distinguish per-site from network data, existing sites from future sites, and restore switched blog context.
2. **Access and privacy:** Check object-aware capabilities independently of nonces. Set a `permission_callback` on each REST route, and keep public routes intentionally public and minimal. Validate requests, escape at output, prepare DB values, and enforce real file access. Include guest/email-linked records in privacy flows when applicable.
3. **Editor and themes:** Keep saved block markup compatible through deprecations/migrations where needed; test old content. Use the release-matched `theme.json` schema and check Site Editor database overrides before changing files or resetting customization. Use the exact parent folder in a child theme's `Template` header; inspect assets to avoid double loading. Keep reusable content/business behavior independent of the active theme.

## Verify the built extension

Use isolated WordPress fixtures and the repository's PHP, JS, and browser tooling. Test allowed and denied requests, upgrades/uninstall/retention, editor/frontend parity, and declared minimum/current or site/network configurations when in scope. Check the built ZIP has one slug directory with the required compiled files. GitHub release assets do not update WordPress.org users. Report commands and results separately from planned checks. See [worked scenarios](examples/worked-scenarios.md).

Use the user's language for the report unless they request another.
