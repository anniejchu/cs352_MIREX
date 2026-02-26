# Beat Tracking Handout

## Goal
Write a beat tracker that outputs beat times for each audio file in a given N-file directory. View the official [MIREX website](https://music-ir.org/mirex/wiki/2025:Audio_Beat_Tracking) for more info.

Your outputs must match the expected file format so the evaluator can score them. We will use the MIREX evaluator to evaluate your beat tracker. 

## Required File Structure
<!-- All paths are under the course repo root `<course_repo>/mirex-beat` [AC TODO: change path]: -->
We should be able to run your evaluator like this.

```
foobar <input_dir_to_audio_samples> <output_dir_to_annotated_beats>
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
  - Example: `blues.00033.wav` -> `blues.00033.lab`
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

## Datasets you can use
Example training datasets you can use include: 

- Ballroom Dataset: [website](https://mtg.upf.edu/ismir2004/contest/tempoContest/node5.html) / [easy_import](https://mirdata.readthedocs.io/en/stable/_modules/mirdata/datasets/ballroom.html)

- We may provide a training subset of GTZAN (dataset we will evaluate on)


## How We Will Evaluate
The dataset used for evaluation will be GTZAN. We will either clone your beat tracker repository and run it on the evaluation day, or provide the evaluation set during the week of finals so you can generate predictions and submit them to us.

You are welcome to try the evaluator itself on your own with whichever training set you use. 

```
python3 mirex-evaluation/main.py audio_beat_detection <EVAL_RUN_NAME> --year 2026
```

Here is the folder structure we will be using for evaluation. 

- `mirex_beat/Audio/GTZAN/`
  - Input audio `.wav` files for the provided N-file directory.
- `mirex-beat/Ground-Truth/GTZAN/`
  - Ground-truth `.lab` files.
- `mirex-beat/2026/GTZAN/<YOUR_TEAM_NAME>/`
  - Your prediction files go here.

Example:
- `mirex-beat/2026/GTZAN/AdaLovelace/blues.00033.lab`

This matches the expect format for the MIREX evaluator should you want to use this during development.

It will compare:
- Ground truth: `mirex-beat/Ground-Truth/GTZAN/*.lab`
- Predictions: `mirex-beat/2026/GTZAN/<YOUR_TEAM_NAME>/*.lab`

## Baseline
A simple energy-based and waveform-peak baseline is provided in `template_beat_tracker.py`.
It detects peaks in short-time RMS energy (or raw waveform amplitude) and writes beat times to `.lab` files.

```bash
python3 cookie-cutters/audio_beat_detection/baselines/template_beat_tracker.py \
  --audio_dir /path/to/audio \
  --out_dir /path/to/output \
  --method energy
```

A stronger deep-learning baseline (Beat This!) is available in `run_beatthis_baseline.py`.

## Submission Checklist
1. You created `<YOUR_MODEL_NAME>/`.
2. Your system will take in a path to audio directory and a path to the output directory of where to put each annotation. 
3. Each output dir will have one `.lab` per audio file in the N-file input directory; each `.lab` contains only beat times (one per line).
4. Filenames match audio basenames exactly.
