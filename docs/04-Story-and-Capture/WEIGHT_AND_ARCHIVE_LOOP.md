---
type: product-doctrine
status: active
created: 2026-08-10
updated: 2026-08-10
product: VibeCast · Moments
area: Games/WoW
role: WEIGHT_KEEP_REJECT_AND_REUSE
---

# Weight + archive loop (what worked, what to reuse)

**Goal:** After play nights, learn **which shot types and peaks Kyle actually KEEP**, archive them for later, and brief the next night — without inventing metrics theater.  
**Parents:** [[ARCHIVE_BROLL_FOR_FUTURE]] · [[CLIP_PEAK_LEDGER]] · [[PRODUCT_SYSTEM_SPEC]] · [[FUTURE_GOALS_PLAY_TO_POST_20260810]]  

---

## Archive (already real)

KEEP → `archive_keep_to_moments.py` → Moments-Library + optional Drive `archive-broll`.  
Tags: `kyle_keep` · `for_future=true` · `shot=…` · `source_day`.

**Reuse later:** stitch · Returner Daily inserts · EP B-roll · “past in the future” montages.  
**Never reuse:** REJECT · untagged masters · invented clips.

---

## Weight ledger (new durable habit)

After each KEEP night, append one row (file or section in day analysis):

| Field | Example |
|-------|---------|
| day | 2026-08-10 |
| KEEP tags | `shot=orbit`, `peak=funny`, `ui=gather_broll` |
| REJECT tags | `load_screen`, `chat_spam` |
| stills used | memento level-up yes/no |
| note | one human/agent line |

**Path intent:**  
`~/Movies/WoW-Broll-Workflow/Returns/returner-daily-YYYY-MM-DD/analysis/WEIGHT.json`  
and/or rollup: `04-Story-and-Capture/CLIP_PEAK_LEDGER.md` (peaks) + Moments tags (visual).

**Green after 3 KEEP nights:** `NEXT_NIGHT_BRIEF` cites real tag wins (“more orbits”, “funny marker worked”, “skip load screens”).

---

## Tag recipes worth archiving

| Recipe | Why reuse |
|--------|-----------|
| `shot=orbit` | Beauty montage |
| `shot=fly` | Zone establish |
| `ui=gather_broll` | Herb/mine atmosphere |
| `peak=funny` / `story=rival_gather` | Personality shorts |
| `audio=mic_cue` + KEEP | Talk energy without full podcast |

---

## Agent steps (post-KEEP)

1. Run archive_keep_to_moments (with `--drive` when offsite wanted).  
2. Write WEIGHT row from verdicts + tags.  
3. Update NEXT_NIGHT_BRIEF one-liner from weight (not vibes alone).  
4. Do **not** invent performance scores or virality ranks.  

---

## Anti-goals

- Weight theater without KEEP data  
- Auto-publish winners  
- Treating REJECT as stock  
- Demoting P0 capture work to chase analytics  

---

## Done-when

- [x] Doctrine on disk (this file)  
- [ ] First WEIGHT row after next real KEEP  
- [ ] Brief cites weight after ≥3 KEEP nights  
