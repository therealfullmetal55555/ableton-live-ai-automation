#!/usr/bin/env python3
"""
Ableton arrangement generator.

Default mode:
    Generates and validates arrangement_plan.json.
    Does NOT connect to Ableton.

Apply mode:
    Sends the plan to the existing JSON/TCP Ableton bridge.
    Never deletes existing clips.

Expected empty MIDI tracks in the Ableton template:
    2 Bass
    3 Kick
    4 Snare
    5 Hats
    6 Lead
    7 Chords

Track indexes are zero-based, matching the original project.
"""

import argparse
import codecs
import json
import random
import socket
from dataclasses import dataclass
from pathlib import Path


BPM = 150
BEATS_PER_BAR = 4
TOTAL_BARS = 80

TRACKS = {
    "bass": 2,
    "kick": 3,
    "snare": 4,
    "hats": 5,
    "lead": 6,
    "chords": 7,
}

# MIDI roots: A2, F2, C2, G2.
# One chord per bar. The progression repeats every four bars.
PROGRESSION = [
    (45, "minor"),
    (41, "major"),
    (36, "major"),
    (43, "major"),
]


@dataclass(frozen=True)
class Section:
    name: str
    start_bar: int
    bars: int


SECTIONS = [
    Section("Intro", 0, 8),
    Section("Verse", 8, 16),
    Section("Breakdown", 24, 8),
    Section("Buildup", 32, 8),
    Section("Drop", 40, 16),
    Section("Climax", 56, 16),
    Section("Outro", 72, 8),
]


def midi_note(pitch, start, duration, velocity):
    return {
        "pitch": int(pitch),
        "start_time": round(float(start), 4),
        "duration": round(float(duration), 4),
        "velocity": int(velocity),
    }


def chord_at(global_bar):
    return PROGRESSION[global_bar % len(PROGRESSION)]


def add_note(parts, part, pitch, start, duration, velocity):
    parts[part].append(midi_note(pitch, start, duration, velocity))


def add_chords(parts, section, local_bar, root, quality):
    name = section.name
    start = local_bar * BEATS_PER_BAR

    # Piano/keys register: mostly C3-A3 for chord roots.
    chord_root = root + 12
    third = chord_root + (3 if quality == "minor" else 4)
    fifth = chord_root + 7

    if name == "Intro":
        velocity = 49
        duration = 3.55

    elif name == "Breakdown":
        velocity = 53
        duration = 3.75

    elif name == "Buildup":
        velocity = 57 + min(local_bar, 7) * 2
        duration = 3.55

    elif name == "Climax":
        velocity = 75
        duration = 3.55

    elif name == "Outro":
        velocity = max(40, 61 - local_bar * 3)
        duration = 3.55

    else:
        velocity = 64
        duration = 3.55

    # Slight strum: avoid mechanically simultaneous note starts.
    for offset, pitch in zip((0.0, 0.025, 0.05),
                             (chord_root, third, fifth)):
        add_note(
            parts,
            "chords",
            pitch,
            start + offset,
            duration - offset,
            velocity,
        )

    # Extra upper note only in climax.
    if name == "Climax" and local_bar % 2 == 0:
        add_note(parts, "chords", chord_root + 12,
                 start + 0.07, 3.40, 54)


