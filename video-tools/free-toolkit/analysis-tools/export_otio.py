#!/usr/bin/env python3
"""Export the selected narration edits as an editable, media-free OTIO timeline."""
from __future__ import annotations

import argparse
import hashlib
import json
from importlib.metadata import version
from pathlib import Path

import opentimelineio as otio

RATE = 48000


def rt(seconds):
    return otio.opentime.RationalTime(round(seconds * RATE), RATE)


def time_range(start, duration):
    return otio.opentime.TimeRange(rt(start), rt(duration))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--voice-url", default="USER_NARRATION_WAV_RELINK_REQUIRED.wav")
    parser.add_argument("--voice-duration", type=float, default=155.167)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    edits = data["timeline"]
    crossfade = data["crossfade_seconds"]
    half = crossfade / 2
    timeline = otio.schema.Timeline(name=data["name"])
    timeline.global_start_time = rt(0)
    timeline.metadata["guma_editorial"] = {
        "original_json_name": args.input.name,
        "original_json_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "video_frame_rate": 30,
        "audio_sample_rate": RATE,
        "voice_relink_required": True,
        "media_not_embedded": True,
        "sources": data["sources"],
        "legal_editorial_notes": data["legal_editorial_notes"],
        "timing_note": data["timing_note"],
        "transition_note": "25 ms equal-overlap edit intent; OTIO audio dissolve interpretation depends on importing editor.",
        "transcript_sentences": data["sentences"],
    }
    audio = otio.schema.Track(name="A1 · Ece kullanıcı seslendirmesi", kind=otio.schema.TrackKind.Audio)
    visual = otio.schema.Track(name="V1 · sahne yer tutucuları", kind=otio.schema.TrackKind.Video)
    expected_clips = []
    for index, item in enumerate(edits):
        trim_in = half if index > 0 else 0
        trim_out = half if index < len(edits) - 1 else 0
        source_start = item["source_start"] + trim_in
        duration = item["source_end"] - item["source_start"] - trim_in - trim_out
        timeline_start = item["start"] + trim_in
        assert source_start >= 0
        assert source_start + duration <= args.voice_duration
        assert abs((item["end"] - item["start"]) - (item["source_end"] - item["source_start"])) < 0.0001
        if index:
            assert abs(edits[index - 1]["end"] - item["start"] - crossfade) < 0.0001
            audio.append(
                otio.schema.Transition(
                    name="25 ms ses geçişi",
                    transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve,
                    in_offset=rt(half),
                    out_offset=rt(half),
                    metadata={"guma_audio_crossfade": {"duration_seconds": crossfade}},
                )
            )
        clip = otio.schema.Clip(
            name=item["id"],
            media_reference=otio.schema.ExternalReference(
                target_url=args.voice_url,
                available_range=time_range(0, args.voice_duration),
                metadata={"relink_required": True, "source_kind": data["source_kind"]},
            ),
            source_range=time_range(source_start, duration),
            metadata={
                "guma_edit": {
                    "id": item["id"],
                    "timeline_start_seconds": timeline_start,
                    "full_selected_source_start": item["source_start"],
                    "full_selected_source_end": item["source_end"],
                    "source_key": item.get("source_key"),
                    "purpose": item["purpose"],
                }
            },
        )
        audio.append(clip)
        placeholder = otio.schema.Clip(
            name=item["id"] + " · görsel tasarlanacak",
            media_reference=otio.schema.MissingReference(),
            source_range=time_range(0, duration),
            metadata={"guma_visual_intent": item["purpose"], "source_key": item.get("source_key")},
        )
        visual.append(placeholder)
        expected_clips.append((item["id"], source_start, duration, timeline_start))
    timeline.tracks.append(visual)
    timeline.tracks.append(audio)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    otio.adapters.write_to_file(timeline, str(args.output))
    restored = otio.adapters.read_from_file(str(args.output))
    restored_audio = restored.tracks[1]
    clips = [x for x in restored_audio if isinstance(x, otio.schema.Clip)]
    transitions = [x for x in restored_audio if isinstance(x, otio.schema.Transition)]
    assert len(clips) == len(edits)
    assert len(transitions) == len(edits) - 1
    assert abs(restored.duration().to_seconds() - data["duration"]) < 1 / RATE
    assert abs(restored_audio.duration().to_seconds() - data["duration"]) < 1 / RATE
    assert abs(restored.tracks[0].duration().to_seconds() - data["duration"]) < 1 / RATE
    for index, (clip, (name, source_start, duration, start)) in enumerate(zip(clips, expected_clips)):
        assert clip.name == name
        assert abs(clip.source_range.start_time.to_seconds() - source_start) < 1 / RATE
        assert abs(clip.duration().to_seconds() - duration) < 1 / RATE
        assert abs(restored_audio.range_of_child(clip).start_time.to_seconds() - start) < 1 / RATE
        assert clip.media_reference.target_url == args.voice_url
    serialized = args.output.read_text(encoding="utf-8")
    assert data["source"] not in serialized, "A local user-audio path leaked into the shareable timeline"
    result = {
        "opentimelineio_version": version("opentimelineio"),
        "original_json_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "timeline": args.output.name,
        "duration_seconds": restored.duration().to_seconds(),
        "audio_clip_count": len(clips),
        "audio_transition_count": len(transitions),
        "visual_placeholder_count": len(restored.tracks[0]),
        "audio_time_rate": RATE,
        "voice_target_url": args.voice_url,
        "raw_media_embedded": False,
        "roundtrip_name_source_ranges_timeline_positions": "PASS",
        "exact_duration_audio_visual_tracks": "PASS",
        "local_original_audio_path_absent": "PASS",
        "editor_import_tested": False,
        "import_note": "OTIO schema and roundtrip tested; no Premiere/Resolve/Kdenlive import claim. Relink narration in your editor; transition support varies.",
    }
    args.output.with_suffix(".validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
