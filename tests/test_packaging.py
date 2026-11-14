"""Offline checks for this instruction-only Agent Skill distribution."""
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
LINK = re.compile(r"\]\(([^)\s]+)\)")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def load_frontmatter(path):
    """Read this repository's flat subset of YAML (bare and JSON-quoted strings)."""
    data = path.read_text(encoding="utf-8").splitlines()
    if not data or data[0] != "---" or "---" not in data[1:]:
        raise ValueError(f"Missing frontmatter: {path}")
    end = data.index("---", 1)
    fields = {}
    for line in data[1:end]:
        key, separator, value = line.partition(": ")
        if not separator or not value.strip() or key in fields:
            raise ValueError(f"Invalid or duplicate field in {path}: {line!r}")
        fields[key] = json.loads(value) if value.startswith('"') else value.strip()
    return fields, "\n".join(data[end + 1:])


def local_markdown_links(text):
    for match in LINK.finditer(text):
        url = urlsplit(match[1])
        if not url.scheme and not url.netloc and url.path:
            yield unquote(url.path)


def assert_local_links(case, files, boundary):
    for doc in files:
        for href in local_markdown_links(doc.read_text(encoding="utf-8")):
            with case.subTest(doc=doc.name, href=href):
                # Check spelling/case explicitly, including on Windows.
                current = doc.parent
                for part in Path(href).parts:
                    if part == "..":
                        current = current.parent
                    elif part != ".":
                        case.assertIn(part, {p.name for p in current.iterdir()})
                        current = current / part
                case.assertTrue(current.resolve().is_relative_to(boundary.resolve()))
                case.assertTrue(current.exists())


class DistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        builds = list((ROOT / "skills").glob("*/SKILL.md"))
        if len(builds) != 1:
            raise AssertionError(f"Expected one packaged skill, got {len(builds)}")
        cls.entry = builds[0]
        cls.skill = cls.entry.parent
        cls.name = cls.skill.name
        cls.fields, cls.body = load_frontmatter(cls.entry)

    def test_canonical_entrypoint(self):
        self.assertRegex(self.name, SLUG)
        self.assertLessEqual(len(self.name), 64)
        self.assertEqual(set(self.fields), {"name", "description", "license"})
        self.assertEqual(self.fields["name"], self.name)
        self.assertIsInstance(self.fields["description"], str)
        self.assertTrue(0 < len(self.fields["description"].strip()) <= 1024)
        self.assertEqual(self.fields["license"], "MIT")
        self.assertTrue(self.body.strip())
        self.assertLessEqual(len(self.body.splitlines()), 100)
        self.assertEqual((self.skill / "LICENSE").read_bytes(), (ROOT / "LICENSE").read_bytes())
        self.assertFalse((self.skill / "scripts").exists(), "The installed skill is instruction-only")

    def test_progressive_references_are_reachable(self):
        refs = set((self.skill / "references").glob("*.md"))
        examples = set((self.skill / "examples").glob("*.md"))
        self.assertTrue(refs and examples)
        linked = set(local_markdown_links(self.body))
        for doc in refs | examples:
            self.assertIn(doc.relative_to(self.skill).as_posix(), linked)

    def test_copy_install_is_self_contained(self):
        with tempfile.TemporaryDirectory(prefix="skill install ") as tmp:
            root = Path(tmp)
            for discovery in (".agents/skills", ".claude/skills", ".cursor/skills", ".github/skills"):
                with self.subTest(discovery=discovery):
                    installed = root / discovery / self.name
                    shutil.copytree(self.skill, installed)
                    fields, _ = load_frontmatter(installed / "SKILL.md")
                    self.assertEqual(fields["name"], installed.name)
                    assert_local_links(self, installed.rglob("*.md"), installed)

    def test_bilingual_readme_links(self):
        for readme in (ROOT / "README.md", ROOT / "README.ar.md"):
            body = readme.read_text(encoding="utf-8")
            self.assertIn(f"skills/{self.name}/SKILL.md", set(local_markdown_links(body)))
            assert_local_links(self, [readme], ROOT)

    def test_manifest_agrees_with_the_skill(self):
        manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(set(manifest), {"$schema", "name", "description", "author", "license", "keywords"})
        self.assertEqual(manifest["$schema"], CANONICAL_PLUGIN_SCHEMA)
        for field in ("name", "description", "license"):
            self.assertEqual(manifest[field], self.fields[field])
        self.assertEqual(set(manifest["author"]), {"name"})
        self.assertIsInstance(manifest["author"]["name"], str)
        self.assertTrue(manifest["author"]["name"].strip())
        self.assertIn("agent-skills", manifest["keywords"])
        self.assertTrue(all(isinstance(x, str) and x.strip() for x in manifest["keywords"]))
        for path in ("mcp.json", ".mcp.json", "hooks"):
            self.assertFalse((ROOT / path).exists())

    def test_client_adapters(self):
        metadata = (self.skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("$" + self.name, metadata)
        rule = ROOT / "rules" / f"{self.name}.mdc"
        config, content = load_frontmatter(rule)
        self.assertEqual(config, {"alwaysApply": "false"})
        for directory in (".agents/skills", ".cursor/skills"):
            self.assertIn(f"{directory}/{self.name}/SKILL.md", content)
