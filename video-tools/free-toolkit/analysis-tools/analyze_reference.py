#!/usr/bin/env python3
"""Measure candidate cuts in a user-supplied reference without exporting media."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from importlib.metadata import version
from pathlib import Path

import cv2
from scenedetect import SceneManager, StatsManager, open_video
from scenedetect.detectors import ContentDetector


def detect(path: Path, threshold: float, min_frames: int, downscale: int):
    video = open_video(str(path), backend="opencv")
    stats = StatsManager()
    manager = SceneManager(stats)
    manager.auto_downscale = False
    manager.downscale = downscale
    manager.add_detector(ContentDetector(threshold=threshold, min_scene_len=min_frames))
    processed = manager.detect_scenes(video, show_progress=False, frame_skip=0)
    scenes = manager.get_scene_list(start_in_scene=True)
    rows = [
        {
            "scene": i + 1,
            "start_frame": start.get_frames(),
            "end_frame_exclusive": end.get_frames(),
            "start_seconds": round(start.get_seconds(), 6),
            "end_seconds": round(end.get_seconds(), 6),
            "duration_seconds": round((end - start).get_seconds(), 6),
        }
        for i, (start, end) in enumerate(scenes)
    ]
    return rows, stats, {
        "threshold": threshold,
        "frame_rate": video.frame_rate,
        "frame_size": list(video.frame_size),
        "processed_frames": processed,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--threshold", type=float, default=27.0)
    parser.add_argument("--comparison-thresholds", nargs="*", type=float, default=[22.0, 32.0])
    parser.add_argument("--min-scene-frames", type=int, default=12)
    parser.add_argument("--downscale", type=int, default=3)
    args = parser.parse_args()
    cv2.setNumThreads(1)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    thresholds = [args.threshold] + [t for t in args.comparison_thresholds if t != args.threshold]
    summary = {
        "source_basename": args.input.name,
        "source_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "software": {n: version(n) for n in ("scenedetect", "opencv-python-headless")},
        "detector": "PySceneDetect ContentDetector (default HSV weights; not adaptive)",
        "min_scene_frames": args.min_scene_frames,
        "downscale_factor": args.downscale,
        "frame_skip": 0,
        "primary_threshold": args.threshold,
        "limitations": [
            "Cuts are algorithmic candidates, not a manual shot list.",
            "Large animated text, flashes and camera motion may be detected as cuts.",
            "Dissolves and layered graphic changes may be missed or split differently.",
            "No reference frames, audio or clips are exported by this script.",
        ],
        "runs": [],
    }
    for threshold in thresholds:
        rows, stats, info = detect(args.input, threshold, args.min_scene_frames, args.downscale)
        suffix = f"{threshold:g}".replace(".", "_")
        path = args.output_dir / f"mavi_candidate_shots_t{suffix}.csv"
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        if threshold == args.threshold:
            stats.save_to_csv(str(args.output_dir / "mavi_frame_change_metrics.csv"))
        durations = [r["duration_seconds"] for r in rows]
        # The source must be covered exactly once with adjacent half-open ranges.
        assert rows[0]["start_frame"] == 0
        assert all(a["end_frame_exclusive"] == b["start_frame"] for a, b in zip(rows, rows[1:]))
        assert rows[-1]["end_frame_exclusive"] == info["processed_frames"]
        info.update(
            {
                "candidate_shot_count": len(rows),
                "candidate_cut_count": len(rows) - 1,
                "median_seconds": round(statistics.median(durations), 4),
                "mean_seconds": round(statistics.mean(durations), 4),
                "min_seconds": min(durations),
                "max_seconds": max(durations),
                "coverage_seconds": rows[-1]["end_seconds"],
                "csv": path.name,
                "contiguous_full_frame_coverage": True,
            }
        )
        summary["runs"].append(info)
        print(json.dumps(info, ensure_ascii=False))
    (args.output_dir / "reference_analysis.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
