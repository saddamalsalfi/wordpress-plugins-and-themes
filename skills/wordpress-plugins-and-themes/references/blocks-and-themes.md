# Blocks, templates, and editor behavior

Keep content compatible across updates and theme switches. Check database-stored customization and the minimum core/editor version before editing file-based templates or schema.

## Build durable blocks and frontend assets

- Register blocks server-side from supported `block.json` metadata and integrate client registration/build output consistently. Select the block API version and fields supported by the minimum core release.
- Use WordPress packages, dependency extraction, generated `.asset.php` files, and supported script registration/enqueueing. Do not bundle duplicate React or incompatible copies of editor packages.
- Distinguish static saved markup from server-rendered dynamic blocks. Preserve saved content and provide deprecations/migrations when changing attributes or serialized markup; test old posts, not only newly inserted blocks.
- Keep authorization and confidential data handling on the server. Client-side restrictions and editor controls do not enforce permissions.
- Preserve block wrapper attributes, styles/supports, accessible semantics, and editor/frontend parity. Verify markup validity and avoid brittle DOM assumptions around core blocks.
- Use maintained editor/data APIs and React patterns; avoid modifying DOM managed by React. Gate experimental Gutenberg-only features and document any hard dependency.
- Enqueue assets on relevant frontend/admin/editor screens with declared dependencies and stable versioning. Do not load heavy assets site-wide when unused or use `time()` as production cache busting.
- Use `wp_json_encode()` and supported data-transfer APIs appropriately; do not concatenate untrusted script text or expose private runtime configuration. Validate script-context safety as well as JSON syntax.

## Implement classic, block, and child themes correctly

- Follow the actual template hierarchy. In classic themes, preserve the Loop, query state, `wp_head()`, `wp_footer()`, `wp_body_open()` where supported, `body_class()`, language attributes, and required navigation/content hooks.
- Use semantic HTML, proper pagination, forms, search, comments, media, and archive behavior. Restore global post state after custom loops; avoid replacing the main query unnecessarily.
- In block themes, use valid serialized block markup in `.html` templates/parts. Do not insert executable PHP into these files; use supported blocks, patterns, render callbacks, or extension points.
- Select `theme.json`'s `version` and a WordPress-release schema compatible with the minimum supported core. Its API version, schema URL, theme release version, and WordPress version are distinct. Do not validate production minimums only against the `trunk` schema.
- Recognize user customizations stored in the database: Site Editor templates, template parts, and global styles can override files. Inspect that precedence before diagnosing a code change as broken; never reset user customizations silently.
- For child themes, set the exact parent folder in the `Template` header. Child `functions.php` loads in addition to, and before, the parent's; do not copy the parent's functions wholesale or assume it is replaced.
- Inspect actual parent asset enqueueing before adding child/parent styles. Use appropriate active-theme or parent-theme file APIs and avoid double-loading stylesheets.
- Keep custom post types, business data, forms processing, and reusable content blocks in suitable plugins. A theme switch should preserve content ownership and avoid functional lock-in.
- Use core design tokens/global styles and scoped CSS instead of broad overrides. Preserve compatibility with default core blocks, editor styles, RTL, dark/color modes when offered, and user style choices.
- Test front page/home, posts/pages, archives, search, 404, comments, protected content, pagination, menus, media, empty states, and long/multilingual content. Test Site Editor and editor/frontend parity for block themes.
- Verify keyboard/focus, headings, landmarks, contrast, alt text, labels, skip links, zoom, touch targets, and reduced motion. Do not claim an accessibility-ready designation without meeting its applicable review criteria.

## Upstream sources

Match these docs and the installed source to the target version; these links are not a support matrix.

- [Block metadata](https://developer.wordpress.org/block-editor/reference-guides/block-api/block-metadata/)
- [Block deprecations](https://developer.wordpress.org/block-editor/reference-guides/block-api/block-deprecation/)
- [Theme Handbook](https://developer.wordpress.org/themes/)
- [Child theme inheritance and assets](https://developer.wordpress.org/themes/advanced-topics/child-themes/)
- [theme.json reference](https://developer.wordpress.org/block-editor/reference-guides/theme-json-reference/)
- [theme.json schema version guidance](https://make.wordpress.org/themes/2024/06/21/theme-json-version-3-frequently-asked-questions/)
- [Gutenberg sources: select the matching release](https://github.com/WordPress/gutenberg)
