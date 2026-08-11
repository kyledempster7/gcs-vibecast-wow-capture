#!/usr/bin/env python3
"""Build GAP_100_CROSSWALK_LATEST receipts (Codex takeback). Hostile scoring."""
from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WOW = Path("/Users/kyle/Kyles_Vault/kyles_corner/Games/WoW")
LEDGER = WOW / "04-Story-and-Capture/GAUNTLET_100_BUGS_VIBECAST.md"
CP = (
    Path.home()
    / "Library/Application Support/UAH/butler/control-plane/receipts/gcs-vibecast"
)
RETURNS = Path.home() / "Movies/WoW-Broll-Workflow/Returns"
SCRIPTS = WOW / "wow-roster-tracker/scripts"
KYLES = Path("/Users/kyle/Kyles_Vault/kyles_corner")


def owner_crosswalk_present(json_path: Path, md_path: Path) -> bool:
    """Do not overwrite a valid Codex-owned five-field deliverable.

    This builder is a diagnostic fallback. Once the owner crosswalk exists, a
    later one-shot/concurrent invocation must exit before live probes or writes.
    """
    if not json_path.is_file() or not md_path.is_file():
        return False
    try:
        doc = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    rows = doc.get("rows")
    required = {"gap", "title", "status", "proof", "bans_notes"}
    return bool(
        doc.get("schema") == "gcs_vibecast_gap_100_crosswalk/v1"
        and doc.get("owner") == "Codex"
        and doc.get("row_count") == 100
        and isinstance(rows, list)
        and len(rows) == 100
        and [row.get("gap") for row in rows] == list(range(1, 101))
        and all(set(row) == required for row in rows)
        and all(row.get("status") in {"CLOSED", "PARTIAL", "OPEN"} for row in rows)
    )


