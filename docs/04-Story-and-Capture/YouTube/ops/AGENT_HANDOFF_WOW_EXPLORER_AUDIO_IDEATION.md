# AGENT HANDOFF — WOW Explorer audio B-roll + content stance ideation

**Status:** DONE (research/ideation only — no install, no HyperFrames wire, no publish)  
**Author seat:** Grok  
**Session date:** 2026-08-05 / receipt 2026-08-06  
**For:** any next agent (Codex, Claude, Grok, HyperFrames media seat)  
**Repo note:** pure product/ops ideation; not a `projects/` code slice

---

## 1. What Kyle asked

1. **Audio:** Start audio B-roll for **WOW Explorer** (Substack). Good mic already. Used to pay for **Auphonic-style auto-tuning** (noise/buzz removal, normalize, nice compress). Not paying for that software right now. Want **web options** + **GitHub/free** that achieve the same *feel* without cheesy AI artifacts. Ear is premium-sensitive.
2. **Pipeline:** Record on **Windows** (WOW B-roll) → Google Drive → Mac/home PC → **HyperFrames** with voice over top.
3. **Content:** Back into WOW, not hyper-obsessive. Prefer **~10–15 min** (sometimes **5**), not hour-long 2016 style. **New/returnee player** perspective, **audience participation**, “learn with me / correct me,” community co-build — **not** expert meta teaching.

---

## 2. What Grok actually did

| Done | Not done |
|------|----------|
| Web research on Auphonic free tier, Adobe Enhance Speech, free/OSS denoise + leveler tools | Install any tool on Kyle’s machines |
| Ranked free chain closest to Auphonic without khaki | Wire HyperFrames template |
| Proposed Windows→Drive→Mac process chain (voice-only rule) | A/B test Auphonic vs PodcastPlugins on a real take |
| Content stance + length ladder + series spines + framing language | Write episode scripts, record, or publish |
| Durable writeup + control-plane receipt | Live Substack/social post |

**No code changes** under `projects/`. No git commits for this work.

---

## 3. Decisions / recommendations next agents should inherit

### Audio (locked intent unless Kyle overrides)

