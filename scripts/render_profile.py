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
      .display { font-family: "Arial Narrow", "Helvetica Neue", Arial, sans-serif; font-weight: 800; letter-spacing: 1px; }
      .sans { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
      .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }
      .white { fill: #f5f5f2; }
      .muted { fill: #8b9693; }
      .ink { fill: #111514; }
      .paper-muted { fill: #666965; }
      .mint { fill: #5ef2b2; }
      .red { fill: #f0442e; }
      .amber { fill: #d8a633; }
      .eyebrow { font-size: 13px; letter-spacing: 2.2px; }
      .label { font-size: 12px; letter-spacing: 1.4px; }
      .micro { font-size: 9px; letter-spacing: 1px; }
      .body { font-size: 14px; }
      .signal { stroke-dasharray: 7 12; animation: signal-flow 12s linear infinite; }
      .pulse { transform-box: fill-box; transform-origin: center; animation: live-pulse 2.4s ease-in-out infinite; }
      @keyframes signal-flow { to { stroke-dashoffset: -190; } }
      @keyframes live-pulse { 0%, 100% { opacity: .55; transform: scale(.84); } 50% { opacity: 1; transform: scale(1.08); } }
      @media (prefers-reduced-motion: reduce) {
        .signal, .pulse { animation: none !important; }
      }
    """


def render_flight_recorder(profile: dict[str, Any], activity: dict[str, Any]) -> str:
    identity = profile["identity"]
    projects = profile["projects"]
    private_programs = profile["private_programs"]
    areas = profile["research_areas"]
    activity_projects = activity.get("projects", {})
    generated_at = activity.get("generated_at")

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900" role="img" aria-labelledby="flight-title flight-desc">',
        '<title id="flight-title">Aakash Agrawal — Flight Recorder</title>',
        '<desc id="flight-desc">A live research map connecting four public projects to three deliberately unnamed private programs, followed by an indexed research ledger.</desc>',
        "<defs>",
        '<pattern id="dark-grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M 28 0 L 0 0 0 28" fill="none" stroke="#18201e" stroke-width="0.7"/></pattern>',
        '<pattern id="paper-grid" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="0.6" fill="#c8c4ba" opacity="0.7"/></pattern>',
        f"<style>{shared_style()}</style>",
        "</defs>",
        '<rect width="1200" height="560" fill="#060909"/>',
        '<rect width="1200" height="560" fill="url(#dark-grid)" opacity="0.54"/>',
        '<rect y="560" width="1200" height="340" fill="#f2f0e9"/>',
        '<rect x="980" y="585" width="185" height="260" fill="url(#paper-grid)" opacity="0.56"/>',
        '<line x1="24" y1="46" x2="1176" y2="46" stroke="#35403d" stroke-width="1"/>',
        svg_text(28, 31, f'{identity["eyebrow"]} / LIVE', "mono eyebrow white"),
        '<circle cx="1160" cy="26" r="5" fill="#5ef2b2" class="pulse"/>',
        svg_text(1147, 31, "LIVE", "mono eyebrow mint", anchor="end"),
        svg_text(28, 118, identity["name"].upper(), "display white", anchor=None).replace('class="display white"', 'class="display white" font-size="58"'),
    ]

    for index, line in enumerate(identity["headline"]):
        parts.append(svg_text(31, 158 + index * 25, line, "mono body white"))

    # Handshake trace: real conceptual steps, no synthetic metrics.
    parts.extend(
        [
            '<rect x="28" y="248" width="345" height="198" fill="#080d0c" stroke="#55615e"/>',
            svg_text(44, 273, "HANDSHAKE TRACE", "mono label muted"),
            '<line x1="44" y1="283" x2="357" y2="283" stroke="#26302e"/>',
        ]
    )
    trace = [
        ("00:00.000", "INIT", "HELLO"),
        ("00:00.153", "HELLO", "CAPABILITIES"),
        ("00:00.287", "CAPABILITIES", "CHALLENGE"),
        ("00:00.421", "CHALLENGE", "PROOF"),
        ("00:00.587", "PROOF", "VERIFY"),
        ("00:00.708", "VERIFY", "ACK"),
    ]
    for row, (stamp, source, target) in enumerate(trace):
        y = 306 + row * 21
        parts.extend(
            [
                svg_text(44, y, stamp, "mono micro muted"),
                svg_text(126, y, source, "mono micro white"),
                svg_text(216, y, "→", "mono micro mint"),
                svg_text(246, y, target, "mono micro white"),
            ]
        )
    parts.extend(
        [
            svg_text(44, 432, "STATUS: TRUST ESTABLISHED", "mono micro mint"),
            '<line x1="802" y1="70" x2="802" y2="858" stroke="#5ef2b2" stroke-width="1" opacity="0.75"/>',
            '<line x1="802" y1="70" x2="802" y2="858" stroke="#5ef2b2" stroke-width="2" class="signal"/>',
            '<circle cx="802" cy="84" r="5" fill="#5ef2b2" class="pulse"/>',
            '<circle cx="802" cy="309" r="6" fill="#5ef2b2"/>',
            '<circle cx="802" cy="560" r="5" fill="#f2f0e9" stroke="#111514"/>',
            # Orbit instrument.
            '<ellipse cx="650" cy="318" rx="272" ry="160" fill="none" stroke="#52605d"/>',
            '<ellipse cx="650" cy="318" rx="205" ry="118" fill="none" stroke="#34403d"/>',
            '<ellipse cx="650" cy="318" rx="128" ry="76" fill="none" stroke="#34403d" stroke-dasharray="3 7"/>',
            '<circle cx="650" cy="318" r="11" fill="#060909" stroke="#f5f5f2"/>',
            '<circle cx="650" cy="318" r="3" fill="#f5f5f2"/>',
            '<line x1="630" y1="318" x2="670" y2="318" stroke="#596360"/>',
            '<line x1="650" y1="298" x2="650" y2="338" stroke="#596360"/>',
        ]
    )

    node_positions = [(529, 202), (771, 217), (485, 382), (744, 427)]
    label_y = [142, 206, 270, 334]
    for project, (node_x, node_y), row_y in zip(projects, node_positions, label_y):
        record = activity_projects.get(project["repo"], {})
        age = relative_age(record.get("pushed_at"), generated_at)
        parts.extend(
            [
                f'<path d="M {node_x} {node_y} Q 735 {node_y - 18} 802 {row_y - 4}" fill="none" stroke="#76817e"/>',
                f'<circle cx="{node_x}" cy="{node_y}" r="6" fill="#5ef2b2" stroke="#060909" stroke-width="2"/>',
                f'<circle cx="802" cy="{row_y - 4}" r="4" fill="#5ef2b2"/>',
                f'<line x1="806" y1="{row_y - 4}" x2="914" y2="{row_y - 4}" stroke="#65716e"/>',
                f'<circle cx="924" cy="{row_y - 4}" r="9" fill="#060909" stroke="#5ef2b2"/>',
                f'<circle cx="924" cy="{row_y - 4}" r="3" fill="#5ef2b2"/>',
                svg_text(946, row_y, project["name"], "mono body white"),
                svg_text(1168, row_y, age, "mono micro mint", anchor="end"),
                f'<line x1="946" y1="{row_y + 10}" x2="1168" y2="{row_y + 10}" stroke="#303b38"/>',
            ]
        )

    for index, private_program in enumerate(private_programs):
        row_y = 402 + index * 52
        parts.extend(
            [
                f'<circle cx="802" cy="{row_y - 4}" r="4" fill="#f0442e"/>',
                f'<line x1="806" y1="{row_y - 4}" x2="914" y2="{row_y - 4}" stroke="#5a3a33" stroke-dasharray="3 6"/>',
                f'<circle cx="924" cy="{row_y - 4}" r="9" fill="#060909" stroke="#f0442e"/>',
                f'<rect x="920" y="{row_y - 8}" width="8" height="7" fill="none" stroke="#f0442e"/>',
                svg_text(946, row_y, private_program["display"], "mono body red"),
                svg_text(1168, row_y, "WITHHELD", "mono micro muted", anchor="end"),
            ]
        )

    sync_label = compact_date(generated_at)
    parts.extend(
        [
            '<line x1="28" y1="502" x2="1172" y2="502" stroke="#35403d"/>',
            svg_text(30, 526, "MODE", "mono micro muted"),
            svg_text(83, 526, profile["status"]["mode"], "mono micro white"),
            svg_text(292, 526, "DISCLOSURE", "mono micro muted"),
            svg_text(382, 526, profile["status"]["disclosure"], "mono micro mint"),
            svg_text(697, 526, "PUBLIC SIGNAL", "mono micro muted"),
            svg_text(792, 526, sync_label, "mono micro white"),
            svg_text(1168, 526, "TELEMETRY / NOMINAL", "mono micro mint", anchor="end"),
            # Paper ledger.
            svg_text(30, 595, "CATALOGUE", "mono label paper-muted"),
            '<line x1="30" y1="607" x2="194" y2="607" stroke="#878982"/>',
            svg_text(30, 632, "ARCHIVE", "mono micro paper-muted"),
            svg_text(105, 632, "AA / FR", "mono micro ink"),
            svg_text(30, 651, "EDITION", "mono micro paper-muted"),
            svg_text(105, 651, "01", "mono micro ink"),
            svg_text(30, 670, "UPDATED", "mono micro paper-muted"),
            svg_text(105, 670, sync_label, "mono micro ink"),
            svg_text(30, 689, "MODE", "mono micro paper-muted"),
            svg_text(105, 689, "OPERATIONAL", "mono micro ink"),
            '<line x1="220" y1="585" x2="220" y2="862" stroke="#767a74"/>',
        ]
    )

    for index, area in enumerate(areas):
        y = 624 + index * 64
        parts.extend(
            [
                svg_text(266, y, area["number"], "display ink").replace('class="display ink"', 'class="display ink" font-size="39"'),
                svg_text(355, y - 2, area["name"], "mono body ink"),
                svg_text(355, y + 20, area["detail"], "mono micro paper-muted"),
                f'<line x1="252" y1="{y + 31}" x2="1150" y2="{y + 31}" stroke="#a9a79f"/>',
                f'<circle cx="802" cy="{y + 31}" r="6" fill="#f2f0e9" stroke="#111514"/>',
                f'<circle cx="802" cy="{y + 31}" r="2" fill="#111514"/>',
            ]
        )

    parts.extend(
        [
            '<rect x="340" y="846" width="590" height="37" fill="none" stroke="#111514" stroke-width="2"/>',
            svg_text(635, 871, profile["closing_line"], "mono body ink", anchor="middle"),
            "</svg>",
        ]
    )
    return "\n".join(parts) + "\n"


def render_handshake(profile: dict[str, Any]) -> str:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="430" viewBox="0 0 1200 430" role="img" aria-labelledby="handshake-title handshake-desc">',
        '<title id="handshake-title">The agentic frontier</title>',
        '<desc id="handshake-desc">Two humans delegate to agents that communicate through verified airlocks. Both sides retain matching signed residue.</desc>',
        "<defs>",
        '<pattern id="handshake-grid" width="34" height="34" patternUnits="userSpaceOnUse"><path d="M 34 0 L 0 0 0 34" fill="none" stroke="#141b1a" stroke-width="0.7"/></pattern>',
        '<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#24d7e8"/></marker>',
        f"<style>{shared_style()}</style>",
        "</defs>",
        '<rect width="1200" height="430" fill="#060909"/>',
        '<rect width="1200" height="430" fill="url(#handshake-grid)" opacity="0.58"/>',
        svg_text(28, 38, "THE AGENTIC FRONTIER / PROOF 01", "mono eyebrow muted"),
        svg_text(28, 91, "THE NEXT SOFTWARE DOES NOT WAIT TO BE OPENED.", "display white").replace('class="display white"', 'class="display white" font-size="36"'),
        svg_text(30, 121, "Delegated authority makes identity, disclosure, and provenance product primitives.", "mono body muted"),
        '<line x1="78" y1="250" x2="1120" y2="250" stroke="#24d7e8" stroke-width="2" stroke-dasharray="6 8" class="signal" marker-end="url(#arrow)"/>',
    ]

    nodes = [
        (78, "HUMAN", "circle"),
        (260, "AGENT", "circle"),
        (430, "AIRLOCK", "hex"),
        (770, "AIRLOCK", "hex"),
        (940, "AGENT", "circle"),
        (1120, "HUMAN", "circle"),
    ]
    for x, label, shape in nodes:
        if shape == "hex":
            points = f"{x},210 {x + 35},230 {x + 35},270 {x},290 {x - 35},270 {x - 35},230"
            parts.extend(
                [
                    f'<polygon points="{points}" fill="#081110" stroke="#24d7e8" stroke-width="1.5"/>',
                    f'<line x1="{x}" y1="222" x2="{x}" y2="278" stroke="#24d7e8" stroke-width="3"/>',
                ]
            )
        else:
            parts.extend(
                [
                    f'<circle cx="{x}" cy="250" r="39" fill="#060909" stroke="#d7ddda"/>',
                    f'<circle cx="{x}" cy="250" r="9" fill="none" stroke="#d7ddda"/>',
                ]
            )
        parts.append(svg_text(x, 317, label, "mono label white", anchor="middle"))

    parts.extend(
        [
            svg_text(600, 238, "A2A WIRE", "mono label mint", anchor="middle"),
            '<path d="M 430 294 L 430 344 Q 430 360 448 360 L 752 360 Q 770 360 770 344 L 770 294" fill="none" stroke="#d8a633" stroke-width="2" stroke-dasharray="4 5"/>',
            '<path d="M 600 344 l 14 8 v 16 q -14 15 -28 0 v -16 z" fill="#060909" stroke="#d8a633"/>',
            '<path d="M 594 359 l 5 5 9 -11" fill="none" stroke="#d8a633" stroke-width="2"/>',
            svg_text(600, 397, "SIGNED RESIDUE / MATCHING RECORDS ON BOTH SIDES", "mono label amber", anchor="middle"),
            '<line x1="28" y1="414" x2="1172" y2="414" stroke="#35403d"/>',
            "</svg>",
        ]
    )
    return "\n".join(parts) + "\n"


def render_public_signal(profile: dict[str, Any], activity: dict[str, Any]) -> str:
    records = activity.get("projects", {})
    generated_at = activity.get("generated_at")
    projects = profile["projects"]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="188" viewBox="0 0 1200 188" role="img" aria-labelledby="signal-title signal-desc">',
        '<title id="signal-title">Public signal</title>',
        '<desc id="signal-desc">Recent push dates and public repository counts for four selected projects.</desc>',
        f"<style>{shared_style()}</style>",
        '<rect width="1200" height="188" fill="#0a0d0d"/>',
        '<line x1="24" y1="44" x2="1176" y2="44" stroke="#35403d"/>',
        svg_text(26, 29, "PUBLIC SIGNAL / AUTO-REFRESHED", "mono eyebrow mint"),
        svg_text(1174, 29, f"SYNC {compact_date(generated_at)}", "mono micro muted", anchor="end"),
    ]

    column_width = 288
    for index, project in enumerate(projects):
        x = 26 + index * column_width
        record = records.get(project["repo"], {})
        if index:
            parts.append(f'<line x1="{x - 14}" y1="62" x2="{x - 14}" y2="165" stroke="#26302e"/>')
        parts.extend(
            [
                svg_text(x, 83, f'{index + 1:02d} / {project["name"]}', "mono label white"),
                svg_text(x, 111, "LAST PUSH", "mono micro muted"),
                svg_text(x + 78, 111, relative_age(record.get("pushed_at"), generated_at), "mono micro mint"),
                svg_text(x, 134, "STARS", "mono micro muted"),
                svg_text(x + 78, 134, record.get("stars", "—"), "mono micro white"),
                svg_text(x, 157, "LANGUAGE", "mono micro muted"),
                svg_text(x + 78, 157, record.get("language") or "—", "mono micro white"),
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
        '<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1180" viewBox="0 0 720 1180" role="img" aria-labelledby="mobile-flight-title mobile-flight-desc">',
        '<title id="mobile-flight-title">Aakash Agrawal — Flight Recorder</title>',
        '<desc id="mobile-flight-desc">Mobile research map with four public projects, private active programs, and four indexed research areas.</desc>',
        "<defs>",
        '<pattern id="mobile-dark-grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M 28 0 L 0 0 0 28" fill="none" stroke="#18201e" stroke-width="0.7"/></pattern>',
        '<pattern id="mobile-paper-grid" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="0.6" fill="#c8c4ba" opacity="0.7"/></pattern>',
        f"<style>{shared_style()}</style>",
        "</defs>",
        '<rect width="720" height="710" fill="#060909"/>',
        '<rect width="720" height="710" fill="url(#mobile-dark-grid)" opacity="0.54"/>',
        '<rect y="710" width="720" height="470" fill="#f2f0e9"/>',
        '<rect x="560" y="730" width="140" height="410" fill="url(#mobile-paper-grid)" opacity="0.5"/>',
        '<line x1="24" y1="48" x2="696" y2="48" stroke="#35403d"/>',
        svg_text(26, 31, f'{identity["eyebrow"]} / LIVE', "mono eyebrow white"),
        '<circle cx="684" cy="26" r="5" fill="#5ef2b2" class="pulse"/>',
        svg_text(26, 108, identity["name"].upper(), "display white").replace('class="display white"', 'class="display white" font-size="49"'),
    ]
    for index, line in enumerate(identity["headline"]):
        parts.append(svg_text(29, 147 + index * 24, line, "mono body white"))

    parts.extend(
        [
            '<line x1="360" y1="230" x2="360" y2="1148" stroke="#5ef2b2" stroke-width="1"/>',
            '<line x1="360" y1="230" x2="360" y2="1148" stroke="#5ef2b2" stroke-width="2" class="signal"/>',
            '<ellipse cx="360" cy="360" rx="242" ry="120" fill="none" stroke="#52605d"/>',
            '<ellipse cx="360" cy="360" rx="174" ry="82" fill="none" stroke="#34403d"/>',
            '<ellipse cx="360" cy="360" rx="94" ry="46" fill="none" stroke="#34403d" stroke-dasharray="3 7"/>',
            '<circle cx="360" cy="360" r="10" fill="#060909" stroke="#f5f5f2"/>',
            '<circle cx="360" cy="360" r="3" fill="#f5f5f2"/>',
            '<circle cx="186" cy="302" r="6" fill="#5ef2b2"/>',
            '<circle cx="502" cy="300" r="6" fill="#5ef2b2"/>',
            '<circle cx="156" cy="407" r="6" fill="#5ef2b2"/>',
            '<circle cx="548" cy="418" r="6" fill="#5ef2b2"/>',
            svg_text(26, 508, "PUBLIC ORBIT", "mono label muted"),
            '<line x1="26" y1="522" x2="694" y2="522" stroke="#35403d"/>',
        ]
    )
    for index, project in enumerate(projects):
        y = 552 + index * 35
        age = relative_age(records.get(project["repo"], {}).get("pushed_at"), generated_at)
        parts.extend(
            [
                svg_text(28, y, f'{index + 1:02d} / {project["name"]}', "mono label white"),
                svg_text(692, y, age, "mono micro mint", anchor="end"),
            ]
        )
    parts.extend(
        [
            svg_text(28, 694, f"{private_count:02d} PRIVATE PROGRAMS / ACTIVE", "mono label red"),
            svg_text(692, 694, "WITHHELD BY DESIGN", "mono micro muted", anchor="end"),
            svg_text(26, 748, "RESEARCH INDEX", "mono label paper-muted"),
            svg_text(694, 748, f"UPDATED {compact_date(generated_at)}", "mono micro paper-muted", anchor="end"),
            '<line x1="26" y1="762" x2="694" y2="762" stroke="#8b8b84"/>',
        ]
    )
    for index, area in enumerate(areas):
        y = 818 + index * 76
        parts.extend(
            [
                svg_text(28, y, area["number"], "display ink").replace('class="display ink"', 'class="display ink" font-size="38"'),
                svg_text(112, y - 5, area["name"], "mono body ink"),
                svg_text(112, y + 20, area["detail"], "mono micro paper-muted"),
                f'<line x1="28" y1="{y + 35}" x2="694" y2="{y + 35}" stroke="#aaa79f"/>',
                f'<circle cx="360" cy="{y + 35}" r="6" fill="#f2f0e9" stroke="#111514"/>',
                f'<circle cx="360" cy="{y + 35}" r="2" fill="#111514"/>',
            ]
        )
    parts.extend(
        [
            '<rect x="78" y="1116" width="564" height="38" fill="none" stroke="#111514" stroke-width="2"/>',
            svg_text(360, 1142, profile["closing_line"], "mono label ink", anchor="middle"),
            "</svg>",
        ]
    )
    return "\n".join(parts) + "\n"


def render_handshake_mobile() -> str:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="720" height="820" viewBox="0 0 720 820" role="img" aria-labelledby="mobile-handshake-title mobile-handshake-desc">',
        '<title id="mobile-handshake-title">The agentic frontier</title>',
        '<desc id="mobile-handshake-desc">Two people delegate to agents that meet through verified airlocks and retain matching signed records.</desc>',
        "<defs>",
        '<pattern id="mobile-handshake-grid" width="34" height="34" patternUnits="userSpaceOnUse"><path d="M 34 0 L 0 0 0 34" fill="none" stroke="#141b1a" stroke-width="0.7"/></pattern>',
        '<marker id="mobile-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#24d7e8"/></marker>',
        f"<style>{shared_style()}</style>",
        "</defs>",
        '<rect width="720" height="820" fill="#060909"/>',
        '<rect width="720" height="820" fill="url(#mobile-handshake-grid)" opacity="0.58"/>',
        svg_text(26, 35, "THE AGENTIC FRONTIER / PROOF 01", "mono eyebrow muted"),
        svg_text(26, 88, "THE NEXT SOFTWARE", "display white").replace('class="display white"', 'class="display white" font-size="37"'),
        svg_text(26, 129, "DOES NOT WAIT TO BE OPENED.", "display white").replace('class="display white"', 'class="display white" font-size="37"'),
        svg_text(28, 164, "Delegated authority requires verifiable boundaries.", "mono body muted"),
        '<line x1="196" y1="246" x2="196" y2="518" stroke="#24d7e8" stroke-width="2" stroke-dasharray="6 8" class="signal" marker-end="url(#mobile-arrow)"/>',
        '<line x1="524" y1="246" x2="524" y2="518" stroke="#24d7e8" stroke-width="2" stroke-dasharray="6 8" class="signal" marker-end="url(#mobile-arrow)"/>',
    ]
    for x, side in ((196, "A"), (524, "B")):
        for y, label in ((246, "HUMAN"), (365, "AGENT")):
            parts.extend(
                [
                    f'<circle cx="{x}" cy="{y}" r="34" fill="#060909" stroke="#d7ddda"/>',
                    f'<circle cx="{x}" cy="{y}" r="8" fill="none" stroke="#d7ddda"/>',
                    svg_text(x + (50 if side == "A" else -50), y + 4, label, "mono label white", anchor="middle"),
                ]
            )
        points = f"{x},470 {x + 34},490 {x + 34},530 {x},550 {x - 34},530 {x - 34},490"
        parts.extend(
            [
                f'<polygon points="{points}" fill="#081110" stroke="#24d7e8" stroke-width="1.5"/>',
                f'<line x1="{x}" y1="482" x2="{x}" y2="538" stroke="#24d7e8" stroke-width="3"/>',
                svg_text(x, 582, "AIRLOCK", "mono label white", anchor="middle"),
            ]
        )
    parts.extend(
        [
            '<line x1="232" y1="510" x2="488" y2="510" stroke="#24d7e8" stroke-width="2" stroke-dasharray="6 8" class="signal" marker-end="url(#mobile-arrow)"/>',
            svg_text(360, 495, "A2A WIRE", "mono label mint", anchor="middle"),
            '<path d="M 196 552 L 196 650 Q 196 668 214 668 L 506 668 Q 524 668 524 650 L 524 552" fill="none" stroke="#d8a633" stroke-width="2" stroke-dasharray="4 5"/>',
            '<path d="M 360 650 l 14 8 v 16 q -14 15 -28 0 v -16 z" fill="#060909" stroke="#d8a633"/>',
            '<path d="M 354 665 l 5 5 9 -11" fill="none" stroke="#d8a633" stroke-width="2"/>',
            svg_text(360, 725, "SIGNED RESIDUE", "mono label amber", anchor="middle"),
            svg_text(360, 753, "MATCHING RECORDS ON BOTH SIDES", "mono micro amber", anchor="middle"),
            '<line x1="26" y1="790" x2="694" y2="790" stroke="#35403d"/>',
            "</svg>",
        ]
    )
    return "\n".join(parts) + "\n"


def render_public_signal_mobile(profile: dict[str, Any], activity: dict[str, Any]) -> str:
    records = activity.get("projects", {})
    generated_at = activity.get("generated_at")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="720" height="430" viewBox="0 0 720 430" role="img" aria-labelledby="mobile-signal-title mobile-signal-desc">',
        '<title id="mobile-signal-title">Public signal</title>',
        '<desc id="mobile-signal-desc">Recent public activity for four selected repositories.</desc>',
        f"<style>{shared_style()}</style>",
        '<rect width="720" height="430" fill="#0a0d0d"/>',
        svg_text(24, 31, "PUBLIC SIGNAL / AUTO-REFRESHED", "mono eyebrow mint"),
        svg_text(696, 31, compact_date(generated_at), "mono micro muted", anchor="end"),
        '<line x1="24" y1="47" x2="696" y2="47" stroke="#35403d"/>',
        '<line x1="360" y1="66" x2="360" y2="405" stroke="#26302e"/>',
        '<line x1="24" y1="230" x2="696" y2="230" stroke="#26302e"/>',
    ]
    positions = [(28, 94), (384, 94), (28, 258), (384, 258)]
    for index, (project, (x, y)) in enumerate(zip(profile["projects"], positions)):
        record = records.get(project["repo"], {})
        parts.extend(
            [
                svg_text(x, y, f'{index + 1:02d} / {project["name"]}', "mono label white"),
                svg_text(x, y + 38, "LAST PUSH", "mono micro muted"),
                svg_text(x + 92, y + 38, relative_age(record.get("pushed_at"), generated_at), "mono micro mint"),
                svg_text(x, y + 66, "STARS", "mono micro muted"),
                svg_text(x + 92, y + 66, record.get("stars", "—"), "mono micro white"),
                svg_text(x, y + 94, "LANGUAGE", "mono micro muted"),
                svg_text(x + 92, y + 94, record.get("language") or "—", "mono micro white"),
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
