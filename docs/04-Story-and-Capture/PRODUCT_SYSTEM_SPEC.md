---
type: product-system-spec
status: active
created: 2026-08-10
updated: 2026-08-10
product: GCS · VibeCast · Returner Daily
area: Games/WoW
role: ONE_COHESIVE_SYSTEM
---

# Product system spec — one cohesive capture→taste→package loop

**Studio:** [[../00-Index/GCS_CITADEL|GCS]] · **Wing:** [[../00-Index/VIBECAST_OS|VibeCast]] · **Brand:** TWE  
**Thesis:** [[../00-Index/PRODUCT_THESIS_VIBECAST|PRODUCT_THESIS_VIBECAST]]  
**Gap ledger:** [[MARKET_100_MISSING]] · **Execute queue:** [[ROADMAP_P0_P2_TOP10]]  
**Intelligence & cost (honest):** [[INTELLIGENCE_STACK_AND_COST]]  
**Play door:** [[../00-Index/KYLE_OS|KYLE_OS]] only (not this file)

---

## 1. Product one-liner

**Real WoW play on Windows → dual-machine harvest → machine shortlist → human KEEP → multi-ratio package held NOT_ARMED until Kyle says go.**

Not: invent FOOTAGE · silent publish · virality score as taste · second vault index.

---

## 2. Jobs to be done (who the system serves)

| Actor | Job | Success |
|-------|-----|---------|
| **Kyle (player)** | Play / talk without assembling posts | ≤60s review later; only go when proud |
| **Windows capture** | Masters + markers + stems + day path | AUDIO_GREEN · SESSION.jsonl · day root SoR |
| **Mac harvest agents** | Pull candidates · score · tags · shortlist | review-pack + Moments · no invent |
| **Armory / publish** | Package multi-platform | NOT_ARMED default; go-only |

---

## 3. Pipeline (single spine)

```
PLAY (Windows OBS + Deck markers + optional Gather UI)
        │ masters + markers\SESSION.jsonl + stills
        ▼
EXPORT / STAGE candidates (sha256 MANIFEST)  ← marker windows when present
        │ LAN / Tailscale only for multi-GB
        ▼
HARVEST Mac  Returns/returner-daily-YYYY-MM-DD/
        │ score · pride · motion · chat detect · speech peaks (VO)
        ▼
REVIEW ≤60s  pride + second-play only  → verdicts / KEEP
        │ 9:16 vertical on pride · Moments Library tags
        ▼
ARCHIVE KEEP  Moments-Library + optional Drive archive-broll  (future projects)
        │ archive_keep_to_moments.py · for_future=true · no invent
        ▼
PACKAGE NOT_ARMED  (still-led Zernio OK if already scheduled; video on go)
        │
        ▼
NEXT_NIGHT_BRIEF  + healthboard  (what shot types won · what to record)
```

