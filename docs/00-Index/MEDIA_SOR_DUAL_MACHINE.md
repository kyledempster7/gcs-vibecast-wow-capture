---
type: media-sor
status: active
created: 2026-08-09
updated: 2026-08-09
---

# Dual-machine media source of truth

**One rule:** raw masters live on **Windows**; vault holds **path lists + drafts + brand** — never a second master library on Mac.

## Registry

Machine JSON: `Games/WoW/00-Index/media_roots.json` (paths only).

| Role | SoR host | Path |
|------|----------|------|
| B-roll / OBS masters | Windows | `D:\WoW B-Roll Storage` |
| Untrusted alternate | Windows | `C:\Users\kyled\Videos\WoW B-Roll` (WinError 448 risk) |
| Memento / Screenshots | Windows | `C:\Program Files (x86)\World of Warcraft\_retail_\Screenshots` |
| Publish/review workspace | Windows | `C:\Users\kyled\Videos\WoW Publishing` |
| Capture path lists | Vault (both) | `Games/WoW/04-Story-and-Capture/capture-inbox/` |
| Memento path lists | Vault | `…/memento-inbox/` |
| Returner Daily drafts | Vault | `…/returner-daily/YYYY-MM-DD/` |
| Essay drop (render out) | Mac | `~/Movies/WoW-Essays/` (create if missing) |
| HyperFrames brand kit | Vault | `Games/WoW/04-Story-and-Capture/hyperframes-brand-kit/` |
| Roster / scorecard | Vault + Windows tracker | `wow-roster-tracker/` · `Characters/scorecards/` |

## Sync rules

1. **Never** claim Mac has the only copy of a master.  
2. Agents list paths into vault; they do not bulk-copy multi-GB into Obsidian.  
3. Optional Drive archive stays outside vault (Capture-to-Publish).  
4. After Windows write, Obsidian Sync moves **markdown lists** — not raw video.

## Jump desktop

When GUI needed (OBS audio, Deck): use Kyle’s jump desktop · see [[JUMP_DESKTOP_PLAYBOOK]]. SSH remains default for scripts.

Related: [[CONNECTIVITY_BOARD]] · [[SCHEDULERS_AND_AUTOMATION_BOARD]] · [[KYLE_OS]]
