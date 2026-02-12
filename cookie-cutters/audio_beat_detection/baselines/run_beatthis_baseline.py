"""Run Beat This! baseline to produce .lab files (no evaluation).

Assumes:
- beat_this is installed and provides a `beat_this` CLI.
- We have audio .wav files in a directory.
- Ground-truth labels are available in the repo under
  MIREX-public-datasets/audio-beat-detection/Ground-Truth/<dataset>.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
GT_ROOT = REPO_ROOT / "mirex-evaluation" / "MIREX-public-datasets" / "audio-beat-detection" / "Ground-Truth"


def collect_audio_basenames(audio_dir: Path):
    basenames = set()
    for p in audio_dir.iterdir():
        if p.is_file() and p.suffix.lower() == ".wav":
            basenames.add(p.stem)
    return basenames


def copy_ground_truth(gt_src: Path, gt_dst: Path, subset_basenames=None):
    gt_dst.mkdir(parents=True, exist_ok=True)
    for p in gt_src.iterdir():
        if p.is_file() and p.suffix.lower() == ".lab":
            if subset_basenames is not None and p.stem not in subset_basenames:
                continue
            shutil.copy2(p, gt_dst / p.name)


def run(cmd, cwd=None):
    print("$", " ".join(cmd))
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def strip_beat_numbers(pred_dir: Path):
    """Convert Beat This! 2-column output to 1-column beat times for mir_eval."""
    if not pred_dir.exists():
        return
    for p in pred_dir.iterdir():
        if not p.is_file() or p.suffix.lower() != ".lab":
            continue
        lines = []
        with open(p, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # keep only first column (time)
                lines.append(line.split()[0])
        with open(p, "w") as f:
            f.write("\n".join(lines) + ("\n" if lines else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio_dir", required=True, help="Directory containing .wav files")
    ap.add_argument("--out_dir", required=True, help="Output directory for .lab files")
    args = ap.parse_args()

    audio_dir = Path(args.audio_dir).resolve()
    if not audio_dir.exists():
        raise SystemExit(f"Audio dir not found: {audio_dir}")

    pred_dst = Path(args.out_dir).resolve()
    pred_dst.mkdir(parents=True, exist_ok=True)
    # Use .lab so evaluator can find predictions.
    run(["beat_this", str(audio_dir), "-o", str(pred_dst), "--suffix", ".lab"])
    # Beat This! writes time + beat number; mir_eval expects time only.
    strip_beat_numbers(pred_dst)


if __name__ == "__main__":
    main()
