> **Vault SoR (2026-07-15):** this folder is the production public roster tool.  
> Optional playground only: `C:\Users\kyled\Documents\tools\wow-public-tracker` — **do not dual-fill secrets**.  
> **Secrets once:** [[SECRETS_ONCE]] · `scripts/save_blizzard_env.ps1` · `scripts/check_blizzard_env.ps1`

# wow-roster-tracker (MVP)

Local, GitHub-ready multi-character **World of Warcraft** roster poller for Kyle’s Thrall (US) alts.

**Method (proven 2026-07-15):** Blizzard **public character Profile API** (client credentials) for summary / active spec / ilvl / equipment — with **Armory HTML SSR** (`characterProfileInitialState`) as a dry-run / emergency parse path. Raider.IO / Warcraft Logs stay empty for mid-level alts; do not depend on them.

## Path choice (this machine)

| Option | Status |
|--------|--------|
| `Claudes_Corner` | **Not present** on this Windows box (Mac-side engine vault) |
| `C:\Users\kyled\tools\` | Exists; pointer file only |
| **This repo** | `kyles_corner/Games/WoW/wow-roster-tracker/` — non-noise vault path Kyle can **move** later to Claudes_Corner or a pure code repo |

**Why vault:** file tools + session workspace are vault-bound. Code is isolated under `Games/WoW/` (not Inbox noise). To relocate: move the folder, update the Daily Note / Character Notes wire instructions if paths change.

Pointer for discoverability: `C:\Users\kyled\tools\wow-roster-tracker\README_POINTER.txt`

## Roster (Thrall US) — care suite

| Name | Notes |
|------|--------|
| **Crimsonpain** | Orc Unholy DK · main |
| **Crimsonagony** | BE Affliction Warlock · P1 |
| **Crimsonhavoc** | BE Vengeance DH · gather |
| **Crimsonrot** | Undead Shadow Priest · P2 (**in suite**) |
| **Crimsonblood** | BE Blood DK · tank school (**in suite**) |
| **Crimsonfaith** | HM Tauren Resto Druid |

**Not owned / not polled:** Crimson Rage (404 until created) · Crimsonlight · Earthen Ring parked — see `config/roster.yaml` → `not_in_roster`.

Config: [`config/roster.yaml`](config/roster.yaml)  
**Human suite board:** `Games/WoW/Characters/armory-suite/index.html` (regenerated every pull)

### Mac (no secrets) vs Windows (API)

```bash
# Public Armory SSR — all care six — no .env required
python3 scripts/fetch_roster.py --ssr --vault-sync

# Profile API — requires gitignored .env (Windows runner preferred)
python3 scripts/fetch_roster.py --live --vault-sync
# exit 2 = fail-closed missing secrets (do not invent keys)
```

---

## Operator runbook (vault)

**Foolproof PowerShell path** (create client → `.env` → `--live --vault-sync` → verify Source `sample`→`api` → exit `2` troubleshooting):  
`Kyle's Notes/Research/World of Warcraft/THRALL_ROSTER_TRACKER_RUNBOOK.md`  
Index: `Kyle's Notes/Research/World of Warcraft/Thrall Roster Tracker.md`

## Quick start

```powershell
cd "D:\KyleData\KnownFolders\Documents\kyles_corner\Games\WoW\wow-roster-tracker"

# No secrets required — print exact curls + write dry-run markdown/JSON
python scripts/fetch_roster.py --dry-run

# SAMPLE readout (vault-known public fields for Crimsonpain + vault-local partials)
python scripts/fetch_roster.py --write-sample

# Live pull + vault land (requires .env secrets — never invent them)
copy .env.example .env
# edit .env: BLIZZARD_CLIENT_ID=... and BLIZZARD_CLIENT_SECRET=...
python scripts/fetch_roster.py --live --vault-sync
echo "EXIT_CODE=$LASTEXITCODE"   # expect 0 when secrets valid; 2 = fail-closed
```

**Fail-closed:** `--live` without `BLIZZARD_CLIENT_ID` + `BLIZZARD_CLIENT_SECRET` **does not** call any API; it prints setup steps and exits **`2`**.

**Verify live Source flip:** after exit `0`, open `output/latest.md` (or vault-sync note). Roster **Source** cells and JSON `characters[].source` must show **`api`** (not `sample`). Provider tags: `api` | `ssr` | `local` | `sample`. **No RIO/WCL as SoT.**

Outputs land in `output/`:

- `roster_readout_YYYYMMDD_HHMMSS.md` — table per character  
- `roster_snapshot_YYYYMMDD_HHMMSS.json` — machine snapshot  
- `latest.md` / `latest.json` — most recent run  
- `output/samples/SAMPLE_*` — committed sample format (when you run `--write-sample`)

