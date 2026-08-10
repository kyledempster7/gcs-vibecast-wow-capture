---
type: product-intelligence
status: active
created: 2026-08-10
updated: 2026-08-10
area: Games/WoW
role: HONEST_MI_LEVEL_AND_COST
---

# Intelligence stack & cost — what actually runs on a scan

**Product law:** no invent FOOTAGE · human KEEP wins · fail-closed publish.  
**Parent:** [[PRODUCT_SYSTEM_SPEC]] · backlog [[MARKET_100_MISSING]] · queue [[ROADMAP_P0_P2_TOP10]]

---

## One-line truth

**Most “every scan” intelligence is local classical CV + rules (ffmpeg), not cloud deep learning.**  
A little **local ML** (Whisper speech, Apple Vision OCR) runs when audio/frames justify it.  
**Cloud clip-AI (Eklipse/Opus-class) is not in the harvest loop today** — that is market gap, not current bill.

**Highest-value “intelligence” is not a model:** it is **Kyle’s Stream Deck markers** (play-state ground truth) + **KEEP**.

---

## Layers (low → high)

| Layer | What | How smart | Cost / night (typical) | Who owns |
|-------|------|-----------|------------------------|----------|
| **L0 Truth** | masters · sha256 · MANIFEST · day paths | File integrity | $0 (disk + LAN) | Windows + Mac |
| **L1 Play-state** | Stream Deck → `SESSION.jsonl` | **Human labels** (broll/rotate/talk/skip/gather) | $0 | **Kyle presses** |
| **L2 Classical scan** | freeze · black · scene density · bitrate · BL chat ROI | Heuristic “v0” rules — **not** neural nets | $0 electricity (ffmpeg CPU/GPU) | Mac scripts |
| **L3 Local ML (optional)** | `mlx_whisper` speech · macOS Vision OCR (Titan strip) | Real ML, **on-device** | $0 API · some heat/time | Mac when VO / Titan up |
| **L4 Product assemble** | pride cuts · 9:16 crop · review SHORTLIST · Moments · stitch dry | Rules + ffmpeg encode | $0 | Mac |
| **L5 Agent orchestration** | harvest, score, brief, handoffs (Grok/Codex seats) | LLM ops — **not** per-frame video models | Seat/subscription budget (AIOS), **not** per-clip SaaS | Agents |
| **L6 Publish** | Zernio / packages | Only on **go** | Zernio only when armed | Kyle go |
| **L7 Not in loop yet** | kill-event AI · virality rank · cloud reframe SaaS | Market leaders’ moat | Would be $ / min if added | [[MARKET_100_MISSING]] 51–55 |

Script self-description (on disk): `tag_motion_shot.py` — **“Heuristics (v0, not ML)”**.

---

## What each scan actually does (Returner day)

```
pull candidates
  → score_candidates     (black/freeze/tiny reject — ffmpeg)
  → tag_motion_shot      (scene hits + freeze → orbit/fly/still)
  → detect_chat_presence (bottom-left edge ROI — classical)
  → speech_peaks         (from local whisper transcript if any; else skip)
  → zone_label_probe     (Vision OCR if Titan chrome; never invent zone)
  → pride / vertical     (cut + center crop — not subject-tracking AI)
  → review-pack          (SHORTLIST for Kyle eyes)
```

**Class (DH vs DK) does not change the scan.** Demon hunter footage is the same engine as Blood DK — markers + motion + taste.

---

## Cost picture (honest)

| Spend type | In current harvest loop? | Notes |
|------------|--------------------------|-------|
| OpenAI / Anthropic **per clip** | **No** | Not wired into scan scripts |
| Eklipse / Opus / Munch | **No** | Competitive optional later |
| mlx_whisper local | **Yes when run** | Electricity + time; model already local |
| Apple Vision OCR | **Yes when probe runs** | Free on Mac |
| ffmpeg encode (720p/9:16/stitch) | **Yes** | CPU/GPU only |
| Zernio | **Only scheduled/go packages** | Separate from “scan every mp4” |
| Agent seats (Codex/Grok) | **Session work** | Building/running the engine — not per-frame pricing |

**Rough night cost for pure video scan path: ≈ $0 variable API** if you stay local.  
**Variable cost grows only if** we bolt on cloud highlight AI or always-on paid caption APIs.

---

## Intelligence level (plain English)

| Claim | Reality |
|-------|---------|
| “Full AI editor like Opus” | **No** — we shortlist; we don’t rewrite stories |
| “Knows it was an orbit” | **Weak-medium** — scene density heuristic + filename overrides; **Deck rotate is stronger** |
| “Knows chat is up” | **Medium** — ROI heuristic; FP possible (223313) |
| “Knows zone” | **Low until Titan location line OCR hits** — chrome can show without zone token |
| “Knows talk peaks” | **Medium when VO exists** — Whisper; **skipped** on ambience nights |
| “Knows what Kyle meant” | **High only if Deck button pressed** |
| “Knows what to publish” | **Kyle KEEP + go only** |

So: **smart enough to refuse garbage and rank eyes; not smart enough to replace play-state or taste.**  
That is intentional — SaaS that “knows” without you often invents or spam-ships.

---

## The Deck trick (product thesis)

If Kyle wires Layer C multi-actions:

```
press broll / rotate / talk / skip / gather
        ↓
SESSION.jsonl ground truth
        ↓
marker-aware export + join windows
        ↓
Mac harvest cuts where the story actually was
```

**That multiplies every L2/L3 model** without buying cloud AI.  
Market tools cannot see your Deck. That is the engine wedge.

Install: [[DECK_MULTI_ACTION_INSTALL]] · script on `D:\_scripts\Append-StreamDeckMarker.ps1`

---

## How we keep growing (engines, not weekly fuss)

1. **100 gaps** = full product backlog → [[MARKET_100_MISSING]]  
2. **Top 10** = only execute queue → [[ROADMAP_P0_P2_TOP10]]  
3. **Agents own weekly ops** after Deck + path + dual audio land: soft-poll → harvest → SHORTLIST → brief  
4. **Kyle owns:** play · a few Deck presses · ≤60s KEEP · go when proud  
5. **Raise intelligence in order:**  
   - Deck live (labels) → dual audio → marker export → better detectors → optional cloud AI as *suggestion only*  
6. **Never** auto-raise “intelligence” by inventing FOOTAGE or silent publish  

Unattended shape (target):

```
play night (Kyle + Deck)
  → Windows day root + markers (auto)
  → Mac soft-poll READY → harvest_mac (agent/cron)
  → SHORTLIST + NEXT_NIGHT_BRIEF (auto)
  → Kyle 60s taste when ready
  → package NOT_ARMED until go
```

---

## “Smarter than we give it credit” — fair ceiling

**Already systemic:** dual-machine harvest, MANIFEST truth, gated blur, Moments, vertical pride, healthboard, cold boot, market→roadmap.  

**Under-credited if Deck is live:** play-state graph becomes a product no clip SaaS has.  

**Over-credited if we say “AI scans everything”:** L2 is mostly ffmpeg rules. Name it **machine intelligence = heuristics + local ML + human graph**, not magic.

---

## Related

- [[MACHINE_INTELLIGENCE_BROLL]] · [[CINEMATIC_ORBIT_UI_MODE]] · [[DECK_MULTI_ACTION_INSTALL]]  
- Scripts: `wow-roster-tracker/scripts/`  
