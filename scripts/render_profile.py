#!/usr/bin/env python3
"""Render the public-safe GitHub profile graphics from local JSON data."""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
ACTIVITY_PATH = ROOT / "data" / "public_activity.json"
ASSET_DIR = ROOT / "assets"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_text(
    x: int | float,
    y: int | float,
    value: object,
    class_name: str,
    *,
    anchor: str | None = None,
) -> str:
    anchor_attr = f' text-anchor="{anchor}"' if anchor else ""
    return (
        f'<text x="{x}" y="{y}" class="{class_name}"{anchor_attr}>'
        f"{esc(value)}</text>"
    )


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def compact_date(value: str | None) -> str:
    timestamp = parse_time(value)
    return timestamp.strftime("%Y.%m.%d") if timestamp else "AWAITING SIGNAL"


def relative_age(value: str | None, reference: str | None) -> str:
    timestamp = parse_time(value)
    now = parse_time(reference) or datetime.now(timezone.utc)
    if not timestamp:
        return "AWAITING SIGNAL"
    delta = max(now - timestamp, now - now)
    seconds = int(delta.total_seconds())
    if seconds < 86_400:
        return "TODAY"
    days = seconds // 86_400
    if days < 30:
        return f"{days}D AGO"
    if days < 365:
        return f"{days // 30}MO AGO"
    return timestamp.strftime("%Y.%m.%d")


def shared_style() -> str:
    return """
      .display { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-weight: 800; letter-spacing: -0.7px; }
      .sans { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
      .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }
      .white { fill: #f5f5f2; }
      .muted { fill: #9aa6a2; }
      .ink { fill: #111514; }
      .paper-muted { fill: #5f625e; }
      .mint { fill: #5ef2b2; }
      .red { fill: #f0442e; }
      .amber { fill: #d8a633; }
      .eyebrow { font-size: 15px; font-weight: 700; letter-spacing: 2px; }
      .label { font-size: 15px; font-weight: 650; letter-spacing: 1.15px; }
      .micro { font-size: 13px; font-weight: 550; letter-spacing: .65px; }
      .body { font-size: 18px; }
      .signal { stroke-dasharray: 7 12; animation: signal-flow 12s linear infinite; }
      .pulse { transform-box: fill-box; transform-origin: center; animation: live-pulse 2.4s ease-in-out infinite; }
      @keyframes signal-flow { to { stroke-dashoffset: -190; } }
      @keyframes live-pulse { 0%, 100% { opacity: .55; transform: scale(.84); } 50% { opacity: 1; transform: scale(1.08); } }
      @media (prefers-reduced-motion: reduce) {
        .signal, .pulse { animation: none !important; }
      }
    """


def wrap_words(value: str, limit: int) -> list[str]:
    """Wrap short SVG labels without relying on foreignObject."""
    lines: list[str] = []
    current: list[str] = []
    for word in value.split():
        candidate = " ".join([*current, word])
        if current and len(candidate) > limit:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


