#!/usr/bin/env python3
"""GCS·VibeCast gauntlet — re-runnable systems checks (honest N, not '100 bugs').

This is an executable check suite (~40–60 checks). The GAUNTLET_100 ledger is a
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
GCS_RECEIPTS = RECEIPTS.parent / "gcs-vibecast"
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


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


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
    rc, out = run([sys.executable, str(SCRIPTS / "resolve_windows_host.py"), "--drive-offload"], 10)
    drive_path = Path(out.strip()) if rc == 0 and out.strip() else None
    drive = drive_path if drive_path and drive_path.is_dir() else None
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

    # Current installed/runtime/custody receipts. These are additive checks;
    # none promotes the real-media G080 product gate.
    rc, launch_out = run(
        ["launchctl", "print", "gui/501/com.kyle.gcs.vibecast-review-feedback"],
        10,
    )
    health_rc, health_out = run(
        ["curl", "-fsS", "--max-time", "3", "http://127.0.0.1:8765/healthz"],
        5,
    )
    try:
        health = json.loads(health_out)
    except Exception:
        health = {}
    feedback_runtime_ok = (
        rc == 0
        and health_rc == 0
        and health.get("ok") is True
        and health.get("may_publish") is False
    )
    checks.append(
        Check(
            "G109",
            "AUTO",
            "review feedback LaunchAgent loopback health",
            "PASS" if feedback_runtime_ok else "FAIL",
            f"launchctl_rc={rc} health_rc={health_rc} day={health.get('day')}",
        )
    )

    parity = read_json(GCS_RECEIPTS / "WINDOWS_SCRIPT_HASH_PARITY_LATEST.json")
    parity_ok = (
        parity.get("status") == "PASS"
        and parity.get("all_match") is True
        and int(parity.get("file_count") or 0) >= 24
    )
    checks.append(
        Check(
            "G110",
            "SOT",
            "Windows deployed-script SHA-256 parity",
            "PASS" if parity_ok else "FAIL",
            f"files={parity.get('file_count')} all_match={parity.get('all_match')}",
        )
    )

    backup = read_json(RECEIPTS / "MAC_BACKUP_VIBECAST_LATEST.json")
    backup_ok = (
        backup.get("status") == "PASS"
        and backup.get("authority_bundle_verified") is True
        and int(backup.get("extension_files") or 0) >= 5
        and backup.get("returns_working_set_verified") is True
    )
    checks.append(
        Check(
            "G111",
            "BACKUP",
            "off-device bundle and working-set backup",
            "PASS" if backup_ok else "FAIL",
            f"schema={backup.get('schema')} extensions={backup.get('extension_files')} "
            f"working_set={backup.get('returns_working_set_files')}",
        )
    )

    schema = read_json(RECEIPTS / "SCHEMA_AUDIT_LATEST.json")
    schema_ok = schema.get("status") == "PASS" and schema.get("missing_n") == 0
    checks.append(
        Check(
            "G112",
            "SOT",
            "versioned JSON schema coverage",
            "PASS" if schema_ok else "FAIL",
            f"files={schema.get('files_scanned')} missing={schema.get('missing_n')}",
        )
    )

    extension = read_json(GCS_RECEIPTS / "EXTENSION_SURFACE_LATEST.json")
    extension_ok = (
        extension.get("status") == "PASS"
        and extension.get("may_publish") is False
        and {"tde-default", "tfe-default"}.issubset(set(extension.get("brand_packs") or []))
        and "TDE_TFE_PORTABLE_PLAN" in set(extension.get("checks") or [])
    )
    checks.append(
        Check(
            "G113",
            "SOT",
            "fail-closed plugin and twin-brand plans",
            "PASS" if extension_ok else "FAIL",
            f"checks={extension.get('checks')}",
        )
    )

    chat = read_json(GCS_RECEIPTS / "CHAT_DETECTOR_REGRESSION_LATEST.json")
    chat_ok = chat.get("status") == "PASS" and all((chat.get("checks") or {}).values())
    checks.append(
        Check(
            "G114",
            "PRODUCT",
            "conditional chat blur real-media regression",
            "PASS" if chat_ok else "FAIL",
            f"checks={chat.get('checks')}",
        )
    )

    rotation = read_json(GCS_RECEIPTS / "LOG_ROTATION_LATEST.json")
    rotation_ok = (
        rotation.get("status") == "PASS"
        and rotation.get("cadence_owner") == "com.kyle.gcs.wow-soft-poll-harvest"
    )
    checks.append(
        Check(
            "G115",
            "AUTO",
            "log retention receipt and cadence owner",
            "PASS" if rotation_ok else "FAIL",
            f"keep={rotation.get('keep_compressed')} owner={rotation.get('cadence_owner')}",
        )
    )

    resume = read_json(GCS_RECEIPTS / "WINDOWS_RESUME_READINESS_LATEST.json")
    resume_ok = (
        resume.get("status") == "READY_FOR_HUMAN_CAPTURE"
        and (resume.get("profile") or {}).get("product_path_ok") is True
        and (resume.get("auto_hide_ui") or {}).get("configured") is True
        and (resume.get("auto_hide_ui") or {}).get("active_profile_is_gather") is True
        and (resume.get("stream_deck") or {}).get("command_sheet_exists") is True
        and (resume.get("resume_card") or {}).get("exists") is True
    )
    checks.append(
        Check(
            "G116",
            "SOT",
            "Windows resume profile and card readback",
            "PASS" if resume_ok else "FAIL",
            f"status={resume.get('status')} auto_hide={(resume.get('auto_hide_ui') or {}).get('installed')}",
        )
    )

    secrets = read_json(GCS_RECEIPTS / "GITLEAKS_FULL_SCAN_LATEST.json")
    head_rc, head_out = run(["git", "rev-parse", "HEAD"], 5)
    secrets_ok = (
        secrets.get("status") == "PASS"
        and (secrets.get("history") or {}).get("findings") == 0
        and (secrets.get("working_tree") or {}).get("findings") == 0
        and head_rc == 0
        and secrets.get("head") == head_out.strip()
    )
    checks.append(
        Check(
            "G117",
            "SOT",
            "full-history and working-tree secret scan at HEAD",
            "PASS" if secrets_ok else "FAIL",
            f"receipt_head={str(secrets.get('head') or '')[:12]} current={head_out.strip()[:12]}",
        )
    )

    feedback_test = read_json(GCS_RECEIPTS / "REVIEW_FEEDBACK_SERVER_TEST_LATEST.json")
    feedback_checks = set(feedback_test.get("checks") or [])
    feedback_test_ok = (
        feedback_test.get("status") == "PASS"
        and {"CONCURRENT_POSTS_PRESERVED", "ATOMIC_JSON_VALID"}.issubset(feedback_checks)
    )
    checks.append(
        Check(
            "G118",
            "AUTO",
            "feedback atomic concurrent-write regression",
            "PASS" if feedback_test_ok else "FAIL",
            f"checks={len(feedback_checks)}",
        )
    )

    rc, out = run([sys.executable, str(SCRIPTS / "test_poll_admission.py")], 20)
    checks.append(
        Check(
            "G119",
            "HARVEST",
            "READY bypasses poll rate-limit cache",
            "PASS" if rc == 0 else "FAIL",
            out.strip()[-160:],
        )
    )
    rc, out = run([sys.executable, str(SCRIPTS / "test_watch_single_instance.py")], 20)
    checks.append(
        Check(
            "G120",
            "AUTO",
            "watch single-instance and unknown-file preservation",
            "PASS" if rc == 0 else "FAIL",
            out.strip()[-160:],
        )
    )

    public_extensions = REPO / "extensions"
    rc, out = run([sys.executable, str(REPO / "scripts" / "vibecast_extensions.py"), "validate"], 20)
    checks.append(
        Check(
            "G121",
            "BACKUP",
            "public sample includes executable extension registry",
            "PASS" if public_extensions.is_dir() and rc == 0 else "FAIL",
            out.strip()[-160:],
        )
    )

    brief = BROLL / "returner-daily-2026-08-09" / "NEXT_NIGHT_BRIEF.md"
    brief_text = brief.read_text(encoding="utf-8") if brief.is_file() else ""
    brief_ok = "c-pride-15s-start" in brief_text and "Human KEEP ids" in brief_text
    checks.append(
        Check(
            "G122",
            "PRODUCT",
            "next-night brief carries real KEEP identifiers",
            "PASS" if brief_ok else "FAIL",
            str(brief),
        )
    )

    hook_rc, hook_out = run(["git", "rev-parse", "--git-path", "hooks/pre-commit"], 5)
    hook = Path(hook_out.strip()) if hook_rc == 0 and hook_out.strip() else None
    hook_text = hook.read_text(encoding="utf-8") if hook and hook.is_file() else ""
    checks.append(
        Check(
            "G123",
            "SOT",
            "pre-commit Windows parity admission installed",
            "PASS" if "BEGIN GCS_VIBECAST_WINDOWS_PARITY_V1" in hook_text else "FAIL",
            str(hook),
        )
    )

    windows_behavior = read_json(GCS_RECEIPTS / "WINDOWS_BEHAVIOR_REGRESSION_LATEST.json")
    behavior_checks = windows_behavior.get("checks") or {}
    behavior_ok = (
        windows_behavior.get("status") == "PASS"
        and all(behavior_checks.get(name) is True for name in (
            "AUTOHIDE_TRANSFORM_SELFTEST",
            "AUTO_SESSION_END_DISPATCH_ON_TODAY_MASTER",
            "AUTO_SESSION_END_SKIP_WITHOUT_MASTER",
        ))
        and windows_behavior.get("fixture_only") is True
        and windows_behavior.get("real_media_touched") is False
    )
    checks.append(
        Check(
            "G124",
            "AUTO",
            "Windows AutoHide transform and Session-End fixture behavior",
            "PASS" if behavior_ok else "FAIL",
            f"checks={behavior_checks}",
        )
    )

    autohide = read_json(GCS_RECEIPTS / "AUTOHIDEUI_CONFIG_LATEST.json")
    autohide_checks = autohide.get("checks") or {}
    autohide_ok = (
        autohide.get("status") == "PASS"
        and autohide.get("state") in {"CONFIGURED", "ALREADY_CONFIGURED"}
        and all(autohide_checks.values())
        and autohide.get("original_preserved") is True
        and autohide.get("wow_running") is False
    )
    checks.append(
        Check(
            "G125",
            "SOT",
            "Windows AutoHideUI named profiles and original backup readback",
            "PASS" if autohide_ok else "FAIL",
            f"state={autohide.get('state')} backup={autohide.get('original_preserved')}",
        )
    )

    marker = read_json(GCS_RECEIPTS / "MANIFEST_MARKER_WINDOWS_LATEST.json")
    marker_ok = (
        marker.get("status") == "PASS"
        and int(marker.get("files_with_windows") or 0) >= 2
        and int(marker.get("matched_windows") or 0) >= 3
        and marker.get("invention") == "none"
    )
    checks.append(
        Check(
            "G126",
            "EXPORT",
            "real manifest has source-bound marker windows",
            "PASS" if marker_ok else "FAIL",
            f"files={marker.get('files_annotated')} windows={marker.get('matched_windows')}",
        )
    )

    rc, out = run([sys.executable, str(SCRIPTS / "test_no_candidate_enhance.py")], 30)
    checks.append(
        Check(
            "G127",
            "HARVEST",
            "empty staged candidates cannot invoke enhancement",
            "PASS" if rc == 0 else "FAIL",
            out.strip()[-160:],
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
