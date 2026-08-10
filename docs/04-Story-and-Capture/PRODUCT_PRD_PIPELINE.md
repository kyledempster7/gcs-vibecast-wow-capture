---
type: product-prd
status: active
created: 2026-08-10
product: GCS VibeCast pipeline
parent: PRODUCT_SYSTEM_SPEC.md
---

# PRD — VibeCast dual-machine pipeline (buildable slices)

**Parent:** [[PRODUCT_SYSTEM_SPEC]]  
**Backlog:** [[MARKET_100_MISSING]] · **Queue:** [[ROADMAP_P0_P2_TOP10]]

## Problem

Kyle records real play; hours of masters die on disk. Market tools (Opus/Eklipse/…) win on volume/vertical/captions but cannot see **play-state** (Deck markers), **dual-machine truth**, or **brand-safe KEEP**. Our tools exist as scripts + doctrine but are not one product loop agents can finish without Kyle as bridge.

## Goals (this PRD)

| ID | Goal | Metric |
|----|------|--------|
| G1 | One spine doc agents follow | PRODUCT_SYSTEM_SPEC + this PRD linked from umbrella |
| G2 | Mac vertical pride product | pride/vertical/*.mp4 9:16 from landscape pride |
| G3 | Speech peaks when VO | SPEECH_PEAKS.json or honest ambience skip |
| G4 | ≤60s review shortlist | SHORTLIST ≤8 primary eyes rows |
| G5 | Marker-aware export path | Export reads SESSION.jsonl when present |
| G6 | Health + next-night brief | one green/red board + NEXT_NIGHT_BRIEF.md |
| G7 | Hostile review of design | ACCEPT / ACCEPT_WITH_NITS / REJECT on disk |
| G8 | No publish without go | packages remain NOT_ARMED |

## Non-goals

Invent footage · auto-publish · force speech cuts on ambience · require Kyle to multi-act Deck setup mid-session (agents install map + prove script).

## User stories

1. **As Kyle**, I play and press Deck states; after logout I open one SHORTLIST and KEEP/REJECT in under a minute.  
2. **As Mac agent**, I harvest when Windows soft-poll READY and produce review-pack + vertical + brief without inventing clips.  
3. **As Windows agent**, I ensure day path + dual audio SoR + Export uses marker windows when JSONL exists.  
4. **As cold agent**, I read handoff → PRODUCT_SYSTEM_SPEC → ROADMAP next open rank and execute.

## Functional requirements

| # | Requirement | Owner | Done-when |
|---|-------------|-------|-----------|
| F1 | pride_vertical center-crop 9:16 v0 | Mac | files + ffprobe 9:16 |
| F2 | enhance_returner_day calls vertical | Mac | shell step |
| F3 | build_review_pack lists vertical + caps SHORTLIST | Mac | SHORTLIST.md |
| F4 | speech_peaks from whisper/srt or skip | Mac | SPEECH_PEAKS.json |
| F5 | Export-ShipCandidates optional -MarkersJsonl | Windows | MANIFEST marker_window |
| F6 | Append record_start formal id | Windows | prove line |
| F7 | moments_stitch_dry montage dry | Mac | montage-dry/ |
| F8 | gcs_pipeline_health + NEXT_NIGHT_BRIEF | Mac | md files |
| F9 | detector calibration fixture table | Mac | fixtures README + rates receipt |
| F10 | Deck multi-action install card | Windows | DECK_MULTI_ACTION_INSTALL.md on D:\_scripts |

## UX requirements (review)

- Pride first, second-play second, rest muted.  
- Vertical link next to landscape pride.  
- CLI: `record_feedback.py --verdict KEEP|REJECT`.  
- Never plate TFE reject-ledger assets (global cork).

## Open risks

| Risk | Mitigation |
|------|------------|
| Human never pressed Deck multi-actions | Install card + agent_prove ≠ done; rank 1 stays OPEN until human press night |
| Dual audio still open | Rank 2 separate; do not fake AUDIO_GREEN |
| Speech empty on ambience nights | Honest skip (already TRANSCRIPT_NOTE) |
| Marker export needs masters on Windows | Only when day has raw masters |

## Ship definition for “product review ready”

- Spec + PRD + hostile review on disk  
- Ranks 4–5,7–10 advanced with proof paths  
- Ranks 1–3,6: Windows scripts/docs landed; human-press residual named  
- Still Zernio schedule untouched; no video publish  