def render_flight_recorder(profile: dict[str, Any], activity: dict[str, Any]) -> str:
    identity = profile["identity"]
    projects = profile["projects"]
    private_programs = profile["private_programs"]
    areas = profile["research_areas"]
    activity_projects = activity.get("projects", {})
    generated_at = activity.get("generated_at")

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620" viewBox="0 0 1200 620" role="img" aria-labelledby="flight-title flight-desc">',
        '<title id="flight-title">Aakash Agrawal — Flight Recorder</title>',
        '<desc id="flight-desc">A compact live research instrument showing four public systems, three deliberately unnamed private programs, and four research axes.</desc>',
        "<defs>",
        '<pattern id="dark-grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M 32 0 L 0 0 0 32" fill="none" stroke="#18201e" stroke-width="0.7"/></pattern>',
        '<pattern id="paper-grid" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="0.6" fill="#c8c4ba" opacity="0.7"/></pattern>',
        f"<style>{shared_style()}</style>",
        "</defs>",
        '<rect width="1200" height="420" fill="#060909"/>',
        '<rect width="1200" height="420" fill="url(#dark-grid)" opacity="0.5"/>',
        '<rect y="420" width="1200" height="200" fill="#f2f0e9"/>',
        '<rect x="950" y="440" width="220" height="150" fill="url(#paper-grid)" opacity="0.54"/>',
        '<line x1="28" y1="48" x2="1172" y2="48" stroke="#35403d"/>',
        svg_text(30, 32, f'{identity["eyebrow"]} / V2', "mono eyebrow white"),
        '<circle cx="1159" cy="27" r="6" fill="#5ef2b2" class="pulse"/>',
        svg_text(1142, 33, "LIVE", "mono eyebrow mint", anchor="end"),
        svg_text(30, 115, identity["name"].upper(), "display white").replace('class="display white"', 'class="display white" font-size="58"'),
    ]

    for index, line in enumerate(identity["headline"]):
        parts.append(svg_text(33, 153 + index * 27, line, "mono body white"))

    parts.extend(
        [
            svg_text(32, 270, "CURRENT THESIS", "mono label muted"),
            '<line x1="32" y1="284" x2="478" y2="284" stroke="#35403d"/>',
            svg_text(32, 319, "TRUST → DELEGATION → VERIFIABLE OUTCOMES", "mono label mint"),
            svg_text(32, 353, "Private by default. Public where proof helps.", "sans body white"),
            svg_text(650, 84, "LIVE SYSTEMS", "mono label muted"),
            '<line x1="625" y1="101" x2="625" y2="376" stroke="#5ef2b2" opacity="0.78"/>',
            '<line x1="625" y1="101" x2="625" y2="376" stroke="#5ef2b2" stroke-width="2" class="signal"/>',
            '<ellipse cx="892" cy="230" rx="238" ry="140" fill="none" stroke="#33403d"/>',
            '<ellipse cx="892" cy="230" rx="166" ry="96" fill="none" stroke="#25302e" stroke-dasharray="4 8"/>',
            '<circle cx="892" cy="230" r="8" fill="#060909" stroke="#7c8884"/>',
            '<circle cx="892" cy="230" r="2.5" fill="#f5f5f2"/>',
        ]
    )

    for index, project in enumerate(projects):
        row_y = 126 + index * 58
        record = activity_projects.get(project["repo"], {})
        age = relative_age(record.get("pushed_at"), generated_at)
        parts.extend(
            [
                f'<circle cx="625" cy="{row_y - 5}" r="5" fill="#5ef2b2"/>',
                f'<line x1="630" y1="{row_y - 5}" x2="662" y2="{row_y - 5}" stroke="#5ef2b2"/>',
                svg_text(680, row_y, project["name"], "sans body white"),
                svg_text(1166, row_y, age, "mono micro mint", anchor="end"),
                svg_text(680, row_y + 22, project["category"], "mono micro muted"),
                f'<line x1="680" y1="{row_y + 34}" x2="1168" y2="{row_y + 34}" stroke="#2b3532"/>',
            ]
        )

    sync_label = compact_date(generated_at)
    parts.extend(
        [
            '<circle cx="625" cy="359" r="5" fill="#f0442e"/>',
            '<line x1="630" y1="359" x2="662" y2="359" stroke="#f0442e" stroke-dasharray="3 5"/>',
            svg_text(680, 365, f"{len(private_programs):02d} PRIVATE PROGRAMS / ACTIVE", "mono label red"),
            svg_text(1166, 365, "WITHHELD BY DESIGN", "mono micro muted", anchor="end"),
            '<line x1="28" y1="396" x2="1172" y2="396" stroke="#35403d"/>',
            svg_text(30, 414, f'MODE  {profile["status"]["mode"]}', "mono micro muted"),
            svg_text(1170, 414, f"SYNC  {sync_label}", "mono micro mint", anchor="end"),
            svg_text(30, 454, "RESEARCH INDEX", "mono label paper-muted"),
            svg_text(1170, 454, profile["closing_line"], "mono micro ink", anchor="end"),
        ]
    )

    column_width = 292
    for index, area in enumerate(areas):
        x = 30 + index * column_width
        detail_lines = wrap_words(area["detail"], 34)[:2]
        if index:
            parts.append(f'<line x1="{x - 20}" y1="474" x2="{x - 20}" y2="590" stroke="#b0ada4"/>')
        parts.extend(
            [
                svg_text(x, 520, area["number"], "display ink").replace('class="display ink"', 'class="display ink" font-size="38"'),
                svg_text(x + 58, 516, area["name"], "sans label ink"),
            ]
        )
        for line_index, detail_line in enumerate(detail_lines):
            parts.append(svg_text(x + 58, 548 + line_index * 18, detail_line, "mono micro paper-muted"))
        parts.append(f'<line x1="{x}" y1="588" x2="{min(x + 260, 1170)}" y2="588" stroke="#a9a79f"/>')

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def render_handshake(profile: dict[str, Any]) -> str:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="390" viewBox="0 0 1200 390" role="img" aria-labelledby="handshake-title handshake-desc">',
        '<title id="handshake-title">The agentic frontier</title>',
        '<desc id="handshake-desc">Two humans delegate to agents that communicate through verified airlocks. Both sides retain matching signed residue.</desc>',
        "<defs>",
        '<pattern id="handshake-grid" width="34" height="34" patternUnits="userSpaceOnUse"><path d="M 34 0 L 0 0 0 34" fill="none" stroke="#141b1a" stroke-width="0.7"/></pattern>',
        '<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#5ef2b2"/></marker>',
        f"<style>{shared_style()}</style>",
        "</defs>",
        '<rect width="1200" height="390" fill="#060909"/>',
        '<rect width="1200" height="390" fill="url(#handshake-grid)" opacity="0.58"/>',
        svg_text(28, 36, "TRUST WIRE / PROOF 01", "mono eyebrow muted"),
        svg_text(28, 92, "DELEGATION NEEDS A VERIFIABLE BOUNDARY.", "display white").replace('class="display white"', 'class="display white" font-size="38"'),
        svg_text(30, 126, "Identity in. Scoped disclosure across. Matching provenance out.", "sans body muted"),
        '<line x1="72" y1="236" x2="1128" y2="236" stroke="#5ef2b2" stroke-width="2" stroke-dasharray="7 10" class="signal" marker-end="url(#arrow)"/>',
    ]

    nodes = [
        (72, "HUMAN", "circle"),
        (258, "AGENT", "circle"),
        (438, "AIRLOCK", "hex"),
        (762, "AIRLOCK", "hex"),
        (942, "AGENT", "circle"),
        (1128, "HUMAN", "circle"),
    ]
    for x, label, shape in nodes:
        if shape == "hex":
            points = f"{x},196 {x + 38},218 {x + 38},254 {x},276 {x - 38},254 {x - 38},218"
            parts.extend(
                [
                    f'<polygon points="{points}" fill="#081110" stroke="#5ef2b2" stroke-width="1.5"/>',
                    f'<line x1="{x}" y1="208" x2="{x}" y2="264" stroke="#5ef2b2" stroke-width="3"/>',
                ]
            )
        else:
            parts.extend(
                [
                    f'<circle cx="{x}" cy="236" r="40" fill="#060909" stroke="#d7ddda"/>',
                    f'<circle cx="{x}" cy="236" r="9" fill="none" stroke="#d7ddda"/>',
                ]
            )
        parts.append(svg_text(x, 302, label, "mono label white", anchor="middle"))

    parts.extend(
        [
            svg_text(600, 224, "A2A WIRE", "mono label mint", anchor="middle"),
            '<path d="M 438 282 L 438 320 Q 438 337 456 337 L 744 337 Q 762 337 762 320 L 762 282" fill="none" stroke="#d8a633" stroke-width="2" stroke-dasharray="4 5"/>',
            '<path d="M 600 319 l 14 8 v 16 q -14 15 -28 0 v -16 z" fill="#060909" stroke="#d8a633"/>',
            '<path d="M 594 334 l 5 5 9 -11" fill="none" stroke="#d8a633" stroke-width="2"/>',
            svg_text(600, 372, "SIGNED RESIDUE / MATCHING RECORDS", "mono label amber", anchor="middle"),
            '<line x1="28" y1="381" x2="1172" y2="381" stroke="#35403d"/>',
            "</svg>",
        ]
    )
    return "\n".join(parts) + "\n"


