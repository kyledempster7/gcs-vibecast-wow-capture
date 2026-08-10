---
type: social-format
status: active
created: 2026-08-09
updated: 2026-08-09
format: F_ACHIEVEMENT_STILL
lane: wow-content-umbrella
---

# Custom achievement frames — social stills for real wins

**Primary daily social product is [[RETURNER_DAILY_SOCIAL|Returner Daily]]** (carousel · B-roll · personality + **Memento** stills).  
**This format** = custom toast art for ops wins, optional IG stills, and **later community / Discord / Explorer’s League** recognition — not a rip of Blizzard achievement UI as the daily engine.

**Idea:** toast-style images when something true moves — gear, level, systems, EP recorded, Layer A — plus future **guild/community** badges.

**Tone:** returner pride · positive friction · calm hype · **not** rage.  
**Publish:** human go only. **No auto-Zernio.**

**Future can-of-worms (noted, not building now):** high-quality character still with custom frame **under** the figure — Photomator / render pipeline later.

---

## Why this format

| Need | Fit |
|------|-----|
| Scorecard deltas exist but don’t feel shareable | Frame turns +9 ilvl into a toast people feel |
| EP01 flight-path VO nights | Still posts while audio cooks |
| IG already likes B-roll | Achievement stills = second surface (carousel slide / story) |
| Fail-closed honesty | Only fire when **source of truth** exists (scorecard · series tick · Layer A OK · capture path) |

---

## Frame family (scan list)

| Code | Title pattern (examples) | Source of truth | Status |
|------|--------------------------|-----------------|--------|
| **A1** | Points of… / Gear notch | Scorecard Δ ilvl | **Candidates live** (Pain +3, Rot +11, Agony +9 — 2026-08-09) |
| **A2** | Level band / ding | Scorecard Δ level | Wait for real ding |
| **A3** | Care six complete | Live API 6/6 | Systems pride (ops → optional soft post) |
| **A4** | First nights systems | EP04 night + optional FOOTAGE | After play |
| **A5** | Layer A proven | Stream Deck checklist Observed OK | After Path B |
| **A6** | EP in the can | Series board **Recorded** ☑ | After Path A audio |
| **A7** | Flight path chapter | Raw VO file path noted | Same night as mic |
| **A8** | Soft letter beat | Class-P draft approved | Later |
| **A9** | Duo silent win | Real duo session note | No guest claims |
| **A10** | Returner milestone | Human one-liner on scorecard | Kyle fills |

**Do not invent:** achievements for media that isn’t on disk, Locked binds “done,” or series Recorded without the tick.

---

## Visual doctrine (custom, not Blizzard asset rip)

Inspired by **achievement toast energy** (shield / banner / points / short title + one-line description) but **original art direction**:

| Layer | Spec |
|-------|------|
| Shape | Horizontal toast (IG 1:1 crop OK) or vertical story 9:16 |
| Frame | Ornamental border · dark glass · cold Northrend / undead crimson accents |
| Icon slot | Class silhouette or simple rune (no ripped Blizzard icon packs) |
| Title | Short, proud, ADHD (≤ ~32 chars ideal) |
| Subtitle | One true fact (“ilvl 107 → 110 · Unholy · Thrall”) |
| Points | Optional fake “points” flavor (10 / 25 / 50) — **flavor only**, not real API |
| Footer | Soft brand: “Wrath brain · returner archive” or series name |
| Exact text | Prefer **HTML/SVG render** (code) so names/numbers never garble |

**Templates on disk:** `social/achievement-frames/`  
**Render later:** screenshot HTML · or HyperFrames still · or Imagine decorative shell + code text overlay.

---

## First batch candidates (evidence-backed · 2026-08-09 scorecard)

| Priority | Achievement title (draft) | Subtitle (true) | Code |
|----------|---------------------------|-----------------|------|
| 1 | **Rot Found Some Teeth** | Crimsonrot · avg ilvl 33 → 44 | A1 |
| 2 | **Agony’s Wardrobe Grew** | Crimsonagony · 49 → 58 | A1 |
| 3 | **Main Notch** | Crimsonpain · 107 → 110 Unholy | A1 |
| 4 | **Care Six Online** | Six Thrall seats live on the board | A3 |
| 5 | **(Hold) EP01 In The Can** | Only after raw VO path + series tick | A6 |

Draft stills: open `achievement-frames/index.html` in a browser → screenshot.  
Decorative empty shells (Imagine, no exact text):  
- `achievement-frames/shell_toast_16x9.jpg`  
- `achievement-frames/shell_story_1x1.jpg`  
Prefer **HTML toasts for exact numbers**; shells for look-dev / future overlays.

---

## Caption rails (IG / story)

**Positive friction optional add-on** (not every post):

1. Name the win.  
2. One friction line if true.  
3. Invite: “what’s your small returner win this week?”  
4. Soft letter **only** if the post is critique-shaped — else skip.

**Unsafe:** “finally better than retail” · gold flex · stranger tags · claiming FOOTAGE.

---

## Flight-path VO pairing

Kyle records **on a flight path** with a **topic list** (not a full script).  
See: [[../YouTube/FLIGHTPATH_VO_TOPICS_EP01|FLIGHTPATH_VO_TOPICS_EP01]]  

After take: optional **A7** achievement still “Chapter recorded mid-air (flight path)” once file path is real.

---

## Pipeline (agent + Kyle)

```
Evidence (scorecard / tick / path)
  → pick frame code A1–A10
  → fill HTML template (exact text)
  → screenshot or export PNG
  → caption draft (not auto-publish)
  → Kyle go
```

**Agent may:** template · fill from scorecard · draft captions · generate decorative empty frames.  
**Agent may not:** publish · invent Δ · tick series Recorded · use ripped Blizzard achievement art as product.

---

## Scan residual

| Item | Status |
|------|--------|
| Doctrine note | **this file** |
| HTML toast templates | `achievement-frames/index.html` |
| Flight-path topic card | `YouTube/FLIGHTPATH_VO_TOPICS_EP01.md` |
| Imagine decorative shells | optional batch |
| Wire scorecard → auto draft PNG | later |
| TWE Zernio / Quad path | separate rails · do not freestyle |

Related: [[../../00-Index/WOW_CONTENT_UMBRELLA|Umbrella]] · [[../capture-inbox/latest|capture-inbox]] · [[../../Characters/scorecards/latest|scorecard]] · [[../YouTube/EP01_CAPTIONS_AND_CUTLIST|EP01 cutlist]]
