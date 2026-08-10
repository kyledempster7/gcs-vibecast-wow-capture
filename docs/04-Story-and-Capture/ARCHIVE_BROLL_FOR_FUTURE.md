---
type: doctrine
status: active
created: 2026-08-10
updated: 2026-08-10
area: Games/WoW
role: KEEPER_ARCHIVE_FOR_FUTURE_PROJECTS
---

# Archive good B-roll for later (fits the shape)

**Yes — this is already the product shape.** Capture nights feed **KEEP** → **Moments Library** → future stitch / EPs / social / HyperFrames. Not a dump of every master.

**Canon media:** `~/Movies/WoW-Broll-Workflow/`  
**Canon doctrine:** this file + [[MACHINE_INTELLIGENCE_BROLL]] + [[PRODUCT_SYSTEM_SPEC]]  
**Script:** `wow-roster-tracker/scripts/archive_keep_to_moments.py`

---

## What “archive” means here

| Layer | What lands | What never lands |
|-------|------------|------------------|
| **Day Returns** | All candidates + analysis (working set) | Silent publish |
| **Moments Library** | **KEEP** (and pride from KEEP) + tags | REJECT / load screens / invent |
| **Drive offload** | Code/docs mirror + keeper clips copy | Secrets / Zernio tokens |
| **GitHub** | Scripts + product docs only | Multi‑GB masters / mp4 |

**Law:** human KEEP wins · no invent FOOTAGE · no always-on blur · publish still go-only.

---

## Pipeline slot (same spine)

```
… → REVIEW ≤60s → human KEEP
        │
        ▼
archive_keep_to_moments  →  Moments-Library/YYYY-MM-DD-<zone>/
        │                    clips/ · stills/ · MOMENTS.json · ARCHIVE.json
        ▼
optional Drive: GCS-VibeCast-Offload/archive-broll/<day>/
        │
        ▼
future projects: stitch · Returner Daily · Explorer EPs · still-led packs
```

Moments is the **durable player library**. Day `returner-daily-*` can be slimmed later; Moments must survive.

---

## Promote rules

1. Read `analysis/human_verdicts.json` (and optional SHORTLIST pride KEEP).  
2. Resolve id → mp4 under `candidates/` or `candidates/pride/`.  
3. Copy (not move) into Moments `clips/` with stable basename.  
4. Append/update `MOMENTS.json` tags: `shot=…`, `kyle_keep`, `source_day`, `for_future=true`.  
5. Write `ARCHIVE.json` with sha256 + source path + utc.  
6. Optional `--drive` copies keepers + ARCHIVE index to Google Drive offload.

---

## Future project use

- **Stitch / montage:** Moments clips only (already montage-dry path).  
- **New EP / podcast insert:** pull orbits/fly from Moments tags.  
- **Social still-led:** stills/ + vertical pride from KEEP.  
- **Never:** treat REJECT or untagged masters as library stock.

---

## Done when (ops)

- [x] Doctrine on disk (this file)  
- [x] `archive_keep_to_moments.py` run after KEEP nights (2026-08-09)  
- [x] Drive `archive-broll/` has latest KEEP set  
- [x] GitHub has scripts/docs (not media)  
- [x] `catalog_query.py` rebuild/query + restore drill 2026-08-10  

---

## Related

- [[MACHINE_INTELLIGENCE_BROLL]] · [[PRODUCT_SYSTEM_SPEC]] · [[ROADMAP_P0_P2_TOP10]]  
- [[IMPROVEMENTS_PLUS10_BEYOND_NOW_20260810]] (next 10 enhancements)  
