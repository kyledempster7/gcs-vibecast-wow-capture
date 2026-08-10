# Autofarm content from real gameplay — product gap map

**North star:** Best-in-class system that turns *actual play* into shippable multi-platform content with minimal Kyle thought — without inventing FOOTAGE or auto-publishing trash.

**Status:** doctrine + gap ledger (2026-08-09)  
**Brands:** TWE / VibeCast under GCS · fail-closed Armory  

---

## 1. What “best on the market” means here

Not “AI makes fake WoW clips.”  
**Real sessions → smart cut/tag/safety → human taste gate → multi-platform package.**

Competitors fail by: inventing footage, always-on dumb filters, no dual-machine truth, no play-state metadata, or full auto-post spam.

We win by: **proof on disk · human KEEP · conditional intelligence · orbit/fly/talk libraries.**

---

## 2. End-state loop (target)

```
PLAY (Windows)
  OBS clean path + dual audio + optional UI-hide scene
  Stream Deck stamps: broll_enter / rotate / talk_peak / skip
  Optional: zone label on frame (photo mode)
       ↓
HARVEST (Windows)
  masters → day root · candidates · MANIFEST · CareSix
  reject load/tiny/freeze early
       ↓
INGEST (Mac)
  Tailscale/Drive pull · score · pride cuts · Moments Library
  chat detect → blur only if present
  transcript if VO · motion tags (orbit/fly)
       ↓
REVIEW (Kyle)
  HTML board + 3 pride clips · plain English feedback
       ↓
PACKAGE (Mac, NOT_ARMED)
  Zernio-shaped dry-run · still + reel
       ↓
GO (Kyle only)
  arm / schedule — never silent publish
```

---

## 3. Gap matrix (fill these to lead the market)

### A. Capture truth (Windows)

| Gap | Why it matters | Fix |
|-----|----------------|-----|
| A1 OBS wrong profile (Fable path) | Masters lost in wrong tree | Boot checklist + agent path scan both places |
| A2 Game audio missing | Mic-only soft VO; no diegetic bed | Dual track OBS; AUDIO_GREEN stamp |
| A3 No Deck markers in file time | Dumb t=0 slices → load screens | SESSION.jsonl + join to media |
| A4 UI always on for fly/orbit/gather | Ugly / less reusable | Gathering B-Roll mode + Alt+Z cinematic — `GATHERING_BROLL_MODE.md` |
| A5 No zone-on-frame | MI can’t name zone | Photo-mode BR label + OCR later |
| A6 No record-start UTC | Can’t map markers → seconds | Write record_start in markers/OBS log |

### B. Harvest / transfer

| Gap | Why | Fix |
|-----|-----|-----|
| B1 Multi‑GB via Drive | Slow thrash | Candidates only; LAN first |
| B2 No day folder contract | Agents thrash paths | `D:\…\<day>\{raw,candidates,markers}` |
| B3 SHA/MANIFEST incomplete | Mac can’t verify | Always sha256 + duration |
| B4 Windows offline | Mac idle | Queue + Drive fallback |

### C. Machine intelligence (Mac)

| Gap | Why | Fix |
|-----|-----|-----|
| C1 Always-on chat blur | Vandalizes clean KEEP | **Detect → act** (shipped v0) |
| C2 Load-screen false keep | Tiny/freeze partial | Stronger score + human cork |
| C3 Orbit/fly not auto-tagged | Manual discovery | Motion classifiers |
| C4 Transcript empty on ambience | VO cuts fail | Tag `audio=ambience` · don’t force speech cuts |
| C5 No stitch graph | Clips isolated | Moments Library + montage planner |
| C6 Zone OCR absent | No “Dragonblight” label | BR OCR when label present |
| C7 Detector false positives | h1 “chat” may be UI | Calibrate on fixtures · human override |

### D. Review / taste

| Gap | Why | Fix |
|-----|-----|-----|
| D1 Too many raw files | Kyle fatigue | Pride 15/20/30 + HTML board only |
| D2 Feedback not training data | Repeat mistakes | Live log + fixtures from rejects |
| D3 No “proud enough” score | Unclear ship bar | Optional scorecard: motion + clean UI + audio |

### E. Product / delivery

| Gap | Why | Fix |
|-----|-----|-----|
| E1 Still vs reel split | YT needs video | KEEP video → dry-run reel; still separate |
| E2 Caption invent risk | Brand damage | Templates + real night facts only |
| E3 Auto-publish temptation | Trust death | NOT_ARMED forever until go |
| E4 Factory vs player b-roll confusion | Meisio week ≠ duo night | Separate Moments vs Factory trees |

### F. Market differentiators (build toward)

1. **Play-state graph** — Deck + OBS scene + zone as first-class data  
2. **Conditional safety** — chat blur only when needed (lesson learned)  
3. **Moments Library** — lifelong stitch bank of *your* orbits/flies  
4. **Dual-machine honesty** — Mac `exists` vs Windows paths never lied about  
5. **Human-in-the-loop as product** — 30s review, not 3h timeline  
6. **Brand-safe by construction** — NO_GUESTS, no invent, TWE caption contract  
7. **Regression fixtures** — failed treatments never re-ship  

---

## 4. Priority road (after this harvest)

| P | Work | Owner | Status 2026-08-09 night |
|---|------|--------|-------------------------|
| P0 | Tonight harvest Windows → Mac pull → score/pride/review | both seats | **DONE** second-play 5 cand + 15 score + review-pack |
| P1 | Deck marker JSONL live on one multi-action | Windows | **script live** `Append-StreamDeckMarker.ps1` + prove line; Deck UI wire TBD |
| P2 | Orbit/fly auto-tag v0 | Mac | **shipped** `tag_motion_shot.py` → `MOTION_TAGS.json` |
| P3 | Clean OBS scene + dual audio proof | Windows + Kyle 10s | OPEN |
| P1b | Join markers → cut windows | Mac | **shipped** `join_markers.py` (Deck + OBS chapter) |
| P0b | harvest_mac `$` bash-eats-PowerShell bug | Mac | **FIXED** via `Stage-ShipCandidates.ps1` |
| P4 | Montage from Moments (3 orbits + 1 fly) dry HyperFrames | Mac |
| P5 | Zone OCR when BR label visible | Mac |
| P6 | Unattended nightly: harvest if ONLINE else skip receipt | cron |
| **P0–P2 top 10** | Ranked market roadmap (Deck → audio → marker export → 9:16 → speech → …) | both | [[ROADMAP_P0_P2_TOP10]] |

---

## 5. Explicit non-goals

- Synthetic gameplay video as “real play”  
- Silent auto-post to Zernio  
- Replacing Kyle taste with LLM judgment on “is this cool” without his KEEP  

---

## 6. One-liner

**Best program = real play + capture stamps + detect-before-edit + Moments bank + 30-second human gate — not always-on filters and not invented footage.**
