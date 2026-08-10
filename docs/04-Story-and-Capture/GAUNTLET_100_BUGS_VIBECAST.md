---
type: systems-gauntlet
status: active
created: 2026-08-10
product: GCS · VibeCast · Returner Daily
role: DECADES_BUG_SURFACE
runner: wow-roster-tracker/scripts/gcs_vibecast_gauntlet.py
---

# Gauntlet — 100 bugs / distortions for a dual-machine capture→taste→package system

**North star:** Kyle plays; system produces; fail-closed publish; rebuildable for decades.  
**Live scored:** 2026-08-10 (tool probes + code review).  
**Legend:** **PASS** proven OK · **FAIL** broken now · **PARTIAL** mitigated · **OPEN** needs human/play · **PARK** future by design  

Re-run: `python3 wow-roster-tracker/scripts/gcs_vibecast_gauntlet.py`

---

## A. Law / invent / publish (1–15)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 1 | Invent FOOTAGE when not READY | **PASS** | harvest skip; today cand=0 |
| 2 | False READY from yesterday | **PASS** | ready_today field; ready==ready_today |
| 3 | Silent auto-publish | **PASS** | stitch may_publish=false; ARM deny |
| 4 | Arm flip without go | **PASS** | arm_state default deny |
| 5 | Re-harvest thrash same day | **PASS** | .harvest_once lock rc=0 |
| 6 | Force KEEP on limbo clips | **PASS** | no force KEEP law |
| 7 | Zernio push from harvest | **PASS** | not wired to go path |
| 8 | Factory path writes from VibeCast | **PASS** | fence blocks WoW-Social-Workflow cwd |
| 9 | Fence missing on harvest | **PASS** | assert in harvest/post_play |
| 10 | False AUDIO_GREEN | **PASS** | stamp OPEN; probe refuses dual |
| 11 | agent_prove labeled as product e2e | **PARTIAL** | export_dry marks agent_prove_only |
| 12 | Publish via review board | **PASS** | KEEP only writes verdicts |
| 13 | Outbox enqueue without arm | **PASS** | stitch skips outbox default |
| 14 | Soft-poll exit wrong (any-day green) | **PASS** | exit ready_today only |
| 15 | Health green while empty tonight | **PARTIAL** | fixed freshness/calendar; still prior cand yellow |

## B. Dual-machine / path SoT (16–30)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 16 | OBS path Fable/Videos | **PASS** | Configure set D: storage |
| 17 | Masters only on untrusted C: Videos | **PARTIAL** | profile fixed; human may switch profile |
| 18 | Day root not created | **PASS** | Configure/day tree |
| 19 | Dual SoT vault vs D:\_scripts drift | **PARTIAL** | deploy exists; must run after edits |
| 20 | Resident soft_poll missing | **PASS** | Test-Path true |
| 21 | SSH dead but TS online | **PARTIAL** | soft_poll freshness now greens health |
| 22 | Tailscale peer offline | **PASS** | ONLINE_TS live this session |
| 23 | Windows path spaces break scp/ssh | **PARTIAL** | still quote-fragile; resident scripts help |
| 24 | Mac vault ≠ git (unbacked) | **PASS** | GH mirror + Drive backup-code |
| 25 | media_roots.json stale | **PARTIAL** | exists; needs version bumps on path change |
| 26 | Returns claimed as masters SoR | **PASS** | MEDIA_SOR doctrine |
| 27 | Move masters thrash historical files | **PASS** | today-only mtime/name filter |
| 28 | Export all base mp4 as today | **PASS** | Session-End today-only |
| 29 | Drive Offload missing | **PASS** | GCS-VibeCast-Offload present |
| 30 | GitHub clone missing | **PASS** | ~/src/gcs-vibecast-wow-capture |

## C. Ready / harvest / export (31–45)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 31 | soft_poll multi-day broken -File | **PASS** | -Command -Days fixed |
| 32 | Nested triple soft_poll per tick | **PASS** | 1 poll/tick |
| 33 | harvest when only stage empty cand | **PASS** | ready = cand or stage |
| 34 | Auto Session-End never runs | **PASS** | windows_auto_session_end wired |
| 35 | Auto Session-End on historical junk | **PASS** | today-only |
| 36 | Session-End PS parse fail (unicode) | **PASS** | PARSE_OK all key scripts |
| 37 | Export ignore markers | **PASS** | join-aligned + tests |
| 38 | skip_zone not hard reject | **PASS** | interval tests |
| 39 | MANIFEST missing marker_window | **OPEN** | needs live e2e night |
| 40 | post_play swallows rc | **PASS** | process substitution fixed earlier |
| 41 | enhance without candidates | **PARTIAL** | harvest gates first |
| 42 | Quiet hours block afternoon export | **PASS** | quiet 03–11 only |
| 43 | LaunchAgent not loaded | **PASS** | plist + print ok |
| 44 | Watch never harvests | **PARTIAL** | watch running; blocked on masters |
| 45 | Rate-limit hides real READY | **PARTIAL** | 90s skip only when not ready |

## D. Capture / Deck / audio (46–60)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 46 | No record_start first row | **OPEN** | human Deck night |
| 47 | Deck map missing record_start | **PASS** | map + install card |
| 48 | agent labels only in SESSION | **OPEN** | current day agent_* only |
| 49 | Dual track not configured | **PASS** | RecTracks=3 + mixers T1/T2 |
| 50 | Mic muted kills night | **OPEN** | human meter check |
| 51 | Game audio silent masters | **OPEN** | AUDIO_GREEN OPEN |
| 52 | Single mixed AAC as dual green | **PASS** | probe refuses |
| 53 | Gather UI not installed | **OPEN** | doctrine only |
| 54 | Cinematic UI not set | **OPEN** | CINEMATIC card |
| 55 | Titan zone empty | **PARTIAL** | probe exists; needs night |
| 56 | OBS Advanced mode breaks record | **PARTIAL** | configured; needs dogfood |
| 57 | Stream Deck multi-act unwired | **OPEN** | DECK_OPEN_COMMANDS ready |
| 58 | Marker join empty windows | **PARTIAL** | product fixture OK; live human open |
| 59 | talk_peak pad wrong | **PASS** | fixtures |
| 60 | Chapter-only markers as product | **PARTIAL** | honest agent_prove_only |

