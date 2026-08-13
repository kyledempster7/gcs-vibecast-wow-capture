---
type: production-fire
status: active
created: 2026-08-13
updated: 2026-08-13T02:55-04:00
system: GCS
audience: cold agents
---

# GCS production fire — if every rail went hot today

**This file is the 10× of the 2026-08-13 stitch.** Not a migrate order. Not a remint.  
**Walk order:** [[GCS_RESEARCH_INDEX]] → this file → [[GCS_LINK_MAP]] → live NOW files.  
**Swarm:** four read-only seats same night (live-vs-sample · factory/Armory/SPE · external DBs · gap registers).

**Verdict:** **HALF-LOOP.** The only rail that would actually fire is **HB-Zernio remainder** (already scheduled). Everything else is UNARMED, default-deny, isolated, or a lying board.

## If production fired right now

| Rail | What happens | Proof |
|------|----------------|-------|
| **HB-Zernio TWE remainder** | **Would try to publish** today's 10:00 / 18:00 / 20:00 ET IDs. Do not remint. | `delivery-independence/HB_ZERNIO_NOW.json` |
| **TikTok 20:00 carousel** | **Likely miss.** Token last GET expires **16:02 ET** — before 20:00 ET slot. Aug-12 carousel-02 TT still consumed/denied. | `HB_ZERNIO_NOW.md` |
| **Saturday factory 08-15 / week 34** | **Does not fire.** `UNARMED`, provider_* false, visual HUMAN_PENDING, Substack access revoked. Front-door LaunchAgent never ran. | `~/.codex/saturday-fleet-readiness/CURRENT.json` |
| **Armory / Returner Daily** | **Does not post.** 08-09 + 08-12 `armed:false` `kyle_go:false`. No 08-13 play folder. | day `ARM_STATE.json` |
| **SPE Class A** | **Nothing to land.** 0/5 VPS packets. SPE-X-001 freeze. Money order still A first. | `LOOP_GAPS.md` |
| **SPE Class D TWE** | Local package only. No `draft_id`. Plist not loaded. Inject illegal before 15:00 ET. | `auto_blogger/twe/CLASS_D_POINTER.md` |
| **SPE letter → social** | Dry seeds only. No Zernio POST. | `SPE_HB_SEED_INDEX.json` `dry:true` |
| **Discord** | Invite page **200**. Guild / weekly nights / waitlist **scaffold**. Stay CTA Thu/Fri/Sun in isolated worktree. | `community.yaml` + League spine |
| **CareSix roster** | `latest.md` stamped live 08-13 02:44. `latest.json` still SSR 08-11. Windows SCH **unproven** (no SSH). | tracker `output/` + reachability |
| **Windows harvest** | **Cannot claim SCH Ready.** 06:49Z `ONLINE_TS` (last_seen 08-12 12:44Z). 06:51Z `OFFLINE` (`tailscale not on PATH`). Both: SSH null. | `WINDOWS_REACHABILITY_*` |
| **Vault layout / “one tree”** | **Frozen.** CLASSIFY_ONLY. Mass move fails. | `VAULT_LAYOUT_EXECUTION_FREEZE.json` |
| **8-slot operator mix** | **Not loaded.** Alarm remains 2 B-roll + 1 carousel. | `TWE_DAILY_EXPECTED.json` |

## What is not linked (dual SoT / missing wire)

