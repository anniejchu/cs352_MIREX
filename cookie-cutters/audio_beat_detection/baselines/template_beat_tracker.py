"""
Simple baseline beat tracker for GTZAN subset.

Usage:
  python template_beat_tracker.py \
    --audio_dir /path/to/audio_files
    --out_dir /path/to/your_predictions
"""

import argparse
from pathlib import Path

import numpy as np
import soundfile as sf


def simple_energy_beats(y, sr, hop=512, win=1024, thresh=0.5):
    """Very simple placeholder: detect peaks in normalized short-time energy."""
    # Pad to full frames
    if len(y) < win:
        return np.array([])
    frames = 1 + (len(y) - win) // hop
    energy = np.zeros(frames, dtype=np.float64)
    for i in range(frames):
        start = i * hop
        frame = y[start:start + win]
        # RMS per frame
        energy[i] = np.sqrt(np.mean(frame * frame))

    # Normalize and find peaks
    if energy.max() > 0:
        energy = energy / energy.max()
    peaks = np.where((energy[1:-1] > energy[:-2]) & (energy[1:-1] > energy[2:]) & (energy[1:-1] > thresh))[0] + 1

    # Convert frame index to time in seconds
    times = (peaks * hop) / sr
    return times


def simple_wave_peaks(y, sr, thresh=0.5, min_gap_sec=0.1):
    """Super simple: normalize waveform and take local peaks above threshold."""
    if y.size == 0:
        return np.array([])
    y = y / (np.max(np.abs(y)) + 1e-9)
    # local maxima above threshold
    idx = np.where((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:]) & (y[1:-1] > thresh))[0] + 1
    if idx.size == 0:
        return np.array([])
    # thin peaks by minimum gap
    min_gap = max(1, int(min_gap_sec * sr))
    kept = [idx[0]]
    for i in idx[1:]:
        if i - kept[-1] >= min_gap:
            kept.append(i)
    times = np.array(kept, dtype=np.float64) / sr
    return times


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio_dir", required=True, help="Directory with .wav files")
    ap.add_argument("--out_dir", required=True, help="Output directory for .lab files")
    ap.add_argument(
        "--method",
        choices=["energy", "wave"],
        default="wave",
        help="Beat extraction method: energy (ST energy peaks) or wave (waveform peaks).",
    )
    args = ap.parse_args()

    audio_dir = Path(args.audio_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    wavs = sorted([p for p in audio_dir.iterdir() if p.is_file() and p.suffix.lower() == ".wav"])
    if not wavs:
        raise SystemExit(f"No .wav files found in {audio_dir}")

    for wav in wavs:
        y, sr = sf.read(wav, dtype="float32")
        if y.ndim > 1:
            y = y.mean(axis=1)

        if args.method == "wave":
            beats = simple_wave_peaks(y, sr)
        else:
            beats = simple_energy_beats(y, sr)
        beats = np.sort(beats)

        out_path = out_dir / f"{wav.stem}.lab"
        with open(out_path, "w") as f:
            for t in beats:
                f.write(f"{t:.6f}\n")


if __name__ == "__main__":
    main()
