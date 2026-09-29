# 🩸 RED RAIN — Playboi Carti x KP Beatz x SALEM "Frost" Flip

[![Ableton Live 12](https://img.shields.io/badge/Ableton%20Live-12%20Suite-000000?style=for-the-badge&logo=abletonlive&logoColor=white)](https://ableton.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MCP Extended](https://img.shields.io/badge/Bridge-Ableton%20MCP-FF4088?style=for-the-badge)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **Autonomous programmatic reconstruction and arrangement of the legendary unreleased snippet *"RED RAIN"* (Playboi Carti / KP Beatz, 8.26.26), which flips the distorted witch-house anthem *"Frost"* by SALEM (*King Night*).**

---

## ⚡ Overview & Sonic Blueprint

This repository contains the complete autonomous builder, sound design DSP chains, MIDI score, and master arrangement for **Ableton Live 12 Suite**.

Unlike synthetic MIDI approximations, this project uses the **original, grimy, analog-distorted audio sample of SALEM's *"Frost"*** combined with a blown-out, earth-shaking **Spinz/BWB 808**, hard-clipping punch kicks, cavernous reverb snares, and Houston screwed rolling hats.

```
Key:         A Minor (Am -> Fmaj7 -> Cmaj -> G/Em)
Tempo:       150.0 BPM (Double-Time Trap / 75.0 BPM Half-Time Feel)
Arrangement: 80 Bars / 320 Beats
DAW:         Ableton Live 12 Suite (MCP Socket Bridge localhost:9877)
```

---

## 🎹 Harmonic & Production Architecture

### 1. The Witch House Sample (Track 8)
- **Source:** *SALEM — "Frost"* (*King Night*, 2010).
- **Processing:** Distorted analog wall of sound with screaming cathedral soprano opera vocal layers warped seamlessly across the arrangement at 150 BPM.

### 2. Blown-Out 808 (Track 2)
- **Harmonic Flow:** $A_1 \ (55.0\text{ Hz}) \to F_1 \ (43.65\text{ Hz}) \to C_1 \ (32.7\text{ Hz}) \to G_1 \ (49.0\text{ Hz})$
- **Octave Slides:** High velocity slides up to $A_2$ (110 Hz), $F_2$, and $C_2$.
- **DSP Chain:** 
  - `Drum Buss`: Drive = 60%, Crunch = 45% (filthy high-frequency rasp), Boom = 70% @ 35–55 Hz, Transients = +0.60, Compressor = ON.
  - `Saturator`: Drive = +10 dB (Sinoid Fold / Hard Curve).

### 3. Drum Section (Tracks 3, 4, 5)
- **Kick (Track 3):** Punchy industrial transient kick clipping hard with the 808 sub.
- **Snare (Track 4):** Crisp snare on the 3rd beat of every bar + 32nd ghost rolls and accent bounces.
- **Hi-Hats (Track 5):** Screwed 8th note base with high-speed 1/32 triplet and laser rolls.

---

## 🎼 Arrangement Structure

| Bars | Beats | Section | Instrumentation |
| :--- | :--- | :--- | :--- |
| **1 – 8** | 0 – 32 | **Intro** | Ethereal distorted SALEM sample floating into the void |
| **9 – 24** | 32 – 96 | **Drop 1 (Verse)** | Full blast: Blown 808 + Punch Kick + Snare + Rolling Hats + Sample |
| **25 – 32** | 96 – 128 | **Breakdown** | Drums cut out; pure witch-house atmosphere |
| **33 – 40** | 128 – 160 | **Buildup** | Rising snare rolls, 32nd laser hats, sample swell |
| **41 – 56** | 160 – 224 | **Main Drop 2** | Devastating maximum-impact 808 drop |
| **57 – 72** | 224 – 288 | **Climax Drop 3** | Full-frequency peak energy |
| **73 – 80** | 288 – 320 | **Outro** | Reverb wash decay into silence |

---

## 🚀 Quick Start & Autonomous Execution

### Prerequisites
1. **Ableton Live 12 Suite** with the [Ableton MCP Remote Script](https://github.com) running on port `9877`.
2. **Python 3.10+**.

### Installation & Run

```bash
# Clone this repository
git clone https://github.com/millymilly29/carti-red-rain-salem-flip.git
cd carti-red-rain-salem-flip

# Run the autonomous builder
python3 build_red_rain.py
```

The script will automatically:
1. Connect to Ableton Live 12 over TCP socket `localhost:9877`.
2. Set tempo to **150.0 BPM** and configure the 320-beat arrangement loop.
3. Configure DSP parameters on Drum Buss and Saturator devices.
4. Place the authentic SALEM audio sample loops across all 80 bars on Track 8.
5. Program all MIDI 808, Kick, Snare, and Hi-Hat clips across the arrangement.
6. Rewind transport to `0.0`.

---

## 📁 Repository Structure

```
carti-red-rain-salem-flip/
├── build_red_rain.py           # Master autonomous Ableton Live 12 builder
├── assets/
│   ├── SALEM_Frost_Loop_Authentic.wav  # Clean 150 BPM warped SALEM "Frost" sample
│   └── RED_RAIN_KP_SNIPPET_RAW.wav     # Reference audio snippet
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
└── README.md                   # Project documentation
```

---

## 📜 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

---

*Engineered with [Antigravity](https://github.com) x Ableton Live 12 MCP.*
