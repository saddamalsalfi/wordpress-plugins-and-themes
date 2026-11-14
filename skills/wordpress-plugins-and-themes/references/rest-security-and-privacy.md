# Object-level access, REST/AJAX, and personal data

Enforce capabilities at each actual operation with its resolved object/site. Reject invalid requests without writes or disclosure; nonces and hiding links do not authorize requests.

## Enforce authorization and safe input/output

- Check capabilities with `current_user_can()` and object-aware meta capabilities such as `edit_post` with an ID where appropriate. Do not authorize by role name, `is_admin()`, logged-in status, or hidden menus alone.
- Verify nonces for the appropriate browser mutation flow and capabilities independently. WordPress nonces are neither authentication nor one-time replay protection; account for logged-out nonce limitations and cached/expired forms.
- Validate structure, types, ranges, ownership, and business rules before persistence. Use `wp_unslash()` for slashed superglobal data when needed; do not blindly unslash REST payloads or sanitize every value with one generic function.
- Use Settings API schemas/sanitize callbacks and registered metadata schemas when applicable. Reject unauthorized object access and cross-site data references in both admin and public requests.
- Escape at output with the correct API, such as `esc_html()`, `esc_attr()`, `esc_url()`, or an appropriate `wp_kses()` allowlist. Sanitization, SQL preparation, and escaping solve different problems; avoid storing HTML-escaped data as canonical content.
- Use `$wpdb->prepare()` for dynamic values and allowlist dynamic identifiers/order expressions; use identifier placeholders only when supported by the minimum core version. Never concatenate untrusted SQL fragments.
- Validate uploads, file types, sizes, paths, ownership, archives, and download permissions. Public uploads are not private storage; protect confidential files through an actual access-controlled delivery/storage design.
- Use the HTTP API, safe URL handling, HTTPS, timeouts, and endpoint restrictions for remote requests. Prevent SSRF, unsafe redirects, unserialization/object injection, and arbitrary PHP execution.
- Keep secrets, personal payloads, SQL details, and stack traces out of user output and routine logs. A direct-access `ABSPATH` guard is useful where appropriate but is not endpoint authorization.

## Implement REST, AJAX, and external integrations explicitly

- Register REST routes on `rest_api_init`, use a unique versioned namespace, define methods/arguments/schemas, and provide a `permission_callback` for every route.
- Use `__return_true` only for intentionally public, safe operations and verify that the response contains only public data. Check per-object capabilities on protected routes.
- Use supported authentication for the deployment: cookie-authenticated browser REST requests need appropriate REST nonce handling; remote clients may use Application Passwords over HTTPS or another authorized scheme. Do not expose credentials in frontend code.
- For `admin-ajax.php` and `admin-post.php`, distinguish authenticated from `nopriv` actions. Validate nonces, capabilities, and object access in the handler; return consistent errors and JSON via supported APIs.
- Handle webhook signatures, timestamps, replay controls, rate limits, duplicate processing, and ambiguous remote failures. Do not use a WordPress nonce as a payment-provider webhook signature.
- Check integration readiness at the correct lifecycle point and degrade safely when an extension is absent. For WooCommerce or other ecosystems, follow their official data APIs and compatibility declarations; do not assume legacy post tables are the supported storage contract.

## Implement privacy based on actual data flows

Inventory profiles, emails, IP addresses, cookies, tracking, form submissions, content metadata, logs, files, background payloads, and external services.

- Minimize data collection and retention. Avoid real personal data in fixtures, screenshots, source control, or diagnostics.
- Add plugin-owned data to core privacy exports using `wp_privacy_personal_data_exporters` and erasure using `wp_privacy_personal_data_erasers` when applicable. Implement pagination, stable item identities, truthful completion, and retained-item explanations.
- Include guest/email-associated records and plugin-owned custom tables/files. Do not assume a user ID is the only personal-data key or core exports automatically cover everything your plugin stores.
- Provide suggested privacy-policy text with `wp_add_privacy_policy_content()` when needed; describe purposes, processors, fields, retention, and cookies honestly.
- Make tracking/external disclosure explicit and follow applicable consent and directory requirements. Avoid loading third-party fonts, analytics, or manuscript/form content into external AI services by default.
- Define retention and erasure for site/network removal, uninstall, and external processors. Do not erase legally/business-required records indiscriminately; explain retention through the approved policy.
- Do not invent Moodle privacy providers for WordPress or claim legal certification from a working exporter, checker, or privacy notice.

## Upstream sources

Match these docs and the installed source to the target version; these links are not a support matrix.

- [Nonce behavior](https://developer.wordpress.org/apis/security/nonces/)
- [REST routes and permission callbacks](https://developer.wordpress.org/rest-api/extending-the-rest-api/adding-custom-endpoints/)
- [Privacy exporters](https://developer.wordpress.org/plugins/privacy/adding-the-personal-data-exporter-to-your-plugin/)
- [Privacy erasers](https://developer.wordpress.org/plugins/privacy/adding-the-personal-data-eraser-to-your-plugin/)
