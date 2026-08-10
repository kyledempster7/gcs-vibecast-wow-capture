# Play-night operator path build — 2026-08-10

## Thesis
Right-size done. Build the **one harvest button** + Loc: zone parse + Stage default Day — not more fleet.

## Shipped
| # | Item | Proof |
|---|------|--------|
| 1 | post_play_harvest.sh | soft_poll→harvest_if_ready→health · NOT_READY rc=1 for 08-10 |
| 2 | KYLE_OS Record content row | 00-Index/KYLE_OS.md |
| 3 | PLAY_NIGHT_CHECKLIST.md | 04-Story-and-Capture |
| 4 | zone Loc: parse | extract_zone loc_line · day zone/zone_slug on ZONE_LABEL |
| 5 | Stage-ShipCandidates default Day | optional -Day; deploy D:\_scripts |
| 6 | This receipt | |

## Not claimed
A1 Deck product · A2 AUDIO_GREEN · A3 export e2e masters · invent FOOTAGE

## Operator
```bash
bash …/scripts/post_play_harvest.sh   # after export/stage has candidates
```

rc=0