def render_public_signal(profile: dict[str, Any], activity: dict[str, Any]) -> str:
    records = activity.get("projects", {})
    generated_at = activity.get("generated_at")
    projects = profile["projects"]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="250" viewBox="0 0 1200 250" role="img" aria-labelledby="signal-title signal-desc">',
        '<title id="signal-title">Public signal</title>',
        '<desc id="signal-desc">Recent push dates and public repository counts for four selected projects.</desc>',
        f"<style>{shared_style()}</style>",
        '<rect width="1200" height="250" fill="#0a0d0d"/>',
        '<line x1="26" y1="48" x2="1174" y2="48" stroke="#35403d"/>',
        svg_text(28, 32, "PUBLIC SIGNAL / AUTO-REFRESHED", "mono eyebrow mint"),
        svg_text(1172, 32, f"SYNC {compact_date(generated_at)}", "mono micro muted", anchor="end"),
        '<line x1="600" y1="66" x2="600" y2="230" stroke="#26302e"/>',
        '<line x1="26" y1="149" x2="1174" y2="149" stroke="#26302e"/>',
    ]

    positions = [(28, 88), (626, 88), (28, 176), (626, 176)]
    for index, (project, (x, y)) in enumerate(zip(projects, positions)):
        record = records.get(project["repo"], {})
        parts.extend(
            [
                svg_text(x, y, f'{index + 1:02d} / {project["name"]}', "mono label white"),
                svg_text(x + 540, y, relative_age(record.get("pushed_at"), generated_at), "mono label mint", anchor="end"),
                svg_text(x, y + 30, f'STARS  {record.get("stars", "—")}   ·   LANGUAGE  {record.get("language") or "—"}   ·   LAST PUSH  {compact_date(record.get("pushed_at"))}', "mono micro muted"),
            ]
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def render_flight_recorder_mobile(profile: dict[str, Any], activity: dict[str, Any]) -> str:
    identity = profile["identity"]
    projects = profile["projects"]
    records = activity.get("projects", {})
    generated_at = activity.get("generated_at")
    areas = profile["research_areas"]
    private_count = len(profile["private_programs"])
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="760" viewBox="0 0 640 760" role="img" aria-labelledby="mobile-flight-title mobile-flight-desc">',
        '<title id="mobile-flight-title">Aakash Agrawal — Flight Recorder</title>',
        '<desc id="mobile-flight-desc">Compact mobile research instrument with four public systems, deliberately unnamed private programs, and four research axes.</desc>',
        "<defs>",
        '<pattern id="mobile-dark-grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M 28 0 L 0 0 0 28" fill="none" stroke="#18201e" stroke-width="0.7"/></pattern>',
        '<pattern id="mobile-paper-grid" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="0.6" fill="#c8c4ba" opacity="0.7"/></pattern>',
        f"<style>{shared_style()}</style>",
        "</defs>",
        '<style>.eyebrow{font-size:17px}.label{font-size:17px}.micro{font-size:15px}.body{font-size:19px}</style>',
        '<rect width="640" height="500" fill="#060909"/>',
        '<rect width="640" height="500" fill="url(#mobile-dark-grid)" opacity="0.54"/>',
        '<rect y="500" width="640" height="260" fill="#f2f0e9"/>',
        '<rect x="480" y="520" width="140" height="212" fill="url(#mobile-paper-grid)" opacity="0.48"/>',
        '<line x1="24" y1="48" x2="616" y2="48" stroke="#35403d"/>',
        svg_text(26, 32, f'{identity["eyebrow"]} / V2', "mono eyebrow white"),
        '<circle cx="608" cy="27" r="6" fill="#5ef2b2" class="pulse"/>',
        svg_text(26, 101, identity["name"].upper(), "display white").replace('class="display white"', 'class="display white" font-size="45"'),
    ]
    for index, line in enumerate(identity["headline"]):
        parts.append(svg_text(29, 139 + index * 27, line, "mono body white"))

    parts.extend(
        [
            svg_text(26, 235, "LIVE SYSTEMS", "mono label muted"),
            '<line x1="320" y1="248" x2="320" y2="462" stroke="#5ef2b2" opacity="0.78"/>',
            '<line x1="320" y1="248" x2="320" y2="462" stroke="#5ef2b2" stroke-width="2" class="signal"/>',
        ]
    )
    for index, project in enumerate(projects):
        y = 276 + index * 43
        age = relative_age(records.get(project["repo"], {}).get("pushed_at"), generated_at)
        parts.extend(
            [
                f'<circle cx="320" cy="{y - 5}" r="5" fill="#5ef2b2"/>',
                svg_text(28, y, f'{index + 1:02d} / {project["name"]}', "mono label white"),
                svg_text(612, y, age, "mono micro mint", anchor="end"),
                f'<line x1="336" y1="{y + 12}" x2="612" y2="{y + 12}" stroke="#28322f"/>',
            ]
        )
    parts.extend(
        [
            '<circle cx="320" cy="447" r="5" fill="#f0442e"/>',
            svg_text(28, 453, f"{private_count:02d} PRIVATE PROGRAMS", "mono label red"),
            svg_text(612, 453, "WITHHELD", "mono micro muted", anchor="end"),
            svg_text(26, 536, "RESEARCH INDEX", "mono label paper-muted"),
            svg_text(614, 536, f"SYNC {compact_date(generated_at)}", "mono micro paper-muted", anchor="end"),
            '<line x1="26" y1="550" x2="614" y2="550" stroke="#8b8b84"/>',
            '<line x1="320" y1="566" x2="320" y2="706" stroke="#b0ada4"/>',
            '<line x1="26" y1="636" x2="614" y2="636" stroke="#b0ada4"/>',
        ]
    )
    for index, area in enumerate(areas):
        column = index % 2
        row = index // 2
        x = 28 + column * 304
        y = 594 + row * 86
        parts.extend(
            [
                svg_text(x, y, area["number"], "display ink").replace('class="display ink"', 'class="display ink" font-size="34"'),
                svg_text(x + 54, y - 4, area["name"], "sans label ink"),
            ]
        )
    parts.extend(
        [
            '<line x1="26" y1="724" x2="614" y2="724" stroke="#111514"/>',
            svg_text(320, 746, profile["closing_line"], "mono micro ink", anchor="middle"),
            "</svg>",
        ]
    )
    return "\n".join(parts) + "\n"


