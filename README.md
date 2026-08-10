# VibeCast — WoW capture → taste → package

**Public product surface** for the GCS **VibeCast** wing (brand **TWE / The WoW Explorer**).  
Dual-machine pipeline: **Windows captures**, **Mac tastes**, **human KEEP** decides what survives.

> This repository is the **shareable program**: scripts, doctrine, fixtures, and a **real KEEP sample**.  
> Multi‑GB masters and private Returns trees stay on the operator machines — not invented, not auto-posted.

## What it is

VibeCast turns real play sessions into reviewable B-roll / social-ready packages:

1. **Capture** — OBS dual-track (game + mic) → masters on Windows `D:\WoW B-Roll Storage`
2. **Export** — `Session-End-Ship.ps1` → day `candidates/*.mp4` + markers
3. **Harvest** — Mac `post_play_harvest.sh` / soft-poll when **today** is ready
4. **Taste** — human review-pack → `human_verdicts` **KEEP / REJECT / REVIEW**
5. **Package** — local `product_ready` package, Moments archive, optional social arm

## Laws (non-negotiable)

| Law | Meaning |
|-----|---------|
| **No invent FOOTAGE** | Never fabricate candidates, masters, or zones |
| **No silent publish** | Social stays `NOT_ARMED` until explicit go |
| **Human KEEP** | Only KEEP media enters Moments / public samples |
| **ARM default deny** | `kyle_go: false` until arm receipt exists |

## Public KEEP sample (real media)

Day **2026-08-09** human KEEP (`c` + `c-pride-15s-start`):

| File | Role |
|------|------|
| [`samples/keep-2026-08-09/c-pride-15s-start-vertical.mp4`](samples/keep-2026-08-09/c-pride-15s-start-vertical.mp4) | KEEP pride vertical (~15s) |
| [`samples/keep-2026-08-09/still-WoWScrnShot.jpg`](samples/keep-2026-08-09/still-WoWScrnShot.jpg) | Session still |
| [`samples/keep-2026-08-09/PRODUCT_PACKAGE.json`](samples/keep-2026-08-09/PRODUCT_PACKAGE.json) | `product_ready=true`, `status=NOT_ARMED` |

See also **[docs/PUBLIC_READY.md](docs/PUBLIC_READY.md)** — one-pager for strangers.

## Quick start (stranger / fork)

```bash
git clone https://github.com/kyledempster7/gcs-vibecast-wow-capture.git
cd gcs-vibecast-wow-capture
# Read doctrine
open docs/PUBLIC_READY.md   # or: less docs/PUBLIC_READY.md
# Inspect real KEEP sample (no network)
ls -la samples/keep-2026-08-09/
python3 -c "import json; print(json.load(open('samples/keep-2026-08-09/PRODUCT_PACKAGE.json'))['product_ready'])"
# Optional: assert write fence helper if you wire full vault paths
python3 scripts/assert_vibecast_write_fence.py  # may no-op outside Kyle vault
```

### Operator machines (full loop)

| Machine | Role | Path |
|---------|------|------|
| Windows | Capture + export | `D:\WoW B-Roll Storage\` + `_scripts\` |
| Mac | Harvest + taste + package | `~/Movies/WoW-Broll-Workflow/` · vault `Games/WoW/` |

Primary vault SoR (private): `Kyles_Vault/kyles_corner/Games/WoW/`  
Pipeline scripts live under `scripts/` here (mirrored from the vault).

Typical Mac harvest after a real export night:

```bash
bash scripts/post_play_harvest.sh            # or: soft_poll → harvest_if_ready
bash scripts/open_review_pack.sh YYYY-MM-DD  # human KEEP ≤60s
python3 scripts/archive_keep_to_moments.py --day-dir ~/Movies/WoW-Broll-Workflow/Returns/returner-daily-YYYY-MM-DD --drive
```

## Layout

```
scripts/          # Mac↔Windows pipeline (soft_poll, harvest, archive, fence, …)
samples/          # Public real KEEP media + PRODUCT_PACKAGE.json
fixtures/         # Join/export/chat calibration fixtures
docs/             # Product spine + PUBLIC_READY one-pager
launchagents/     # Optional macOS schedule stubs
```

## Social publish

**Not automatic.** Packages are `NOT_ARMED` until an on-disk arm / `kyle_go` receipt exists.  
Public proof without arm = **GitHub Release** of this repo (sample + docs), not a silent Zernio post.

## License / media

Code and docs: for Kyle’s public program surface.  
Sample clips: original capture from operator play — keep attribution if you re-share.

## Related

- GitHub: https://github.com/kyledempster7/gcs-vibecast-wow-capture  
- Brand: The WoW Explorer (TWE) · studio wing: VibeCast under GCS  
- Story frame: Explorers League order hall of alts (content layer; not invent FOOTAGE)
