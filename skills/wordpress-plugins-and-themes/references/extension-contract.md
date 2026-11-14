# Plugin deployment, theme models, identity, and headers

Choose deployment type or theme model before designing filenames and headers. The distribution channel can impose additional requirements beyond WordPress core.

## Establish the target and acceptance criteria

1. Read repository instructions, existing architecture, headers, dependency manifests, build configuration, tests, and release scripts.
2. Identify the exact WordPress/PHP/database versions, single-site or Multisite deployment, active theme/parent, editor setup, relevant extensions, and update channel.
3. Record minimum supported versions, tested versions, optional integrations, data ownership, user capabilities, and required behavior/failure modes.
4. Determine whether the project is a plugin, theme, child theme, MU plugin, drop-in, or a combination of separate deliverables. Select the appropriate lifecycle before scaffolding.
5. Inspect version-matched official documentation and core/plugin source before using unfamiliar APIs. Development Gutenberg features and current handbook examples may exceed the target's supported core version.
6. Preserve published slugs, text domains, basenames, block names, data keys, routes, and hooks unless a deliberate migration is in scope.
7. Ask only for missing decisions that affect compatibility, content loss, external disclosure, or authorization. Proceed with routine reversible choices.

Use hooks and extension APIs before modifying core or third-party files. Keep content types and persistent business functionality in plugins so a theme switch does not remove them. Do not assume WordPress.com hosting supports the same deployment operations as a self-hosted installation.

## Distinguish plugin deployment types and feature categories

WordPress does not assign Moodle-style type prefixes or PKP category directories to ordinary feature plugins. A block, SEO, reporting, WooCommerce-extension, or API-integration plugin usually remains a standard plugin with additional contracts.

| Deployment type | Conventional location | Lifecycle and constraints |
| --- | --- | --- |
| Standard plugin | `wp-content/plugins/example-plugin/` | Discovered through a main PHP header; site activation/deactivation and updates |
| Network-active standard plugin | Same plugin directory | Activated network-wide; still requires explicit site/network data and permission design |
| Network-only plugin | Same plugin directory | `Network: true` header restricts activation to the network; it does not implement network setup automatically |
| Must-use plugin | `wp-content/mu-plugins/` | Root PHP files load automatically before ordinary plugins; no normal activation/update lifecycle |
| Drop-in | Reserved filename under the configured content directory | Special core loading contract, such as `object-cache.php` or `advanced-cache.php`; not an ordinary optional plugin |

Treat these as conventional paths: content and plugin directories may be relocated. Use WordPress path/URL APIs rather than assuming the literal `wp-content` location.

- For MU plugins, use a root loader for code in a subdirectory; WordPress does not recursively discover that code. Design explicit installation, migration, maintenance, and removal processes instead of relying on activation hooks.
- For drop-ins, verify the exact filename, load timing, required constants, and core API. Detect an existing drop-in and preserve ownership; never overwrite a host/cache provider's file silently.
- For extension plugins, detect the required extension and compatible API version before calling it. Distinguish installation, activation, readiness, and optional feature availability.
- For blocks, shortcodes, widgets, REST endpoints, payment gateways, CLI commands, and scheduled work, implement their feature-specific contracts without inventing new runtime plugin categories.

## Select the theme model intentionally

| Model | Primary templates | Key distinction |
| --- | --- | --- |
| Classic theme | PHP template hierarchy | Traditional rendering; may support blocks and `theme.json` |
| Block theme | Block-markup HTML in `templates/` and `parts/` | Site Editor and block-based templates; includes the block theme index template |
| Hybrid theme | Classic templates plus selected block-era features | A descriptive approach, not a separate core installation type |
| Child theme | Overrides/extensions of one parent theme | Inherits the parent's architecture; identifies the exact parent directory in `Template` |

For a standalone classic theme, the runtime minimum includes `style.css` and `index.php`; a block theme uses `style.css` and `templates/index.html`. Check separate directory submission requirements and child-theme inheritance rather than applying the standalone minimum universally. `functions.php` and `theme.json` are useful but not universally required runtime files.

Do not assume adding `theme.json` alone turns a classic theme into a block theme. Inspect actual template files and core theme detection. Choose a child theme for scoped parent customization; WordPress does not provide arbitrary grandchild-theme inheritance.

## Keep names and identities consistent

Choose a distinctive lowercase hyphenated slug. Check existing directory names, WordPress.org availability when relevant, trademarks, and reserved identifiers before publishing. Preserve an established valid slug during maintenance.

| Identity | Plugin example | Theme example |
| --- | --- | --- |
| Suggested Git repository name | `wp-journal-tools` | `wp-journal-elegance-theme` |
| Runtime directory / slug | `journal-tools` | `journal-elegance` |
| Main identification file | `journal-tools.php` | `style.css` |
| Text domain | `journal-tools` | `journal-elegance` |
| Unique global function prefix | `acme_journal_tools_` | `acme_journal_elegance_` |
| Example PHP namespace | `Acme\Journal_Tools` | `Acme\Journal_Elegance` |
| Example REST namespace | `acme-journal-tools/v1` | Usually owned by a functional plugin |
| Example block name | `acme-journal-tools/notice` | Prefer a plugin for content blocks that must survive theme switches |

