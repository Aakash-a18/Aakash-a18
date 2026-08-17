# Flight Recorder v2 design lock

## Brief

Designing a GitHub profile README for technical peers, research collaborators, and
curious builders. The profile should make the current research frontier legible without
turning private work into accidental disclosure. It should feel like an independent lab
instrument: exact, active, and unusually personal.

## Audit findings

- At GitHub's real content widths, several 9–12 px SVG labels rendered at roughly 5–8 px.
- A private-program row collided with the desktop section divider.
- The mobile signal spine crossed the closing statement.
- The 900/1180 px hero canvases delayed the first inspectable project link.
- The handshake diagram introduced cyan even though mint already meant verified passage.
- The three-column native project table compressed descriptions and status labels on mobile.

## Reference lock

- **Primary direction:** Research Instrument v2 / compact mission control.
- **Preserve:** split dark-and-paper canvas, operational signal line, sharp geometry,
  monospaced metadata, and industrial catalogue numbering.
- **Borrow only:** large legible system labels from technical status boards; the explicit
  human → agent → airlock → wire diagram for the trust thesis.
- **Role rules:** mint means a live or verified path only; vermilion means active but
  withheld only; warm paper is the catalogue surface only; amber is reserved for signed
  residue in the handshake diagram.
- **Media strategy:** deterministic, code-native SVG. No generated bitmap ships in the
  profile and no external font or image dependency is required.
- **Reject:** microtype below a useful rendered size, badge walls, skill clouds,
  contribution-stat cards, decorative gradients, rounded card grids, fake metrics,
  private repository metadata, and generic AI imagery.

## Token commitments

- **Canvas:** `#060909` operational field; `#f2f0e9` catalogue field.
- **Primary text:** `#f5f5f2` on dark and `#111514` on paper.
- **Live / verified:** `#5ef2b2` only.
- **Withheld / active:** `#f0442e` only.
- **Signed residue:** `#d8a633` only.
- **Type:** system sans for display/body, system mono for metadata; no narrow-font dependency.
- **Minimum desktop source type:** 13 px metadata, designed for a 896 px GitHub content width.
- **Minimum mobile source type:** 15 px metadata on a 640 px source canvas.

## Decision ledger

| Decision | Source | Role | Why |
|---|---|---|---|
| Compact dark operational upper field | Existing Flight Recorder + audit | Active work | Keeps the first proof close to the first viewport |
| Paper ledger lower field | Index concept + industrial catalogue reference | Research taxonomy | Separates enduring questions from changing activity |
| Mint signal | Mission Control concept | Public/live/verified only | Gives activity one unambiguous visual meaning |
| Vermilion status | Index concept | Private active status only | Signals presence without revealing identity |
| Handshake diagram | Agentic Frontier concept + Mesherra architecture | Public proof | Explains the trust thesis instead of merely naming it |
| Native Markdown below SVG | GitHub constraint + accessibility | Semantic fallback | Keeps links, headings, and descriptions inspectable |
| Native stacked proof entries | Mobile audit + GitHub Markdown | Project navigation | Avoids table compression and horizontal overflow |
| 2×2 / stacked public signal | Typography craft reference | Activity telemetry | Preserves scannability at real rendered widths |

## Privacy boundary

`data/profile.json` may contain only intentionally public content. Private programs have
two allowed fields: a generic display label and a generic status. The updater queries
only repositories explicitly listed under `projects`; every listed repository must be
public.

## Motion

Only two continuous motions ship: the live-dot pulse and the signal-line dash. Both
reinforce system activity, and both are disabled by `prefers-reduced-motion`.
