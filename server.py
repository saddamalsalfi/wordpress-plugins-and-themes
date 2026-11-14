"""Read-only MCP access to this repository's bundled Agent Skill."""
import argparse
from pathlib import Path
import re
import tomllib

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.mcpserver.resources import TextResource
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations

ROOT = Path(__file__).resolve().parent
SLUG = "wordpress-plugins-and-themes"
NAME = "io.github.saddamalsalfi/" + SLUG
VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
MAX_DOCUMENT_BYTES = 64 * 1024
TOPIC_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)


def _load_documents():
    """Load only checked-in Markdown from this skill, before handling client input."""
    expected_root = ROOT / "skills" / SLUG
    if expected_root.resolve(strict=True) != expected_root:
        raise RuntimeError("Skill directory must not be redirected")
    locations = {
        "overview": "SKILL.md",
        "worked-scenarios": "examples/worked-scenarios.md",
    }
    ref_dir = expected_root / "references"
    if ref_dir.resolve(strict=True) != ref_dir:
        raise RuntimeError("References directory must not be redirected")
    for path in sorted(ref_dir.glob("*.md")):
        topic = path.stem
        if topic in locations or not TOPIC_ID.fullmatch(topic):
            raise RuntimeError("Invalid or duplicate reference identifier")
        locations[topic] = path.relative_to(expected_root).as_posix()
    if len(locations) < 3:
        raise RuntimeError("No bundled references found")

    documents = {}
    for key, rel in locations.items():
        file = expected_root / rel
        if file.resolve(strict=True) != file or not file.is_file():
            raise RuntimeError("Documentation must be a regular bundled file")
        with file.open("rb") as handle:
            raw = handle.read(MAX_DOCUMENT_BYTES + 1)
        if not 0 < len(raw) <= MAX_DOCUMENT_BYTES:
            raise RuntimeError("Bundled documentation is empty or too large")
        content = raw.decode("utf-8")
        title = next((line[2:] for line in content.splitlines() if line.startswith("# ")), key)
        documents[key] = {"title": title, "text": content, "uri": f"skill://{SLUG}/{key}"}
    return documents


DOCUMENTS = _load_documents()
mcp = MCPServer(
    NAME,
    title="WordPress Plugins and Themes",
    description="Read-only access to bundled documentation for this Agent Skill.",
    instructions="Call list_guidelines, then get_guidelines with a listed topic. Only bundled Markdown is served.",
    version=VERSION,
    log_level="WARNING",
    subscriptions=False,
)


@mcp.tool(annotations=READ_ONLY)
def list_guidelines() -> list[dict[str, str]]:
    """List the fixed topic IDs, titles and Markdown resource URIs."""
    return [{"topic": topic, "title": doc["title"], "uri": doc["uri"]} for topic, doc in DOCUMENTS.items()]


@mcp.tool(annotations=READ_ONLY, structured_output=False)
def get_guidelines(topic: str = "overview") -> str:
    """Read the full Markdown for one exact topic ID returned by list_guidelines."""
    if len(topic) > 80 or topic not in DOCUMENTS:
        raise ToolError("Unknown topic. Call list_guidelines to see available topic IDs.")
    return DOCUMENTS[topic]["text"]


for topic_id, document in DOCUMENTS.items():
    mcp.add_resource(TextResource(
        uri=document["uri"], name=topic_id, title=document["title"],
        mime_type="text/markdown", text=document["text"],
    ))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transport", choices=("stdio", "streamable-http"), default="stdio")
    parser.add_argument("--host", choices=("127.0.0.1", "0.0.0.0"), default="127.0.0.1",
                        help="Use 0.0.0.0 only inside an isolated container behind a restricted port or HTTPS gateway.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--allowed-host", action="append", default=[], metavar="HOST[:PORT]",
                        help="Additional exact Host header for a controlled HTTP gateway.")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    if any(not re.fullmatch(r"[A-Za-z0-9.-]+(?::[0-9]{1,5})?", host)
           or host.startswith((".", "-")) for host in args.allowed_host):
        parser.error("--allowed-host must be an exact DNS name or IPv4 address, optionally with a port")
    if args.transport == "stdio":
        mcp.run(transport="stdio")
        return
    # Browser origins are restricted to the local endpoint. A public, browser-facing
    # deployment must use a gateway with its own explicit origin and access policy.
    loopback = ["127.0.0.1", "localhost"]
    mcp.run(
        transport="streamable-http", host=args.host, port=args.port,
        streamable_http_path="/mcp", stateless_http=True, json_response=True,
        max_request_body_size=32 * 1024,
        transport_security=TransportSecuritySettings(
            allowed_hosts=[*loopback, *(f"{host}:*" for host in loopback), *args.allowed_host],
            allowed_origins=[*(f"http://{host}:*" for host in loopback)],
        ),
    )


if __name__ == "__main__":
    main()
