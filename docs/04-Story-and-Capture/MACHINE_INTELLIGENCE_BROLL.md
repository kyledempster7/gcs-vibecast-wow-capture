# Machine intelligence — player b-roll (TWE / VibeCast)

**Status:** active doctrine · updated 2026-08-10  
**Law:** no invent FOOTAGE · no auto-publish · human KEEP wins

## Kyle product truth (2026-08-10 — absorb, don’t re-ask)

1. **Footage is getting cooler** — keep orbit / second-play harvest direction; human KEEP still wins.  
2. **TitanPanel location** when the bar is up is a real **machine-readable zone signal** (not required stack — optional when visible).  
3. **Cinematic / photo clean UI for camera orbits was NOT set up** last play — still OPEN → [[CINEMATIC_ORBIT_UI_MODE]].  
4. **Mic audio is present** in masters — treat primarily as **AI cue layer** (moments, talk_peak seeds, “something happened”), **not** as default publish VO. Much of the night is **background / B-roll bed**, not speech product.  
5. **Game/desktop dual-track** still OPEN if product wants in-world SFX ([[GAME_AUDIO_RESETUP]]).

## What Kyle wants the system to learn

| Signal | Why | Capture how |
|--------|-----|-------------|
| **Camera orbits** around toon | Stitchable beauty · “cool little orbit” | Tag moment `shot=orbit` · keep in Moments Library |
| **Fly / travel** (e.g. h1) | Zone establish · best with **minimal UI** | Prefer photo/cinematic hide UI; minimap OK — [[CINEMATIC_ORBIT_UI_MODE]] |
| **Zone name on frame** | Machine knows Howling Fjord vs Dragonblight | **TitanPanel location when up** + BR photo label → OCR probe |
| **Chat safety** | Mass production stays appropriate | Bottom-left blur **only if chat present** (detect or force) — never always-on |
| **Mic as AI cue** | Not studio VO by default | Flag `audio=mic_cue` · speech_peaks only if real words; else ambience+B-roll |
| **Stream Deck states** | Enter b-roll / rotate | JSONL markers (Windows contract) |

## Moments Library (on-disk file history)

```
~/Movies/WoW-Broll-Workflow/Moments-Library/
  YYYY-MM-DD-<zone>/
    clips/          # keeper mp4s
    stills/         # sampled frames
    prototypes/     # blur / grade experiments
    MOMENTS.json    # tags for agents
```

Not “everything forever” — **tagged keepers** only (orbits, fly, talk peaks).

## Audio truth (2026-08-09 → 2026-08-10)

- **Mic track:** present on recent candidates (aac stereo) — **AI cue first**, publish VO only on intentional talk nights.  
- **Game / desktop:** still treat as **not proven GREEN** until 10s dual-meter stamp ([[GAME_AUDIO_RESETUP]] · AUDIO_GREEN_STAMP).  
- House squeak / artifacts OK for **background B-roll energy**.  
- Product default for muddy play: **B-roll + stills + optional music bed**; mic peaks inform shortlist, do not force speech cuts on empty whispers.

## UI policy for pride exports

| Region | Default mass-product rule |
|--------|---------------------------|
| Bottom-left chat | **Detect then blur** — if `chat_present=false`, **leave alone** |
| Full HUD | Prefer **hide UI** for fly/orbit heroes |
| Minimap | Allowed if intentional |
| Bottom-right zone label | **Encourage** — photo mode BR |
| **TitanPanel top bar** | **Keep on for MI nights** when zone OCR wanted — not required for play |

### Cork law (2026-08-09 Kyle)

**Always-on region blur is not intelligence.**  
`orbit-chatblur-v0` = **FAILED_TREATMENT** (blurred empty ground on clean orbit).  
Pipeline: **SEE → DECIDE → ACT → PROVE**. Filters need a detection bit or `--force`.

Scripts: `detect_chat_presence.py` · `apply_chat_blur.py` (gated).  
Fixture: no-chat orbit must passthrough (sha match source).

## Agent scoring (next)

1. Detect orbit-ish motion (camera rotate around subject) → auto-tag.  
2. Detect high freeze + low bitrate → load screen reject (done partially).  
3. Zone OCR: TitanPanel strip (top) + optional BR label — `zone_label_probe.swift` / `zone_label_probe.py`.  
4. **Chat presence first** → blur only if true (or force).  
5. Stitch: ordered moments → HyperFrames / general-video montage (later).  
6. Classify night role: `broll_bed` vs `talk_product` from speech_peaks status + human.

## Kyle vs system

| Kyle | System |
|------|--------|
| Taste: “blur wrong / keep orbit / h1 needs less UI” | Detect, gate, archive, shortlist |
| Find zone-label hotkey once | Document + OCR later |
| **go** only when proud | Never unconditioned destructive filters |

## Related paths

- **Gathering B-Roll UI mode (canon):** `04-Story-and-Capture/GATHERING_BROLL_MODE.md` — minimap+nodes on; Vault-Tec `WOWCAP.GATHER_UI_ON/OFF`; Alt+Z unchanged  
- **Cinematic orbit UI (OPEN):** `CINEMATIC_ORBIT_UI_MODE.md`  
- **TitanPanel MI signal:** `00-Index/TITANPANEL_AND_ADDON_BRIDGE.md`  
- Marker sidecar: `capture-inbox/STREAM_DECK_MARKER_SIDECAR_CONTRACT.md`  
- Reject probe: `wow-roster-tracker/scripts/score_candidates.py`  
- Enhance: `enhance_returner_day.sh`  
- Mac harvest one-shot: `wow-roster-tracker/scripts/harvest_mac.sh`  
- Market gap map: `AUTOFARM_CONTENT_PRODUCT_GAPS.md`  
- Moments: `Movies/…/Moments-Library/2026-08-09-*/`  

