---
type: package-contract
status: active
created: 2026-08-09
product: RETURNER_DAILY
delivery: Zernio Armory
---

# Zernio package contract — Returner Daily (no auto-fire)

**Estate law (2026-08-08 Fable handoff):** **stay on Zernio** for multipost delivery. Late→Zernio rebrand; do not rebuild a full publisher “because shutdown.”  
**WoW/Returner Daily:** packages prepare here; **Kyle go** only then schedule/publish.

## Package folder shape

```
returner-daily/YYYY-MM-DD/
  README.md
  caption.md
  SOURCES.md          # video + still paths
  QA.md               # qa_returner_daily.py
  zernio_package.json # this contract filled — see template
```

## `zernio_package.json` template

```json
{
  "product": "returner_daily",
  "day": "YYYY-MM-DD",
  "status": "DRAFT_HOLD",
  "platforms": ["instagram", "tiktok", "youtube", "x"],
  "media": {
    "video": null,
    "still": null,
    "sha256": null
  },
  "caption_body": null,
  "first_comment": null,
  "scheduledFor": null,
  "kyle_go": false,
  "zernio_post_id": null,
  "notes": "Do not schedule until kyle_go true and QA READY_FOR_HUMAN_GO"
}
```

## Gate order

1. Real media paths (not scaffold em dash)  
2. QA.md not HOLD for both empty  
3. Caption filled  
4. **kyle_go: true** (human)  
5. Agent/API schedule only after 4  

## Pricing note

Official ladder (2026-08-09): 2 free · then $6 / $3 / $1 per connected account. X pass-through separate. See [[../../00-Index/UNIFIED_BOT_AND_CREATOR_GAPS|UNIFIED_BOT_AND_CREATOR_GAPS]] §3.

## Do not

- Auto-publish Returner Daily  
- Confuse Class-P letters with this product  
- Build a full Zernio replacement without cost model + Kyle program go  
