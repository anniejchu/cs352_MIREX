"""Simple chord baseline for MIREX chord estimation.

Writes predictions with a single chord label spanning the entire audio duration,
or uses chroma template matching to produce a chord sequence.

Usage:
python template_chord_baseline.py \
    --audio_dir /path/to/audio_files
    --out_dir /path/to/your_predictions
"""

import argparse
import wave
from pathlib import Path

import numpy as np
import librosa


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
    ap.add_argument("--audio_dir", required=True, help="Directory with .wav files")
    ap.add_argument("--out_dir", required=True, help="Output directory for .lab files")
    ap.add_argument("--label", default="N", help="Chord label to use for full file (constant method)")
    ap.add_argument("--method", choices=["constant", "chroma"], default="chroma",
                    help="Baseline method: constant (single label) or chroma (template matching)")
    ap.add_argument("--sr", type=int, default=22050, help="Sample rate for chroma baseline")
    ap.add_argument("--hop_length", type=int, default=512, help="Hop length for chroma baseline")
    ap.add_argument("--chroma_thresh", type=float, default=0.3, help="Min score to accept chord, else N")
    args = ap.parse_args()

    audio_dir = Path(args.audio_dir).resolve()
    if not audio_dir.exists():
        raise SystemExit(f"Audio dir not found: {audio_dir}")

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    wavs = sorted([p for p in audio_dir.iterdir() if p.is_file() and p.suffix.lower() == ".wav"])
    if not wavs:
        raise SystemExit(f"No .wav files found in {audio_dir}")

    for wav in wavs:
        out_path = out_dir / (wav.stem + ".lab")
        if args.method == "chroma":
            labels, idxs, frame_times, duration = chroma_chord_sequence(
                wav, sr=args.sr, hop_length=args.hop_length, thresh=args.chroma_thresh
            )
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
            with open(out_path, "w") as f:
                for s, e, lab in segments:
                    f.write(f"{s:.3f}\t{e:.3f}\t{lab}\n")
        else:
            dur = wav_duration_seconds(wav)
            with open(out_path, "w") as f:
                f.write(f"0.000\t{dur:.3f}\t{args.label}\n")

    print(f"Wrote predictions to: {out_dir}")


if __name__ == "__main__":
    main()
