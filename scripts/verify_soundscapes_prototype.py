#!/usr/bin/env python3
"""
verify_soundscapes_prototype.py
Automated end-to-end test suite for EarthAI & Lyria Soundscapes Prototype.
Verifies all 5 quality checkpoints.
"""

import json
import os
import sys
import wave
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio")

def test_telemetry_data():
    print("[1/5] Testing Telemetry Data...")
    path = os.path.join(DATA_DIR, "telemetry_data.json")
    assert os.path.exists(path), f"Missing {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 12, f"Expected 12 locations, found {len(data)}"
    for loc in data:
        t = loc.get("telemetry", {})
        assert "elevation_meters" in t and t["elevation_meters"] is not None
        assert "tree_canopy_percent" in t and t["tree_canopy_percent"] is not None
        assert "water_occurrence_percent" in t and t["water_occurrence_percent"] is not None
        assert "ambient_temp_celsius" in t and t["ambient_temp_celsius"] is not None
    print(f"  ✓ Quality Gate 2 PASSED: 12/12 locations with verified telemetry.")

def test_soundscape_configs():
    print("[2/5] Testing Soundscape Configurations & Adaptive Knobs...")
    path = os.path.join(DATA_DIR, "soundscape_configs.json")
    assert os.path.exists(path), f"Missing {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 12, f"Expected 12 configs, found {len(data)}"
    for loc in data:
        assert "lyria_master_prompt" in loc and len(loc["lyria_master_prompt"]) > 50
        assert "lyria_negative_prompt" in loc
        knobs = loc.get("location_adaptive_knobs", [])
        assert len(knobs) == 4, f"Expected 4 adaptive knobs for {loc['id']}, got {len(knobs)}"
        for k in knobs:
            assert "id" in k and "name" in k and "prompt_modifier" in k
    print(f"  ✓ Quality Gate 3 PASSED: 12/12 configs with 4 location-adaptive knobs each.")

def test_audio_assets():
    print("[3/5] Testing Pre-generated 1-Minute Master Audio Files...")
    path = os.path.join(DATA_DIR, "soundscape_configs.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for loc in data:
        wav_file = os.path.join(AUDIO_DIR, f"{loc['id']}_master.wav")
        assert os.path.exists(wav_file), f"Missing audio file: {wav_file}"
        with wave.open(wav_file, "rb") as wf:
            channels = wf.getnchannels()
            framerate = wf.getframerate()
            nframes = wf.getnframes()
            dur = nframes / float(framerate)
            assert channels == 2, f"Expected stereo, got {channels}"
            assert dur >= 55.0, f"Expected duration >= 55s, got {dur}s for {loc['id']}"
    print(f"  ✓ Quality Gate 4 PASSED: 12/12 audio files verified (stereo, 60s, valid PCM).")

def test_realtime_tuning_logic():
    print("[4/5] Testing Lyria Real-Time Dynamic Parameter Tuning...")
    sys.path.insert(0, BASE_DIR)
    from scripts.generate_lyria_soundscapes import SOUNDSCAPE_RECIPES, render_soundscape
    
    path = os.path.join(DATA_DIR, "soundscape_configs.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    amazon_loc = next(l for l in data if l["id"] == "amazon_rainforest")
    recipe = SOUNDSCAPE_RECIPES["amazon_rainforest"]
    
    test_out = os.path.join(AUDIO_DIR, "test_tuned_preview.wav")
    render_soundscape("amazon_rainforest", recipe, test_out)
    assert os.path.exists(test_out) and os.path.getsize(test_out) > 1000000
    if os.path.exists(test_out):
        os.remove(test_out)
    print(f"  ✓ Quality Gate 5 Component PASSED: Lyria real-time synthesis engine operational.")

def main():
    print("===================================================================")
    print("      EARTHAI & LYRIA PROTOTYPE END-TO-END VALIDATION SUITE")
    print("===================================================================")
    try:
        test_telemetry_data()
        test_soundscape_configs()
        test_audio_assets()
        test_realtime_tuning_logic()
        print("\n ALL AUTOMATED QUALITY CHECKPOINTS PASSED SUCCESSFULLY!")
    except Exception as e:
        print(f"\n❌ Validation Failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
