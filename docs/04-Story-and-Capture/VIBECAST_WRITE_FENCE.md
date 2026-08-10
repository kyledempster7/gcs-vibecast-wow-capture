---
type: safety-fence
status: active
created: 2026-08-10
area: Games/WoW
role: MULTI_AGENT_GCS_SAFETY
wing: VibeCast
parent: GCS
---

# VibeCast write fence (GCS multi-agent safety)

**Parent studio:** [[../00-Index/GCS_CITADEL|GCS]]  
**This wing only:** VibeCast · brand TWE · play-night capture→taste→package  
**Sibling wing:** Factory (Saturday fleet) — **other agents own it**

## MAY write

| Path | Why |
|------|-----|
| `Games/WoW/**` | Doctrine + scripts (wow-roster-tracker) |
| `~/Movies/WoW-Broll-Workflow/Returns/**` | Harvest working set |
| `~/Movies/WoW-Broll-Workflow/Moments-Library/**` | KEEP archive |
| `…/control-plane/receipts/wow/**` | Lane receipts |
| `~/Library/LaunchAgents/com.kyle.gcs.wow-soft-poll-harvest.plist` | This wing only |
| Drive `My Drive/GCS-VibeCast-Offload/**` | Offsite code + KEEP |
| GitHub `kyledempster7/gcs-vibecast-wow-capture` | Code/docs mirror |

## MUST NOT write

| Path | Owner |
|------|-------|
| `~/.codex/saturday-fleet-readiness/**` | Factory agents |
| `~/Movies/WoW-Social-Workflow/**` | Factory social products |
| Factory TWE/TDE/TFE carousel pipelines | Factory |
| UAH plant outside `receipts/wow` | Other lanes |
| ARM force true / Zernio live push | Human go only |

## Shared read OK

GCS_CITADEL · brand packs · Armory doctrine · media_roots.json

## Assert

```bash
python3 wow-roster-tracker/scripts/assert_vibecast_write_fence.py
```

Harvest/post_play call this assert before acting.

## Windows note

Masters SoR remains `D:\WoW B-Roll Storage`. Mac never claims sole masters.
