#!/usr/bin/env python3
"""
Agent-assisted walkthrough for Kyle.

Modes:
  --print          Print full friendly script (default) for agent to read aloud / show
  --path PATH      audio|vibe|clean|deck|housing|publish|overview
  --checklist      Refresh KYLE_HELP_NEEDED.md from JSON
  --mark ID STATUS Mark help item OPEN|CLOSED (agent after Kyle proof)
  --ask            Interactive terminal prompts (when Kyle is at the Mac with agent)
  --tomorrow       Print preflight + audio + vibe only (tomorrow session path)
  --housing        Alias for --path housing (Y1 pocket + Layer A optional)

Does not publish. Does not invent media paths.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
INDEX = WOW / "00-Index"
HELP_JSON = INDEX / "KYLE_HELP_NEEDED.json"
HELP_MD = INDEX / "KYLE_HELP_NEEDED.md"
SESSION_LOG = INDEX / "walkthrough-sessions"


PATHS = {
    "overview": [
        ("O1", "Big picture", "GCS is one studio. VibeCast is the wing for your play nights. Factory is Saturday carousels. You mostly play and sometimes say go."),
        ("O2", "What you open", "Tomorrow: TOMORROW_SESSION. Play: SIMPLE_START. Help list: KYLE_HELP_NEEDED."),
        ("O3", "What you never open on play night", "Factory trees, outbox SQLite, SCH numbers, Titan research."),
    ],
    "tomorrow": [
        ("T0", "Open", "Open TOMORROW_SESSION (or phone sheet). Only one note."),
        ("T1", "Preflight", "PREFLIGHT_WINDOWS: headphones, OBS Muddy/Essay, save folder D:\\WoW B-Roll Storage preferred."),
        ("T2", "Audio (optional gold)", "10s game audio test. Green stamp or voice-only OK."),
        ("T3", "Mode", "Default vibe-cast muddy: play for real, talk when it hits."),
        ("T4", "Record", "Record if you want content. Stop while fun."),
        ("T5", "Close", "Save · full logout · optional one-liner muddy Xm · game audio yes/no."),
        ("T6", "Stop", "Do not edit or publish. Agents harvest after."),
    ],

    "audio": [
        ("K1a", "Windows + OBS", "Open your usual WoW Hybrid scene."),
        ("K1b", "Meters", "Talk — mic moves. Make WoW sound — game/desktop meter moves."),
        ("K1c", "10 second test", "Record 10s, play back. Hear game audio?"),
        ("K1d", "Stamp", "If yes: tell agent 'game audio green' and path. If no: voice-only is OK tonight."),
    ],
    "vibe": [
        ("K2a", "Mode", "Pick vibe-cast (muddy): play for real, talk when it hits."),
        ("K2b", "Gate", "Mic OK. Game sound or voice-only."),
        ("K2c", "Record", "Start record if you want talk saved. Play. Stop while fun."),
        ("K2d", "Close", "Save file · full logout · optional one-liner to agent."),
    ],
    "clean": [
        ("K3a", "Mode", "Talk clean — flight path, not combat chaos."),
        ("K3b", "Topics", "Use FLIGHTPATH_VO_TOPICS_EP01 — glance only, no wiki."),
        ("K3c", "Record", "10–15 min talk · save · logout."),
        ("K3d", "Tell agent", "Path to file when you have it — they attach to registry."),
    ],
    "deck": [
        ("K4a", "Toon", "Log Crimsonagony on Windows."),
        ("K4b", "Checklist", "Open LAYER_A_POCKET or WOW_LAYER_A_VERIFY_CHECKLIST."),
        ("K4c", "Press", "Smoke five: hearth · mount · prof1 · prof2 · DE · mark OK / wrong / empty."),
        ("K4d", "Stop", "When Layer A is mostly OK — fill Locked binds · do not redesign ElvUI · housing page only after."),
    ],
    "housing": [
        ("H0", "Open", "Open HOUSING_Y1_POCKET (or HOUSING_DECK_SESSION). One path only."),
        ("H1", "Deck optional", "If Layer A unproven: keyboard + H is enough. Deck is travel later."),
        ("H2", "Buy", "Adams fence stacks → Zuldazar Mukra lights + small tent (+ brazier if WR)."),
        ("H3", "Place", "Posts/rails → green → tent → stop when readable from road."),
        ("H4", "House UI", "Key H opens Housing Dashboard. Save a layout before big moves."),
        ("H5", "Close", "Logout · optional one-liner housing Y1 · deck ok/no. No second room."),
    ],
    "publish": [
        ("K5a", "See draft", "Agent shows caption + media. You watch once."),
        ("K5b", "Decide", "Good → say go. Bad → say what's wrong. Never auto."),
        ("K5c", "Factory same rule", "Carousel weeks need your ACCEPT on the review sheet."),
    ],
}


def load_help() -> dict:
    return json.loads(HELP_JSON.read_text(encoding="utf-8"))


def write_help_md(data: dict) -> None:
    open_rows = []
    closed_rows = []
    for it in data["items"]:
        row = f"| **{it['id']}** | {it['title']} | {it['effort']} | {it['path']} | {it['status']} |"
        if it["status"] == "CLOSED":
            closed_rows.append(row)
        else:
            open_rows.append(row)
    body = f"""---
type: kyle-help-tally
status: active
updated: {datetime.now().strftime('%Y-%m-%d')}
audience: Kyle
---

# What only Kyle can unlock

