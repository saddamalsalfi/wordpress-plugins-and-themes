# Upgrades, Multisite, and scheduled work

Identify the owner of data, schema, rewrite rules and scheduled effects. Test upgrades on an existing install rather than relying only on first activation.

## Manage lifecycle and database changes safely

- Register activation/deactivation handlers using the main plugin file at the appropriate bootstrap stage. Keep activation bounded and idempotent; avoid unsolicited remote calls, output, and bulk data processing.
- Do not rely only on activation for upgrades: plugin updates do not generally re-run activation hooks. Store a schema/data version and use a guarded upgrade path compatible with normal and network operation.
- Keep deactivation separate from uninstall. Deactivation should normally unschedule owned work and release temporary state; it should not erase content or settings.
- Implement opt-in/documented permanent cleanup through supported uninstall mechanisms. Guard `uninstall.php` with `WP_UNINSTALL_PLUGIN`; delete only data owned by this package and consider Multisite scope.
- Prefer core objects, metadata, settings, and options when they fit. Add custom tables only for justified query/lifecycle needs, using `$wpdb->prefix` or `$wpdb->base_prefix` intentionally.
- Use WordPress-compatible SQL, prepared values, schema tools such as `dbDelta()` where appropriate, and its actual syntax requirements. Do not assume `dbDelta()` handles every destructive migration or rename.
- Keep migrations resumable, version-guarded, and bounded. Use preflight checks; do not assume DDL or database/filesystem operations are one atomic transaction.
- Flush rewrite rules only at justified lifecycle points after registering the relevant structures, never on every request. Preserve custom content and URLs during upgrades/theme switches.

## Make scheduled work and performance predictable

- Treat WP-Cron as a scheduler triggered by requests by default, not a guarantee of exact execution time. Document real cron/CLI integration for timing-sensitive work.
- Avoid duplicate scheduled events; use stable hook names and consistent arguments, then unschedule owned events appropriately. Handle upgrades to event shape and recurrence.
- Process bulk work in bounded batches with durable checkpoints, safe retry limits, idempotent effects, and observable failure states. A transient alone is not a reliable atomic distributed lock.
- Revalidate object state/site scope when jobs execute. Avoid assuming a background request has the initiating user's authenticated session; record only necessary audit identity.
- Avoid unbounded queries, N+1 patterns, excessive autoloaded options, repeated remote requests, and large synchronous admin actions. Use core query/cache APIs with scoped keys and deliberate invalidation.
- Treat transients as disposable cache entries that may disappear early. Do not store the only copy of workflow state or authorization decisions in them.
- Measure performance on representative workloads. Do not equate background execution with parallelism or claim speed/resource improvements from architecture alone.

## Upstream sources

Match these docs and the installed source to the target version; these links are not a support matrix.

- [Activation and deactivation](https://developer.wordpress.org/plugins/plugin-basics/activation-deactivation-hooks/)
- [Uninstall mechanisms](https://developer.wordpress.org/plugins/plugin-basics/uninstall-methods/)
- [WordPress scheduling](https://developer.wordpress.org/plugins/cron/)
