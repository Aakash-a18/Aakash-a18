from __future__ import annotations

import json
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProfileRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "render_profile.py")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_generated_svgs_are_valid_xml(self) -> None:
        for name in (
            "flight-recorder.svg",
            "flight-recorder-mobile.svg",
            "agentic-handshake.svg",
            "agentic-handshake-mobile.svg",
            "public-signal.svg",
            "public-signal-mobile.svg",
        ):
            path = ROOT / "assets" / name
            self.assertTrue(path.exists(), name)
            ET.parse(path)

    def test_flight_recorder_contains_locked_content(self) -> None:
        svg = (ROOT / "assets" / "flight-recorder.svg").read_text(encoding="utf-8")
        for expected in (
            "AAKASH AGRAWAL",
            "MESHERRA",
            "MESHYCAL",
            "CHRONICA",
            "FUNDA",
            "03 PRIVATE PROGRAMS / ACTIVE",
            "DISCLOSE THE QUESTION. PROTECT THE WORK.",
        ):
            self.assertIn(expected, svg)
        self.assertNotIn("<script", svg.lower())
        self.assertNotIn("foreignObject", svg)
        self.assertIn("prefers-reduced-motion", svg)

    def test_v2_assets_hold_legibility_and_semantic_color_lock(self) -> None:
        desktop = (ROOT / "assets" / "flight-recorder.svg").read_text(encoding="utf-8")
        mobile = (ROOT / "assets" / "flight-recorder-mobile.svg").read_text(encoding="utf-8")
        handshake = (ROOT / "assets" / "agentic-handshake.svg").read_text(encoding="utf-8")
        self.assertIn('width="1200" height="620"', desktop)
        self.assertIn('width="640" height="760"', mobile)
        self.assertIn(".micro { font-size: 13px", desktop)
        self.assertIn(".micro{font-size:15px}", mobile)
        self.assertNotIn("#24d7e8", handshake)

    def test_private_program_schema_cannot_hold_repository_metadata(self) -> None:
        profile = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
        for program in profile["private_programs"]:
            self.assertEqual(set(program), {"display", "status"})
            self.assertEqual(program["display"], "PRIVATE / ACTIVE")

    def test_only_explicit_public_repositories_feed_activity(self) -> None:
        profile = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
        activity = json.loads((ROOT / "data" / "public_activity.json").read_text(encoding="utf-8"))
        allowed = {project["repo"] for project in profile["projects"]}
        self.assertTrue(set(activity.get("projects", {})).issubset(allowed))

    def test_readme_assets_and_links_exist(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for name in (
            "flight-recorder.svg",
            "flight-recorder-mobile.svg",
            "agentic-handshake.svg",
            "agentic-handshake-mobile.svg",
            "public-signal.svg",
            "public-signal-mobile.svg",
        ):
            self.assertIn(f"./assets/{name}", readme)
            self.assertTrue((ROOT / "assets" / name).exists())
        self.assertIn("https://github.com/Aakash-a18/mesherra", readme)
        self.assertNotIn("<table>", readme)


if __name__ == "__main__":
    unittest.main()
