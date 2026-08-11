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
**Canonical source:** Codex 100-row owner crosswalk; run `sync_gap_100_ledger.py` after a refresh.
**Legend:** **CLOSED** current proof closes the named bug · **PARTIAL** safe work complete but real/human proof remains · **OPEN** real capture/audio/human action required

Re-run: `python3 wow-roster-tracker/scripts/gcs_vibecast_gauntlet.py`

---

## A. Law / invent / publish (1–15)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 1 | Invent FOOTAGE when not READY | **CLOSED** | CLOSED is the refusal control, not media/product delivery. No FOOTAGE was invented. |
| 2 | False READY from yesterday | **CLOSED** | Residual or prior-day media never counts as today. |
| 3 | Silent auto-publish | **CLOSED** | No provider/publish action was run. |
| 4 | Arm flip without go | **CLOSED** | A historical filename containing ARMED is not current ARM authority. |
| 5 | Re-harvest thrash same day | **CLOSED** | Residual idempotency is not first-run or same-day Branch-A E2E. |
| 6 | Force KEEP on limbo clips | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 7 | Zernio push from harvest | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 8 | Factory path writes from VibeCast | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 9 | Fence missing on harvest | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 10 | False AUDIO_GREEN | **CLOSED** | Audio itself remains OPEN; only false-green prevention is closed. |
| 11 | agent_prove labeled as product e2e | **PARTIAL** | Structural/idempotent checks cannot promote Branch A. |
| 12 | Publish via review board | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 13 | Outbox enqueue without arm | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 14 | Soft-poll exit wrong (any-day green) | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 15 | Health green while empty tonight | **CLOSED** | Empty-night health cannot be presented as PRODUCT_GREEN. |

## B. Dual-machine / path SoT (16–30)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 16 | OBS path Fable/Videos | **CLOSED** | Profile-path closure does not claim a recording occurred. |
| 17 | Masters only on untrusted C: Videos | **CLOSED** | No historical Fable file was moved or reclassified. |
| 18 | Day root not created | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 19 | Dual SoT vault vs D:\_scripts drift | **CLOSED** | Closure is deployed byte parity plus admission control, not live capture. |
| 20 | Resident soft_poll missing | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 21 | SSH dead but TS online | **CLOSED** | Reachability is current-session proof; future loss must fail closed. |
| 22 | Tailscale peer offline | **CLOSED** | Current-session reachability only. |
| 23 | Windows path spaces break scp/ssh | **CLOSED** | Spaced-path transport is proven for this deployed surface; real gameplay is separate. |
| 24 | Mac vault ≠ git (unbacked) | **CLOSED** | The authority bundle and sample are recovery custody; neither is PRODUCT_GREEN. |
| 25 | media_roots.json stale | **CLOSED** | Future path changes still require a version bump and fresh readback. |
| 26 | Returns claimed as masters SoR | **CLOSED** | Fable Aug10 files remain non-SoR unless a human refiles them. |
| 27 | Move masters thrash historical files | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 28 | Export all base mp4 as today | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 29 | Drive Offload missing | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 30 | GitHub clone missing | **CLOSED** | Public sample is not live-vault authority. |

## C. Ready / harvest / export (31–45)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 31 | soft_poll multi-day broken -File | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 32 | Nested triple soft_poll per tick | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 33 | harvest when only stage empty cand | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 34 | Auto Session-End never runs | **CLOSED** | The regression used disposable fixture bytes and touched no real media. |
| 35 | Auto Session-End on historical junk | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 36 | Session-End PS parse fail (unicode) | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 37 | Export ignore markers | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 38 | skip_zone not hard reject | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 39 | MANIFEST missing marker_window | **CLOSED** | Historical real-media annotation does not prove the next same-day Branch A run. |
| 40 | post_play swallows rc | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 41 | enhance without candidates | **CLOSED** | This closes the no-candidate safety bug, not same-day Branch-A E2E. |
| 42 | Quiet hours block afternoon export | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 43 | LaunchAgent not loaded | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 44 | Watch never harvests | **PARTIAL** | Needs one same-day READY→harvest pass. |
| 45 | Rate-limit hides real READY | **CLOSED** | This closes cache masking, not media readiness. |

