"""Real MCP subprocess and loopback-only transports, plus optional container tests."""
import asyncio
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
NAME, VERSION = REGISTRY["name"], REGISTRY["version"]
SLUG = NAME.rsplit("/", 1)[1]
SKILL = ROOT / "skills" / SLUG
IMAGE = os.environ.get("SKILL_MCP_TEST_IMAGE", "")
HAS_MCP = importlib.util.find_spec("mcp") is not None

if HAS_MCP:
    import httpx2
    from httpx2 import AsyncClient
    from mcp.client import Client
    from mcp.client.stdio import StdioServerParameters

EXPECTED_TEXT = {
    "overview": (SKILL / "SKILL.md").read_text(encoding="utf-8"),
    "worked-scenarios": (SKILL / "examples/worked-scenarios.md").read_text(encoding="utf-8"),
    **{file.stem: file.read_text(encoding="utf-8") for file in (SKILL / "references").glob("*.md")},
}


def launch(*flags, cwd=None):
    return StdioServerParameters(
        command=sys.executable,
        args=["-B", str(ROOT / "server.py"), *flags],
        cwd=cwd,
    )


@unittest.skipUnless(HAS_MCP, "Install requirements.txt to run the MCP integration tests")
class McpTests(unittest.IsolatedAsyncioTestCase):
    async def assert_catalog(self, transport, mode="auto"):
        async with asyncio.timeout(90):
            async with Client(transport, mode=mode, read_timeout_seconds=40, cache=None) as client:
                self.assertEqual(client.server_info.name, NAME)
                self.assertEqual(client.server_info.version, VERSION)
                tools = {tool.name: tool for tool in (await client.list_tools()).tools}
                self.assertEqual(set(tools), {"list_guidelines", "get_guidelines"})
                for tool in tools.values():
                    self.assertTrue(tool.annotations.read_only_hint)
                    self.assertFalse(tool.annotations.destructive_hint)
                    self.assertFalse(tool.annotations.open_world_hint)

                result = await client.call_tool("list_guidelines")
                self.assertFalse(result.is_error)
                # Tool results carry a typed list via structuredContent or a text fallback.
                catalog = result.structured_content
                if isinstance(catalog, dict):
                    catalog = catalog["result"]
                if catalog is None:
                    catalog = json.loads(result.content[0].text)
                self.assertEqual({row["topic"] for row in catalog}, set(EXPECTED_TEXT))
                resources = {r.uri: r.mime_type for r in (await client.list_resources()).resources}
                self.assertEqual(resources, {f"skill://{SLUG}/{topic}": "text/markdown" for topic in EXPECTED_TEXT})
                for row in catalog:
                    topic = row["topic"]
                    uri = f"skill://{SLUG}/{topic}"
                    self.assertEqual(row["uri"], uri)
                    self.assertTrue(row["title"].strip())
                    tool = await client.call_tool("get_guidelines", {"topic": topic})
                    self.assertFalse(tool.is_error)
                    self.assertEqual(tool.content[0].text, EXPECTED_TEXT[topic])
                    resource = await client.read_resource(uri)
                    self.assertEqual(resource.contents[0].text, EXPECTED_TEXT[topic])
                default = await client.call_tool("get_guidelines")
                self.assertEqual(default.content[0].text, EXPECTED_TEXT["overview"])

                for unknown in ("../../LICENSE", "https://example.invalid/never-read", "x" * 81):
                    with self.subTest(unknown=unknown):
                        bad = await client.call_tool("get_guidelines", {"topic": unknown})
                        self.assertTrue(bad.is_error)
                        self.assertIn("Unknown topic", bad.content[0].text)
                        self.assertNotIn(unknown, bad.content[0].text)

    async def test_stdio_from_non_repository_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            await self.assert_catalog(launch(cwd=tmp))

    async def test_stdio_legacy_client(self):
        await self.assert_catalog(launch("--transport", "stdio"), mode="legacy")

    async def test_streamable_http_local(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-B", str(ROOT / "server.py"), "--transport", "streamable-http", "--port", str(port),
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        url = f"http://127.0.0.1:{port}/mcp"
        try:
            for _ in range(150):
                try:
                    _, writer = await asyncio.open_connection("127.0.0.1", port)
                    writer.close()
                    await writer.wait_closed()
                    break
                except OSError:
                    if proc.returncode is not None:
                        stderr = (await proc.communicate())[1].decode(errors="replace")
                        self.fail(f"MCP server exited: {stderr}")
                    await asyncio.sleep(0.1)
            else:
                self.fail("MCP server did not listen on loopback")

            async with AsyncClient(timeout=5, trust_env=False) as http:
                checks = (("Origin", "https://example.invalid"), ("Host", "example.invalid"))
                for header, value in checks:
                    response = await http.post(
                        url, json={"jsonrpc": "2.0", "method": "ping", "id": 1},
                        headers={header: value, "Accept": "application/json, text/event-stream"},
                    )
                    self.assertIn(response.status_code, (403, 421))

            await self.assert_catalog(url)
        finally:
            if proc.returncode is None:
                with contextlib.suppress(ProcessLookupError):
                    proc.terminate()
                try:
                    await asyncio.wait_for(proc.communicate(), 5)
                except TimeoutError:
                    proc.kill()
                    await proc.communicate()

    @unittest.skipUnless(IMAGE and shutil.which("docker"), "Set SKILL_MCP_TEST_IMAGE to a built image tag")
    async def test_docker_stdio_without_network(self):
        image = json.loads(subprocess.check_output(["docker", "image", "inspect", IMAGE], text=True))[0]
        self.assertEqual(image["Config"]["User"], "10001:10001")
        self.assertEqual(image["Config"]["Labels"]["io.modelcontextprotocol.server.name"], NAME)
        self.assertEqual(image["Config"]["Labels"]["org.opencontainers.image.version"], VERSION)
        await self.assert_catalog(StdioServerParameters(
            command=shutil.which("docker"),
            args=["run", "--platform", f'linux/{image["Architecture"]}', "--rm", "-i", "--network", "none", "--read-only", "--cap-drop", "ALL",
                  "--security-opt", "no-new-privileges", IMAGE],
        ))

    @unittest.skipUnless(IMAGE and shutil.which("docker"), "Set SKILL_MCP_TEST_IMAGE to a built image tag")
    async def test_docker_streamable_http_loopback(self):
        docker = shutil.which("docker")
        arch = subprocess.check_output([docker, "image", "inspect", "--format", "{{.Architecture}}", IMAGE],
                                       text=True).strip()
        cid = subprocess.check_output(
            [docker, "run", "--platform", f"linux/{arch}", "--rm", "-d", "--read-only", "--cap-drop", "ALL", "--security-opt",
             "no-new-privileges", "-p", "127.0.0.1::8000", IMAGE, "--transport", "streamable-http",
             "--host", "0.0.0.0"], text=True
        ).strip()
        try:
            binding = subprocess.check_output([docker, "port", cid, "8000/tcp"], text=True).strip()
            self.assertTrue(binding.startswith("127.0.0.1:"), binding)
            port = int(binding.rsplit(":", 1)[1])
            for _ in range(250):
                try:
                    _, writer = await asyncio.open_connection("127.0.0.1", port)
                    writer.close()
                    await writer.wait_closed()
                    # Port forwarding may accept TCP before the app is ready.
                    async with AsyncClient(timeout=2, trust_env=False) as http:
                        response = await http.post(
                            f"http://127.0.0.1:{port}/mcp",
                            json={"jsonrpc": "2.0", "method": "ping", "id": 1},
                            headers={"Accept": "application/json, text/event-stream"},
                        )
                        if response.status_code == 200 and response.json().get("id") == 1:
                            break
                except (OSError, httpx2.TransportError):
                    pass
                await asyncio.sleep(0.12)
            else:
                self.fail("Container did not serve /mcp on loopback")
            await self.assert_catalog(f"http://127.0.0.1:{port}/mcp")
        finally:
            subprocess.run([docker, "stop", "--timeout", "3", cid], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