1. **Process voice only.** Never run speech enhancers on game capture (SFX/music die).
2. **Good mic + decent room → light processing.** Prefer natural over “studio AI max.”
3. **Two viable paths (A/B one real take, then lock):**
   - **Path A (one-button):** [Auphonic](https://auphonic.com/) free = **2 h/month** → enough for ~8–12 eps at 10–15 min VO-only.
   - **Path B (offline free):** optional [DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) (only if noisy) → [PodcastPlugins](https://github.com/trummerschlunk/PodcastPlugins) TRACK+MASTER (Style slightly **natural** of center) → **ffmpeg loudnorm**.
4. **Loudness targets:** podcast/Substack-ish **I=-16 TP=-1.5 LRA≈11**; YouTube-leaning **I=-14**.
5. **Avoid as default:** Adobe Podcast Enhance at full strength (robotic/overcooked risk on free tier); random web “AI enhance” sites for series.
6. **Capture contract:** separate **48 kHz WAV** mic track on Windows; do not rely only on audio baked into game video.

### Pipeline sketch (target architecture)

```
WINDOWS: OBS/game B-roll + separate mic VO WAV
    → Google Drive / NAS
MAC: optional DeepFilterNet → PodcastPlugins → loudnorm → voice_clean.wav
    → HyperFrames: B-roll + voice over (duck game under VO)
```

### Content stance (locked intent)

| Topic | Stance |
|--------|--------|
| Length | Default **10–15 min**; allow **~5**; long form rare |
| Role | Returnee / field notebook, not guru |
| Audience | Lead with them: correct me, co-build, one decision per ep |
| Positioning line | “Exploring Azeroth again, out loud — help me not get lost.” |
| Cadence | Sustainable **2–3×/week** > daily perfection trap |

**Series spines worth reusing:** returnee diary; wrong-on-purpose; audience quest log; co-build route; myth-vs-memory (2016); soft LFG without gatekeeping.

**Framing phrases:** “correct me”; “not a guide, a field notebook”; “helpers not dunks.”

---

## 4. Canonical artifacts (read these first)

| File | Role |
|------|------|
| `/Users/kyle/Documents/Codex/2026-08-05/wow-explorer-audio-broll-ideation/WOW_EXPLORER_AUDIO_BROLL_IDEATION_20260805.md` | Full ideation (audio options, pipeline, content) |
| `/Users/kyle/Documents/Codex/2026-08-05/wow-explorer-audio-broll-ideation/RECEIPT_IDEATION_DONE_20260806.md` | Done receipt (Codex tree) |
| `/Users/kyle/Documents/Codex/2026-08-05/wow-explorer-audio-broll-ideation/AGENT_HANDOFF_WOW_EXPLORER_AUDIO_IDEATION.md` | **This handoff** |
| `/Users/kyle/Library/Application Support/UAH/butler/control-plane/receipts/capacity/grok/RECEIPT_WOW_EXPLORER_AUDIO_IDEATION_20260806.md` | Control-plane receipt copy |
| `/Users/kyle/Library/Application Support/UAH/butler/control-plane/receipts/capacity/grok/WOW_EXPLORER_AUDIO_BROLL_IDEATION_20260805.md` | Control-plane detail copy |
| `/Users/kyle/Documents/Codex/2026-08-05/wow-explorer-audio-broll-ideation/WOW_EXPLORER_IDEATION_EXECUTE_NOW.txt` | Optional Codex ACK-only packet (archive; not a build job) |
| `/Users/kyle/Kyles_Vault/Claudes_Corner/projects/handoffs/wow-explorer/HANDOFF_AUDIO_BROLL_IDEATION_LATEST.md` | Short pointer in projects handoffs tree |

**Mirror:** same ideation also under control-plane `receipts/capacity/grok/` for no-dally EXEC_PROOF compliance.

---

## 5. Context agents often miss

- **Blog:** WOW Explorer — social handles seen in fleet export as `the_wow_explorer` / `thewowexplorer`; site `wowexplorer.substack.com`.
- **HyperFrames:** composition system for final video; media-use/hyperframes skills apply when building templates — **not started this turn**.
- **Blog-empire lane:** Claude owns read-only fleet ingest; **Codex owns deep Substack/autoblogger** work. This handoff is **content + audio ops ideation**, not auto_blogger code.
- **Kyle sensitivity:** rejects cheesy AI “khaki” voice; used premium tools before; hand processing has no value — automation ok if quality holds.

---

## 6. Residual backlog (only if Kyle orders)

Priority order if continuing:

1. **A/B one real VO take:** Auphonic free vs PodcastPlugins+loudnorm; lock house chain.
2. **One-page processing checklist** (Windows capture + Mac finish commands).
3. **HyperFrames template:** cold open → title → VO+B-roll beats → CTA; VO spine, game as texture.
4. **Week-1 episode slate:** 3–5 titles, each with one audience-owned decision.
5. Optional: scripted Pedalboard/ffmpeg batch once house sound is locked.

Do **not** treat residual as open blocker. Ideation slice is **closed**.

---

## 7. Resume line (paste for next agent)

```
Resume WOW Explorer post-ideation from:
  /Users/kyle/Documents/Codex/2026-08-05/wow-explorer-audio-broll-ideation/AGENT_HANDOFF_WOW_EXPLORER_AUDIO_IDEATION.md
Full research:
  .../WOW_EXPLORER_AUDIO_BROLL_IDEATION_20260805.md
Locked intent: voice-only process; Auphonic free 2h/mo OR DeepFilterNet(opt)+PodcastPlugins natural+loudnorm;
  10–15m (sometimes 5) learn-with-me returnee; no expert-meta default.
Next only if Kyle orders: A/B real take → checklist → HyperFrames template → ep slate.
Do not re-research Auphonic alternatives from zero — inherit this packet.
```

---

## 8. Verification

- Ideation file non-empty (~6.8 KB).
- Receipt closed=true, rc=0.
- No software installed by this seat for this job.
- Gate path used: control-plane receipts under `.../receipts/capacity/grok/`.

**Handoff complete for agent consumption.**
