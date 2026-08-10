---
type: product-shape
status: active
created: 2026-08-10
updated: 2026-08-10
brand: The WoW Explorer (TWE)
series: Explorers League · Field Notes
role: AUDIO_OR_VO_OVER_GATHER_BROLL
---

# Explorers League — **Field Notes**

**Yes — call it Field Notes.**  
Fits **Explorer’s League / The WoW Explorer** across gaming blogs: short, honest, first-person notes from the field — not a wiki essay, not a rage stream.

| Layer | Name |
|-------|------|
| Brand | **The WoW Explorer** |
| Community energy | **Explorer’s League** (never invent members) |
| This audio product | **Field Notes** (series title) |
| Optional subtitle | *Returner / new-again in Azeroth* |

**Pairs with:** gather / herb-mine B-roll (minimap-only goal) · muddy talk · Audacity VO bed  
**Laws:** no invent FOOTAGE · no silent publish · human KEEP · ARM deny  

**Windows plain script:** `wow-roster-tracker/scripts/FIELD_NOTES_SCRIPT_TODAY.md` → `D:\_scripts\`

---

## Product shapes (pick one per session)

| Shape | What you do | Agent later |
|-------|-------------|-------------|
| **A. Field Notes VO** | Audacity (or OBS mic) · 3–8 min · script below | Clean peaks · optional bed under B-roll |
| **B. Muddy gather** | Play + talk while herb/mine | Peaks from long take |
| **C. B-roll only** | Silent gather / zoom crop | Visual Moments only |

Do **not** stack A+C pressure the same night unless fun.

---

## Windows capture reminder (after any B-roll)

If masters are still on OBS path / not in day `candidates`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\WoW B-Roll Storage\_scripts\Session-End-Ship.ps1"
```

Soft-poll today stays `markers_only` until **candidates/*.mp4** exist. Zoom-in crop in OBS is fine — still need Session-End.

---

## Audacity on Windows (truth for agents)

| Claim | Reality |
|-------|---------|
| “Codex/Grok plugin drives Audacity” | **No first-class plugin.** Audacity is not a clean agent API. |
| What works | **You** record in Audacity (or OBS mic track). Save WAV/FLAC to a known folder. |
| Cleanup agents can do | **ffmpeg** noise/level/export on the **saved file** (Mac or Windows CLI) — not click-Audacity UI. |
| Optional Audacity | Built-in **Noise Reduction** · Normalize · Compressor — manual, 2 minutes. Macros exist but are fragile for remote agents. |
| Best handoff path | `D:\WoW B-Roll Storage\YYYY-MM-DD\audio\field-notes-*.wav` → Mac harvest / Moments later |

**Do not** wait for an “Audacity MCP” to ship Field Notes tonight. Record → save → optional light cleanup → done.

---

## Rest-of-plan (ordered)

1. **Session-End** today’s B-roll if not exported → Mac harvest/review  
2. **Field Notes** 3–6 min Audacity take (script in `_scripts\FIELD_NOTES_SCRIPT_TODAY.md`)  
3. **Minimap-only gather** — Windows ticket `MINIMAP_ONLY_GATHER_BROLL.md` (Auto Hide + layout)  
4. **Deck** multi-act + dual audio green when recording video  
5. KEEP → Moments → package (social still NOT_ARMED until go)

---

## Related

- [[YouTube/FLIGHTPATH_VO_TOPICS_EP01]] — longer flight essay  
- [[YouTube/STREAM_MUDDY_TALK_CARD]] — combat+chat energy  
- [[GATHERING_BROLL_MODE]] — minimap-only harvest B-roll  
- [[../00-Index/BRAND_TWE_EXPLORER]] — brand bible  