Live `output/*` is gitignored except `output/samples/`.

---

## 1) Create a Battle.net API client

1. Log into Battle.net → **API Access**: https://develop.battle.net/access/clients  
2. **Create client** — personal tooling; use `http://localhost` / “I do not have a service URL” if offered.  
3. Copy **Client ID** + **Client Secret** into a password manager — **never** into the vault or git.  
4. New clients can take up to ~15 minutes before auth works.  
5. Docs:  
   - Getting started: https://develop.battle.net/documentation/guides/getting-started  
   - Client credentials: https://develop.battle.net/documentation/guides/using-oauth/client-credentials-flow  
   - Profile APIs: https://develop.battle.net/documentation/world-of-warcraft/profile-apis  

Auth mode for this tool: **client credentials** (public character Profile APIs). No browser login loop.

## 2) Set environment variables

```powershell
# Option A — project .env (gitignored)
copy .env.example .env
# BLIZZARD_CLIENT_ID=...
# BLIZZARD_CLIENT_SECRET=...

# Option B — session env (PowerShell)
$env:BLIZZARD_CLIENT_ID = "your-id"
$env:BLIZZARD_CLIENT_SECRET = "your-secret"
```

Do **not** commit `.env`. `.gitignore` already excludes it.

## 3) Run once (live + vault)

```powershell
python scripts/fetch_roster.py --live --vault-sync
echo "EXIT_CODE=$LASTEXITCODE"
```

Fetches per character (US, `profile-us`, realm `thrall`):

| Endpoint | Fields |
|----------|--------|
| `GET .../character/{realm}/{name}` | level, race, class, active_spec, avg/equipped ilvl, guild, achievement_points |
| `GET .../equipment` | equipped slots |
| `GET .../specializations` | full specs payload |
| `GET .../collections/mounts` | **optional** (`--mounts`) — owned mount id/name list for Spooky evidence |

**Exit codes:** `0` ok · `1` token/HTTP/config error · **`2` fail-closed (no secrets, no API calls)**.

## 4) Run weekly

```powershell
# After secrets are in .env
cd "D:\KyleData\KnownFolders\Documents\kyles_corner\Games\WoW\wow-roster-tracker"
python scripts/fetch_roster.py --live --vault-sync
```

Optional Windows Task Scheduler: weekly trigger → same command → open vault `Thrall Roster Readouts/YYYY-MM-DD.md` or tool `output/latest.md`. Prefer first green live before scheduling.  
Operator runbook: vault `THRALL_ROSTER_TRACKER_RUNBOOK.md`.

## 5) Dry-run + Armory fixture (no secrets)

```powershell
python scripts/fetch_roster.py --dry-run
# Optional: save Armory HTML into fixtures/armory_crimsonpain.html then:
python scripts/fetch_roster.py --dry-run --parse-fixture
```

See [`fixtures/README.md`](fixtures/README.md).

## 5b) Optional mount evidence (Spooky join — extend, don’t fork)

**Design:** `Kyle's Notes/Research/World of Warcraft/SPOOKY_COLLECTIBLES_TRACKER_DESIGN.md` §2.2 / §4.  
**Scope:** Profile `collections/mounts` only. Evidence lane for later checklist join (`owned` + `evidence: api`). **Does not** auto-edit the vault Spooky checklist.

| Mode | Command | Behavior |
|------|---------|----------|
| Dry-run | `python scripts/fetch_roster.py --dry-run --mounts` | Print exact mounts URLs/curls; write `output/collections_mounts_*.json` with **URLs only** (empty `mounts[]`, no invent) |
| Live | `python scripts/fetch_roster.py --live --mounts` | Requires secrets; GET mounts per roster char; JSON list of `{id, name}` |
| Fail-closed | `--live --mounts` without secrets | Exit **`2`**, setup steps, **no** API calls, **no** invented ownership |
| Config | `config/roster.yaml` → `fetch_mounts: true` | Same as CLI `--mounts` (CLI still fine to pass explicitly) |

```powershell
# URLs only (safe, no secrets)
python scripts/fetch_roster.py --dry-run --mounts

# Live mount evidence (same .env as roster)
python scripts/fetch_roster.py --live --mounts
```

**Outputs (when `--mounts` / `fetch_mounts`):**

| File | Role |
|------|------|
| `output/collections_mounts_YYYYMMDD_HHMMSS.json` | Per-run evidence |
| `output/latest_mounts.json` | Pointer to newest |

Shape (live success, provider-neutral tags):

