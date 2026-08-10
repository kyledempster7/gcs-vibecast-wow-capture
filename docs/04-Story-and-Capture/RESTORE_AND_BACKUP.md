---
type: ops
status: active
created: 2026-08-10
area: Games/WoW
role: DISK_LOSS_RESILIENCE
---

# Restore & backup — GCS / VibeCast capture engine

## What is protected where

| Asset | Local SoR | Offsite |
|-------|-----------|---------|
| Scripts + fixtures | `Games/WoW/wow-roster-tracker/` | **GitHub** private mirror |
| Product doctrine | `Games/WoW/04-Story-and-Capture/` | GitHub + Drive `backup-code/` |
| Receipts | `…/control-plane/receipts/wow/` | Drive `backup-code/receipts-wow/` (optional) |
| KEEP media | `Movies/…/Moments-Library/` | Drive `archive-broll/<day>/` |
| Day working set | `Movies/…/Returns/returner-daily-*` | Optional; not required for code restore |
| Masters | `D:\WoW B-Roll Storage\` (Windows) | Windows backup separate |

**Never in GitHub:** multi‑GB masters, full Returns trees, secrets.

## GitHub

Private repo: `kyledempster7/gcs-vibecast-wow-capture` (created 2026-08-10).  
Contents: scripts, fixtures, product docs under 04-Story-and-Capture spine, README.

```bash
# cold restore (Mac)
gh repo clone kyledempster7/gcs-vibecast-wow-capture ~/src/gcs-vibecast-wow-capture
# copy scripts into vault tree if needed:
# rsync -a ~/src/gcs-vibecast-wow-capture/scripts/ \
#   ~/Kyles_Vault/kyles_corner/Games/WoW/wow-roster-tracker/scripts/
```

## Google Drive

Root: `My Drive/GCS-VibeCast-Offload/`

| Folder | Content |
|--------|---------|
| `backup-code/` | scripts + doctrine + fixtures + this RESTORE |
| `archive-broll/<day>/` | KEEP clips + ARCHIVE.json + MOMENTS.json |
| `<day>/` | optional stage offload from harvest |

## After KEEP night

```bash
python3 wow-roster-tracker/scripts/archive_keep_to_moments.py \
  --day-dir ~/Movies/WoW-Broll-Workflow/Returns/returner-daily-YYYY-MM-DD \
  --zone <zone_slug> --drive
```

## Laws

no invent FOOTAGE · no silent publish · human KEEP · ARM deny until go  
