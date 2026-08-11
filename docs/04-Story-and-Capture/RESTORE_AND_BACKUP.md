---
type: ops
status: active
created: 2026-08-10
updated: 2026-08-11
area: Games/WoW
role: DISK_LOSS_RESILIENCE
wing: VibeCast · GCS
---

# Restore & backup — GCS / VibeCast capture engine

**Fence:** [[VIBECAST_WRITE_FENCE]] — never restore into Factory paths.

## What is protected where

| Asset | Local SoR | Offsite |
|-------|-----------|---------|
| Scripts + fixtures | `Games/WoW/wow-roster-tracker/` | **GitHub** private `gcs-vibecast-wow-capture` |
| Product doctrine | `Games/WoW/04-Story-and-Capture/` + `00-Index` pins | GitHub `docs/` + Drive `backup-code/` |
| Receipts | `…/control-plane/receipts/wow/` | Drive `backup-code/receipts-wow/` |
| LaunchAgent | `~/Library/LaunchAgents/com.kyle.gcs.wow-soft-poll-harvest.plist` | Drive `backup-code/launchagents/` + repo `launchagents/` |
| KEEP media | `Movies/…/Moments-Library/` | Drive `archive-broll/<day>/` |
| Moments indexes | CATALOG + KEEP_ONLY | Drive `backup-code/moments-index/` |
| Day working Returns | `Movies/…/Returns/returner-daily-*` | Drive `backup-code/returns-working-set/` metadata/review mirror; video re-harvests from masters |
| Masters | `D:\WoW B-Roll Storage\` (Windows) | Windows PC / separate backup |

**Never in GitHub:** multi‑GB masters, full Returns trees, secrets.

## One-command Mac backup (M1)

```bash
bash ~/Kyles_Vault/kyles_corner/Games/WoW/wow-roster-tracker/scripts/mac_backup_vibecast.sh
```

Pushes GitHub + rsyncs Drive backup-code (scripts, extensions, docs pins,
receipts, plist, moments-index, and the non-video Returns working set).

## ASAP restore (stolen / dead Mac) — target ≤30 min to harvest-capable

```bash
# 1) Code from GitHub
gh repo clone kyledempster7/gcs-vibecast-wow-capture ~/src/gcs-vibecast-wow-capture
# or: git -C ~/src/gcs-vibecast-wow-capture pull --ff-only

rsync -a ~/src/gcs-vibecast-wow-capture/scripts/ \
  ~/Kyles_Vault/kyles_corner/Games/WoW/wow-roster-tracker/scripts/

# 2) Doctrine (if vault empty / new machine)
rsync -a ~/src/gcs-vibecast-wow-capture/docs/04-Story-and-Capture/ \
  ~/Kyles_Vault/kyles_corner/Games/WoW/04-Story-and-Capture/
rsync -a ~/src/gcs-vibecast-wow-capture/docs/00-Index/ \
  ~/Kyles_Vault/kyles_corner/Games/WoW/00-Index/ 2>/dev/null || true

# 3) LaunchAgent
bash ~/Kyles_Vault/kyles_corner/Games/WoW/wow-roster-tracker/scripts/install_mac_soft_poll_launchagent.sh

# 4) KEEP media from Drive (Google Drive path may vary)
# rsync -a ".../GCS-VibeCast-Offload/archive-broll/" \
#   ~/Movies/WoW-Broll-Workflow/Moments-Library/
python3 ~/Kyles_Vault/kyles_corner/Games/WoW/wow-roster-tracker/scripts/catalog_query.py --rebuild

# 5) Prove
python3 …/assert_vibecast_write_fence.py
bash …/soft_poll_windows.sh
python3 …/gcs_pipeline_health.py
# Open KYLE_OS — play door lives again
```

## After KEEP night

```bash
python3 wow-roster-tracker/scripts/archive_keep_to_moments.py \
  --day-dir ~/Movies/WoW-Broll-Workflow/Returns/returner-daily-YYYY-MM-DD \
  --zone <zone_slug> --drive
bash wow-roster-tracker/scripts/mac_backup_vibecast.sh
```

## Google Drive layout

Root: `My Drive/GCS-VibeCast-Offload/`

| Folder | Content |
|--------|---------|
| `backup-code/gcs-vibecast-wow-capture/` | scripts + docs mirror |
| `backup-code/receipts-wow/` | control-plane receipts |
| `backup-code/moments-index/` | CATALOG / KEEP_ONLY |
| `backup-code/launchagents/` | soft-poll plist |
| `backup-code/00-Index-pins/` | citadel doors |
| `backup-code/returns-working-set/` | Returns JSON/MD/HTML and review thumbnails; no masters |
| `archive-broll/<day>/` | KEEP clips + ARCHIVE.json |

## GitHub

Private: `kyledempster7/gcs-vibecast-wow-capture`  
Docs-only series mirror (separate): `wow-explorer-portable` — see [[../00-Index/GITHUB_PORTABLE]]

## Laws

no invent FOOTAGE · no silent publish · human KEEP · ARM deny until go · no Factory path writes  
