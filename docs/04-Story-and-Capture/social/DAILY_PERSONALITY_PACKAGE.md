---
type: social-recipe
status: active
created: 2026-08-10
updated: 2026-08-10
product: Returner Daily · Personality shape
area: Games/WoW
role: MACHINE_DAILY_PACKAGE
---

# Daily personality package (when Kyle played)

**Name:** Returner Daily · **Personality shape**  
**Do not call this Class-P.** Class-P is a separate TWE letter / editorial lane.  
**Parent social doctrine:** [[RETURNER_DAILY_SOCIAL]]  
**Style:** [[CONTENT_STYLE_COMMUNITY]] · **Funny peaks:** [[../FUNNY_MIC_CUE_MOMENTS]]  
**Laws:** real play only · no invent · package NOT_ARMED · go-only publish  

---

## Gate

| Condition | Action |
|-----------|--------|
| `played_today` + masters/candidates real | Build package draft |
| No play / markers-only / empty candidates | **No post day** |
| KEEP empty after review | Archive nothing; no social draft |

---

## Package contents (minimum)

| Slot | Source | Role |
|------|--------|------|
| **1 · Video** | KEEP pride **or** funny/mic-cue peak (8–20s preferred) | Personality + moment |
| **2 · Still** | Memento / achievement / level-up screenshot (new mtime that day) | “What just happened” |
| **3 · Story block** | Signals only (see below) | 1–3 sentences for caption / X |
| **4 · Caption seeds** | Style templates + story facts | X / IG / optional story |

**MVP:** 1 video + 1 still + 1 story line. Missing either media side → story-single or skip — never fake media.

Optional slide 3+: second still, soft title card, achievement frame (later).

---

## Story block — allowed signals only

Compose from **disk truth**, never training fluff:

| Signal | Where |
|--------|--------|
| Level delta | Armory / roster API preferred; Memento level still secondary |
| Achievements / toasts | Memento stills + filenames only if real |
| Zone / gather | Markers · zone OCR when Titan up · KEEP tags (`shot=gather`, `story=rival_gather`) |
| Talk / funny | SPEECH_PEAKS · mic_cue · Deck `funny_moment` / `talk_peak` |
| Mode | broll_bed vs talk_product from night classification |

**Never invent:** rival class/race, exact herb counts, “three levels” unless level-delta or Kyle KEEP note proves it.

---

## Output shape (draft)

```
returner-daily-YYYY-MM-DD/
  package/
    DAILY_PERSONALITY_DRAFT.md   # story + caption seeds
    MEDIA_MAP.json               # paths only; sha when known
    armed: false
```

Publish path remains Armory / Zernio contract: **NOT_ARMED** until kyle_go.

---

## Agent order after harvest + KEEP

1. Resolve KEEP video + best still for day  
2. Collect signals (level, memento, peaks, tags)  
3. Write story block under community style  
4. Write caption seeds (X short · IG slightly longer)  
5. Leave package NOT_ARMED · notify review/brief  
6. Weight ledger row → [[../WEIGHT_AND_ARCHIVE_LOOP]]  

---

## Platforms (intent)

| Surface | Default unit |
|---------|----------------|
| X | 1 clip or still + short caption (personality) |
| IG / similar | Carousel: video + still(s) |
| Archive | Moments tags for future montage |

No silent multipost. No Class-P letter auto-mix.
