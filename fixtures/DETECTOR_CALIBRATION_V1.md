---
type: detector-calibration
status: active
created: 2026-08-10
rank: ROADMAP P1-7
---

# Detector calibration v1

**Law:** tag only · no publish · no invent · chat blur only if `chat_present=true`

## Fixture set (on disk)

| Fixture | Path | Expected |
|---------|------|----------|
| No-chat orbit | `Moments-Library/2026-08-09-dragonblight/analysis/FIXTURE_no_chat_orbit.json` | `chat_present=false` · gated blur = passthrough |
| Gated blur | `…/FIXTURE_gated_blur.json` | blur only when true |
| Orbit chat summary | `…/CHAT_DETECT_SUMMARY.json` | rates snapshot |
| Second-play chat | `Returns/returner-daily-2026-08-09/analysis/chat_detect_wow-*.json` | mixed T/F |

## Name overrides (shipped)

| Pattern | Tag | Why |
|---------|-----|-----|
| `h1` / `hero` in filename | `fly_or_travel` | dense scene edges mis-tagged orbit |

See `tag_motion_shot.py`.

## Documented rates (2026-08-09 second-play + pride)

### v0 max-decision (pre 2026-08-10 wave)

| Slice | chat_true | chat_false | Note |
|-------|-----------|------------|------|
| pride cuts (3) | 0 | 3 | clean pride · scores 0.0 |
| wow-220442, 221847 | 0 | 2 | orbit clean · scores 0.0 |
| wow-223313 * (3) | 3 | 0 | FP risk cluster · max 1.0 |
| **Totals** | **3** | **5** | 8 detects |

### v1.1 majority + tighter BL ROI (2026-08-10 re-rate)

Code: `detect_chat_presence.py` schema `gcs_chat_detect/v1.1` · `decision=majority` · ROI frac x 0.012–0.22 · y 0.68–0.97.

| Slice | chat_true | chat_false | Note |
|-------|-----------|------------|------|
| pride cuts (3) | 0 | 3 | guard PASS · max 0.0 |
| wow-220442, 221847 | 0 | 2 | guard PASS · max 0.0 |
| wow-223313 * (3) | 3 | 0 | **still true** · hot 5–6/3 · edge heuristic irreducible (combat UI density in BL) |
| **Totals** | **3** | **5** | same rate; decision/ROI reduced max-only false triggers elsewhere |

**223313 policy:** do not always-on blur; prefer Deck `skip_zone` or gather hide for combat-dense clips; KEEP eyes with `chat_present` badge. True chat vs combat UI needs vision/OCR later — not Phase A.

**ROI residual:** edge ratio cannot separate 223313 combat from chat; next would be vision/OCR or manual skip markers — optional after play night.

## Fly vs orbit

| Signal | orbit | fly |
|--------|-------|-----|
| scene hits/sec high + short | orbit | |
| sustained motion + hero/h1 name | | fly |
| filename hero | force fly | |

Optical-flow confidence = later; v1 is name + scene-hit heuristics.

## Pass criteria for “cal v1 done”

- [x] Fixture files exist and are cited  
- [x] Name override for h1  
- [x] Rates table for last harvest  
- [x] ROI + majority v1.1 landed; 223313 still T under edge (honest residual)  
- [ ] Vision/OCR chat if KEEP still hurt by 223313 badge (post Phase A)  
