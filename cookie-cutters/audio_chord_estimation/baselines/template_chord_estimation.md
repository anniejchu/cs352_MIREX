# Chord Estimation Handout

## Goal
Write a chord estimator that outputs chord labels with timestamps for each audio file in a given N-file directory.
View the official [MIREX website](https://music-ir.org/mirex/wiki/2025:Audio_Chord_Estimation) for more info.

Your outputs must match the expected file format so the evaluator can score them.
We will use the MIREX evaluator to evaluate your chord estimator.

## Required File Structure
We should be able to run your estimator like this:

```
foobar <input_dir_to_audio_samples> <output_dir_to_chord_labels>
```

Such that it looks like this:
```
├── input_folder
│   ├── Dataset1
│   │   ├── track1.wav
│   │   └── ...
│   └── ...
├── output_folder
│   ├── Dataset1
│   │   ├── track1.lab
│   │   └── ...
│   └── ...
```

## Output File Format
One output file per audio file.

- **Filename**: same basename as audio, extension `.lab`
  - Example: `RM-P001.wav` -> `RM-P001.lab`
- **Content**: tab-separated rows of `start_time`, `end_time`, `chord_label`.
- **Times** in seconds (3 decimal places).
- **No gaps or overlaps**: segments must cover the full audio duration without breaks.
- **No headers**.

Valid example:
```
0.000	1.860	C:maj
1.860	3.712	A:min
3.712	5.574	F:maj
5.574	7.459	G:maj
7.459	30.000	N
```

Invalid example (missing end time, single-column):
```
0.000 C:maj
1.860 A:min
```

### Chord Label Vocabulary
Use standard MIREX chord labels. The evaluator recognizes:

- **Root**: `C  C#  D  Eb  E  F  F#  G  Ab  A  Bb  B`
- **Quality**: `:maj`, `:min`  (and `:7`, `:maj7`, `:min7`, etc. for the Sevenths metric)
- **No chord**: `N`

Examples: `C:maj`, `F#:min`, `Bb:maj`, `N`

## Datasets You Can Use
We will likely provide you with a training subset of RWC-Popular as it's difficult to obtain the source files due to copyright.

Example training datasets include:
- RWC-Popular: available via [website](https://staff.aist.go.jp/m.goto/RWC-MDB/) [mirdata](https://mirdata.readthedocs.io/en/stable/_modules/mirdata/datasets/rwc_popular.html)
- Billboard Dataset: [website](https://ddmal.ca/research/The_McGill_Billboard_Project_(Chord_Analysis_Dataset)/)
  / [easy_import](https://mirdata.readthedocs.io/en/stable/_modules/mirdata/datasets/billboard.html)


## How We Will Evaluate
We will use an evaluation subset of RWC-Popular. We will either clone your repository and run it on evaluation day, or provide the evaluation set during finals week so you can generate predictions
and submit them to us.

You are welcome to try the evaluator yourself with whichever training set you use.

```
python3 mirex-evaluation/main.py audio_chord_estimation <EVAL_RUN_NAME> --year 2026
```

Here is the folder structure we will be using for evaluation.

- `mirex-chord/Audio/RWC-Popular/`
  - Input audio `.wav` files.
- `mirex-chord/Ground-Truth/RWC-Popular/`
  - Ground-truth `.lab` files.
- `mirex-chord/2026/RWC-Popular/<YOUR_TEAM_NAME>/`
  - Your prediction files go here.

Example:
- `mirex-chord/2026/RWC-Popular/AdaLovelace/RM-P001.lab`

It will compare:
- Ground truth: `mirex-chord/Ground-Truth/RWC-Popular/*.lab`
- Predictions: `mirex-chord/2026/RWC-Popular/<YOUR_TEAM_NAME>/*.lab`

### Evaluation Metrics
The MIREX chord evaluator (MusOOEvaluator) scores several metrics:

| Metric | What it checks |
|---|---|
| MirexRoot | Root note correct |
| MirexMajMin | Root + major/minor quality correct |
| MirexMajMinBass | MajMin + correct bass note |
| MirexSevenths | Root + seventh quality correct |
| MirexSeventhsBass | Sevenths + correct bass note |
| Segmentation (Inner) | Boundary placement quality |

Scores are reported as percentages weighted by duration.

## Baseline
A simple chroma-based template matching baseline is provided in `build_chord_baseline.py`.
It extracts a CQT chromagram, matches each frame against 24 major/minor chord templates,
and collapses consecutive identical labels into timed segments.

```bash
python3 cookie-cutters/audio_chord_estimation/baselines/build_chord_baseline.py \
  --audio_dir /path/to/audio \
  --method chroma \
  --dataset RWC-Popular \
  --year 2026 \
  --submission YourTeamName
```

## Submission Checklist
1. You created `<YOUR_MODEL_NAME>/`.
2. Your system takes an input audio directory and an output directory for chord label files.
3. Each output `.lab` has tab-separated `start end chord` rows covering the full duration.
4. Chord labels use the MIREX vocabulary (`C:maj`, `A:min`, `N`, etc.).
5. Filenames match audio basenames exactly (`.wav` -> `.lab`).
