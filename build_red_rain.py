#!/usr/bin/env python3
"""
RED RAIN (Playboi Carti x KP Beatz x SALEM "Frost" Flip)
=========================================================
Autonomous Ableton Live 12 DAW Arrangement & Production Script
Key: A Minor (Am -> Fmaj7 -> Cmaj -> G/Em)
BPM: 150.0
DAW: Ableton Live 12 Suite via MCP / TCP Socket Bridge (localhost:9877)
"""

import os
import sys
import socket
import json
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_PATH = os.path.join(SCRIPT_DIR, "assets", "SALEM_Frost_Loop_Authentic.wav")

class AbletonClient:
    def __init__(self, host='localhost', port=9877):
        self.host = host
        self.port = port
        self.sock = None
        self.connect()

    def connect(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(10.0)

    def send(self, cmd_type, params=None):
        cmd = json.dumps({'type': cmd_type, 'params': params or {}})
        try:
            self.sock.sendall(cmd.encode('utf-8'))
        except (socket.error, BrokenPipeError):
            self.connect()
            self.sock.sendall(cmd.encode('utf-8'))

        buf = ''
        while True:
            chunk = self.sock.recv(16384)
            if not chunk:
                raise ConnectionError("Socket connection closed by Ableton MCP server")
            buf += chunk.decode('utf-8')
            try:
                return json.loads(buf)
            except json.JSONDecodeError:
                continue

    def close(self):
        if self.sock:
            self.sock.close()

def build_red_rain():
    if not os.path.exists(SAMPLE_PATH):
        print(f"Error: Sample file not found at {SAMPLE_PATH}")
        sys.exit(1)

    print("=" * 70)
    print("  PLAYBOI CARTI x KP BEATZ x SALEM - 'RED RAIN' INSTRUMENTAL BUILDER")
    print("=" * 70)

    try:
        client = AbletonClient()
    except Exception as e:
        print(f"Failed to connect to Ableton Live MCP Bridge on localhost:9877: {e}")
        print("Please ensure Ableton Live 12 is running with the MCP Remote Script active.")
        sys.exit(1)

    # 1. Transport & Global Settings
    print("\n[1/6] Setting Global Transport (150.0 BPM, 320-beat loop)...")
    client.send('set_tempo', {'tempo': 150.0})
    client.send('set_arrangement_loop', {'loop_start': 0.0, 'loop_length': 320.0, 'enabled': True})
    client.send('set_song_time', {'time': 0.0})
    client.send('set_view', {'view_name': 'Arranger'})

    # 2. Clear Existing Arrangement Clips
    print("[2/6] Clearing existing arrangement clips across all tracks...")
    info = client.send('get_arrangement_info')
    tracks = info.get('result', {}).get('tracks', [])
    for t_idx, trk in enumerate(tracks):
        clips = trk.get('arrangement_clips', [])
        for i in range(len(clips) - 1, -1, -1):
            client.send('delete_arrangement_clip', {'track_index': t_idx, 'clip_index': i})

    # 3. DSP & Distortion Chains
    print("[3/6] Dialing in heavy 808 distortion and drum processing...")
    # Track 2: 808 Pure (Drum Buss + Saturator)
    client.send('set_device_parameter', {'track_index': 2, 'device_index': 1, 'parameter_name': 'Compressor On', 'value': 1.0})
    client.send('set_device_parameter', {'track_index': 2, 'device_index': 1, 'parameter_name': 'Drive', 'value': 0.60})
    client.send('set_device_parameter', {'track_index': 2, 'device_index': 1, 'parameter_name': 'Crunch', 'value': 0.45})
    client.send('set_device_parameter', {'track_index': 2, 'device_index': 1, 'parameter_name': 'Boom Amt', 'value': 0.70})
    client.send('set_device_parameter', {'track_index': 2, 'device_index': 1, 'parameter_name': 'Boom Freq', 'value': 0.35})
    client.send('set_device_parameter', {'track_index': 2, 'device_index': 1, 'parameter_name': 'Transients', 'value': 0.60})
    client.send('set_device_parameter', {'track_index': 2, 'device_index': 2, 'parameter_name': 'Drive', 'value': 0.65})

    # Track 3: Kick (Drum Buss)
    client.send('set_device_parameter', {'track_index': 3, 'device_index': 1, 'parameter_name': 'Drive', 'value': 0.45})
    client.send('set_device_parameter', {'track_index': 3, 'device_index': 1, 'parameter_name': 'Transients', 'value': 0.70})

    # Track 4: Snare (Drum Buss)
    client.send('set_device_parameter', {'track_index': 4, 'device_index': 2, 'parameter_name': 'Drive', 'value': 0.40})
    client.send('set_device_parameter', {'track_index': 4, 'device_index': 2, 'parameter_name': 'Crunch', 'value': 0.35})

    # 4. Helper Functions
    def add_midi_clip(track_idx, pos, length, notes, name=""):
        client.send('create_arrangement_clip', {'track_index': track_idx, 'position': pos, 'length': length})
        arr_info = client.send('get_arrangement_info')
        arr_clips = arr_info['result']['tracks'][track_idx]['arrangement_clips']
        target_idx = None
        for i, c in enumerate(arr_clips):
            if abs(c['start_time'] - pos) < 0.05:
                target_idx = i
                break
        if target_idx is not None:
            client.send('add_notes_to_arrangement_clip', {
                'track_index': track_idx,
                'clip_index': target_idx,
                'notes': notes
            })
            if name:
                client.send('set_arrangement_clip_property', {
                    'track_index': track_idx,
                    'clip_index': target_idx,
                    'property': 'name',
                    'value': name
                })

    def add_audio_clips(track_idx, positions):
        for pos in positions:
            client.send('create_arrangement_audio_clip', {
                'track_index': track_idx,
                'position': pos,
                'file_path': SAMPLE_PATH
            })

    # ========================================================
    # PATTERN GENERATORS
    # ========================================================
    def get_808_notes(loops=1):
        # A Minor root notes with octave slides: A1(45)->A2(57), F1(41)->F2(53), C1(36)->C2(48), G1(43)/E1(40)
        sub_pattern = [
            (0.0, 2.5, 45, 127),
            (2.75, 0.75, 45, 120),
            (3.5, 0.5, 57, 115),
            (4.0, 2.0, 41, 127),
            (6.5, 0.75, 41, 120),
            (7.25, 0.75, 53, 115),
            (8.0, 2.25, 36, 127),
            (10.5, 1.0, 36, 120),
            (11.5, 0.5, 48, 110),
            (12.0, 1.75, 43, 127),
            (14.0, 1.0, 40, 125),
            (15.25, 0.75, 45, 120)
        ]
        notes = []
        for l in range(loops):
            offset = l * 16.0
            for start, dur, p, vel in sub_pattern:
                notes.append({'pitch': p, 'start_time': offset + start, 'duration': dur, 'velocity': vel})
        return notes

    def get_kick_notes(loops=1):
        hits = [0.0, 2.75, 4.0, 6.5, 8.0, 10.5, 12.0, 14.0]
        notes = []
        for l in range(loops):
            offset = l * 16.0
            for h in hits:
                notes.append({'pitch': 36, 'start_time': offset + h, 'duration': 0.35, 'velocity': 127})
        return notes

    def get_snare_notes(loops=1):
        notes = []
        for l in range(loops):
            offset = l * 16.0
            for b in [2.0, 6.0, 10.0, 14.0]:
                notes.append({'pitch': 38, 'start_time': offset + b, 'duration': 0.5, 'velocity': 127})
            notes.append({'pitch': 38, 'start_time': offset + 7.5, 'duration': 0.2, 'velocity': 105})
            for r in range(4):
                notes.append({'pitch': 38, 'start_time': offset + 15.0 + (r * 0.25), 'duration': 0.15, 'velocity': 85 + (r * 10)})
        return notes

    def get_hat_notes(loops=1):
        notes = []
        for l in range(loops):
            offset = l * 16.0
            for step in range(32):
                t = step * 0.5
                if (6.5 <= t < 8.0) or (14.5 <= t < 16.0):
                    continue
                vel = 112 if step % 2 == 0 else 90
                notes.append({'pitch': 42, 'start_time': offset + t, 'duration': 0.2, 'velocity': vel})
            for r in range(6):
                notes.append({'pitch': 42, 'start_time': offset + 6.5 + (r * 0.25), 'duration': 0.12, 'velocity': 85 + (r * 7)})
            for r in range(12):
                notes.append({'pitch': 42, 'start_time': offset + 14.5 + (r * 0.125), 'duration': 0.08, 'velocity': 75 + (r * 4)})
        return notes

    # 5. Writing Arrangement Clips
    print("[4/6] Placing authentic SALEM 'Frost' sample loops across all 80 bars...")
    # Find audio track index (Track 8 or first available audio track)
    audio_track_idx = 8
    add_audio_clips(audio_track_idx, [i * 16.0 for i in range(20)])

    print("[5/6] Writing 808 sub, kick punch, cavernous snares, and rolling hats...")
    # Drop 1: Bars 9-24 (32.0 -> 96.0)
    add_midi_clip(2, 32.0, 64.0, get_808_notes(4), "Drop 1 808 Blown")
    add_midi_clip(3, 32.0, 64.0, get_kick_notes(4), "Drop 1 Punch Kick")
    add_midi_clip(4, 32.0, 64.0, get_snare_notes(4), "Drop 1 Snare")
    add_midi_clip(5, 32.0, 64.0, get_hat_notes(4), "Drop 1 Houston Hats")

    # Buildup: Bars 33-40 (128.0 -> 160.0)
    add_midi_clip(4, 144.0, 16.0, get_snare_notes(1), "Buildup Snare Roll")
    add_midi_clip(5, 128.0, 32.0, get_hat_notes(2), "Buildup Hats")

    # Main Drop 2: Bars 41-56 (160.0 -> 224.0)
    add_midi_clip(2, 160.0, 64.0, get_808_notes(4), "Drop 2 808 Blown")
    add_midi_clip(3, 160.0, 64.0, get_kick_notes(4), "Drop 2 Punch Kick")
    add_midi_clip(4, 160.0, 64.0, get_snare_notes(4), "Drop 2 Snare")
    add_midi_clip(5, 160.0, 64.0, get_hat_notes(4), "Drop 2 Houston Hats")

    # Climax Drop 3: Bars 57-72 (224.0 -> 288.0)
    add_midi_clip(2, 224.0, 64.0, get_808_notes(4), "Climax 808 Blown")
    add_midi_clip(3, 224.0, 64.0, get_kick_notes(4), "Climax Punch Kick")
    add_midi_clip(4, 224.0, 64.0, get_snare_notes(4), "Climax Snare")
    add_midi_clip(5, 224.0, 64.0, get_hat_notes(4), "Climax Houston Hats")

    # 6. Finalize
    print("[6/6] Rewinding transport to 0.0 and focusing Arranger view...")
    client.send('set_song_time', {'time': 0.0})
    client.close()

    print("\n" + "=" * 70)
    print("  SUCCESS: 'RED RAIN' INSTRUMENTAL IS FULLY BUILT IN ABLETON LIVE 12!")
    print("  Hit Spacebar in Ableton Live to play.")
    print("=" * 70)

if __name__ == '__main__':
    build_red_rain()