1. **Sample `~/src/gcs-vibecast-wow-capture` ≠ live scripts.** LaunchAgents run vault `wow-roster-tracker/scripts/`. Filenames+bytes match **working tree** tonight (168 files, 0 hash drift) — **not** the claimed authority worktree.  
2. **`media_roots.json` authority_worktree** (`codex/gcs-vibecast-unattended-custody-20260811`) is a **second checkout**. Missing `harvest_completeness.py`; has Windows-return scripts live does not. Agents rooted there run the wrong tree.  
3. **Vault git** `kyles_corner` is local-only (`gcs/reliability-20260812`, dirty scripts, **no remotes**). Sample is the only GitHub copy. `GITHUB_PORTABLE.md` still says the vault is not a git repo — **stale**.  
4. **Factory catalog** `projects/social media tools` ≠ **engine** `projects/.worktrees/saturday-fleet-engine-authority/social media tools`.  
5. **`community.yaml`** lives in `projects/.worktrees/gcs-review-community-20260813/` — not in the Saturday engine adapters path the spine names as SoT. Stay-CTA code is a third worktree.  
6. **`TWE_SERIES_CONTRACT.discord_live: false`** vs spine/packet/community.yaml **invite live**. Guild/events still scaffold. Read both flags.  
7. **LIVE_WEEK / GCS_TWE_NOW** still show carousel 03/04/05 `zernio_id: null`. HB_ZERNIO_NOW already holds those remainder IDs.  
8. **Armory `ARM_STATE`** vs **08-09 `ZERNIO_LIVE.json` `kyle_go: true`** — two go stories. Default-deny wins unless Kyle hashes a package.  
9. **GCS_STATUS** Factory 🟢 / Returner Daily `2026-08-13` vs UNARMED + no 08-13 day root. Pipeline health 🟢 Windows while verdict is OFFLINE/`ONLINE_TS`.  
10. **SPE Class D** isolated from VibeCast. **n8n / Notion** are not GCS product DBs. Local sqlite (outbox, saturday ledger, editorial_claims) are files, not a shared engine.

## Gaps / errors that look like product

| Error | Class |
|-------|--------|
| False-green boards (file present = 🟢) | Honesty |
| `latest.md` live vs `latest.json` SSR | Dual pointer |
| Aug-12 TikTok carousel-02 never created | Provider deny (do not retry consumed occurrence) |
| TikTok token expires before tonight's 20:00 | Clock |
| Saturday UNARMED vs remainder already scheduled | Dual story — both true |
| K1–K10 all OPEN | Kyle plate (do not fake) |
| AUDIO_GREEN still OPEN | Play-night proof |
| EPISODE_REGISTRY 7 outlines, `audio_path: null` | Field Notes not recorded |
| `auto_review_admitted` string `STALE_FALSE_THEN_REMAINDER_UPLOADS_SUCCEEDED` | Admit flag is not a boolean |
| `projects/gcs` committed on `fix/tpg-prosc-failclosed-20260811` | Wrong branch — do not push as TPG |

## Fastest stable finish line

Not more houses. Not a mass migrate. This order:

1. **Treat HB-Zernio remainder as the live fire.** Watch 10:00 / 18:00 / 20:00 ET. Do **not** remint listed IDs. Refresh TikTok **before 16:02 ET** or accept TT miss on the 20:00 carousel.  
2. **Leave Saturday UNARMED.** Front-door never ran. Visual still HUMAN_PENDING. Do not call Saturday `zernio_schedule_transport`.  
3. **Class A packets stay the money north star** (sibling rail). Do not inject TWE Class D before 15:00 ET or from this lane.  
4. **Reconcile stale factory ledgers** (LIVE_WEEK / GCS_TWE_NOW) to HB GET — docs only, no new posts.  
5. **Play night or SKIP.** No 08-13 masters → write `returner-daily/2026-08-13/SKIP.md`. Do not fake Returner Daily.  
6. **Stitch, don't clone.** Cold agents open `Claudes_Corner/projects/gcs/` then this file. New code → live vault scripts → selective sample sync. Vault freeze stays CLASSIFY_ONLY.

Somebody still = named series + one Field Notes + one door. Alarm stays **2 + 1**.

## Cold-agent bans (same as gameplan)

Publish · remint remainder IDs · retry consumed TT occurrence `29fe6e49…` · raise alarm to 8 · mass-copy vault → `projects/` · arm Saturday from a green board · invent League roster · close K* without proof · treat `~/src` as live SoT · treat authority worktree as live SoT.