**Canon media root (Mac):** `~/Movies/WoW-Broll-Workflow/`  
**Canon capture root (Windows):** `D:\WoW B-Roll Storage\<day>\`  
**Canon doctrine:** `Games/WoW/` (this tree). Research notes support only.

---

## 4. System surfaces (one house, many doors)

| Surface | Path / tool | Owner |
|---------|-------------|--------|
| Play door | KYLE_OS · SIMPLE_START | Kyle |
| Gather mode | GATHERING_BROLL_MODE + Deck gather_ui | Windows |
| Deck map | DECK_BUTTON_MAP + Append-StreamDeckMarker.ps1 | Windows |
| Export | Export-ShipCandidates.ps1 (+ marker windows) | Windows |
| Soft poll / pull | soft_poll_windows · harvest_mac · Stage-ShipCandidates | Mac↔Win |
| Score / pride / tags | score_candidates · pride_cuts · tag_motion · detect_chat | Mac |
| Vertical product | pride_vertical.py → candidates/pride/vertical/ | Mac |
| Speech peaks | speech_peaks.py → analysis/SPEECH_PEAKS.json | Mac (VO nights) |
| Review | review-pack/index.html · SHORTLIST · record_feedback | Mac + Kyle |
| Moments | Moments-Library/YYYY-MM-DD-*/ | Mac |
| KEEP archive | archive_keep_to_moments.py · ARCHIVE_BROLL_FOR_FUTURE · Drive archive-broll | Mac |
| Stitch dry | moments_stitch_dry.py (NOT_ARMED) | Mac |
| Health + brief | gcs_pipeline_health · NEXT_NIGHT_BRIEF | Mac |
| Market gaps | MARKET_100_MISSING (100) | Agents |
| Ranked work | ROADMAP_P0_P2_TOP10 | Agents |

---

## 5. Contracts (machine-readable truths)

| Artifact | Schema intent | Law |
|----------|---------------|-----|
| MANIFEST.json | ship candidates + sha256 | purity; no log pollution |
| SESSION.jsonl | gcs_obs_marker/v1 | first row should be record_start |
| MARKER_JOIN.json | cut windows | empty = honest AUTO score |
| MOTION_TAGS.json | shot=orbit/fly/… | tag only |
| chat_detect_*.json | chat_present bool | blur only if true |
| SPEECH_PEAKS.json | talk windows | skip if ambience |
| human_verdicts.json | KEEP/REJECT | human wins |
| PRIDE_CUTS.json | landscape pride | source for 9:16 |
| vertical/*.mp4 | 9:16 pride product | no publish |
| zernio package | NOT_ARMED | go only |

---

## 6. Acceptance (product-level, not “docs exist”)

1. **Capture night** produces day root + optional markers without Kyle opening agent trees.  
2. **Harvest** lands candidates + SHORTLIST ≤8 eyes items (pride + second-play first).  
3. **Vertical** pride clips exist when landscape pride exists.  
4. **Speech** shortlist only when VO proven (else honest skip).  
5. **KEEP** path writes verdicts; never invents clips.  
6. **Publish** cannot arm without explicit Kyle go.  
7. **Cold agent** boots from latest handoff + this spec + ROADMAP next row in ≤5 minutes.  
8. **Healthboard** shows Windows online · audio · markers · candidates · arm state.

---

## 7. Non-goals (hard)

- Invent FOOTAGE / fake kill cams  
- Silent auto-publish / scheduler spam  
- Virality score replacing KEEP  
- ElvUI / Titan as required stack  
- Second competing vault index  
- Always-on chat blur  

---

## 8. Dependency order (build)

Matches ROADMAP ranks 1→10:

1 Deck multi-act → 2 OBS dual audio+path → 3 marker export → 4 pride 9:16 → 5 speech  
→ 6 gather live → 7 detector cal → 8 stitch dry → 9 60s review → 10 health+brief  

Market 100 is the full backlog; top 10 is the only execute queue until reset.

---

## 9. Review product (Kyle surface)

| Step | Max time | Input | Output |
|------|----------|-------|--------|
| Open SHORTLIST | 5s | review-pack/SHORTLIST.md | eyes order |
| Watch pride + top second-play | ≤45s | proxies / vertical | taste |
| One-liners | 10s | `record_feedback.py` | verdicts.json |
| Go video? | optional | proud only | Armory arm |

Phone-friendly later = same SHORTLIST + vertical proxies (rank 9 polish).

---

## 10. Related (do not fork)

- Umbrella: [[../00-Index/WOW_CONTENT_UMBRELLA]]  
- Intel: [[MACHINE_INTELLIGENCE_BROLL]] · [[GATHERING_BROLL_MODE]]  
- Media SoR: [[../00-Index/MEDIA_SOR_DUAL_MACHINE]]  
- Scripts: `Games/WoW/wow-roster-tracker/scripts/`  
- Receipts: `…/control-plane/receipts/wow/`  
