# Localization and site/network boundaries

Check what is shared across the network and what remains per site. Keep translations separate from writable identifiers and preserve blog context through all exits.

## Localize and support Multisite deliberately

- Use literal text domains, translation functions, context/plural APIs, translator comments, and complete translatable phrases with placeholders. Escape translated strings according to their output context.
- Use `@wordpress/i18n` and supported script-translation loading for JavaScript. Generate translation files using matching tools; do not assume PHP localization covers editor scripts.
- Follow current just-in-time/manual translation timing requirements rather than loading translations prematurely. Test locale switching, Arabic RTL, long strings, and locale-aware dates/numbers.
- Separate per-site options/tables from network options/tables and site users from network-level identities. Network activation does not automatically initialize every site's schema or future sites.
- Use bounded site iteration and explicit new-site initialization when needed. Pair every `switch_to_blog()` with `restore_current_blog()`, including error paths, and scope caches/jobs correctly.
- Check network/site capabilities at the operation's actual scope. Test site deletion, domain mapping, subdirectory installs, and site-specific activation where supported.

## Upstream sources

Match these docs and the installed source to the target version; these links are not a support matrix.

- [Plugin internationalization](https://developer.wordpress.org/plugins/internationalization/)
- [Blog switching and restore contract](https://developer.wordpress.org/reference/functions/switch_to_blog/)
