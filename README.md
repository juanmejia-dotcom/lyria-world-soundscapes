# 🌍 EarthAI Soundscapes (Lyria Neural Studio)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Vertex%20AI-4285F4.svg)](https://cloud.google.com/vertex-ai)
[![Google DeepMind](https://img.shields.io/badge/DeepMind-Lyria%202-EA4335.svg)](https://deepmind.google/)
[![Earth Engine](https://img.shields.io/badge/Google-Earth%20Engine-34A853.svg)](https://earthengine.google.com/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

An interactive bioacoustic intelligence platform that translates planetary satellite observation telemetry (canopy density, elevation, topographic relief, precipitation rate, and wind vectors) into dual-engine spatial soundscapes:
1. **Authentic Field Recording Soundscape**: Multi-track spatial audio master composed of regional natural recordings.
2. **Google DeepMind Lyria 2 Neural Soundscape**: Ultra-realistic 48kHz neural environmental biophony and geophony synthesized via Google DeepMind's `lyria-002` foundation model on Vertex AI.

---

## 🎧 Dual-Engine Audio Architecture

Every global location features two independent, broadcast-mastered audio engines:

```
📍 Selected Global Location (e.g., Central Amazon Rainforest)
│
├── 🔊 Engine 1: Authentic Field Recording Soundscape
│   ├── Audio Source: Multi-track stem mix of high-fidelity field recordings (Wikimedia Commons / NPS)
│   ├── Processing: Multi-band EQ, spatial stereophony, dynamic range compression, EBU R128 (-16 LUFS)
│   └── Characteristics: Authentic acoustic grounding with documented species and environmental biophony
│
└── 🔮 Engine 2: Google DeepMind Lyria 2 Neural Soundscape
    ├── Synthesis Model: Google DeepMind Lyria 2 (`lyria-002`) on Vertex AI
    ├── Conditioning: Real-time satellite telemetry (canopy %, elevation, water occurrence %, rain rate, wind speed)
    ├── Constraints: STRICT ZERO LYRICS / ZERO VOCALS / ZERO INSTRUMENTS (Pure Environmental Acoustics)
    └── Characteristics: Generative continuous bioacoustic simulation modeled on environmental acoustics
```

---

## 🌍 Planetary Locations & Biomes

| # | Location | Region | Biome | Key Acoustic Elements |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Tongass National Forest** | Alaska, USA | Coastal Temperate Rainforest & Glacial Fjords | Bald eagle chatter, glacier meltwater torrents, Pacific surf, Sitka spruce rain drips |
| **2** | **Grand Canyon National Park** | Arizona, USA | Arid Deep Gorge & Riparian Corridor | Red-tailed hawk canyon shrieks, gorge thermal updrafts, Colorado River rapids roar |
| **3** | **Central Amazon Rainforest** | Amazonas, Brazil | Tropical Lowland Wet Rainforest | Toco toucan yelps, night tree frogs, cicada chorus, heavy broadleaf canopy drip |
| **4** | **Borneo & Kalimantan** | Central Kalimantan, Indonesia | Lowland Dipterocarp & Peat Swamp Forest | Lar gibbon dawn chorus, peat swamp river murmurs, equatorial thunder, canopy insects |
| **5** | **Sundarbans Mangrove Delta** | Khulna, Bangladesh | Coastal Mangrove Estuary & Tidal Delta | Brackish tidal surges, mangrove prop-root current, coastal amphibians, estuary breeze |
| **6** | **Western Ghats Mountain Range** | Kerala / Tamil Nadu, India | Montane Shola-Grassland & Tropical Moist Forest | Anamalai dawn chorus, Shola stream cascades, Southwest Monsoon thunder rolls |
| **7** | **Daintree Rainforest & Coast** | Queensland, Australia | Coastal Tropical Rainforest & Coral Sea Interface | Coral Sea beach surf, tropical broadleaf canopy rustle, endemic rainforest bird calls |
| **8** | **Great Barrier Reef** | Coral Sea, Australia | Coral Atoll & Pelagic Open Marine | Rolling open-ocean wave swells, shallow coral reef bubbling current stream, hydroacoustics |
| **9** | **Greater Khingan Taiga** | Inner Mongolia, China | Boreal Taiga Coniferous Forest | Subzero Siberian winter wind whistling through Dahurian larch needles, boreal silence |
| **10** | **Valdivian Rainforest** | Los Ríos, Chile | Southern Temperate Rainforest & Andean Cordillera | Turbulent Andean mountain torrents, Pacific westerlies, Alerce tree rain drips |
| **11** | **Great Bear Rainforest** | British Columbia, Canada | Pacific Coastal Temperate Rainforest & Granite Fjords | Coastal Sea Wolf pack howling, salmon spawning rapids, Pacific fjord wave surf |
| **12** | **Mount Everest & Khumbu Icefall** | Solukhumbu, Nepal | Alpine Tundra & Glacial Col (>5,000m) | Subzero jet-stream gales, thin-air acoustic damping (<350 hPa), glacial serac cracking |

---

## 🔬 Earth Observation Data Translation Matrix

| Satellite Dataset | Ingested Parameter | Physical & Acoustic Translation | Soundscape Impact |
| :--- | :--- | :--- | :--- |
| **Hansen Global Forest Change (30m)** | `tree_canopy_percent` | Dense closed canopy (>75%) acts as an acoustic absorption chamber ($T_{60} < 0.8\text{s}$), damping long-range reflections while amplifying rich biophony. | Multi-tier canopy cicadas, foliage moisture drips |
| **Copernicus GLO-30 DEM** | `elevation_meters`, `slope_degrees` | High altitude (>4,000m) creates thin atmospheric air pressure (<350 hPa) that severely damps high frequencies. Steep slopes produce specular multi-surface echoes. | High-frequency acoustic damping, cavernous slapback echoes |
| **EC JRC Global Surface Water** | `water_occurrence_percent` | High surface water permanence (>70%) shifts acoustic propagation into hydroacoustic dominance (sound travels 4.3x faster in water). | Rolling ocean swells, rushing mountain rapids |
| **ECMWF ERA5-Land Hourly** | `precipitation_rate_mm_h` | Heavy rainfall (>5 mm/h) generates dominant geophonic white noise (Score: >85/100) masking low-amplitude biophony. | Roaring monsoon downpour, thunder claps |
| **ECMWF ERA5 Reanalysis** | `wind_speed_ms`, `wind_dir` | High wind speed (>10 m/s) generates low-frequency aerodynamic rumble and mechanical needle friction. | Howling subzero gales, canopy sway |

---

## 🚀 Quick Start

### Prerequisites
* Python 3.10+
* `ffmpeg` (for audio processing and streaming)

### 1. Clone & Setup
```bash
git clone https://github.com/juanmejia-dotcom/lyria-world-soundscapes.git
cd lyria-world-soundscapes
```

### 2. Run the Local Server
```bash
python3 server.py 8085
```
Open **[http://localhost:8085](http://localhost:8085)** in your browser.

---

## 🛠️ Project Structure

```
.
├── data/
│   ├── earthai_telemetry.json        # Extracted Earth Engine biophysical telemetry (12 locations)
│   └── soundscape_configs.json       # Soundscape prompts, acoustic derivations, and provenance
├── scripts/
│   ├── generate_all_lyria2_soundscapes.py  # Vertex AI Lyria 2 batch generation pipeline
│   ├── master_lyria_audio.py               # EBU R128 broadcast loudness mastering suite
│   ├── mix_realistic_soundscapes.py        # Multi-track spatial audio mixer (ffmpeg)
│   └── verify_soundscapes_prototype.py     # Automated prototype validation suite
├── static/
│   ├── audio/                        # 24 Master 48kHz Stereo 16-bit PCM Audio Files
│   ├── css/style.css                 # Material Design 3 styling and responsive layout
│   ├── js/app.js                     # Web Audio API dual-player visualizer logic
│   └── index.html                    # Responsive single-page application
├── server.py                         # Standalone Python HTTP server with byte-range streaming
└── README.md
```

---

## 📄 License
Apache 2.0. See [LICENSE](LICENSE) for details.
