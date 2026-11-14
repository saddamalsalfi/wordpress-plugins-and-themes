# WordPress Plugins and Themes

[العربية](README.ar.md) · [Skill](skills/wordpress-plugins-and-themes/SKILL.md) · [Examples](skills/wordpress-plugins-and-themes/examples/worked-scenarios.md) · [MIT License](LICENSE)

An independent [Agent Skill](https://agentskills.io/specification) for WordPress extension development. Separates runtime plugin and theme types from WordPress.org distribution rules and project naming. This is instruction and reference content for coding agents, not an installable WordPress extension. The skill name is not the runtime identifier of any extension you build.

## What it covers

- Choose ordinary, network, must-use, or drop-in lifecycle; keep slug, text domain, and public identifiers stable.
- Review per-object REST permissions, privacy exports/erasure, migrations, and Multisite scope.
- Support classic, block, and child themes without losing saved block content or Site Editor customizations.

## Install

Copy the **whole** `skills/wordpress-plugins-and-themes/` folder into a discovery directory in the **target application**. Keep its name, references, and examples intact.

| Agent | Project directory |
|---|---|
| [Codex](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) | `.agents/skills/` |
| [Claude Code](https://code.claude.com/docs/en/skills#choose-where-skills-load) | `.claude/skills/` |
| [Cursor](https://cursor.com/docs/skills) | `.agents/skills/` or `.cursor/skills/` |
| [GitHub Copilot](https://docs.github.com/en/copilot/concepts/customizations/agent-skills) | `.github/skills/` or `.agents/skills/` where supported |
| [Google Antigravity](https://antigravity.google/docs/customization-discovery/) | `.agents/skills/` |

A single copy in `.agents/skills/` works for clients that share that project path. Use the client-specific path when required; avoid duplicate copies for the same client.

For example, from the **target project root** (PowerShell; point `$skill` to the checked-out skill directory, and use a fresh destination):

```powershell
$skill = 'C:/path/to/wordpress-plugins-and-themes/skills/wordpress-plugins-and-themes'
New-Item -ItemType Directory -Path '.agents/skills' -Force | Out-Null
Copy-Item -LiteralPath $skill -Destination '.agents/skills/' -Recurse
```

**Optional installer:** From the target project, use a local checkout with the [skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md):

```sh
npx skills add "/path/to/wordpress-plugins-and-themes" --list
npx skills add "/path/to/wordpress-plugins-and-themes" --skill wordpress-plugins-and-themes
```

After publishing to GitHub, pass the repository's `OWNER/REPO` instead of the local path. This works independently of the optional [Agent Plugins manifest](https://agent-plugins.org/plugin-authors/manifest). Installing the native skill does not start or require the optional MCP server or Docker. See the client's documentation for hosted or organization-managed installations.

**Optional Cursor rule:** After installing the skill, copy [the manual rule](rules/wordpress-plugins-and-themes.mdc) to the target project's `.cursor/rules/` and mention `@wordpress-plugins-and-themes` as a rule in chat. Prefer the native skill when available; this shortcut does not replace it. [Cursor rules docs](https://cursor.com/docs/rules)

## MCP and Docker

Use the read-only MCP server if your client needs MCP instead of direct skill discovery. It serves the same bundled references over stdio or Streamable HTTP. See the [setup and publishing guide](docs/distribution.md) for Python, Docker, Glama, and the official MCP Registry.

## Try it

```text
Use the wordpress-plugins-and-themes skill. Review this WordPress block plugin before release. Confirm its minimum core support, protect the REST operation with per-object capabilities, and verify existing saved blocks and a clean install from the built ZIP.
```

In Codex you can also start with `$wordpress-plugins-and-themes`; in Claude Code, use `/wordpress-plugins-and-themes`. The skill reports in the user's language unless they request another.

## Maintainer checks

Run from this repository root with Python 3.10+:

```sh
python -B -m unittest discover -s tests -v
```

The standard-library checks cover installation, metadata, and local links. To exercise MCP, install the locked dependencies as described in the setup guide and rerun the suite. The GitHub Actions workflow runs these checks on Windows and Linux. They do **not** exercise WordPress runtime code or certify that a resulting package is compatible or accepted upstream.

This repository is independent and not endorsed by WordPress. The MIT license applies to this skill; check the applicable license and directory requirements for any extension it helps you build.

## Source

Adapted from the project guide `wordpress-plugin-and-theme-best-practices.md`. Topic-specific documentation is bundled under `skills/wordpress-plugins-and-themes/references/`.
