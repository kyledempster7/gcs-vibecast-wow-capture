#!/usr/bin/env python3
"""GCS·VibeCast gauntlet — re-runnable systems checks (honest N, not '100 bugs').

This is an executable check suite (~30–40 checks). The GAUNTLET_100 ledger is a
separate wishlist of risk themes — do not claim 100 behavioral checks ran.

Exit 0 if no FAIL in critical classes; 1 if any critical FAIL; 2 tool error.
No invent FOOTAGE. No publish. No Factory writes.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
WOW = SCRIPTS.parents[1]
BROLL = Path.home() / "Movies" / "WoW-Broll-Workflow" / "Returns"
RECEIPTS = (
    Path.home()
    / "Library"
    / "Application Support"
    / "UAH"
    / "butler"
    / "control-plane"
    / "receipts"
    / "wow"
)
REPO = Path.home() / "src" / "gcs-vibecast-wow-capture"
STORY = WOW / "04-Story-and-Capture"
CRITICAL_PREFIXES = ("LAW", "INVENT", "PUBLISH", "HARVEST", "SOT", "BACKUP")


@dataclass
class Check:
    id: str
    cls: str
    title: str
    status: str  # PASS | FAIL | PARTIAL | OPEN | N/A
    note: str = ""


def run(cmd: list[str], timeout: int = 60) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return 99, str(e)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def main() -> int:
    checks: list[Check] = []
    today = datetime.now().strftime("%Y-%m-%d")

    # --- LAW / INVENT / PUBLISH ---
    soft = BROLL / "SOFT_POLL_LATEST.json"
    ready_today = False
    if soft.is_file():
        d = json.loads(soft.read_text(encoding="utf-8"))
        ready_today = bool(d.get("ready_today"))
        checks.append(
            Check(
                "G001",
                "LAW",
                "SOFT_POLL has ready_today field",
                "PASS" if "ready_today" in d else "FAIL",
                f"ready_today={d.get('ready_today')} ready={d.get('ready')}",
            )
        )
        checks.append(
            Check(
                "G002",
                "LAW",
                "ready mirrors ready_today (no false green any-day)",
                "PASS" if d.get("ready") == d.get("ready_today") else "FAIL",
                f"ready={d.get('ready')} ready_today={d.get('ready_today')} ready_any={d.get('ready_any')}",
            )
        )
    else:
        checks.append(Check("G001", "LAW", "SOFT_POLL_LATEST exists", "FAIL", "missing"))

    day10 = BROLL / f"returner-daily-{today}" / "candidates"
    n_today = len(list(day10.glob("*.mp4"))) if day10.is_dir() else 0
    checks.append(
        Check(
            "G003",
            "INVENT",
            "No invented candidates when not READY",
            "PASS" if (ready_today or n_today == 0) else "FAIL",
            f"ready_today={ready_today} today_mp4={n_today}",
        )
    )

    rc, out = run([sys.executable, str(SCRIPTS / "arm_state.py"), "--self-test"], 30)
    checks.append(
        Check("G004", "PUBLISH", "arm_state self-test", "PASS" if rc == 0 else "FAIL", out[-200:])
    )

    pkgs = list(
        (
            Path.home()
            / "Library/Application Support/UAH/butler/control-plane/delivery-independence/packages"
        ).glob("returner_daily_*.json")
    )
    armed_bad = []
    for p in pkgs:
        try:
            j = json.loads(p.read_text(encoding="utf-8"))
            if j.get("may_publish") is True or str(j.get("arm", "")).upper() == "ARMED":
                if "NOT_ARMED" not in p.name.upper():
                    armed_bad.append(p.name)
        except Exception:
            pass
    checks.append(
        Check(
            "G005",
            "PUBLISH",
            "No silent ARMED returner packages",
            "PASS" if not armed_bad else "FAIL",
            ",".join(armed_bad) or "all hold/not_armed",
        )
    )

    # --- HARVEST ---
    rc, out = run(["bash", str(SCRIPTS / "harvest_if_ready.sh"), today], 90)
    checks.append(
        Check(
            "G010",
            "HARVEST",
            "harvest_if_ready refuses empty today",
            "PASS" if (ready_today and rc == 0) or ((not ready_today) and rc == 1) else "FAIL",
            f"rc={rc}",
        )
    )
    lock = BROLL / "returner-daily-2026-08-09" / ".harvest_once"
    if lock.is_file():
        rc2, _ = run(["bash", str(SCRIPTS / "harvest_if_ready.sh"), "2026-08-09"], 30)
        checks.append(
            Check(
                "G011",
                "HARVEST",
                "re-harvest lock idempotent exit 0",
                "PASS" if rc2 == 0 else "FAIL",
                f"rc={rc2}",
            )
        )
    else:
        checks.append(Check("G011", "HARVEST", "re-harvest lock present 08-09", "PARTIAL", "no lock"))

    # --- SOT / scripts ---
    critical = [
        "soft_poll_windows.sh",
        "harvest_if_ready.sh",
        "post_play_harvest.sh",
        "Session-End-Ship.ps1",
        "Export-ShipCandidates.ps1",
        "mac_vibecast_operator.sh",
        "mac_backup_vibecast.sh",
        "gcs_pipeline_health.py",
        "assert_vibecast_write_fence.py",
        "watch_ready_harvest_once.sh",
        "windows_auto_session_end.sh",
        "Auto-Session-End-If-Masters.ps1",
    ]
    miss = [c for c in critical if not (SCRIPTS / c).is_file()]
    checks.append(
        Check("G020", "SOT", "critical scripts on disk", "PASS" if not miss else "FAIL", str(miss))
    )

    if REPO.is_dir():
        drift = []
        for c in critical:
            a, b = SCRIPTS / c, REPO / "scripts" / c
            if a.is_file() and b.is_file() and sha(a) != sha(b):
                drift.append(c)
            elif a.is_file() and not b.is_file():
                drift.append(f"GH_MISS:{c}")
        checks.append(
            Check(
                "G021",
                "BACKUP",
                "vault scripts match GitHub clone",
                "PASS" if not drift else "FAIL",
                ",".join(drift) or "match",
            )
        )
    else:
        checks.append(Check("G021", "BACKUP", "GitHub clone present", "FAIL", str(REPO)))

    # fence
    rc, out = run([sys.executable, str(SCRIPTS / "assert_vibecast_write_fence.py")], 15)
    checks.append(Check("G030", "LAW", "fence OK from vault cwd", "PASS" if rc == 0 else "FAIL", out.strip()))

    factory = Path.home() / "Movies" / "WoW-Social-Workflow"
    if factory.is_dir():
        old = Path.cwd()
        try:
            os.chdir(factory)
            rc, out = run([sys.executable, str(SCRIPTS / "assert_vibecast_write_fence.py")], 15)
            checks.append(
                Check(
                    "G031",
                    "LAW",
                    "fence blocks Factory cwd",
                    "PASS" if rc == 2 else "FAIL",
                    f"rc={rc} {out.strip()[:120]}",
                )
            )
        finally:
            os.chdir(old)

    # unit tests
    rc, out = run([sys.executable, str(SCRIPTS / "test_join_markers.py")], 30)
    checks.append(Check("G040", "EXPORT", "join_markers fixtures", "PASS" if rc == 0 else "FAIL", out[-120:]))
    rc, out = run([sys.executable, str(SCRIPTS / "test_export_marker_intervals.py")], 30)
    checks.append(
        Check("G041", "EXPORT", "export interval parity", "PASS" if rc == 0 else "FAIL", out[-120:])
    )

    # launchagent
    plist = Path.home() / "Library/LaunchAgents/com.kyle.gcs.wow-soft-poll-harvest.plist"
    checks.append(
        Check("G050", "AUTO", "LaunchAgent plist exists", "PASS" if plist.is_file() else "FAIL", str(plist))
    )

    # docs
    for i, rel in enumerate(
        [
            "PRODUCT_SYSTEM_SPEC.md",
            "RESTORE_AND_BACKUP.md",
            "VIBECAST_WRITE_FENCE.md",
            "PLAY_NIGHT_CHECKLIST.md",
            "AUDIO_GREEN_STAMP.md",
        ],
        start=60,
    ):
        p = STORY / rel
        checks.append(
            Check(f"G0{i}", "DOCS", f"doctrine {rel}", "PASS" if p.is_file() else "FAIL", str(p))
        )

    # product OPEN honesty
    audio = STORY / "AUDIO_GREEN_STAMP.md"
    if audio.is_file():
        t = audio.read_text(encoding="utf-8")
        open_ok = "status: OPEN" in t.split("---", 2)[1] if t.count("---") >= 2 else "OPEN" in t[:200]
        checks.append(
            Check(
                "G070",
                "AUDIO",
                "AUDIO_GREEN not falsely stamped",
                "PASS" if open_ok or "status: GREEN" in t else "PARTIAL",
                "OPEN honest" if open_ok else "check stamp",
            )
        )

    checks.append(
        Check(
            "G080",
            "PRODUCT",
            "Phase A human gates still OPEN (Deck/export/audio e2e)",
            "OPEN",
            "needs real play night — not a fail of system law",
        )
    )

    # decades tools present
    for gid, name in (
        ("G081", "rotate_gcs_logs.sh"),
        ("G082", "park_limbo_shortlist.py"),
        ("G083", "schema_audit.py"),
        ("G084", "gcs_vibecast_gauntlet.py"),
    ):
        p = SCRIPTS / name
        checks.append(
            Check(gid, "AUTO", f"tool {name}", "PASS" if p.is_file() else "FAIL", str(p))
        )
    ext = STORY / "EXTENSIBILITY_SPINE.md"
    checks.append(
        Check("G085", "DOCS", "EXTENSIBILITY_SPINE", "PASS" if ext.is_file() else "FAIL", str(ext))
    )
    gauntlet_doc = STORY / "GAUNTLET_100_BUGS_VIBECAST.md"
    checks.append(
        Check(
            "G086",
            "DOCS",
            "GAUNTLET_100 ledger",
            "PASS" if gauntlet_doc.is_file() else "FAIL",
            str(gauntlet_doc),
        )
    )

    # Drive backup-code
    drive = None
    cloud = Path.home() / "Library/CloudStorage"
    if cloud.is_dir():
        for p in cloud.rglob("GCS-VibeCast-Offload"):
            if p.is_dir():
                drive = p
                break
    checks.append(
        Check(
            "G090",
            "BACKUP",
            "Drive GCS-VibeCast-Offload present",
            "PASS" if drive else "FAIL",
            str(drive),
        )
    )
    if drive:
        bc = drive / "backup-code" / "receipts-wow"
        checks.append(
            Check(
                "G091",
                "BACKUP",
                "Drive receipts-wow mirror non-empty",
                "PASS" if bc.is_dir() and any(bc.iterdir()) else "FAIL",
                str(bc),
            )
        )

    # --- reliability residual checks (Codex waves) ---
    soft = BROLL / "SOFT_POLL_LATEST.json"
    if soft.is_file():
        try:
            sd = json.loads(soft.read_text(encoding="utf-8"))
            schema_ok = str(sd.get("schema") or "").startswith("gcs_soft_poll_ready/")
            checks.append(
                Check(
                    "G100",
                    "LAW",
                    "soft_poll schema present",
                    "PASS" if schema_ok else "FAIL",
                    str(sd.get("schema")),
                )
            )
            # v2 qualifies if any day reports candidates_qualified_n field
            days = sd.get("days") or []
            has_q = any(
                isinstance(d, dict) and "candidates_qualified_n" in d for d in days
            )
            checks.append(
                Check(
                    "G101",
                    "HARVEST",
                    "soft_poll reports candidates_qualified_n (v2 quality)",
                    "PASS" if has_q else "PARTIAL",
                    "qualified field present" if has_q else "redeploy soft_poll_windows.ps1",
                )
            )
            rt = sd.get("ready_today")
            if rt is None and days:
                today = datetime.now().strftime("%Y-%m-%d")
                for d in days:
                    if isinstance(d, dict) and d.get("day") == today:
                        rt = bool(d.get("ready"))
            checks.append(
                Check(
                    "G102",
                    "LAW",
                    "ready mirrors ready_today when both set",
                    "PASS"
                    if sd.get("ready") is None or rt is None or bool(sd.get("ready")) == bool(rt)
                    else "FAIL",
                    f"ready={sd.get('ready')} ready_today={rt}",
                )
            )
        except Exception as e:
            checks.append(Check("G100", "LAW", "soft_poll readable", "FAIL", str(e)))
    else:
        checks.append(Check("G100", "LAW", "SOFT_POLL_LATEST exists", "FAIL", str(soft)))

    harvest_src = (SCRIPTS / "harvest_if_ready.sh").read_text(encoding="utf-8", errors="replace")
    checks.append(
        Check(
            "G103",
            "HARVEST",
            "harvest_if_ready claims before analysis",
            "PASS" if ".harvest_claim.lockdir" in harvest_src else "FAIL",
            "claimdir gate",
        )
    )
    guards = SCRIPTS / "Gcs-SessionEnd-Guards.ps1"
    checks.append(
        Check(
            "G104",
            "SOT",
            "Gcs-SessionEnd-Guards.ps1 present",
            "PASS" if guards.is_file() else "FAIL",
            str(guards),
        )
    )
    export_src = (SCRIPTS / "Export-ShipCandidates.ps1").read_text(
        encoding="utf-8", errors="replace"
    )
    checks.append(
        Check(
            "G105",
            "EXPORT",
            "export fail-closed skip_zone (NO_USABLE_WINDOWS)",
            "PASS" if "NO_USABLE_WINDOWS" in export_src else "FAIL",
            "W0-4 string",
        )
    )
    dual = SCRIPTS / "run_dual_audio_10s_probe.sh"
    checks.append(
        Check(
            "G106",
            "AUDIO",
            "dual_audio 10s probe wrapper present",
            "PASS" if dual.is_file() else "FAIL",
            str(dual),
        )
    )
    # League evidence honesty
    league_sb = (
        STORY
        / "social"
        / "package"
        / "EXPLORERS_LEAGUE_PITCH_STORYBOARD.json"
    )
    if league_sb.is_file():
        try:
            lb = json.loads(league_sb.read_text(encoding="utf-8"))
            caps = [s for s in (lb.get("shots") or []) if s.get("captured")]
            labeled = all(
                s.get("evidence_class") in ("agent_assigned", "human_confirmed", "detector")
                for s in caps
            ) if caps else True
            checks.append(
                Check(
                    "G107",
                    "PRODUCT",
                    "League captured shots have evidence_class",
                    "PASS" if labeled else "FAIL",
                    f"captured={len(caps)}",
                )
            )
        except Exception as e:
            checks.append(Check("G107", "PRODUCT", "League storyboard readable", "FAIL", str(e)))

    # LaunchAgent loaded vs merely present
    plist = Path.home() / "Library/LaunchAgents/com.kyle.gcs.wow-soft-poll-harvest.plist"
    rc, out = run(["launchctl", "list"], 10)
    la_loaded = "com.kyle.gcs.wow-soft-poll-harvest" in (out or "")
    checks.append(
        Check(
            "G108",
            "AUTO",
            "LaunchAgent loaded in launchctl list",
            "PASS" if la_loaded else ("PARTIAL" if plist.is_file() else "FAIL"),
            "loaded" if la_loaded else "plist only or missing",
        )
    )

    # write report
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    n_checks = len(checks)
    summary = {
        "schema": "gcs_vibecast_gauntlet/v2",
        "name": "gcs_vibecast_executable_checks",
        "not_100_bug_claim": True,
        "n_executable_checks": n_checks,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "counts": {
            s: sum(1 for c in checks if c.status == s)
            for s in ("PASS", "FAIL", "PARTIAL", "OPEN", "N/A")
        },
        "checks": [asdict(c) for c in checks],
        "law": "no_invent_no_publish_no_factory_writes; honest_N_not_100",
    }
    out_json = RECEIPTS / f"GAUNTLET_RUN_{ts}.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (RECEIPTS / "GAUNTLET_RUN_LATEST.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    fails = [c for c in checks if c.status == "FAIL"]
    crit_fails = [c for c in fails if c.cls in ("LAW", "INVENT", "PUBLISH", "HARVEST", "SOT", "BACKUP")]
    print(f"n_executable_checks={n_checks} (not a 100-bug claim)")
    print(json.dumps(summary["counts"], indent=2))
    for c in checks:
        print(f"{c.status:7} {c.id} [{c.cls}] {c.title} — {c.note[:100]}")
    print(f"report={out_json}")
    if crit_fails:
        print("CRITICAL_FAIL", [c.id for c in crit_fails])
        return 1
    if fails:
        print("NONCRIT_FAIL", [c.id for c in fails])
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
