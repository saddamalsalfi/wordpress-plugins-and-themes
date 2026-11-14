# Distribute the skill and its MCP server

The repository ships two entry points from the same Markdown. The [Agent Skill](../skills/wordpress-plugins-and-themes/SKILL.md) is discoverable without starting a process; the read-only MCP server exposes the same content to clients that use MCP. Docker packages the server; it does not enroll either entry point in a directory.

| Channel | What to publish or configure |
|---|---|
| Agent Skills clients and the [skills CLI](https://github.com/vercel-labs/skills#install-a-skill) | Push this Git repository. Use `npx skills add saddamalsalfi/wordpress-plugins-and-themes --skill wordpress-plugins-and-themes` in a target project after the repository is available. |
| Agent Plugins clients with local stdio and [portable placeholders](https://agent-plugins.org/plugin-authors/mcp-servers) | Use the root [plugin manifest](../plugin.json) and [MCP config](../mcp.json). The launcher needs `uv` and a supported Python interpreter; it uses the lockfile and the client's plugin data directory. |
| [Glama](https://glama.ai/mcp/hosting) | Submit the public GitHub URL following Glama's flow. The repo includes a root [Dockerfile](../Dockerfile) and [maintainer metadata](../glama.json). Its default stdio mode can be wrapped by the hosting service. |
| [Official MCP Registry (OCI)](https://modelcontextprotocol.io/registry/package-types#dockeroci-images) | Publish the public OCI image recorded in [server.json](../server.json), then submit the metadata with `mcp-publisher`. |
| Hosted clients or catalogs that require a URL, e.g. [OpenAI's public plugin submission](https://developers.openai.com/plugins/build/plugins#bundled-mcp-servers-and-lifecycle-hooks) | Deploy first and use the actual HTTPS Streamable HTTP `/mcp` URL with the client or catalog. Local `stdio` is not a remote endpoint. Each catalog may have separate submission, access, or review requirements. |

## MCP tools

- `list_guidelines` returns topic identifiers, titles, and resource URIs.
- `get_guidelines` reads one topic by exact ID; it defaults to `overview`.
- Resources expose the same Markdown as `skill://wordpress-plugins-and-themes/<topic>`. No tool writes files, runs commands, reads paths supplied by users, or fetches URLs.

Try: **“Call `list_guidelines` first, then read the most relevant topic using `get_guidelines`. Apply it to the current WordPress task and report the checks you actually ran.”**

## Run locally

Install the locked dependencies from the repository root with Python 3.13 or 3.14. In PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes --only-binary=:all: -r requirements.txt
.\.venv\Scripts\python.exe -B server.py --transport streamable-http
```

On macOS/Linux the virtual environment interpreter is `.venv/bin/python`. The HTTP test endpoint is `http://127.0.0.1:8000/mcp`. For a client that launches a process, set the command to the **absolute** interpreter path and arguments to the **absolute** `server.py` path plus `--transport`, `stdio`. No manual stdio process needs to stay open.

Build with Docker (from the repository root):

```sh
docker build -t wordpress-plugins-and-themes-mcp:local .
```

A local stdio configuration entry for clients using an `mcpServers` JSON object (such as Cursor; merge the named entry into your existing config):

```json
{
  "mcpServers": {
    "wordpress-plugins-and-themes": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--network", "none", "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "wordpress-plugins-and-themes-mcp:local"]
    }
  }
}
```

For [Codex](https://learn.chatgpt.com/docs/extend/mcp) and [Claude Code](https://code.claude.com/docs/en/mcp), the same launch command can be added with:

```sh
codex mcp add wordpress-plugins-and-themes -- docker run --rm -i --network none --read-only --cap-drop ALL wordpress-plugins-and-themes-mcp:local
claude mcp add --transport stdio wordpress-plugins-and-themes -- docker run --rm -i --network none --read-only --cap-drop ALL wordpress-plugins-and-themes-mcp:local
```

For local HTTP through Docker, publish only to loopback (change the host-side port if in use):

```sh
docker run --rm --read-only --cap-drop ALL -p 127.0.0.1:8000:8000 wordpress-plugins-and-themes-mcp:local --transport streamable-http --host 0.0.0.0
```

An internet-facing deployment should terminate TLS at a gateway, restrict the upstream port and accepted Host/Origin, and apply authentication/access policy and rate limits as needed. For a proxy that preserves the upstream host, pass an exact `--allowed-host HOST[:PORT]`; by default the server accepts only loopback hosts. Use the deployed URL in a separate remote client configuration. Do not put credentials or an illustrative URL in submitted metadata.

## Publish the OCI image and register it

These are release-time steps, not part of the test workflow:

1. Push this repository to GitHub and publish a Git tag such as `v1.0.0` for a verified commit. Keep the version in `pyproject.toml`, the Docker version label, and `server.json` aligned before tagging.
2. From the tagged checkout, authenticate to [GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry) with package write access, use a Buildx builder that supports both platforms, and publish the exact version recorded in `server.json`.

   ```sh
   docker buildx build --platform linux/amd64,linux/arm64 --tag ghcr.io/saddamalsalfi/wordpress-plugins-and-themes:1.0.0 --push .
   docker buildx imagetools inspect ghcr.io/saddamalsalfi/wordpress-plugins-and-themes:1.0.0
   ```

3. Make the GHCR package public, confirm an unauthenticated pull and the MCP identity label, then run `mcp-publisher login github` and `mcp-publisher publish` from the repository root. See the [MCP Registry quickstart](https://modelcontextprotocol.io/registry/quickstart). The registry serves metadata, not the image. Other [registries and aggregators](https://modelcontextprotocol.io/registry/registry-aggregators) may follow a separate indexing or submission process.

## Verify or update

- Verify with `python -B -m unittest discover -s tests -v` in the environment containing the locked dependencies.
- To test the container over real MCP stdio, set `SKILL_MCP_TEST_IMAGE` to the built image tag and run the same suite.
- After changing SDK dependencies in `pyproject.toml`, update `uv.lock` with `uv lock` and regenerate the hashed `requirements.txt` with `uv export --locked --no-dev --no-emit-project --format requirements-txt --output-file requirements.txt`. Recheck supported Python versions and verify both builds before publishing.
