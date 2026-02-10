# Beat Tracking Assignment Handout (GTZAN Subset)

## Goal
Write a beat tracker that outputs beat times for each audio file in the provided N-file subset. Your outputs must match the expected file format so the evaluator can score them.

## Required File Structure
All paths are under the course repo root `<course_repo>/mirex-beat` [AC TODO: change path]:

- `mirex_beat/Audio/GTZAN/`
  - Input audio `.wav` files for the provided N-file subset.
- `mirex-beat/Ground-Truth/GTZAN/`
  - Ground-truth `.lab` files (provided). We will provide you 25 "training" examples.
- `mirex-beat/2026/GTZAN/<YOUR_TEAM_NAME>/`
  - Your prediction files go here.

Example:
- `mirex-beat/2026/GTZAN/AdaLovelace/blues.00033.lab`

This matches the expect format for the MIREX evaluator should you want to use this during development.

## Output File Format
One output file per audio file.

- **Filename**: same basename as audio, extension `.lab`
  - Example: `blues.00033.wav` → `blues.00033.lab`
- **Content**: one beat time per line, in seconds.
- **No headers**, **no extra columns**.
- **Sorted ascending**.
- **Empty file** if no beats are detected.

Valid example:
```
0.44
1.38
2.32
3.32
4.28
```

Invalid example (extra column):
```
0.44 1
1.38 2
```

## How We Will Evaluate
We run the MIREX evaluator on a separate _evaluation_ subset of GTZAN files. Though you are welcome to try the evaluator itself on your own with the training set provided to you.

```
python3 mirex-evaluation/main.py audio_beat_detection <EVAL_RUN_NAME> --year 2026
```

It will compare:

- Ground truth: `mirex-beat/Ground-Truth/GTZAN/*.lab`
- Predictions: `mirex-beat/2026/GTZAN/<YOUR_TEAM_NAME>/*.lab`

## Submission Checklist
1. You created `<YOUR_MODEL_NAME>/`.
2. You have one `.lab` per audio file in the N-file subset.
3. Each `.lab` contains only beat times (one per line).
4. Filenames match audio basenames exactly.
