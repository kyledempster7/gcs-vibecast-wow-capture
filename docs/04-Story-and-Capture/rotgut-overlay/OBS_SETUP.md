# Rotgut L0 — OBS browser source setup

**File:** `index.html` in this folder  
**Doctrine:** `00-Index/ROTGUT_STREAM_COMPANION.md`  
**Status:** L0 only — no Twitch chat, no LLM, no secrets

## Add source

1. OBS → Sources → **Browser**
2. **Local file** → pick `index.html`  
   - Or Custom CSS blank; width **400** · height **420**
3. Check **Shutdown source when not visible** (optional)
4. Place bottom-left or bottom-right; keep over non-critical HUD

## URL params (refresh browser source after change)

| Param | Example | Effect |
|-------|---------|--------|
| `state` | `?state=talk` | idle · notice · talk · sulk · hype |
| `text` | `&text=hi%20chat` | force bubble line |
| `cycle` | `?cycle=1` | demo cycle states every 4s (test only) |

Local file URLs often ignore query — use **Local file** for idle art, or:

```bash
cd "$(dirname "$0")"
python3 -m http.server 8765
# Browser source URL: http://127.0.0.1:8765/index.html?state=idle
```

## Demo keyboard (browser window focused, not OBS)

| Key | State |
|-----|-------|
| 1 | idle |
| 2 | notice |
| 3 | talk |
| 4 | sulk |
| 5 | hype |
| Space | next state |

## Art swap

Replace CSS sphere with real Rotgut still/GIF **when Kyle supplies path** — do not invent assets.

## L1 (not enabled)

Chat keyword bot → sets `state` via local websocket later.  
Design pack: `00-Index/ROTGUT_L1_DESIGN_PACK.md` — **no live keys until Kyle says build**.