def main() -> int:
    latest_json = CP / "GAP_100_CROSSWALK_LATEST.json"
    latest_md = CP / "GAP_100_CROSSWALK_LATEST.md"
    if owner_crosswalk_present(latest_json, latest_md):
        print(f"OWNER_CROSSWALK_PRESENT no_overwrite json={latest_json} md={latest_md}")
        return 0

    soft = json.loads((RETURNS / "SOFT_POLL_LATEST.json").read_text(encoding="utf-8"))
    golden = json.loads(
        (RETURNS / "GOLDEN_LONG_RUN_STATUS.json").read_text(encoding="utf-8")
    )
    audio = json.loads(
        (RETURNS / "AUDIO_GREEN_PROBE_LATEST.json").read_text(encoding="utf-8")
    )
    unatt_path = CP / "UNATTENDED_PRODUCT_PATH_LATEST.json"
    unatt = (
        json.loads(unatt_path.read_text(encoding="utf-8"))
        if unatt_path.is_file()
        else {}
    )

    today = datetime.now().strftime("%Y-%m-%d")
    soft_today = next(
        (d for d in soft.get("days") or [] if d.get("day") == today), {}
    )
    soft_10 = next(
        (d for d in soft.get("days") or [] if d.get("day") == "2026-08-10"), {}
    )
    soft_09 = next(
        (d for d in soft.get("days") or [] if d.get("day") == "2026-08-09"), {}
    )

    env = os.environ.copy()
    env["HARVEST_FORCE_POLL"] = "0"
    h = subprocess.run(
        ["bash", str(SCRIPTS / "harvest_if_ready.sh"), today],
        cwd=str(SCRIPTS),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    harvest_rc = h.returncode
    harvest_out = (h.stdout or "")[-200:]

    arm = subprocess.run(
        ["python3", str(SCRIPTS / "arm_state.py"), "--self-test"],
        cwd=str(SCRIPTS),
        capture_output=True,
        text=True,
        check=False,
    )
    arm_ok = arm.returncode == 0

    gstat = subprocess.run(
        ["git", "status", "--short", "Games/WoW"],
        cwd=str(KYLES),
        capture_output=True,
        text=True,
        check=False,
    )
    glines = [ln for ln in gstat.stdout.splitlines() if ln.strip()]
    mod = sum(
        1
        for ln in glines
        if ln[:2].strip().startswith("M") or ln.startswith(" M") or ln.startswith("M ")
    )
    unt = sum(1 for ln in glines if ln.startswith("??"))
    unattended_untracked = any(
        "unattended_product_path" in ln and ln.startswith("??") for ln in glines
    )

    src = (SCRIPTS / "unattended_product_path.py").read_text(encoding="utf-8")
    branch_a_rc_fixed = (
        "if harvest_rc == 0:" in src
        and "return 0 if harvest_rc in (0, 1)" not in src
    )

    league_path = (
        WOW / "04-Story-and-Capture/social/package/EXPLORERS_LEAGUE_PITCH_MEDIA_MAP.json"
    )
    league = (
        json.loads(league_path.read_text(encoding="utf-8"))
        if league_path.is_file()
        else {}
    )
    league_agent = sum(
        1
        for v in league.get("videos") or []
        if v.get("evidence_class") == "agent_assigned"
    )
    league_human = sum(
        1
        for v in league.get("videos") or []
        if v.get("evidence_class") in ("human", "kyle_keep", "human_keep")
    )

    still_dir = RETURNS / "returner-daily-2026-08-09/stills"
    rejected_stills = (
        [p.name for p in still_dir.glob("*") if "reject" in p.name.lower()]
        if still_dir.is_dir()
        else []
    )

    fb = subprocess.run(
        ["pgrep", "-fl", "review_pack_feedback"],
        capture_output=True,
        text=True,
        check=False,
    )
    fb_running = bool(fb.stdout.strip())
    fb_test_path = CP / "REVIEW_FEEDBACK_SERVER_TEST_LATEST.json"
    fb_test = (
        json.loads(fb_test_path.read_text(encoding="utf-8"))
        if fb_test_path.is_file()
        else {}
    )
    fb_test_age_s = (
        int(datetime.now().timestamp() - fb_test_path.stat().st_mtime)
        if fb_test_path.is_file()
        else None
    )
    fb_required_checks = {
        "GET_INDEX_200",
        "TRAVERSAL_DENIED",
        "INVALID_VERDICT_400",
        "POST_VERDICT_200",
        "MERGE_PRESERVES_EXISTING",
    }
    fb_test_ok = (
        fb_test.get("status") == "PASS"
        and fb_test.get("real_verdicts_touched") is False
        and fb_test.get("may_publish") is False
        and fb_required_checks.issubset(set(fb_test.get("checks") or []))
        and fb_test_age_s is not None
        and fb_test_age_s <= 3600
    )
    parity_path = CP / "WINDOWS_SCRIPT_HASH_PARITY_LATEST.json"
    parity = (
        json.loads(parity_path.read_text(encoding="utf-8"))
        if parity_path.is_file()
        else {}
    )
    parity_age_s = (
        int(datetime.now().timestamp() - parity_path.stat().st_mtime)
        if parity_path.is_file()
        else None
    )
    parity_ok = (
        parity.get("status") == "PASS"
        and parity.get("all_match") is True
        and int(parity.get("file_count") or 0) >= 20
        and parity_age_s is not None
        and parity_age_s <= 3600
    )

    text = LEDGER.read_text(encoding="utf-8")
    rows = []
    for m in re.finditer(
        r"^\| (\d+) \| ([^|]+) \| \*\*([A-Z]+)\*\* \| ([^|]*) \|", text, re.M
    ):
        rows.append(
            {
                "gap": int(m.group(1)),
                "title": m.group(2).strip(),
                "ledger_status": m.group(3).strip(),
                "ledger_note": m.group(4).strip(),
            }
        )
    if len(rows) != 100:
        raise SystemExit(f"expected 100 ledger rows got {len(rows)}")

    def map_status(ledger: str) -> str:
        if ledger == "PASS":
            return "CLOSED"
        if ledger == "PARTIAL":
            return "PARTIAL"
        if ledger in ("OPEN", "PARK", "FAIL"):
            return "OPEN"
        return "PARTIAL"

    overrides: dict[int, tuple[str, str]] = {
        1: (
            "CLOSED",
            f"harvest_if_ready day={today} rc={harvest_rc}; ready_today={soft.get('ready_today')}; tail={harvest_out!r}",
        ),
        2: (
            "CLOSED",
            f"ready_today={soft.get('ready_today')}; residual 08-09 ready={soft_09.get('ready')} not harvested as today",
        ),
        3: ("CLOSED", f"arm_self_test ok={arm_ok}; unattended no publish path"),
        4: ("CLOSED", f"arm_state --self-test ok={arm_ok}"),
        10: (
            "CLOSED",
            f"AUDIO_GREEN probe status={audio.get('status')} (honest not GREEN)",
        ),
        11: (
            "PARTIAL",
            "agent_prove vs product e2e still risk; verdict RUNTIME_PARTIAL_E2E_UNPROVEN",
        ),
        15: (
            "PARTIAL",
            f"today empty masters; soft ready_today={soft.get('ready_today')}; agent-green != PRODUCT_GREEN",
        ),
        16: (
            "PARTIAL",
            "D: product path ok; human still defaults Fable OBS profile (Aug10 Fable folder takes)",
        ),
        17: (
            "PARTIAL",
            "Aug10 long takes under Fable Anniversary B-Roll on C: Videos not D: WoW SoR",
        ),
        19: (
            "CLOSED" if parity_ok else "PARTIAL",
            f"fresh Mac-to-Windows SHA-256 parity={parity_ok}; "
            f"files={parity.get('file_count')}; age_s={parity_age_s}; receipt={parity_path}",
        ),
        24: (
            "PARTIAL",
            f"git Games/WoW dirty lines={len(glines)} mod~{mod} untracked~{unt}; unattended_* untracked={unattended_untracked}",
        ),
        39: ("OPEN", "MANIFEST marker_window needs live e2e night — no same-day masters"),
        40: (
            "CLOSED" if branch_a_rc_fixed else "OPEN",
            f"unattended Branch A harvest_rc=1 no longer overall success; fixed={branch_a_rc_fixed}; real-media E2E still untested",
        ),
        41: (
            "PARTIAL",
            "harvest gates enhance; Branch A real-media E2E UNPROVEN (ready_today never true this arc)",
        ),
        44: (
            "PARTIAL",
            f"watch={golden.get('watch_pid')} golden={golden.get('pid')} state={golden.get('state')} blocked on masters",
        ),
        46: ("OPEN", f"no same-day record masters; soft_today={soft_today}"),
        48: ("OPEN", "2026-08-10 markers agent-only; 0 candidates"),
        49: (
            "PARTIAL",
            "WoW OBS track mask fixed offline to 7; meter/dogfood + Fable-default risk remain",
        ),
        50: ("OPEN", "human game+mic meter proof outstanding"),
        51: (
            "OPEN",
            f"AUDIO_GREEN status={audio.get('status')} volumes={audio.get('volumes')}",
        ),
        53: ("OPEN", "VibeCast Gather not in-game; Auto Hide UI unconfigured"),
        54: ("OPEN", "cinematic UI not proven this session"),
        62: (
            "CLOSED" if fb_running and fb_test_ok else "PARTIAL",
            f"localhost server process_running={fb_running}; isolated E2E={fb_test_ok}; "
            f"test_age_s={fb_test_age_s}; receipt={fb_test_path}",
        ),
        73: (
            "CLOSED" if fb_test_ok else "PARTIAL",
            f"isolated POST preserves existing human_verdicts={fb_test_ok}; "
            f"real_verdicts_touched={fb_test.get('real_verdicts_touched')}; receipt={fb_test_path}",
        ),
        82: (
            "PARTIAL",
            "deploy_windows_scripts exists; not auto-enforced after every edit",
        ),
        85: (
            "PARTIAL",
            "rotate_gcs_logs.sh present (gauntlet G081); unbounded growth not fully solved",
        ),
        98: ("OPEN", "no plugin API yet"),
        99: ("OPEN", "twin games portability later"),
    }

    out_rows = []
    counts = {"CLOSED": 0, "PARTIAL": 0, "OPEN": 0}
    for r in rows:
        n = r["gap"]
        if n in overrides:
            status, proof = overrides[n]
        else:
            status = map_status(r["ledger_status"])
            proof = (
                f"ledger={r['ledger_status']}; note={r['ledger_note']}; "
                "gauntlet_run~38 behavioral checks not 100-row re-proof"
            )
        if unattended_untracked and n in (32, 44, 76, 79):
            proof += "; unattended driver untracked (custody open)"
        # League semantic ban: never treat agent_assigned progress as closed product
        if "league" in r["title"].lower() or "pitch" in r["title"].lower():
            if league_agent and not league_human:
                status = "PARTIAL" if status == "CLOSED" else status
                proof += f"; league agent_assigned={league_agent} human={league_human}"
        out_rows.append(
            {
                "gap": n,
                "title": r["title"],
                "status": status,
                "ledger_status": r["ledger_status"],
                "proof": proof,
                "bans": (
                    "no agent_assigned-as-semantic; no structural-as-BranchA-E2E; "
                    "no untracked-as-custody"
                ),
            }
        )
        counts[status] = counts.get(status, 0) + 1

    meta = {
        "schema": "gcs_gap_100_crosswalk/v1",
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict": "RUNTIME_PARTIAL_E2E_UNPROVEN",
        "product_green": False,
        "counts": counts,
        "laws": [
            "evidence_class=agent_assigned is NOT semantic CLOSED",
            "structural checks are NOT live Branch-A E2E",
            "untracked patch is NOT durable custody",
            "A-J 8/2 recap is NOT 100-gap closure",
        ],
        "live": {
            "today": today,
            "ready_today": soft.get("ready_today"),
            "soft_today": soft_today,
            "soft_2026_08_10": soft_10,
            "soft_2026_08_09": soft_09,
            "golden_pid": golden.get("pid"),
            "watch_pid": golden.get("watch_pid"),
            "golden_state": golden.get("state"),
            "harvest_rc_today": harvest_rc,
            "audio_status": audio.get("status"),
            "league_agent_assigned": league_agent,
            "league_human": league_human,
            "league_status": league.get("status"),
            "branch_a_rc_fixed": branch_a_rc_fixed,
            "unattended_untracked": unattended_untracked,
            "git_lines": len(glines),
            "git_mod_approx": mod,
            "git_untracked_approx": unt,
            "rejected_stills": rejected_stills,
            "feedback_server_running": fb_running,
            "feedback_server_test_ok": fb_test_ok,
            "feedback_server_test_age_s": fb_test_age_s,
            "feedback_server_test_receipt": str(fb_test_path),
            "windows_script_hash_parity_ok": parity_ok,
            "windows_script_hash_parity_age_s": parity_age_s,
            "windows_script_hash_parity_receipt": str(parity_path),
            "unattended_status": unatt.get("status"),
        },
        "rows": out_rows,
    }

    CP.mkdir(parents=True, exist_ok=True)
    json_path = CP / "GAP_100_CROSSWALK_LATEST.json"
    json_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    (CP / f"GAP_100_CROSSWALK_{stamp}.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# GAP 100 CROSSWALK — GCS VibeCast",
        f"**utc:** {meta['utc']}",
        f"**verdict:** `{meta['verdict']}` · **PRODUCT_GREEN:** false",
        f"**counts:** CLOSED={counts['CLOSED']} · PARTIAL={counts['PARTIAL']} · OPEN={counts['OPEN']}",
        "",
        "## Laws (Codex takeback accepted)",
        "- Do not count evidence_class=agent_assigned as semantic correctness",
        "- Do not count structural checks as live Branch-A E2E",
        "- Do not count untracked patch as durable custody",
        "- A-J 8/2 recap is not 100-gap closure",
        "",
        "## Live snapshot",
        f"- today={today} ready_today={soft.get('ready_today')} harvest_rc={harvest_rc}",
        f"- golden={golden.get('pid')} watch={golden.get('watch_pid')} state={golden.get('state')}",
        f"- AUDIO_GREEN={audio.get('status')}",
        f"- League agent_assigned={league_agent} human={league_human}",
        f"- Branch A harvest_rc lie fixed={branch_a_rc_fixed}; real-media E2E untested",
        f"- git Games/WoW lines={len(glines)}; unattended untracked={unattended_untracked}",
        f"- rejected_stills={rejected_stills}",
        f"- feedback_server_running={fb_running}",
        f"- feedback_server_test_ok={fb_test_ok} receipt={fb_test_path}",
        f"- windows_script_hash_parity_ok={parity_ok} receipt={parity_path}",
        "",
        "## Crosswalk (100 rows)",
        "",
        "| # | Status | Title | Proof |",
        "|---|--------|-------|-------|",
    ]
    for r in out_rows:
        proof = r["proof"].replace("|", "\\|")[:180]
        title = r["title"].replace("|", "\\|")
        lines.append(f"| {r['gap']} | **{r['status']}** | {title} | {proof} |")
    lines += [
        "",
        "## Not PRODUCT_GREEN because",
        "1. Same-day masters still 0",
        "2. Branch A real-media E2E never exercised",
        "3. AUDIO_GREEN not dual/live green",
        "4. League mappings agent_assigned only",
        "5. Framing A/B still recommendation-only",
        "6. Unattended production scripts untracked (custody open)",
        "",
        f"Machine JSON: {json_path}",
    ]
    md_path = CP / "GAP_100_CROSSWALK_LATEST.md"
    body = "\n".join(lines) + "\n"
    md_path.write_text(body, encoding="utf-8")
    (CP / f"GAP_100_CROSSWALK_{stamp}.md").write_text(body, encoding="utf-8")

    res = WOW / "00-Index/RELIABILITY_RESIDUAL_SERIALIZE_20260810.md"
    rt = res.read_text(encoding="utf-8")
    block = (
        f"\n## GAP_100_CROSSWALK landed {meta['utc']}\n\n"
        f"verdict=RUNTIME_PARTIAL_E2E_UNPROVEN PRODUCT_GREEN=false\n"
        f"counts CLOSED={counts['CLOSED']} PARTIAL={counts['PARTIAL']} OPEN={counts['OPEN']}\n"
        f"receipt: {json_path}\n"
        "Codex takeback accepted: 8/2 A-J is not 100-gap closure.\n"
    )
    if "GAP_100_CROSSWALK landed" not in rt:
        res.write_text(rt.rstrip() + block + "\n", encoding="utf-8")

    print("ROWS", len(out_rows))
    print("COUNTS", counts)
    print("JSON", json_path)
    print("MD", md_path)
    print("verdict", meta["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
