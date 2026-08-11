---
type: architecture
status: active
created: 2026-08-10
product: GCS · VibeCast
role: DECADES_PLUGIN_SURFACE
---

# Extensibility spine — new engines without forking the house

**Parent:** [[../00-Index/GCS_CITADEL|GCS]] · **Wing:** VibeCast · **Law:** [[VIBECAST_WRITE_FENCE]]

## Stable contracts (do not rename casually)

| Contract | Purpose | Version field |
|----------|---------|---------------|
| `gcs_obs_marker/v1` | Deck / session markers | schema |
| `gcs_soft_poll_ready/v1` | Multi-day READY | schema + ready_today |
| `gcs_vibecast_ship_candidates/v1` | Export MANIFEST | schema |
| `gcs_marker_join/v0` | Cut windows | schema |
| `gcs_arm_state/v0` | Publish deny/go | schema |
| `gcs_audio_role/v0` | Mic/game night role | schema |
| Moments `CATALOG.json` | KEEP library | generated_at + paths |

## How to add a new engine (checklist)

1. **Read** PRODUCT_SYSTEM_SPEC pipeline — plug at one stage only.  
2. **Never** invent masters or flip ARM.  
3. **Write** only under VibeCast fence paths (or a new wing with its own fence).  
4. **Emit** versioned JSON with `schema` string.  
5. **Add** one row to ROADMAP or gauntlet — not a second index tree.  
6. **Register** optional hook in `enhance_returner_day.sh` *after* harvest, gated on file presence.  
7. **Mirror** scripts via `mac_backup_vibecast.sh` + GitHub.  
8. **Prove** with gauntlet or a fixture test.

## Hook points (current)

```
PLAY (Windows) → soft_poll → harvest → enhance → review → archive → package NOT_ARMED
                      ↑              ↑ optional detectors / speech / pride
                 auto Session-End
```

| Hook | File | Safe add |
|------|------|----------|
| After harvest lock | `harvest_if_ready.sh` | notify, catalog |
| After score | `enhance_returner_day.sh` | new scorer if input exists |
| After KEEP | `archive_keep_to_moments.py` | extra mirror |
| Package | `stitch_returner_package.py` | new surface still NOT_ARMED |
| Health | `gcs_pipeline_health.py` | new row |
| Gauntlet | `gcs_vibecast_gauntlet.py` | new G-id |

## Executable extension contract

```bash
python3 wow-roster-tracker/scripts/vibecast_extensions.py validate
python3 wow-roster-tracker/scripts/vibecast_extensions.py plan --brand tde-default
python3 wow-roster-tracker/scripts/vibecast_extensions.py plan --brand tfe-default
```

- Brand packs live under `wow-roster-tracker/extensions/brand-packs/` and must emit `NOT_ARMED` plans.
- Plugins live under `wow-roster-tracker/extensions/plugins/`; only contained Python entrypoints and suggestion-only hooks are admitted.
- Plugin output must be versioned, must set `may_publish=false`, and cannot invent media, arm a package, or write a provider.
- `test_vibecast_extensions.py` proves the TDE/TFE plan shape and the bundled AI-advisor no-write contract.

## Twin brands / new games later

Same spine; different brand pack + media root entry in `media_roots.json`.
The executable TDE/TFE plan fixtures prove contract portability; real media E2E remains game-specific.
Do **not** clone the whole vault wing until one game dogfoods Phase A.

## AI upgrades

Phase A (real capture e2e) before cloud kill-AI. The implemented advisor hook is suggestion-only and provider-dark. Intel stack: [[INTELLIGENCE_STACK_AND_COST]].

## Related

[[PRODUCT_SYSTEM_SPEC]] · [[GAUNTLET_100_BUGS_VIBECAST]] · [[RESTORE_AND_BACKUP]]
