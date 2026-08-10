---
type: operating-note
status: active
created: 2026-08-09
updated: 2026-08-09
area: Games/WoW/04-Story-and-Capture
role: GATHERING_BROLL_UI_MODE
canon: Games/WoW
---

# Gathering B-Roll mode (UI operating note)

**Canon surface:** `Games/WoW/` only.  
**Research support (not a second index):** [[Kyle's Notes/Research/World of Warcraft/WoW Stream Deck Uniform Keybinds|Stream Deck Uniform Keybinds]].  
**Umbrella:** [[../00-Index/WOW_CONTENT_UMBRELLA|WOW_CONTENT_UMBRELLA]].  
**TitanPanel:** optional research only — [[../00-Index/TITANPANEL_AND_ADDON_BRIDGE|TITANPANEL_AND_ADDON_BRIDGE]] (not the owner of this mode).

**Law:** no invent FOOTAGE · no auto-publish · Layer A two-deck action-bar work remains **P0 in parallel**.  
**Alt+Z** stays the full cinematic hide (unchanged). This mode is **not** Alt+Z.

---

## Intent

Herb/mining and outdoor travel B-roll that keeps **node tracking + minimap** while stripping combat/chat clutter — so machine harvest and Moments Library get clean-ish frames without losing gather UX.

---

## On-screen contract

| Keep fully visible | Hide or fade |
|--------------------|--------------|
| **Minimap** | Action bars |
| **Herb / mining node tracking** | Unit frames |
| (world + nodes) | Chat |
| | Objectives / quest tracker |
| | Bags / menus |
| | Buffs / debuffs chrome |
| | Other non-essential clutter |

**Recover** the full interface for combat and panels (exit mode).  
**Cinematic total clean** = still **Alt+Z** only — do not replace or rebind Alt+Z for this mode.

---

## Vault-Tec entry / exit (capture Layer C)

| Action | Sequence |
|--------|----------|
| **Enter Gathering B-Roll** | toggle mode → **100 ms** → `WOWCAP.GATHER_UI_ON` |
| **Exit Gathering B-Roll** | `WOWCAP.GATHER_UI_OFF` → **100 ms** → restore interface |

- `WOWCAP.GATHER_UI_ON` / `WOWCAP.GATHER_UI_OFF` are the machine event names for Stream Deck / binder hooks.  
- Prefer **Vault-Tec** capture page (Layer C) — never steal Layer A combat/utility keys.  
- Optional: also append marker via `D:\WoW B-Roll Storage\_scripts\Append-StreamDeckMarker.ps1` with `button_id` e.g. `layer_c.gather_ui_on` / `layer_c.gather_ui_off` when wiring multi-actions (see [[capture-inbox/DECK_BUTTON_MAP|DECK_BUTTON_MAP]] + contract).

---

## Addon: Auto Hide UI (authorized install)

| Rule | Detail |
|------|--------|
| **Product** | **Auto Hide UI v1.2.13 only** (no ElvUI/Titan as dependency for this mode) |
| **When install allowed** | WoW client **confirmed closed** |
| **If WoW running** | Remain **safely staged** — do not inject under a live client |
| **Who** | WoW manager / Windows seat with this note as authority |
| **Not** | Mass addon install · WTF thrash · Bartender overwrite |

Default **two-deck action-bar** (bars 3–4 → SD1/SD2) remains **P0 in parallel** — this mode does not deprioritize that.

---

## Agent / harvest implications

| When mode is ON | Prefer |
|-----------------|--------|
| Chat chrome gone | Chat blur often unnecessary (`chat_present=false`) |
| Minimap kept | OK for fly/gather establish (MI doctrine) |
| Nodes visible | Tag sessions `ui=gather_broll` when markers fire |
| Mode OFF / combat | Full UI — score/reject as usual |

Markers + MANIFEST may record `gather_ui=on|off` when Deck fires; Mac join tools treat them as press-evidence until human KEEP.

---

## Related (single farm — no competing index)

| Need | Path |
|------|------|
| Content umbrella | [[../00-Index/WOW_CONTENT_UMBRELLA]] |
| Front door | [[../00-Index/README]] |
| MI / detect→act | [[MACHINE_INTELLIGENCE_BROLL]] |
| Record night pin | [[../00-Index/RECORD_NIGHT_NOW]] |
| Deck marker sidecar | [[capture-inbox/STREAM_DECK_MARKER_SIDECAR_CONTRACT]] |
| Deck Layer C map | [[capture-inbox/DECK_BUTTON_MAP]] |
| Stream Deck doctrine (research) | [[Kyle's Notes/Research/World of Warcraft/WoW Stream Deck Uniform Keybinds]] |

---

## One-liner

**Gathering B-Roll = minimap + nodes on, clutter off; Vault-Tec ON/OFF with 100 ms pad; Alt+Z still full clean; Auto Hide UI v1.2.13 only when WoW closed; bars-to-Deck stays P0.**