## E. Score / review / archive (61–75)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 61 | SHORTLIST >8 eyes fatigue | **PASS** | cap ≤8 |
| 62 | One-tap board missing | **PASS** | review_pack_feedback_server |
| 63 | open_review_pack broken | **PASS** | script present |
| 64 | REVIEW_READY never written | **PASS** | notify on harvest/enhance |
| 65 | Pride vertical missing | **PASS** | shipped 08-09 |
| 66 | Speech forced on ambience | **PASS** | SKIP_AMBIENCE |
| 67 | Chat FP always blur | **PARTIAL** | v1.1; 223313 edge |
| 68 | KEEP archive not on Drive | **PASS** | archive-broll mirrored |
| 69 | CATALOG corrupt/unqueryable | **PASS** | catalog_query + rebuild |
| 70 | Moments no tag vocab | **PASS** | TAG_VOCAB + lint |
| 71 | Package stub missing | **PASS** | NOT_ARMED package exists |
| 72 | Stitch dry publishes | **PASS** | NOT_ARMED |
| 73 | human_verdicts overwritten | **PARTIAL** | record_feedback merges ids |
| 74 | Second-play limbo forever | **OPEN** | taste; no force |
| 75 | NEXT_NIGHT_BRIEF empty loop | **PARTIAL** | script; needs KEEP tags |

## F. Automation / ops (76–85)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 76 | LaunchAgent thrash SSH 24/7 | **PASS** | quiet morning + 30m |
| 77 | Stage SCH broken thrash | **PASS** | demoted/unregistered |
| 78 | Operator re-poll spam | **PASS** | 90s rate-limit |
| 79 | Watch duplicate processes | **PARTIAL** | deduped; still manual risk |
| 80 | Health mtime false 0h | **PASS** | lock/calendar age |
| 81 | GCS_STATUS fossil date | **PARTIAL** | refreshable citadel_status |
| 82 | deploy not after every edit | **PARTIAL** | process; not enforced |
| 83 | soft_poll force scp thrash | **PASS** | resident prefer |
| 84 | mac_backup not run | **PARTIAL** | exists; needs habit/cron |
| 85 | Logs unbounded growth | **OPEN** | Library/Logs — add rotate later |

## G. Backup / restore / multi-agent (86–95)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 86 | Disk loss no code restore | **PASS** | GH + Drive + RESTORE v2 |
| 87 | KEEP media only local | **PASS** | archive-broll |
| 88 | Returns working set lost | **PARK** | acceptable; re-harvest masters |
| 89 | LaunchAgent not in backup | **PASS** | plist in GH/Drive |
| 90 | Restore drill never run | **PASS** | match=90 drift=0 |
| 91 | Other GCS agents collide | **PASS** | write fence |
| 92 | Secrets in GitHub | **PASS** | law; no .env in mirror |
| 93 | Portable doc repo stale | **PARTIAL** | wow-explorer-portable separate |
| 94 | Receipts not mirrored | **PASS** | receipts-wow Drive |
| 95 | Gauntlet not re-runnable | **PASS** | gcs_vibecast_gauntlet.py (this file) |

## H. Future-proof / decades (96–100)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 96 | No schema versions | **PARTIAL** | some schemas v1; not all |
| 97 | Hardcoded host IP only | **PARTIAL** | WINDOWS_SSH_HOST env + default |
| 98 | No plugin surface for new engines | **OPEN** | spine contracts allow; no plugin API yet |
| 99 | Twin games (TDE/TFE) not portable | **OPEN** | brand packs later; same spine |
| 100 | AI upgrade path unclear | **PARTIAL** | INTEL stack doc; Phase A before cloud AI |

---

## Score snapshot (live)

| Status | ~Count |
|--------|--------|
| PASS | majority of wired law/spine |
| PARTIAL | ops habits, dual-SoT discipline, detectors |
| OPEN | human play A1–A3, limbo taste, log rotate, plugin API |
| FAIL | re-run runner for current FAIL list |
| PARK | Returns full offline |

## Patches shipped with this gauntlet wave

1. `gcs_vibecast_gauntlet.py` — re-runnable harness  
2. Health Windows green when soft_poll SSH fresh (<15m)  
3. This ledger as decades bug surface  

## Top 10 to tackle next (priority)

1. Real play night close A1–A3 (OPEN product)  
2. Enforce deploy_windows_scripts after every PS edit (hook/receipt)  
3. mac_backup on successful harvest (wire post_play)  
4. Watch single-instance lockfile  
5. Log rotation for gcs-vibecast-wow logs  
6. Schema version audit across JSON artifacts  
7. ONLINE_SSH true probe optional in reachability  
8. Limbo SHORTLIST auto-park after N days  
9. Portable + gcs-vibecast dual-doc sync one command  
10. Plugin/extension README for new engines under same spine  

## Related

[[PRODUCT_SYSTEM_SPEC]] · [[VIBECAST_WRITE_FENCE]] · [[RESTORE_AND_BACKUP]] · [[ROADMAP_P0_P2_TOP10]] · [[../00-Index/GCS_CITADEL]]