def add_lead(parts, section, local_bar, root, quality):
    name = section.name
    start = local_bar * BEATS_PER_BAR

    tonic = root + 24
    third = tonic + (3 if quality == "minor" else 4)
    fifth = tonic + 7
    octave = tonic + 12

    # One recognizable motif with different density and endings.
    if name == "Intro":
        if local_bar % 2 == 0:
            add_note(parts, "lead", fifth, start + 0.0, 0.8, 55)
            add_note(parts, "lead", third, start + 2.5, 0.75, 51)

    elif name == "Verse":
        if local_bar % 2 == 0:
            add_note(parts, "lead", fifth, start + 0.0, 0.65, 82)
            add_note(parts, "lead", third, start + 1.5, 0.40, 73)
            add_note(parts, "lead", tonic, start + 2.5, 0.80, 78)
        else:
            add_note(parts, "lead", third, start + 1.0, 0.45, 65)
            add_note(parts, "lead", tonic, start + 3.0, 0.65, 69)

    elif name == "Breakdown":
        if local_bar % 2 == 0:
            add_note(parts, "lead", fifth, start + 1.0, 1.75, 56)

    elif name == "Buildup":
        add_note(parts, "lead", tonic, start + 0.0, 0.70, 65)
        add_note(parts, "lead", third, start + 2.0, 0.60, 70)

        if local_bar >= 4:
            add_note(parts, "lead", fifth, start + 3.0, 0.40, 76)

    elif name in ("Drop", "Climax"):
        gain = 5 if name == "Climax" else 0

        add_note(parts, "lead", fifth, start + 0.0, 0.70, 87 + gain)
        add_note(parts, "lead", third, start + 1.5, 0.40, 77 + gain)
        add_note(parts, "lead", tonic, start + 2.5, 0.45, 82 + gain)

        ending = octave if local_bar % 4 == 3 else third
        add_note(parts, "lead", ending, start + 3.25, 0.45, 78 + gain)

        # Answering note, only in the climax.
        if name == "Climax" and local_bar % 2 == 1:
            add_note(parts, "lead", fifth, start + 2.0, 0.30, 67)

    elif name == "Outro":
        if local_bar % 2 == 0:
            add_note(parts, "lead", tonic, start + 0.0, 1.8,
                     max(42, 57 - local_bar * 2))


def add_drums_and_bass(parts, section, local_bar, root, rng):
    name = section.name

    if name in ("Intro", "Breakdown", "Outro"):
        return

    start = local_bar * BEATS_PER_BAR
    last_bar = local_bar == section.bars - 1

    if name == "Verse":
        kick_beats = [0.0, 2.75] if local_bar % 2 == 0 else [0.0, 2.5]

    elif name == "Buildup":
        kick_beats = [0.0] if local_bar < 4 else [0.0, 2.5]

    else:
        kick_beats = [0.0, 2.5]

        if name == "Climax" and local_bar % 4 == 3:
            kick_beats.append(3.5)

    for beat in kick_beats:
        add_note(parts, "kick", 36, start + beat, 0.20, 112)

    if name != "Buildup":
        add_note(parts, "snare", 38, start + 2.0, 0.20, 105)

    elif local_bar < 6:
        add_note(parts, "snare", 38, start + 2.0, 0.20, 83)

    if name != "Buildup":
        add_note(parts, "bass", root, start + 0.0, 1.5, 101)

        if name == "Verse":
            if local_bar % 2 == 0:
                add_note(parts, "bass", root,
                         start + 2.75, 0.60, 91)

        else:
            add_note(parts, "bass", root,
                     start + 2.5, 0.75, 98)

            if local_bar % 4 == 3:
                add_note(parts, "bass", root + 12,
                         start + 3.5, 0.30, 73)

    # Verse is sparse; drops have eighth-note hats.
    hat_step = 1.0 if name == "Verse" else 0.5

    for step in range(int(BEATS_PER_BAR / hat_step)):
        beat = step * hat_step

        if name == "Verse" and local_bar % 4 == 2 and beat == 3.0:
            continue

        velocity = 72
        velocity += 8 if step % 2 == 0 else -7
        velocity += rng.randint(-4, 4)

        if name == "Buildup":
            velocity += min(local_bar * 2, 14)

        add_note(
            parts,
            "hats",
            42,
            start + beat,
            0.14,
            max(45, min(105, velocity)),
        )

    # Only section endings get prominent fills.
    if last_bar and name in ("Verse", "Buildup", "Drop", "Climax"):
        if name == "Buildup":
            for index in range(8):
                add_note(
                    parts,
                    "snare",
                    38,
                    start + 3.0 + index * 0.125,
                    0.08,
                    min(117, 70 + index * 6),
                )

        else:
            for index, beat in enumerate((3.0, 3.25, 3.5, 3.75)):
                add_note(
                    parts,
                    "snare",
                    38,
                    start + beat,
                    0.13,
                    69 + index * 9,
                )


def validate_sections():
    expected_start = 0

    for section in SECTIONS:
        if section.start_bar != expected_start:
            raise ValueError(
                f"Gap or overlap before section {section.name}"
            )

        if section.bars <= 0:
            raise ValueError(
                f"Invalid length for section {section.name}"
            )

        expected_start += section.bars

    if expected_start != TOTAL_BARS:
        raise ValueError(
            f"Expected {TOTAL_BARS} bars, got {expected_start}"
        )