def render_handshake_mobile() -> str:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="600" viewBox="0 0 640 600" role="img" aria-labelledby="mobile-handshake-title mobile-handshake-desc">',
        '<title id="mobile-handshake-title">The agentic frontier</title>',
        '<desc id="mobile-handshake-desc">Two people delegate to agents that meet through verified airlocks and retain matching signed records.</desc>',
        "<defs>",
        '<pattern id="mobile-handshake-grid" width="34" height="34" patternUnits="userSpaceOnUse"><path d="M 34 0 L 0 0 0 34" fill="none" stroke="#141b1a" stroke-width="0.7"/></pattern>',
        '<marker id="mobile-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#5ef2b2"/></marker>',
        f"<style>{shared_style()}</style>",
        "</defs>",
        '<style>.eyebrow{font-size:17px}.label{font-size:17px}.micro{font-size:15px}.body{font-size:18px}</style>',
        '<rect width="640" height="600" fill="#060909"/>',
        '<rect width="640" height="600" fill="url(#mobile-handshake-grid)" opacity="0.58"/>',
        svg_text(26, 34, "TRUST WIRE / PROOF 01", "mono eyebrow muted"),
        svg_text(26, 83, "DELEGATION NEEDS A", "display white").replace('class="display white"', 'class="display white" font-size="33"'),
        svg_text(26, 120, "VERIFIABLE BOUNDARY.", "display white").replace('class="display white"', 'class="display white" font-size="33"'),
        svg_text(28, 153, "Identity in. Scoped disclosure across.", "sans body muted"),
        svg_text(28, 178, "Matching provenance out.", "sans body muted"),
        '<line x1="170" y1="244" x2="170" y2="444" stroke="#5ef2b2" stroke-width="2" stroke-dasharray="7 10" class="signal" marker-end="url(#mobile-arrow)"/>',
        '<line x1="470" y1="244" x2="470" y2="444" stroke="#5ef2b2" stroke-width="2" stroke-dasharray="7 10" class="signal" marker-end="url(#mobile-arrow)"/>',
    ]
    for x, side in ((170, "A"), (470, "B")):
        for y, label in ((244, "HUMAN"), (338, "AGENT")):
            parts.extend(
                [
                    f'<circle cx="{x}" cy="{y}" r="35" fill="#060909" stroke="#d7ddda"/>',
                    f'<circle cx="{x}" cy="{y}" r="8" fill="none" stroke="#d7ddda"/>',
                    svg_text(x + (66 if side == "A" else -66), y + 5, label, "mono label white", anchor="middle"),
                ]
            )
        points = f"{x},405 {x + 37},427 {x + 37},463 {x},485 {x - 37},463 {x - 37},427"
        parts.extend(
            [
                f'<polygon points="{points}" fill="#081110" stroke="#5ef2b2" stroke-width="1.5"/>',
                f'<line x1="{x}" y1="417" x2="{x}" y2="473" stroke="#5ef2b2" stroke-width="3"/>',
                svg_text(x, 514, "AIRLOCK", "mono label white", anchor="middle"),
            ]
        )
    parts.extend(
        [
            '<line x1="208" y1="445" x2="432" y2="445" stroke="#5ef2b2" stroke-width="2" stroke-dasharray="7 10" class="signal" marker-end="url(#mobile-arrow)"/>',
            svg_text(320, 431, "A2A WIRE", "mono label mint", anchor="middle"),
            '<path d="M 170 490 L 170 538 Q 170 552 188 552 L 452 552 Q 470 552 470 538 L 470 490" fill="none" stroke="#d8a633" stroke-width="2" stroke-dasharray="4 5"/>',
            '<path d="M 320 534 l 14 8 v 16 q -14 15 -28 0 v -16 z" fill="#060909" stroke="#d8a633"/>',
            '<path d="M 314 549 l 5 5 9 -11" fill="none" stroke="#d8a633" stroke-width="2"/>',
            svg_text(320, 588, "SIGNED RESIDUE / MATCHING RECORDS", "mono micro amber", anchor="middle"),
            "</svg>",
        ]
    )
    return "\n".join(parts) + "\n"


