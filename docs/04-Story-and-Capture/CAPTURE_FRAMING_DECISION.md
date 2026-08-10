---
type: decision-record
status: open-recommendation
created: 2026-08-10
updated: 2026-08-10
product: VibeCast capture
area: Games/WoW
role: OBS_FRAMING_MASTERS_POLICY
---

# Capture framing — zoom-crop vs full-frame

**Problem (Kyle 2026-08-10):** Tight OBS crop feels great for social, but Titan/zone chrome is **not always in frame** (names flash, not sticky top-corner). Full-frame is better for **Twitch/stream** and for machine intelligence that wants HUD signals. Zoomed masters may cost less GPU; full-frame may cost more.

**Law:** do not thrash OBS mid-session · record decision · product crop can still be tight on Mac.

---

## Modes

| Mode | Masters (Windows) | Product (Mac) | Stream/Twitch | MI (Titan / names / zone) | Cost |
|------|-------------------|---------------|---------------|---------------------------|------|
| **A · Zoom-crop OBS** | Tight cinematic | Little extra crop | Viewers get zoomed FOV | Titan may leave frame | Often lighter |
| **B · Full-frame + Mac crop** | Full game UI | Crop for Returner Daily | Stream-ready full game | More HUD signals in masters | Heavier encode/disk |

---

## Recommendation (agents)

**Default recommend: Mode B** when dual-use (daily social **and** possible stream / better MI) matters.

Reasons:

1. Re-capture is expensive; crop is cheap later.  
2. Zone/name/Titan signals show up more often in full frame.  
3. Social can still deliver the “nice zoomed” look via Mac crop / pride vertical.  
4. Twitch path does not require a second master policy.

**Mode A** is OK temporary if GPU/disk forces it — label masters `framing=zoom_obs` so agents know OCR may miss Titan.

---

## Status

| Field | Value |
|-------|--------|
| **Kyle confirmed default** | **OPEN** (recommendation B until confirmed) |
| **Do not mid-session thrash** | Yes — finish herb night under current OBS setup |
| **When to set default** | Next calm Windows seat pass · document in packet + this file |

When confirmed, set:

```
framing_default: A | B
confirmed_utc: …
```

---

## Ops tags

| Tag | Meaning |
|-----|---------|
| `framing=full_master` | Mode B masters |
| `framing=zoom_obs` | Mode A masters |
| `product_crop=tight` | Mac social crop applied |

---

## Related

- [[TITANPANEL_AND_ADDON_BRIDGE]] via `00-Index` · zone OCR when bar visible  
- [[GATHERING_BROLL_MODE]] · minimap-only is UI policy, orthogonal to full vs crop  
- Windows packet: `WINDOWS_FUTURE_GOALS_PACKET.md`  