def validate_clip(clip):
    length = clip["length"]

    if length <= 0 or clip["position"] < 0:
        raise ValueError(f"Invalid clip position/length: {clip['name']}")

    for item in clip["notes"]:
        if not 0 <= item["pitch"] <= 127:
            raise ValueError(f"Invalid MIDI pitch: {item}")

        if not 1 <= item["velocity"] <= 127:
            raise ValueError(f"Invalid MIDI velocity: {item}")

        if item["start_time"] < 0 or item["duration"] <= 0:
            raise ValueError(f"Invalid MIDI timing: {item}")

        if item["start_time"] + item["duration"] > length + 0.0001:
            raise ValueError(
                f"Note extends past clip '{clip['name']}': {item}"
            )


def build_plan(seed):
    validate_sections()
    rng = random.Random(seed)
    clips = []

    for section in SECTIONS:
        parts = {name: [] for name in TRACKS}

        for local_bar in range(section.bars):
            global_bar = section.start_bar + local_bar
            root, quality = chord_at(global_bar)

            add_chords(parts, section, local_bar, root, quality)
            add_lead(parts, section, local_bar, root, quality)

            add_drums_and_bass(
                parts,
                section,
                local_bar,
                root,
                rng,
            )

        for part_name, notes in parts.items():
            if not notes:
                continue

            clip = {
                "track_index": TRACKS[part_name],
                "position": section.start_bar * BEATS_PER_BAR,
                "length": section.bars * BEATS_PER_BAR,
                "name": f"GEN | {section.name} | {part_name}",
                "notes": sorted(
                    notes,
                    key=lambda item: (
                        item["start_time"],
                        item["pitch"],
                    ),
                ),
            }

            validate_clip(clip)
            clips.append(clip)

    return {
        "format_version": 1,
        "bpm": BPM,
        "bars": TOTAL_BARS,
        "seed": seed,
        "tracks": TRACKS,
        "sections": [
            {
                "name": section.name,
                "start_bar": section.start_bar,
                "bars": section.bars,
            }
            for section in SECTIONS
        ],
        "clips": clips,
    }


class AbletonClient:
    """
    Client for the JSON-over-TCP bridge used by the original project.

    No automatic retries: repeating create_arrangement_clip after an
    uncertain timeout could create duplicate clips.
    """

    def __init__(self, host="127.0.0.1", port=9877):
        self.sock = socket.create_connection((host, port), timeout=10)
        self.sock.settimeout(15)
        self.text_decoder = codecs.getincrementaldecoder("utf-8")()
        self.buffer = ""

    def send(self, command, params=None):
        request = json.dumps({
            "type": command,
            "params": params or {},
        })

        # Keep the original project's request format: raw JSON over TCP.
        self.sock.sendall(request.encode("utf-8"))

        decoder = json.JSONDecoder()

        while True:
            stripped = self.buffer.lstrip()

            if stripped:
                try:
                    response, end = decoder.raw_decode(stripped)
                    self.buffer = stripped[end:]
                    break

                except json.JSONDecodeError:
                    pass

            chunk = self.sock.recv(16384)

            if not chunk:
                raise ConnectionError(
                    f"Bridge closed connection during '{command}'"
                )

            self.buffer += self.text_decoder.decode(chunk)

            if len(self.buffer) > 4_000_000:
                raise RuntimeError(
                    "Bridge response is unexpectedly large"
                )

        if not isinstance(response, dict):
            raise RuntimeError(
                f"Unexpected response to '{command}': {response!r}"
            )

        if response.get("success") is False or response.get("error"):
            raise RuntimeError(
                f"Bridge rejected '{command}': {response!r}"
            )

        return response

    def close(self):
        self.sock.close()


def read_tracks(client):
    response = client.send("get_arrangement_info")
    result = response.get("result")

    if not isinstance(result, dict):
        raise RuntimeError(
            "Unexpected get_arrangement_info response: "
            f"{response!r}"
        )

    tracks = result.get("tracks")

    if not isinstance(tracks, list):
        raise RuntimeError(
            "Bridge response has no tracks list: "
            f"{response!r}"
        )

    return tracks