**Machine source:** `KYLE_HELP_NEEDED.json`  
**Tutorial:** [[KYLE_WALKTHROUGH]] · say *“walk me through”* → `walk_with_kyle.py`  
**Tomorrow focus:** **K1 → K2** · open [[TOMORROW_SESSION]] first · `walk_with_kyle.py --tomorrow`

## Open tally

| ID | You do | Time | Path | Status |
|----|--------|------|------|--------|
{chr(10).join(open_rows) if open_rows else '| — | none open | | | |'}

## Closed

| ID | You do | Time | Path | Status |
|----|--------|------|------|--------|
{chr(10).join(closed_rows) if closed_rows else '| — | none yet | | | |'}

## Agents own (not listed)

CareSix · scorecards · inboxes · scaffolds · NOT_ARMED packages · SCH · factory *builds*

Related: [[GCS_CITADEL]] · [[SIMPLE_START]] · [[INTERPROMO_MAP]]
"""
    HELP_MD.write_text(body, encoding="utf-8")


def print_path(name: str) -> None:
    steps = PATHS.get(name)
    if not steps:
        print(f"Unknown path: {name}. Choose: {', '.join(PATHS)}", file=sys.stderr)
        return
    print(f"\n=== Walk-through path: {name} ===\n")
    print("Agent: read each step to Kyle. Wait for his answer before next.\n")
    for i, (sid, title, text) in enumerate(steps, 1):
        print(f"Step {i} [{sid}] — {title}")
        print(f"  {text}")
        print(f"  Agent asks: “Done, skip, or need help?”")
        print()


def print_full() -> None:
    print("# Kyle walk-through script (agent reads)\n")
    print("Start: open KYLE_WALKTHROUGH.md if he wants the full essay.")
    print("Or stay here and run one path at a time.\n")
    data = load_help()
    open_n = sum(1 for i in data["items"] if i["status"] != "CLOSED")
    print(f"Open Kyle items: {open_n}/{len(data['items'])}\n")
    print("Recommended order: overview → audio (if video) → vibe · or housing · or deck → publish when ready.\n")
    for name in ("overview", "audio", "vibe", "housing", "clean", "deck", "publish"):
        print_path(name)


def interactive(path: str) -> None:
    steps = PATHS.get(path) or PATHS["overview"]
    SESSION_LOG.mkdir(parents=True, exist_ok=True)
    log = SESSION_LOG / f"{datetime.now().strftime('%Y-%m-%d_%H%M%S')}_{path}.md"
    lines = [f"# Walk session {path}", f"started: {datetime.now().isoformat()}", ""]
    print(f"Interactive path={path}. Answers logged to {log}\n")
    for i, (sid, title, text) in enumerate(steps, 1):
        print(f"\n--- Step {i}: {title} ---")
        print(text)
        ans = input("Kyle / agent note (enter=ok, s=skip, q=quit): ").strip()
        if ans.lower() == "q":
            lines.append(f"- ABORT at {sid}")
            break
        status = "skip" if ans.lower() == "s" else ("ok" if not ans else ans)
        lines.append(f"- {sid}: {status}")
        print(f"  recorded: {status}")
    lines.append(f"\nended: {datetime.now().isoformat()}\n")
    log.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nSession saved: {log}")


def mark(item_id: str, status: str) -> int:
    status = status.upper()
    if status not in ("OPEN", "CLOSED"):
        print("status must be OPEN or CLOSED", file=sys.stderr)
        return 2
    data = load_help()
    found = False
    for it in data["items"]:
        if it["id"].upper() == item_id.upper():
            it["status"] = status
            if status == "CLOSED":
                it["closed_at"] = datetime.now().strftime("%Y-%m-%d")
            found = True
            break
    if not found:
        print(f"Unknown id {item_id}", file=sys.stderr)
        return 2
    data["updated"] = datetime.now().strftime("%Y-%m-%d")
    HELP_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")
    write_help_md(data)
    print(f"marked {item_id} -> {status}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Walk Kyle through GCS / VibeCast steps")
    ap.add_argument("--print", dest="do_print", action="store_true", help="Print script")
    ap.add_argument("--path", choices=list(PATHS.keys()), default=None)
    ap.add_argument("--checklist", action="store_true", help="Regenerate HELP md from JSON")
    ap.add_argument("--mark", nargs=2, metavar=("ID", "STATUS"), help="Mark K1 CLOSED etc")
    ap.add_argument("--ask", action="store_true", help="Interactive prompts")
    ap.add_argument("--tally", action="store_true", help="Print open tally only")
    ap.add_argument("--tomorrow", action="store_true", help="Tomorrow session path only")
    ap.add_argument("--housing", action="store_true", help="Housing Y1 walk path")
    args = ap.parse_args()

    if args.mark:
        return mark(args.mark[0], args.mark[1])
    if args.checklist:
        write_help_md(load_help())
        print(f"checklist -> {HELP_MD}")
        return 0
    if args.tally:
        data = load_help()
        for it in data["items"]:
            if it["status"] != "CLOSED":
                print(f"{it['id']}\t{it['status']}\t{it['title']}")
        return 0
    if args.tomorrow:
        print("Open note: Games/WoW/00-Index/TOMORROW_SESSION.md\n")
        print_path("tomorrow")
        return 0
    if args.housing:
        print("Open note: Games/WoW/00-Index/HOUSING_Y1_POCKET.md\n")
        print_path("housing")
        return 0
    if args.ask:
        interactive(args.path or "overview")
        return 0
    if args.path:
        print_path(args.path)
        return 0
    # default: full print
    print_full()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
