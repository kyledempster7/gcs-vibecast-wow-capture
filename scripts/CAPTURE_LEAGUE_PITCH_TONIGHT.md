# Capture tonight — Explorer’s League pitch B-roll (zero thought)

**product_id:** `twe_explorers_league_community_pitch_v1`  
**Vault pack:** `04-Story-and-Capture/social/EXPLORERS_LEAGUE_PITCH_BROLL_PACK.md`  
**Laws:** fun first · no invent · Session-End after stop · ARM deny  

Deployed to: `D:\WoW B-Roll Storage\_scripts\CAPTURE_LEAGUE_PITCH_TONIGHT.md`

---

## Goal tonight (pick 3–5 shots)

You already play for fun. When something looks like pitch fuel, linger 5–15s.

| Priority | shot_id | What to film |
|----------|---------|--------------|
| **P0** | `pitch.hub_thrall` | Orgrimmar / Horde hub establish (fly in, stand, turn) |
| **P0** | `pitch.craft_cast` or `pitch.prof_panel` | Crafting fair tease — craft cast or open professions |
| **P0** | `pitch.gather_to_craft` | Herb/mine → bank/craft (you’re already herbing) |
| **P1** | `pitch.ah_browse` | AH mats browse (short) |
| **P1** | `pitch.cast_lineup` | Character select still (optional) |
| **P1** | `pitch.flight_soft` | Calm flight for welcome bed |
| Skip unless real | `pitch.dungeon_*` | Only if you actually dungeon |

**Flash text** is Mac/edit later (`league-pitch-flash` cards). You just capture world.

---

## OBS (required — path is already product)

Probe says profile points at `D:\WoW B-Roll Storage` + dual tracks.  
**You still must press OBS Record** (red button). Deck markers alone do not create masters.

## Deck while recording

| When | Press |
|------|--------|
| Start | OBS **Record** + Deck `record_start` |
| 10s dual audio | talk + game sound |
| Beauty | `broll_enter` … `rotate` … `broll_exit` |
| Funny / talk | `funny_moment` or `talk_peak` |
| End | stop OBS · full logout |

---

## After stop (required)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\WoW B-Roll Storage\_scripts\Session-End-Ship.ps1"
```

Mac golden/watch harvests when `ready_today`. You only KEEP later.

---

## Do not claim on mic (unless true)

- “Guild is live” / member counts  
- Fake Discord invite  
- “Fair is this Saturday” without real plan  

Soft OK: “Explorer’s League energy · Thrall · Horde · welcome back.”

---

## One-liner

**Bank hub + craft/gather beauty for the League pitch pack. Session-End. Walk away.**
