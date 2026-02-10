#!/usr/bin/env python3
"""Build an input folder + trivial chord baseline for MIREX chord estimation.

Copies Ground-Truth .lab files and writes predictions with a single chord label
spanning the entire audio duration.
"""

import argparse
import shutil
import wave
from pathlib import Path

import numpy as np
import librosa

REPO_ROOT = Path(__file__).resolve().parents[3]
GT_ROOT = REPO_ROOT / "mirex-evaluation" / "MIREX-public-datasets" / "audio-chord-estimation" / "Ground-Truth"


def wav_duration_seconds(path: Path) -> float:
    with wave.open(str(path), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
    if rate == 0:
        return 0.0
    return frames / float(rate)

CHORD_ROOTS = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def build_templates():
    """Return (labels, templates) for 12 major + 12 minor + N."""
    templates = []
    labels = []
    for i, root in enumerate(CHORD_ROOTS):
        maj = np.zeros(12, dtype=np.float32)
        min_ = np.zeros(12, dtype=np.float32)
        maj[i] = 1.0
        maj[(i + 4) % 12] = 1.0
        maj[(i + 7) % 12] = 1.0
        min_[i] = 1.0
        min_[(i + 3) % 12] = 1.0
        min_[(i + 7) % 12] = 1.0
        labels.append(f"{root}:maj")
        templates.append(maj)
        labels.append(f"{root}:min")
        templates.append(min_)
    labels.append("N")
    templates.append(np.zeros(12, dtype=np.float32))
    return labels, np.stack(templates, axis=0)


def chroma_chord_sequence(audio_path: Path, sr=22050, hop_length=512, thresh=0.3):
    """Compute a simple chord sequence via chroma template matching."""
    y, sr = librosa.load(str(audio_path), sr=sr, mono=True)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
    # Normalize per frame
    chroma = chroma / (np.linalg.norm(chroma, axis=0, keepdims=True) + 1e-8)
    labels, templates = build_templates()
    # Template match
    scores = templates @ chroma
    best_idx = np.argmax(scores, axis=0)
    best_score = np.max(scores, axis=0)
    # Apply threshold: if low energy, label as N
    n_idx = labels.index("N")
    best_idx = np.where(best_score < thresh, n_idx, best_idx)
    frame_times = librosa.frames_to_time(np.arange(chroma.shape[1]), sr=sr, hop_length=hop_length)
    return labels, best_idx, frame_times, float(len(y)) / float(sr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="RWC-Popular", help="Dataset under Ground-Truth")
    ap.add_argument("--audio_dir", required=True, help="Directory with .wav files")
    ap.add_argument("--out_dir", default=None, help="Output directory for .lab files (optional)")
    ap.add_argument("--input_root", default="./mirex-chord-input", help="Output input_folder root")
    ap.add_argument("--year", default="2025", help="Year folder to create")
    ap.add_argument("--submission", default="BaselineN", help="Submission folder name")
    ap.add_argument("--label", default="N", help="Chord label to use for full file")
    ap.add_argument("--method", choices=["constant", "chroma"], default="constant",
                    help="Baseline method: constant (single label) or chroma (template matching)")
    ap.add_argument("--sr", type=int, default=22050, help="Sample rate for chroma baseline")
    ap.add_argument("--hop_length", type=int, default=512, help="Hop length for chroma baseline")
    ap.add_argument("--chroma_thresh", type=float, default=0.3, help="Min score to accept chord, else N")
    ap.add_argument("--gt_src", default=None, help="Optional path to GT dataset folder to use")
    ap.add_argument("--subset_list", default=None, help="Optional file listing basenames to include")
    args = ap.parse_args()

    gt_src = Path(args.gt_src).resolve() if args.gt_src else (GT_ROOT / args.dataset)
    if not gt_src.exists():
        raise SystemExit(f"Ground-truth dataset not found: {gt_src}")

    audio_dir = Path(args.audio_dir).resolve()
    if not audio_dir.exists():
        raise SystemExit(f"Audio dir not found: {audio_dir}")

    input_root = Path(args.input_root).resolve() if args.input_root else None
    gt_dst = input_root / "Ground-Truth" / args.dataset if input_root else None
    pred_dst = Path(args.out_dir).resolve() if args.out_dir else (
        input_root / str(args.year) / args.dataset / args.submission
    )
    if gt_dst:
        gt_dst.mkdir(parents=True, exist_ok=True)
    pred_dst.mkdir(parents=True, exist_ok=True)

    gt_files = sorted([p for p in gt_src.iterdir() if p.is_file() and p.suffix.lower() == ".lab"])
    if not gt_files:
        raise SystemExit(f"No .lab files found in {gt_src}")

    subset = None
    if args.subset_list:
        subset = set()
        with open(args.subset_list, "r") as f:
            for line in f:
                name = line.strip()
                if not name:
                    continue
                subset.add(Path(name).stem)

    # Copy GT and create predictions
    missing_audio = []
    for gt in gt_files:
        if subset is not None and gt.stem not in subset:
            continue
        if gt_dst:
            shutil.copy2(gt, gt_dst / gt.name)
        wav = audio_dir / (gt.stem + ".wav")
        if wav.exists():
            if args.method == "chroma":
                labels, idxs, frame_times, duration = chroma_chord_sequence(
                    wav, sr=args.sr, hop_length=args.hop_length, thresh=args.chroma_thresh
                )
                # Collapse consecutive frames into segments
                segments = []
                start_t = 0.0
                cur_idx = idxs[0] if len(idxs) else labels.index("N")
                for i in range(1, len(idxs)):
                    if idxs[i] != cur_idx:
                        end_t = frame_times[i]
                        segments.append((start_t, end_t, labels[cur_idx]))
                        start_t = end_t
                        cur_idx = idxs[i]
                segments.append((start_t, duration, labels[cur_idx]))
                with open(pred_dst / gt.name, "w") as f:
                    for s, e, lab in segments:
                        f.write(f"{s:.3f}\t{e:.3f}\t{lab}\n")
                continue
            dur = wav_duration_seconds(wav)
        else:
            # Fallback: use end time of last GT segment
            with open(gt, "r") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
            if lines:
                try:
                    dur = float(lines[-1].split()[1])
                except Exception:
                    dur = 0.0
            else:
                dur = 0.0
            missing_audio.append(gt.stem)
        with open(pred_dst / gt.name, "w") as f:
            f.write(f"0.000\t{dur:.3f}\t{args.label}\n")

    if missing_audio:
        print(f"Warning: missing audio for {len(missing_audio)} files.")
        print("First few:", ", ".join(missing_audio[:5]))

    if gt_dst:
        print(f"Wrote GT to: {gt_dst}")
    print(f"Wrote predictions to: {pred_dst}")


if __name__ == "__main__":
    main()
