---
type: product-doctrine
status: active
created: 2026-08-10
updated: 2026-08-10
product: VibeCast · Returner Daily
area: Games/WoW
role: FUNNY_MIC_CUE_CAPTURE
---

# Funny / mic-cue moments (herb rival class)

**Why:** Kyle’s best personality fuel is often a **quick laugh mid-play** — e.g. Alliance rival on the same herb node (“my herb forest”) — not a 12-minute EP.  
**Law:** no invent comedy · no invent rival identity · short clip beats full VOD  
**Related:** [[MACHINE_INTELLIGENCE_BROLL]] (mic as AI cue) · [[social/DAILY_PERSONALITY_PACKAGE]] · Deck map  

---

## Product shape

| Piece | Spec |
|-------|------|
| Length | **8–20s** preferred (pad ±3s around peak) |
| Audio | Mic energy optional in product; game audio when dual GREEN |
| Visual | Character + world; minimap-only gather OK |
| Caption | Community-playful · never cruel to the other player |
| Publish | NOT_ARMED until kyle_go |

---

## Capture paths (best → fallback)

| Rank | Path | Owner | Notes |
|------|------|-------|-------|
| **1 Best** | Deck `layer_c.funny_moment` within ~5–10s of the laugh | Windows | Marker window → export join |
| **2 Good** | Mic peak / laughter / real speech window on dual masters | Mac | speech_peaks · mic_cue; tag `peak=funny` |
| **3 Fallback** | Human KEEP on review shortlist of talk peaks | Kyle + Mac | Always valid |
| **Never** | Fabricate rival race/class, dialogue, or “funny” from silent ambience | — | Fail-closed |

Optional sibling markers already in map: `talk_peak` (personality line) · `broll_enter/exit` · `skip_zone`.

---

## Tags (Moments / MANIFEST notes)

| Tag | Use |
|-----|-----|
| `peak=funny` | Shortlist + package video slot |
| `story=rival_gather` | Shared-node / herb-forest energy when true |
| `audio=mic_cue` | Mic used as cue not studio VO |
| `for_future=true` | Archive for later montage |

---

## Windows residual (zero-thought)

1. Keep dual meters moving (Desktop + Mic) for 10s at record start.  
2. When something is funny: press **funny_moment** (once wired) or **talk_peak**.  
3. Session-End as usual — Mac harvests.  
4. Do not stop mid-session to rename files.

Packet: `wow-roster-tracker/scripts/WINDOWS_FUTURE_GOALS_PACKET.md`

---

## Mac residual

1. Prefer marker windows when `funny_moment` / `talk_peak` present.  
2. Else speech/mic peaks → shortlist section “funny / talk”.  
3. Never invent a rival story if only silent gather frames exist.  
4. Package: clip + caption seed under [[social/CONTENT_STYLE_COMMUNITY]].

---

## Example (template only — do not ship as fact)

> **If** dual audio + KEEP proves a shared-node laugh:  
> “Someone else wanted the same herb. Shared forest energy.”  
> **If** not on disk: skip the rival sentence entirely.

---

## Done-when (product)

- [ ] Deck id documented + optional human press path  
- [ ] Mac shortlist can surface funny/talk peaks without invent  
- [ ] At least one real KEEP night uses `peak=funny` or talk KEEP  
- [ ] Caption style never mocks the other player by name  
