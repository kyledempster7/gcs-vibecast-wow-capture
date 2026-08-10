# Vibe-podcast / audio-essay scaffold

**Product:** listen-first Explorer essays (house-friendly).  
**Sibling:** vibe-cast (muddy play+talk) — same nights can feed both.  
**Not:** live Twitch requirement · Class-P letters.

**Human:** [[../../../00-Index/VIBECAST_OS|VibeCast OS]] · clean mode topics [[../FLIGHTPATH_VO_TOPICS_EP01|flight path]]  
**Agents:** `log_vibe_session.py --mode clean` creates `show-notes/YYYY-MM-DD-vibe.md`

## Drop folders

| Role | Path |
|------|------|
| Mac renders / masters out | `~/Movies/WoW-Essays/` |
| Vault show notes drafts | this folder `show-notes/` |
| EP packs | parent `../EP*_*.md` |
| Vibe sessions | `../../vibe-sessions/` |
| Episode registry | `../../EPISODE_REGISTRY.json` |

## When Kyle vibes clean

1. Flight topics only (no wiki spiral)  
2. Save audio somewhere obvious  
3. Logout  
4. Agents attach **real** `audio_path` to registry only when file exists  
5. Fill show-notes beats from real talk — blanks beat fakes  

## RSS

When first EP audio exists: generate feed from show-notes + audio URLs.  
Until then: **no fake feed items**.

## Show notes template

See `show-notes/_TEMPLATE.md` · daily vibe stubs: `show-notes/*-vibe.md`
