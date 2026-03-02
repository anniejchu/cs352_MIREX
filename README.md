# WI26 CS352 Final Projects: MIREX Challenges

This repo contains  starter code and baselines for two MIREX music analysis tasks.

### Tasks

**Audio Beat Detection** — `cookie-cutters/audio_beat_detection/`
- `beat_tracking_handout.md` — task description, output format, and evaluation instructions
- `baselines/template_beat_tracker.py` — simple energy/waveform peak baseline to get you started
- `baselines/run_beatthis_baseline.py` — wrapper to run the BeatThis model (state-of-the-art)
- `_external_baselines/beat_this/` — [BeatThis](https://github.com/CPJKU/beat_this) source (ISMIR 2024)

**Audio Chord Estimation** — `cookie-cutters/audio_chord_estimation/`
- `chord_estimation_handout.md` — task description, output format, and evaluation instructions
- `baselines/template_chord_baseline.py` — chroma template matching baseline to get you started

If you're having trouble sourcing datasets email Annie (TA) at anniechu [at] u.northwestern.edu

### Evaluation

Here's the `mirex-evaluation` repo link: [github](https://github.com/ismir-mirex/mirex-evaluation)

If you want to try the mirex-evaluation scripts that live in the `mirex-evaluation/` submodule. To set it up:

```bash
git submodule update --init
```

Then follow the instructions in `mirex-evaluation/README.MD`.


### Tips

See `cookie-cutters/Helpful_tips.md` for some general advice from EJ on getting started.

For more info on MIREX, check out their [website](https://music-ir.org/mirex/wiki/MIREX_HOME)
