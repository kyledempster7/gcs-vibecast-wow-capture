# Audacity + Field Notes (Windows) — agent/tool truth

## Can Codex / Grok “use Audacity”?

| Path | Status |
|------|--------|
| Official Audacity plugin for Codex/Grok/Claude | **No** |
| Click-by-click Audacity automation (UI RPA) | Fragile · not product default |
| **You record** in Audacity · save WAV | **Yes — preferred** |
| Agent **ffmpeg** cleanup on saved file | **Yes — product path** |
| OBS mic track instead of Audacity | Also fine |

## Your workflow tonight

1. Open Audacity · record Field Notes (script: `FIELD_NOTES_SCRIPT_TODAY.md`)  
2. Export WAV → `D:\WoW B-Roll Storage\YYYY-MM-DD\audio\`  
3. Optional manual: Noise Reduction + Normalize in Audacity (2 min)  
4. Stop. Mac can loudnorm later if needed.

## If an agent cleans audio later

```text
ffmpeg -i field-notes.wav -af "highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11" field-notes-clean.wav
```

No invent · no publish · file must already exist.
