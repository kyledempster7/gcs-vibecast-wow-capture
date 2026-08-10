# WINDOWS TICKET — Minimap-only gather B-roll (OPEN)

**When:** 2026-08-10  
**For:** Windows seat / Kyle while playing  
**Also on Mac vault:** `04-Story-and-Capture/GATHERING_BROLL_MODE.md`  
**Deploy target:** `D:\WoW B-Roll Storage\_scripts\MINIMAP_ONLY_GATHER_BROLL.md`

## Goal (Kyle)

Harvester **B-roll**: character runs the world gathering **herbs / ore** with the HUD reduced to **basically only the minimap** (node tracking OK if required to play).

That is the product look. **We do not have it yet.**

## Already good (do not undo)

- Bottom **action bars hide until hover** — beneficial. Keep.

## Not good enough yet

Edit Mode can turn a lot off, but these still tend to show:

- Objective / quest **tracker**
- **Chat**
- Quest objective chrome
- Some bar residue

So: **not minimap-only.**

## What “done” means

1. One **named** layout or one **Deck** press enters minimap-only gather.  
2. Kyle can run harvest routes without staring at chat/tracker.  
3. Exit restores normal play UI.  
4. Optional: marker `layer_c.gather_ui_on` / `off` for Mac harvest tags.

## How to figure it out (order)

1. **Edit Mode** — create layout `VibeCast Gather`: hide tracker, chat, bags, frames; leave **minimap**. Save. Note what refuses to hide.  
2. **Addon (likely):** **Auto Hide UI v1.2.13 only** — install **only if WoW is fully closed**. Configure hide-list so **minimap stays**.  
3. Wire Deck Layer C `gather_ui_on` / `gather_ui_off` when layout/addon is reliable.  
4. Do **not** install ElvUI for this. Do **not** invent FOOTAGE. Do **not** publish.

## Full clean fly (different product)

**Alt+Z** = hide **everything** (including minimap). Use for cinematic orbit, **not** for harvest navigation B-roll.

## Law

no invent FOOTAGE · no silent publish · human KEEP · ARM deny  
