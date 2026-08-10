# Right-size swarm — 2026-08-10

## Verdict
Spine KEEP. Always-on wire/schedule wave was **overbuilt** for 1–3 play nights/week.
Product residual remains play night A1–A3 (Deck, AUDIO_GREEN, export e2e) — not more fleet.

## Swarm
- Right-size: overbuilt; play-night mode default
- Gaps: Deck/AUDIO/export still open; schedule thrash + Stage SCH -Day bug
- Audit: triple soft_poll/tick, re-scp every poll, catalog idle rebuild, Stage SCH broken

## Shipped this wave (trim)
| Change | Result |
|--------|--------|
| 1 soft_poll SSH/tick | loop: multi-day once only |
| harvest_if_ready from LATEST | no nested poll when today not ready |
| soft_poll resident D:\_scripts | no scp thrash (force via SOFT_POLL_FORCE_SCP=1) |
| Quiet hours 03–19 local | play-night window 20:00–02:59 |
| No idle catalog rebuild | rebuild only on HARVEST_OK |
| Stage SCH demoted | unregistered; harvest_mac owns stage |
| LaunchAgent RunAtLoad=false | no install double-fire |

## Park until play night
MARKET_100 thrash · more plus-10 · one-tap board · HyperFrames brand · chat vision · Zernio

## Laws
no invent FOOTAGE · no silent publish · freeze infra growth until one full product night

rc=0