The `wp-...` repository names are project suggestions, not a mandatory WordPress-wide naming scheme. The repository name may differ from the runtime slug. Do not invent `moodle-`, `local_`, PKP category prefixes, or an official endorsement in the package name.

- Use plugin/theme files directly at a standalone repository's root, or document the build output when using a monorepo. Build installable ZIPs with the correct slug directory, not GitHub's automatic `repository-tag` wrapper.
- Keep WordPress.org text domains aligned with the directory slug. Prefix global functions, constants, options, transients, hooks, asset handles, and custom data identifiers with a unique project identity; do not use reserved core prefixes.
- Follow WordPress PHP naming: `$post_id`, `get_report()`, and classes such as `Report_Service`; use uppercase underscore-separated constants. Do not apply Moodle's `$postid` convention or PKP's camelCase PHP convention.
- Use the configured WPCS-compatible filename convention, such as `class-report-service.php`, or a documented Composer/PSR-4 mapping. Do not assume WordPress automatically autoloads namespaced classes.
- Follow JavaScript/React and CSS conventions separately. Use lowercase `namespace/block-name` block identifiers and a versioned REST namespace; preserve public identifiers once content or clients depend on them.
- Keep PHP symbols independent of display names/translations. Never derive executable identifiers from translated strings.

## Organize only the files the project needs

| File or path | Responsibility |
| --- | --- |
| `<slug>.php` | Plugin header, bootstrap, shared constants, lifecycle/hook registration |
| `includes/` or `src/` | Cohesive services, data access, authorization, REST, and integration code |
| `admin/` | Optional administration controllers/views; not a mandatory folder |
| `assets/`, `src/`, `build/` | Frontend/editor sources and compiled runtime assets |
| `blocks/<name>/block.json` | Optional block metadata according to the chosen source/build layout |
| `languages/` | Translation sources and distributable files when required |
| `uninstall.php` | Explicit uninstall cleanup, guarded by `WP_UNINSTALL_PLUGIN` |
| `readme.txt` | WordPress.org plugin metadata, usage, requirements, and changelog |
| `style.css` | Theme identity header and optional CSS |
| `functions.php`, `inc/` | Theme setup and presentation integration; keep bootstrap focused |
| `templates/*.html`, `parts/*.html` | Block theme templates and reusable block parts |
| `index.php`, `single.php`, `archive.php`, etc. | Classic theme hierarchy when applicable |
| `theme.json`, `styles/*.json` | Global settings/styles and supported style variations |
| `patterns/*.php` | Theme block patterns using the expected pattern metadata |
| `tests/`, `phpcs.xml.dist`, test/build configs | Meaningful verification and automated tooling |

Keep bootstrap and request handlers thin. Separate validation, capability checks, data operations, and rendering. Small plugins may stay procedural; do not add a framework or class hierarchy solely for appearance. Never manually include `wp-load.php` to create ad hoc web endpoints.

Use `plugin_dir_path()`, `plugins_url()`, theme path/URI helpers, `wp_upload_dir()`, and application URL helpers as appropriate. Distinguish parent-theme paths from active child-theme paths. Keep filesystem paths separate from URLs and use the Filesystem API where its deployment context requires it.

## Define headers, versions, and dependencies accurately

- Put the standard plugin header in its main PHP file: name, version, description, author, license, text domain, minimum WordPress, and minimum PHP as applicable. Use the theme's `style.css` header for theme identity and requirements.
- Use a consistently increasing version accepted by PHP `version_compare()`. Keep header, constants, package metadata, release tag, changelog, and plugin `Stable tag` aligned. Do not copy PKP's four-part or Moodle's timestamp build requirement into WordPress.
- Treat `Tested up to` as a statement of testing, not a runtime maximum or evidence created by changing a field. Document tested WordPress/PHP/database combinations separately from minimum requirements.
- Use `Requires Plugins` only according to the target core's supported slug-based dependency semantics. It does not express dependency version ranges or guarantee arbitrary load order; guard dependent calls and check required versions/features at runtime.
- Document dependencies not covered by native headers, including premium/private extensions and parent-theme versions. Do not silently download or activate optional dependencies without an authorized installation workflow.
- For privately distributed packages, assess `Update URI` and the intended update mechanism to avoid collisions with directory packages. An Update URI alone does not implement an updater; validate packages and authenticated endpoints separately.
- Keep the minimum PHP bootstrap parseable on supported runtimes. Guard optional APIs or raise declared minimums deliberately; runtime checks cannot rescue a PHP file that fails to parse.
- Verify block API versions, metadata fields, script-module APIs, `theme.json` schema/features, and editor package support against the minimum WordPress version. Gutenberg plugin support is a separate tested configuration, not proof of core support.

## Upstream sources

Match these docs and the installed source to the target version; these links are not a support matrix.

- [Plugin Handbook](https://developer.wordpress.org/plugins/)
- [Plugin headers](https://developer.wordpress.org/plugins/plugin-basics/header-requirements/)
- [Must-use plugins](https://developer.wordpress.org/advanced-administration/plugins/mu-plugins/)
- [Core drop-in registry](https://developer.wordpress.org/reference/functions/_get_dropins/)
- [Theme headers](https://developer.wordpress.org/themes/core-concepts/main-stylesheet/)
- [WordPress PHP coding standards](https://developer.wordpress.org/coding-standards/wordpress-coding-standards/php/)