```json
{
  "mode": "live",
  "item_type": "mount",
  "evidence": "api",
  "source": "api",
  "provider": "profile-api",
  "characters": [
    {
      "character_id": "us:thrall:crimsonpain",
      "name": "Crimsonpain",
      "mount_count": 0,
      "mounts": [{"id": 123, "name": "Example Mount"}]
    }
  ]
}
```

**Join later (not this tool):** match `mounts[].id` / `name` → Spooky checklist `item_id` / `item_name` → propose `status: owned`, `evidence: api`. Human or separate dry-run patch only — **no auto-write of vault checklist here**.

**Not in human roster tables:** full mount lists stay out of Thrall Roster Readout sheets (noise). Roster = identity/ilvl/spec; mounts = evidence JSON.

## 6) Push to GitHub

```powershell
cd "D:\KyleData\KnownFolders\Documents\kyles_corner\Games\WoW\wow-roster-tracker"
git init
git add .
git status   # confirm .env is NOT staged
git commit -m "Initial MVP: multi-character WoW roster tracker (Thrall)"
# Create empty repo on GitHub, then:
git remote add origin https://github.com/<you>/wow-roster-tracker.git
git branch -M main
git push -u origin main
```

If you prefer the tool **outside** the Obsidian vault later, move this folder first, then `git init` there. Secrets stay local.

---

## Wire into kyles_corner

Canonical vault index:  
`Kyle's Notes/Research/World of Warcraft/Thrall Roster Tracker.md`  
Template: `Templates/Thrall Roster Readout.md`  
Landing folder: `Thrall Roster Readouts/`

### A) Auto vault-sync (preferred)

```powershell
python scripts/fetch_roster.py --live --vault-sync
# or without secrets:
python scripts/fetch_roster.py --write-sample --vault-sync
```

Writes a template-shaped note under:

`Kyle's Notes/Research/World of Warcraft/Thrall Roster Readouts/`

- Live: prefers `YYYY-MM-DD.md` (or `YYYY-MM-DD-tool-live.md` if the date file already exists)  
- Sample/dry-run: `YYYY-MM-DD-tool-sample.md` / `…-tool-dry-run.md` (won’t clobber the human seed)

Then append a row to the readout index table in **Thrall Roster Tracker**.

### B) Daily Note (session closeout)

1. Run pull (live or sample).  
2. Open `output/latest.md` **or** the vault-sync note.  
3. Paste the roster table into `Daily Notes/YYYY-MM-DD.md` under `## WoW roster pull`, **or** just link the readout.  
4. Link the project: `Games/WoW/wow-roster-tracker/`

### C) Character Notes (optional deep sheet)

`Kyle's Notes/Research/World of Warcraft/Character Notes/`

- Per character: update/create `Name-Thrall.md` (see `Crimsonpain-Thrall.md`).  
- Prefer **Thrall Roster Readouts/** for multi-character cadence; Character Notes for deep single-toon sheets.

### D) Manual copy helper

```powershell
$src = "D:\KyleData\KnownFolders\Documents\kyles_corner\Games\WoW\wow-roster-tracker\output\latest.md"
$dst = "D:\KyleData\KnownFolders\Documents\kyles_corner\Kyle's Notes\Research\World of Warcraft\Thrall Roster Readouts\$(Get-Date -Format yyyy-MM-dd)-manual.md"
Copy-Item $src $dst -Force
```

---

## Safety

| Rule | Behavior |
|------|----------|
| No secrets in git | `.env` gitignored; only `.env.example` committed |
| No API without secrets | `--live` / `--live --mounts` fails closed with setup steps |
| Default without flags | `--dry-run` (prints curls, writes dry-run artifacts) |
| Sample data labeled | `--write-sample` marks SAMPLE in markdown |
| Mount ownership | Never invented; dry-run = URLs only; live = Profile API evidence JSON only |
| Vault checklist | **Not** auto-edited by this tool (Spooky join is separate / human) |

## Layout

```
wow-roster-tracker/
  README.md
  .env.example
  .gitignore
  requirements.txt          # stdlib-only; empty install OK
  config/roster.yaml
  scripts/fetch_roster.py
  fixtures/                 # optional Armory HTML
  output/                   # live pulls (gitignored)
  output/samples/           # SAMPLE format (commit-friendly)
```

## Evidence / origin

- Feasibility + curls: `kyles_corner/Daily Notes/2026-07-15.md` § *WoW public character data*  
- Public Crimsonpain sheet: `Kyle's Notes/Research/World of Warcraft/Character Notes/Crimsonpain-Thrall.md`  
- Name spellings: `WoW Characters and Professions.md`
