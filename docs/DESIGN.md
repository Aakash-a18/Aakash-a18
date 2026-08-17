# Flight Recorder design lock

## Brief

Designing a GitHub profile README for technical peers, research collaborators, and
curious builders. The profile should make the current research frontier legible without
turning private work into accidental disclosure. It should feel like an independent lab
instrument: exact, active, and unusually personal.

## Reference lock

- **Primary direction:** Flight Recorder / Research Mission Control.
- **Preserve:** split dark-and-paper canvas, central signal spine, operational density,
  sharp geometry, monospaced labels, and an orbital map connecting public and private work.
- **Borrow only:** industrial catalogue numbering for the research ledger; the explicit
  human → agent → airlock → wire diagram for the Mesherra thesis.
- **Role rules:** mint means a live or verified path only; vermilion means active but
  withheld only; warm paper is the catalogue surface only; amber is reserved for signed
  residue in the handshake diagram.
- **Media strategy:** deterministic, code-native SVG. No generated bitmap ships in the
  profile and no external font or image dependency is required.
- **Reject:** badge walls, skill clouds, contribution-stat cards, decorative gradients,
  rounded card grids, fake metrics, private repository metadata, and generic AI imagery.

## Decision ledger

| Decision | Source | Role | Why |
|---|---|---|---|
| Dark operational upper field | Selected Flight Recorder mockup | Active work | Makes the profile feel like a system currently running |
| Paper ledger lower field | Index concept + industrial catalogue reference | Research taxonomy | Separates enduring questions from changing activity |
| Mint signal | Mission Control concept | Public/live/verified only | Gives activity one unambiguous visual meaning |
| Vermilion status | Index concept | Private active status only | Signals presence without revealing identity |
| Handshake diagram | Agentic Frontier concept + Mesherra architecture | Public proof | Explains the trust thesis instead of merely naming it |
| Native Markdown below SVG | GitHub constraint + accessibility | Semantic fallback | Keeps links, headings, and descriptions inspectable |

## Privacy boundary

`data/profile.json` may contain only intentionally public content. Private programs have
two allowed fields: a generic display label and a generic status. The updater queries
only repositories explicitly listed under `projects`; every listed repository must be
public.

## Motion

Only two continuous motions ship: the live-dot pulse and the signal-line dash. Both
reinforce system activity, and both are disabled by `prefers-reduced-motion`.

