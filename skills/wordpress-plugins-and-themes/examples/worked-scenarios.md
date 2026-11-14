# Worked scenarios

These examples show how to select the right reference and verify a result. No example is a report of tests actually executed.

## Upgrade a block plugin without losing saved content

**Prompt:** “Add a field to our existing dynamic block and expose it through a protected REST route; support our declared minimum core version.”

**Route:** [Extension contract](../references/extension-contract.md), [blocks and themes](../references/blocks-and-themes.md), and [REST and privacy](../references/rest-security-and-privacy.md).

1. Preserve the registered block name, existing attributes and saved content. Check the metadata API version in actual supported core. Document any required compatibility handling.
2. Give the route an object-aware `permission_callback`; validate and explicitly map accepted data. Nonces serve the browser request flow and are not a substitute for permission checks.
3. Test an existing saved block and a new insertion; verify permitted and denied requests and no unauthorized persistence. Include the built block files and validate the final slug ZIP using [testing and release](../references/testing-and-release.md).

## Fix a child-theme template that is hidden by Site Editor settings

**Prompt:** “My updated template file is not appearing on an existing WordPress site.”

**Route:** [Blocks and themes](../references/blocks-and-themes.md). Identify the selected template and whether database-stored Site Editor content takes precedence. Preserve the user's saved customization, check the exact parent folder in the child `Template` header, and report the smallest targeted adjustment rather than resetting all templates.
