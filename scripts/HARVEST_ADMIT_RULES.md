# Harvest admit rules (R0-2)

**Law:** no invent FOOTAGE · claim before work · READY = qualified media only

## Order (mandatory)

1. **Fence** — `assert_vibecast_write_fence.py`  
2. **Claim** — `returner-daily-<day>/.harvest_claim.lockdir` taken *before* any analysis/soft_poll side effects that could race  
3. **Already harvested?** — `.harvest_once` → exit 0 skip  
4. **READY** — from `SOFT_POLL_LATEST` today row `ready=true`  
   - Prefer existing LATEST if fresh; `HARVEST_FORCE_POLL=1` for post_play path  
5. **Qualified media** — Windows soft_poll v2: min bytes + exclusive open + duration when ffprobe  
6. **harvest_mac** — pull real candidates only  
7. **Commit** — write `.harvest_once` then release claim  

## Soft_poll writers (one cadence)

| Owner | When |
|-------|------|
| **Golden / operator** | golden_long_run alive → owns soft_poll |
| **LaunchAgent** | defers if golden alive |
| **Watch** | defers soft_poll if golden alive; else **one** soft_poll/tick |
| **post_play_harvest** | force-poll once for human kick |

## Refuse

- today not ready  
- claim held by other live pid (exit 3)  
- fence fail (exit 2)  
- invent candidates when empty  

## Admit (harvest proceeds)

- claim held by self  
- today `ready=true` with qualified_n ≥ 1 (or legacy ready with qualified field)  
- Windows reachable for harvest_mac  

## After admit

- enhance / review pack / KEEP are separate  
- ARM stays deny until kyle_go  
