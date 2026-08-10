# WOW Explorer — Audio B-roll + Returnee Content Ideation
**Date:** 2026-08-05  
**Owner research:** Grok (web + product knowledge)  
**Scope:** Free/web/GitHub Auphonic-like voice processing; Windows→Drive→Mac/HyperFrames path; 10–15 min community-first content stance  
**Status:** IDEATION complete (no code/wire required for this turn)

---

## 1. What “Auphonic-like” means (no khaki)

Auphonic’s value is a **chain**, not one magic filter:

| Stage | Job | Artifact risk |
|--------|-----|----------------|
| Noise / hum / buzz kill | Static + some non-stationary junk | Over-AI → plastic voice, lost consonants |
| Leveling | Even loudness across the take | Pumping / noise-floor breathing |
| Compression | Gentle density | Radio smash → fatigue |
| EQ / de-ess / de-plosive | Clarity | Generic AutoEQ “podcast khaki” |
| Loudness target | ~-16 LUFS podcast / ~-14 YouTube | Wrong target → platform re-gain |

**Rule:** good mic + decent room → **light** denoise + solid leveler + natural compression.  
**Hard rule:** process **voice only**. Never run speech enhancers on WOW game audio (SFX/music die).

---

## 2. Web options

### Auphonic free (still best one-button)
- **2 free hours/month** (no card required for free tier).
- At 10–15 min VO only: ~8–12 eps/month on free tier.
- Still the best taste/effort ratio if Kyle already trusts the sound.

### Adobe Podcast Enhance Speech
- Free web denoise/enhance at podcast.adobe.com/enhance.
- **Risk for Kyle’s ear:** free tier often full-strength; community reports robotic/overcooked at max.
- Use only for dirty takes; blend light if available; not default for a nice mic.

### Other web “all-in-ones”
- Riverside-class tools: record+clean, more lock-in, less premium hand feel.
- Random AI enhance sites: skip for series (privacy + quality variance).

---

## 3. GitHub / free local (closest free substitute)

There is **no single OSS product that fully clones Auphonic**. Closest free stack:

### Recommended free chain
1. **DeepFilterNet** (https://github.com/Rikorose/DeepFilterNet) — neural denoise, full-band 48 kHz. Use only if room/fan/hiss present; skip if clean.
2. **PodcastPlugins** (https://github.com/trummerschlunk/PodcastPlugins) — free TRACK + MASTER (VST3/AU/CLAP/LV2). Spectral balancer, leveler, multiband dynamics, limiter. Defaults ~-16 LUFS. Style knob: natural ↔ radio. Prefer **slightly natural of center**.
3. **ffmpeg loudnorm** (or ffmpeg-normalize) finish:
   - Podcast/Substack-ish: `I=-16:TP=-1.5:LRA=11`
   - YouTube-leaning: `I=-14`

### Other OSS pieces
| Project | Role | Note |
|---------|------|------|
| RNNoise / noise-suppression-for-voice | Light/real-time denoise | Can sound gated |
| Resemble Enhance | Denoise + bandwidth restore | Can over-enhance |
| noisereduce (Python) | Spectral gating | Easy to over-gate |
| Spotify Pedalboard | Scripted plugin chains | Later automation |

### Host DAW
Audacity (free) or Reaper (cheap, durable) to host PodcastPlugins.

---

## 4. Pipeline aim (Windows game + Mac finish + HyperFrames)

```
WINDOWS (capture day)
├── Track A: WOW B-roll (OBS/game)
└── Track B: Mic VO WAV 48 kHz separate (always)
        ↓ Google Drive / NAS
MAC (or home PC)
├── Optional DeepFilterNet if noisy
├── PodcastPlugins TRACK → MASTER (defaults / slight natural)
├── loudnorm → voice_clean.wav
└── HyperFrames: B-roll + voice_clean over top
        (duck game audio under VO if both present)
```

**Capture hygiene:**
- Separate mic WAV, not only baked into game video
- Peak ~-12 to -6 dBFS headroom
- Kill fans/AC when possible
- Short takes match free-tier + attention reality

**HyperFrames template spine:** cold open B-roll → title → VO beats + cutaways → soft CTA end card. VO is spine; game footage is texture.

---

## 5. Content stance — 10–15 min returnee explorer

### Thesis
**“Learn with me / build with me”** > **“I teach the meta.”**  
Audience investment spikes when they lead and correct. Twitch “new/returning player” energy ports to short Substack video + notes.

### Length ladder (permission structure)
| Length | When | Purpose |
|--------|------|---------|
| ~5 min | Low energy / one discovery | One loop, one audience question |
| 10–15 min | Default | Story + 2–3 moments + invite help |
| 30–60 min | Rare | Only when genuinely obsessed that week |

Promise variable length: “Some days five minutes, some days fifteen. No filler.”

### Series spines
1. Returnee diary — UI assumptions for cold returns  
2. Wrong on purpose — state model, invite correction  
3. Audience quest log — one decision per ep; next opens with their answer  
4. Co-build character/route — Kyle executes, audience steers  
5. Myth vs memory — 2016 recall vs now  
6. Soft social / LFG without gatekeeping

### Framing language
- “I’m coming back cold. Here’s how I understand it — **correct me**.”
- “Not a guide. A **field notebook**.”
- “If you’ve got a better loop, dump it; I’ll try it on camera.”
- “Expert takes welcome as **helpers**, not dunks.”

### Positioning line
**“Exploring Azeroth again, out loud — help me not get lost.”**

### Avoid (for now)
Hour-long lore dumps, ranked/meta authority, daily high-production captivity.

---

## 6. Product package (WOW Explorer / Substack)

| Layer | Deliverable |
|--------|-------------|
| Core | 10–15 min (or 5) video + short note: 3 bullets + one ask |
| Hook | One explicit decision the audience owns |
| Audio bar | Consistent VO loudness, low noise; game audio secondary |
| Cadence | 2–3×/week sustainable > daily perfection |
| Social | Clip one “I was wrong / you fixed it” moment |

---

## 7. Low-regret path for “start tomorrow”

1. Record **separate mic WAV** + game B-roll.  
2. A/B one take: **Auphonic free** vs **PodcastPlugins defaults + loudnorm**. Trust ears.  
3. Ship one **8–12 min** “I’m back, here’s what confuses me” with a single audience ask.  
4. Do not default Adobe max-enhance on clean mics.

**If free Auphonic hours cover cadence:** keep it.  
**If offline/unlimited needed:** DeepFilterNet (optional) + PodcastPlugins + loudnorm.  
**If it sounds AI-podcast:** reduce denoise first; Style → natural.

---

## 8. Deferred (not this turn)

- One-page VO processing checklist (Mac/Windows)  
- HyperFrames reusable WOW Explorer composition template  
- First-week five-title episode slate with audience prompts  

---

## Sources (research anchors)
- Auphonic free tier / features: auphonic.com pricing + product pages  
- Adobe Podcast Enhance Speech: podcast.adobe.com/enhance  
- DeepFilterNet: github.com/Rikorose/DeepFilterNet  
- PodcastPlugins: github.com/trummerschlunk/PodcastPlugins  
- ffmpeg loudnorm / spoken-word targets community practice (-16 / -14 LUFS)