def find_clip_index(client, track_index, position):
    tracks = read_tracks(client)

    if track_index >= len(tracks):
        raise RuntimeError(
            f"Track {track_index} disappeared during execution"
        )

    arrangement_clips = tracks[track_index].get(
        "arrangement_clips"
    )

    if not isinstance(arrangement_clips, list):
        raise RuntimeError(
            f"Cannot inspect clips on track {track_index}"
        )

    matches = []

    for index, clip in enumerate(arrangement_clips):
        try:
            start_time = float(clip["start_time"])
        except (KeyError, TypeError, ValueError):
            continue

        if abs(start_time - position) < 0.01:
            matches.append(index)

    if len(matches) != 1:
        raise RuntimeError(
            "Cannot uniquely identify newly created clip "
            f"on track {track_index} at beat {position}. "
            "Stopped to avoid writing into the wrong clip."
        )

    return matches[0]


def apply_plan(plan, host, port):
    client = AbletonClient(host, port)

    try:
        tracks = read_tracks(client)

        # Strict preflight: never delete or overwrite existing material.
        for index in sorted(set(plan["tracks"].values())):
            if index >= len(tracks):
                raise RuntimeError(
                    f"Required track index {index} does not exist"
                )

            clips = tracks[index].get("arrangement_clips")

            if not isinstance(clips, list):
                raise RuntimeError(
                    f"Cannot verify that track {index} is empty"
                )

            if clips:
                raise RuntimeError(
                    f"Track {index} contains arrangement clips. "
                    "Use an empty project template. "
                    "No existing clips were deleted."
                )

        client.send("set_tempo", {"tempo": plan["bpm"]})

        for number, clip in enumerate(plan["clips"], start=1):
            track_index = clip["track_index"]

            client.send("create_arrangement_clip", {
                "track_index": track_index,
                "position": clip["position"],
                "length": clip["length"],
            })

            clip_index = find_clip_index(
                client,
                track_index,
                clip["position"],
            )

            client.send("add_notes_to_arrangement_clip", {
                "track_index": track_index,
                "clip_index": clip_index,
                "notes": clip["notes"],
            })

            client.send("set_arrangement_clip_property", {
                "track_index": track_index,
                "clip_index": clip_index,
                "property": "name",
                "value": clip["name"],
            })

            print(
                f"[{number}/{len(plan['clips'])}] "
                f"{clip['name']}"
            )

        client.send("set_song_time", {"time": 0.0})
        print("Done. Check the arrangement in Ableton.")

    finally:
        client.close()


def run_self_test():
    first = build_plan(seed=42)
    second = build_plan(seed=42)

    assert first == second, "Same seed must reproduce the same plan"
    assert first["bars"] == TOTAL_BARS
    assert first["clips"]

    for clip in first["clips"]:
        validate_clip(clip)

    positions_by_track = {}

    for clip in first["clips"]:
        track = clip["track_index"]
        start = clip["position"]
        end = start + clip["length"]

        positions_by_track.setdefault(track, []).append(
            (start, end)
        )

    for track, intervals in positions_by_track.items():
        intervals.sort()

        for previous, current in zip(
            intervals,
            intervals[1:],
        ):
            assert previous[1] <= current[0], (
                f"Overlapping clips on track {track}"
            )

    print("Self-test passed.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate and optionally apply an Ableton arrangement"
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Send generated clips to Ableton",
    )

    parser.add_argument(
        "--confirm-template",
        action="store_true",
        help="Confirm that an empty Ableton template is open",
    )

    parser.add_argument(
        "--self-test",
        action="store_true",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    parser.add_argument(
        "--output",
        default="arrangement_plan.json",
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=9877,
    )

    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    plan = build_plan(args.seed)

    output_path = Path(args.output)
    output_path.write_text(
        json.dumps(
            plan,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    note_count = sum(
        len(clip["notes"])
        for clip in plan["clips"]
    )

    print(
        f"Saved {output_path}: "
        f"{plan['bars']} bars, "
        f"{len(plan['clips'])} clips, "
        f"{note_count} notes."
    )

    if not args.apply:
        print(
            "Offline mode: Ableton was not modified."
        )
        return

    if not args.confirm_template:
        parser.error(
            "--apply requires --confirm-template"
        )

    apply_plan(
        plan,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()
