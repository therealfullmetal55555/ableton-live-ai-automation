# 🎛️ Ableton Live 12 Autonomous AI Arrangement & DSP Engine

[![Ableton Live 12](https://img.shields.io/badge/Ableton%20Live-12%20Suite-000000?style=for-the-badge&logo=abletonlive&logoColor=white)](https://ableton.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MCP Protocol](https://img.shields.io/badge/Protocol-MCP%20%2F%20TCP%20Bridge-FF4088?style=for-the-badge)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **A programmatic, autonomous AI framework for full-scale music production, timeline arrangement, MIDI composition, and real-time DSP device parameter manipulation in Ableton Live 12 Suite via TCP Socket / Model Context Protocol (MCP).**

---

## ⚡ System Architecture

This project demonstrates programmatic bi-directional control of Ableton Live 12 using a custom Python Remote Script socket bridge (`localhost:9877`). An AI agent or Python script can autonomously construct complete, broadcast-ready musical arrangements in seconds.

```
┌─────────────────────────┐          JSON over TCP Socket          ┌─────────────────────────┐
│     AI Agent / Script   │ ─────────────────────────────────────► │  Ableton Live 12 Suite  │
│                         │                                        │  (Remote Script Bridge) │
│  - Timeline Arranger    │ ◄───────────────────────────────────── │                         │
│  - MIDI Generator       │             State & Telemetry          │  - Transport & Tempo    │
│  - DSP Chain Controller │                                        │  - Track & Device Trees │
│  - Audio Clip Warper    │                                        │  - MIDI & Audio Clips   │
└─────────────────────────┘                                        └─────────────────────────┘
```

---

## 🌟 Key Capabilities

### 1. Multi-Track Arrangement Automation
- Full 80-bar / 320-beat structured timeline generation.
- Programmatic division into distinct song sections: **Intro**, **Drop 1 (Verse)**, **Breakdown**, **Buildup**, **Main Drop 2**, **Climax Drop 3**, and **Outro**.
- Transport manipulation: dynamic tempo adjustment (BPM), loop region setup, cue points, and playhead positioning.

### 2. Procedural MIDI Generation & Polyphony
- Sub-bass patterns with micro-timed pitch-slide intervals and octave shifts.
- Dynamic drum scoring: transient kicks, 1/32 snare roll accelerations, and multi-resolution hi-hat patterns (8th notes, triplets, 32nd laser rolls).
- Velocity mapping and duration quantization.

### 3. Real-Time DSP Device Parameter Control
- Direct hardware/software parameter automation via Live's native device tree:
  - **`Drum Buss`**: `Drive`, `Crunch`, `Boom Amt`, `Boom Freq`, `Transients`, `Compressor On`.
  - **`Saturator`**: `Drive`, `Curve Type`, `Output Gain`, `Dry/Wet`.
  - **`Auto Filter`**, **`Reverb`**, **`Delay`**, and **`Chorus-Ensemble`**.

### 4. Audio Clip Slicing & Warping
- Automatic placement of audio assets directly onto arranger tracks (`create_arrangement_audio_clip`).
- Seamless loop boundary synchronization aligned with project tempo.

---

## 🚀 Quick Start

### Prerequisites
1. **Ableton Live 12 Suite** installed on macOS or Windows.
2. **Ableton MCP Remote Script** active in Ableton Live Preferences $\to$ `Link, Tempo & MIDI` $\to$ `Control Surfaces`.
3. **Python 3.10+**.

### Installation & Execution

```bash
# Clone repository
git clone https://github.com/therealfullmetal55555/ableton-live-ai-automation.git
cd ableton-live-ai-automation

# Run the autonomous arrangement engine
python3 ableton_ai_automation.py
```

---

## 📡 MCP / Socket Command Reference

The automation engine communicates via structured JSON payloads:

```python
# 1. Set Global Tempo & Transport
client.send("set_tempo", {"tempo": 150.0})
client.send("set_arrangement_loop", {"loop_start": 0.0, "loop_length": 320.0, "enabled": True})
client.send("set_song_time", {"time": 0.0})

# 2. Create Arrangement MIDI Clip & Inject Notes
client.send("create_arrangement_clip", {"track_index": 2, "position": 32.0, "length": 64.0})
client.send("add_notes_to_arrangement_clip", {
    "track_index": 2,
    "clip_index": 0,
    "notes": [
        {"pitch": 45, "start_time": 0.0, "duration": 2.5, "velocity": 127},
        {"pitch": 57, "start_time": 3.5, "duration": 0.5, "velocity": 115}
    ]
})

# 3. Modify DSP Device Parameters
client.send("set_device_parameter", {
    "track_index": 2,
    "device_index": 1,
    "parameter_name": "Drive",
    "value": 0.60
})

# 4. Insert Audio Sample Clip
client.send("create_arrangement_audio_clip", {
    "track_index": 8,
    "position": 0.0,
    "file_path": "/path/to/sample.wav"
})
```

---

## 📁 Repository Structure

```
.
├── ableton_ai_automation.py    # Master AI arrangement & DSP execution script
├── assets/
│   ├── sample_loop.wav         # Audio loop asset
│   └── reference_snippet.wav   # Reference audio
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
└── README.md                   # Technical documentation
```

---

## 📜 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