def render_public_signal_mobile(profile: dict[str, Any], activity: dict[str, Any]) -> str:
    records = activity.get("projects", {})
    generated_at = activity.get("generated_at")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="430" viewBox="0 0 640 430" role="img" aria-labelledby="mobile-signal-title mobile-signal-desc">',
        '<title id="mobile-signal-title">Public signal</title>',
        '<desc id="mobile-signal-desc">Recent public activity for four selected repositories.</desc>',
        f"<style>{shared_style()}</style>",
        '<style>.eyebrow{font-size:17px}.label{font-size:17px}.micro{font-size:15px}.body{font-size:18px}</style>',
        '<rect width="640" height="430" fill="#0a0d0d"/>',
        svg_text(24, 31, "PUBLIC SIGNAL / AUTO-REFRESHED", "mono eyebrow mint"),
        svg_text(616, 31, compact_date(generated_at), "mono micro muted", anchor="end"),
        '<line x1="24" y1="48" x2="616" y2="48" stroke="#35403d"/>',
    ]
    positions = [(28, 91), (28, 179), (28, 267), (28, 355)]
    for index, (project, (x, y)) in enumerate(zip(profile["projects"], positions)):
        record = records.get(project["repo"], {})
        parts.extend(
            [
                svg_text(x, y, f'{index + 1:02d} / {project["name"]}', "mono label white"),
                svg_text(612, y, relative_age(record.get("pushed_at"), generated_at), "mono label mint", anchor="end"),
                svg_text(x, y + 30, f'STARS  {record.get("stars", "—")}   ·   LANGUAGE  {record.get("language") or "—"}   ·   PUSH  {compact_date(record.get("pushed_at"))}', "mono micro muted"),
                f'<line x1="28" y1="{y + 52}" x2="612" y2="{y + 52}" stroke="#26302e"/>',
            ]
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def render_all() -> None:
    profile = load_json(PROFILE_PATH)
    activity = load_json(ACTIVITY_PATH)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        "flight-recorder.svg": render_flight_recorder(profile, activity),
        "flight-recorder-mobile.svg": render_flight_recorder_mobile(profile, activity),
        "agentic-handshake.svg": render_handshake(profile),
        "agentic-handshake-mobile.svg": render_handshake_mobile(),
        "public-signal.svg": render_public_signal(profile, activity),
        "public-signal-mobile.svg": render_public_signal_mobile(profile, activity),
    }
    for filename, content in outputs.items():
        (ASSET_DIR / filename).write_text(content, encoding="utf-8")
        print(f"rendered assets/{filename}")


if __name__ == "__main__":
    render_all()