## D. Capture / Deck / audio (46–60)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 46 | No record_start first row | **OPEN** | Agent markers cannot replace a human capture row. |
| 47 | Deck map missing record_start | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 48 | agent labels only in SESSION | **OPEN** | agent_assigned/agent_* is not semantic or human correctness. |
| 49 | Dual track not configured | **CLOSED** | Rows 50 and 51 remain OPEN until the real mic and game audio are heard. |
| 50 | Mic muted kills night | **OPEN** | Requires real media/meter/playback. |
| 51 | Game audio silent masters | **OPEN** | BAN false AUDIO_GREEN. |
| 52 | Single mixed AAC as dual green | **CLOSED** | False-green prevention is separate from audio success. |
| 53 | Gather UI not installed | **CLOSED** | Offline SavedVariables configuration is proven; no in-game screenshot is invented. |
| 54 | Cinematic UI not set | **PARTIAL** | A real in-game visual/orbit still must prove the cinematic result. |
| 55 | Titan zone empty | **PARTIAL** | The unproven remainder stays open; no structural or agent-assigned promotion. |
| 56 | OBS Advanced mode breaks record | **PARTIAL** | The unproven remainder stays open; no structural or agent-assigned promotion. |
| 57 | Stream Deck multi-act unwired | **PARTIAL** | The running Stream Deck application's button bindings and a real human press remain unproven. |
| 58 | Marker join empty windows | **CLOSED** | Historical proof closes the empty-window join bug; the next play-night E2E remains row 11/44. |
| 59 | talk_peak pad wrong | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 60 | Chapter-only markers as product | **PARTIAL** | The unproven remainder stays open; no structural or agent-assigned promotion. |

## E. Score / review / archive (61–75)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 61 | SHORTLIST >8 eyes fatigue | **CLOSED** | Count cap is not semantic approval. |
| 62 | One-tap board missing | **CLOSED** | Feedback writes verdicts only; it cannot arm or publish. |
| 63 | open_review_pack broken | **CLOSED** | No browser focus or foreground-control claim is made. |
| 64 | REVIEW_READY never written | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 65 | Pride vertical missing | **CLOSED** | Physical/hash existence does not certify visual quality. |
| 66 | Speech forced on ambience | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 67 | Chat FP always blur | **CLOSED** | Closure is bounded to the cited real-media regression. |
| 68 | KEEP archive not on Drive | **CLOSED** | Local Google Drive sync-surface proof; not authenticated provider API readback. |
| 69 | CATALOG corrupt/unqueryable | **CLOSED** | Current read-only query proof only. |
| 70 | Moments no tag vocab | **CLOSED** | Current lint scope only. |
| 71 | Package stub missing | **CLOSED** | Stale non-primary paths are excluded; package product_ready is not whole PRODUCT_GREEN. |
| 72 | Stitch dry publishes | **CLOSED** | No provider action was run. |
| 73 | human_verdicts overwritten | **CLOSED** | The regression used an isolated fixture and did not touch real verdicts. |
| 74 | Second-play limbo forever | **CLOSED** | Park is not KEEP or REJECT. |
| 75 | NEXT_NIGHT_BRIEF empty loop | **CLOSED** | KEEP identifiers guide capture; they do not arm a package. |

## F. Automation / ops (76–85)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 76 | LaunchAgent thrash SSH 24/7 | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 77 | Stage SCH broken thrash | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 78 | Operator re-poll spam | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 79 | Watch duplicate processes | **CLOSED** | Single-owner enforcement is code/fixture proof plus current one-watch state. |
| 80 | Health mtime false 0h | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 81 | GCS_STATUS fossil date | **CLOSED** | Status remains RUNTIME_PARTIAL_E2E_UNPROVEN. |
| 82 | deploy not after every edit | **CLOSED** | Later PS1 changes must pass the same admission again. |
| 83 | soft_poll force scp thrash | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 84 | mac_backup not run | **CLOSED** | Backup success is custody, not scheduled/product green. |
| 85 | Logs unbounded growth | **CLOSED** | Retention is scoped to VibeCast logs. |

