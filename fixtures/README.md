# Fixtures

Optional saved Armory HTML for dry-run parse mode (no API secrets).

## How to capture

1. Open the character Armory page, e.g.  
   `https://worldofwarcraft.blizzard.com/en-us/character/us/thrall/crimsonpain`
2. Save the full HTML (Ctrl+S → Webpage, HTML only).
3. Place as `fixtures/armory_<name_lower>.html`  
   Example: `fixtures/armory_crimsonpain.html`
4. Run:

```bash
python scripts/fetch_roster.py --dry-run --parse-fixture
```

The parser looks for embedded `characterProfileInitialState` JSON (SSR), not React DOM text.
See Daily Notes 2026-07-15 feasibility report for background.
