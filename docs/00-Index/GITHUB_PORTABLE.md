---
type: backup-doctrine
status: active
created: 2026-08-06
updated: 2026-08-06
area: WoW portable GitHub mirror
---

# GitHub portable pack — WoW Explorer return series

**Problem:** Vault root `kyles_corner` is an **Obsidian vault**, not a git repo (and should stay that way — personal notes, `.obsidian`, bulk outputs).  
**Solution:** A **portable mirror** of the *recording + cast + story* docs only, with a clean git tree, private GitHub remote for restore later.

| Item                       | Path                                                         |                                    |                   |
| -------------------------- | ------------------------------------------------------------ | ---------------------------------- | ----------------- |
| **Export tree (git root)** | `Reference/wow-explorer-portable/`                           |                                    |                   |
| **Sync script**            | `Reference/wow-explorer-portable/scripts/sync_from_vault.sh` |                                    |                   |
| **GitHub (private)**       | https://github.com/kyledempster7/wow-explorer-portable       |                                    |                   |
| **Human pin in vault**     | [[README                                                     | Games/WoW/00-Index]] · [[SYSTEM_DISK_MAP | SYSTEM_DISK_MAP]] |

**First ship:** 2026-08-06 · clean `main` · **117 files** · no secrets · re-sync via script after vault edits.

---

## What ships (allowlist)

| Included | Why |
|----------|-----|
| `Games/WoW/00-Index` key maps | pin + disk map + this note |
| `Games/WoW/04-Story-and-Capture/**` | series, packs, lore, rails, week plan |
| `Games/WoW/01-Play/**` (play cards) | duo / SL packs |
| `Games/WoW/Characters/**` | cast + play sheet |
| `Games/WoW/community-surface/**` | packs + wishlist + EP bridge |
| `Games/WoW/toons/**` CHARACTER/EVIDENCE + README/COVERAGE/handoffs | ops mirror (no secrets) |
| `Games/WoW/WOW_INDEX.md` + `Games/WoW/README.md` | tools doors |
| Select Research prose | Character Notes README + cards, proff mesh, Stream Deck, Capture-to-Publish, Hub (no raw secrets) |

## What never ships

| Excluded | Why |
|----------|-----|
| `wow-roster-tracker/.env` · any API keys | secrets once doctrine |
| `wow-economy-readout/output/**` | bulk auto noise (~thousands of files) |
| `.obsidian/` · Daily Notes · Inbox | vault personal / noise |
| Plugin packs · binary | not series docs |

---

## Agent / Kyle restore later

```bash
# clone private repo (name set at first push)
git clone git@github.com:kyledempster7/<repo>.git
# or: open vault and re-sync FROM portable INTO vault paths (manual) —
# portable is backup SoT for *these docs*, vault remains live edit surface
```

**Live edit surface stays the vault.** After vault edits: re-run sync script → commit → push.

---

## Status

See portable `README.md` after first sync for remote URL + last commit.

**Footer:** [[README|Pin]] · [[SYSTEM_DISK_MAP|Disk map]] · [[../04-Story-and-Capture/YouTube/WORKBOOK|Tour]] · [[GITHUB_PORTABLE|GitHub]]