## G. Backup / restore / multi-agent (86–95)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 86 | Disk loss no code restore | **CLOSED** | This is scoped disaster-recovery custody, not a full-vault backup claim. |
| 87 | KEEP media only local | **CLOSED** | Local Google Drive sync-surface proof; not authenticated provider API readback. |
| 88 | Returns working set lost | **CLOSED** | Raw masters remain excluded by policy and re-harvestable. |
| 89 | LaunchAgent not in backup | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 90 | Restore drill never run | **CLOSED** | Does not cover remote-less authority additions. |
| 91 | Other GCS agents collide | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 92 | Secrets in GitHub | **CLOSED** | Secret scan is redacted and scoped to the authority history/current WoW tree. |
| 93 | Portable doc repo stale | **CLOSED** | Portable docs exclude binary media and secrets; they are not source authority. |
| 94 | Receipts not mirrored | **CLOSED** | Closure is bounded to the cited control; it is not same-day Branch-A E2E or PRODUCT_GREEN. |
| 95 | Gauntlet not re-runnable | **CLOSED** | Thirty-eight checks cannot stand in for 100 row-specific proofs. |

## H. Future-proof / decades (96–100)

| # | Bug | Status | Note |
|---|-----|--------|------|
| 96 | No schema versions | **CLOSED** | External/legacy exemptions remain explicit rather than inferred green. |
| 97 | Hardcoded host IP only | **CLOSED** | The configured IP may change only through the versioned config/readback path. |
| 98 | No plugin surface for new engines | **CLOSED** | Extensions are fail-closed and cannot create media, arm, publish, or write providers. |
| 99 | Twin games (TDE/TFE) not portable | **CLOSED** | Portability is proven at the implementation/contract layer; no TDE/TFE media or product-green claim is made. |
| 100 | AI upgrade path unclear | **CLOSED** | AI advice cannot create evidence, media, ARM state, or provider effects. |

---

## Score snapshot (canonical)

- **CLOSED:** 89
- **PARTIAL:** 7
- **OPEN:** 4
- **Verdict:** `RUNTIME_PARTIAL_E2E_UNPROVEN`
- **First boundary:** `HUMAN_AUDIO_AND_REAL_CAPTURE_REQUIRED`

The executable gauntlet is supporting evidence; this 100-row ledger is the complete risk crosswalk.

## Patches shipped with this gauntlet wave

1. Proved residual-day idempotency without re-harvest, media creation, or false same-day promotion
2. Deployed and hash-read-back all 24 Windows-facing scripts/cards through the spaced product path
3. Configured guarded AutoHideUI Gather/Cinematic profiles offline with original-file backup and exact readback
4. Proved Auto Session-End dispatch and no-candidate enhancement refusal with isolated fixtures
5. Installed and proved the durable loopback review-feedback LaunchAgent and atomic concurrency contract
6. Annotated the real 08-09 manifest with source-master marker windows without cross-master inference
7. Validated fail-closed TDE/TFE portable plans and the suggestion-only local AI extension
8. Backed up the exact authority branch, executable extensions, receipts, and non-video Returns working set
9. Pushed and read back both the public VibeCast sample and refreshed wow-explorer-portable main
10. Ran the full history/current-tree secret scan and the 57-check executable gauntlet at final authority HEAD

## Remaining product/human boundaries (11)

11. **PARTIAL — agent_prove labeled as product e2e:** Structural/idempotent checks cannot promote Branch A.
44. **PARTIAL — Watch never harvests:** Needs one same-day READY→harvest pass.
46. **OPEN — No record_start first row:** Agent markers cannot replace a human capture row.
48. **OPEN — agent labels only in SESSION:** agent_assigned/agent_* is not semantic or human correctness.
50. **OPEN — Mic muted kills night:** Requires real media/meter/playback.
51. **OPEN — Game audio silent masters:** BAN false AUDIO_GREEN.
54. **PARTIAL — Cinematic UI not set:** A real in-game visual/orbit still must prove the cinematic result.
55. **PARTIAL — Titan zone empty:** The unproven remainder stays open; no structural or agent-assigned promotion.
56. **PARTIAL — OBS Advanced mode breaks record:** The unproven remainder stays open; no structural or agent-assigned promotion.
57. **PARTIAL — Stream Deck multi-act unwired:** The running Stream Deck application's button bindings and a real human press remain unproven.
60. **PARTIAL — Chapter-only markers as product:** The unproven remainder stays open; no structural or agent-assigned promotion.

Canonical receipt: `/Users/kyle/Library/Application Support/UAH/butler/control-plane/receipts/gcs-vibecast/GAP_100_CROSSWALK_LATEST.json`

## Related

[[PRODUCT_SYSTEM_SPEC]] · [[VIBECAST_WRITE_FENCE]] · [[RESTORE_AND_BACKUP]] · [[ROADMAP_P0_P2_TOP10]] · [[../00-Index/GCS_CITADEL]]
