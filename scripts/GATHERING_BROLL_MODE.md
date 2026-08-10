---
type: operating-note
status: active
created: 2026-08-09
updated: 2026-08-10
area: Games/WoW/04-Story-and-Capture
role: GATHERING_BROLL_UI_MODE
canon: Games/WoW
goal: MINIMAP_ONLY_HARVEST_BROLL
---

# Gathering B-Roll mode — **minimap-only harvest** (product goal)

**Canon surface:** `Games/WoW/` only.  
**Windows seat ticket (plain):** `wow-roster-tracker/scripts/MINIMAP_ONLY_GATHER_BROLL.md` (also deploys to `D:\WoW B-Roll Storage\_scripts\`).  
**Related:** [[CINEMATIC_ORBIT_UI_MODE]] · [[MACHINE_INTELLIGENCE_BROLL]] · Deck Layer C.

**Law:** no invent FOOTAGE · no auto-publish · Layer A bars-to-Deck stays P0 in parallel.  
**Alt+Z** = full cinematic hide (everything gone, including minimap). **This mode is different.**

---

## Product goal (Kyle 2026-08-10 — locked intent)

> A **harvester B-roll** setup: character **runs around gathering herbs/ore** while the screen shows **essentially only the minimap** (plus node tracking if needed to play). No chat, no quest tracker, no bags, no unit frames, no sticky bars. That is the **good B-roll**. We do **not** have this working yet. Figure it out (Edit Mode layout and/or **addon** — likely **Auto Hide UI**).

| | |
|--|--|
| **Done-when** | Named layout or one-key enter/exit; Kyle can herb/mine with **minimap-only** (nodes OK); record → harvest tags clean gather frames |
| **Not done-when** | Hover-hide bars alone (nice, but not enough) · Edit Mode partial hide with chat/tracker still on · full Alt+Z (too clean — loses minimap navigation) |

---

## On-screen contract (target)

| **ON (keep)** | **OFF (must hide)** |
|---------------|---------------------|
| **Minimap** | Chat |
| **Herb/mine node tracking** (if needed to gather) | Objective / quest **tracker** |
| World / character | Unit frames · bags · buffs chrome · extra panels |
| | Action bars (hover-hide is OK interim; ideal = fully hidden while gathering) |

**Interim live (2026-08-10):** bottom bars **hide until hover** — beneficial for play; **does not** close minimap-only.

**Known friction:** stock **Edit Mode** can kill a lot but **chat + objective tracker often stick**. Need addon rules and/or a dedicated saved layout — not more random toggles mid-session.

---

## How we expect to close it (Windows work)

| Approach | Notes |
|----------|--------|
| **A. Auto Hide UI v1.2.13** (authorized) | Install only when **WoW closed**. Configure: hide chat, tracker, bars, frames; **exclude minimap** (and node tracker if separate). |
| **B. Edit Mode layout** named e.g. `VibeCast Gather` | Save layout; document which HUD elements still refuse to hide → feed addon config. |
| **C. Deck Layer C** | `gather_ui_on` / `gather_ui_off` → `WOWCAP.GATHER_UI_ON/OFF` + marker (100 ms pad). |
| **D. Not ElvUI** as a dependency for this mode | No mass addon thrash. |

**If WoW is open:** stage notes only — do not force-install under live client.

---

## Vault-Tec / Deck (when wiring)

| Action | Sequence |
|--------|----------|
| **Enter gather B-roll** | toggle → **100 ms** → `WOWCAP.GATHER_UI_ON` |
| **Exit** | `WOWCAP.GATHER_UI_OFF` → **100 ms** → restore |

Prefer Vault-Tec capture page (Layer C). Optional marker: `Append-StreamDeckMarker.ps1` `layer_c.gather_ui_on|off`.

---

## Agent / harvest implications

| When mode is ON | Prefer |
|-----------------|--------|
| Chat gone | Chat blur often unnecessary |
| Minimap kept | Fly/gather establish OK for MI |
| Nodes visible | Tag `ui=gather_broll` |
| Mode OFF | Full combat UI — score as usual |

---

## One-liner

**Goal = minimap-only (nodes OK) while Kyle runs harvest routes for B-roll; not solved yet; Auto Hide + named layout + Deck ON/OFF; Alt+Z still full clean only.**
