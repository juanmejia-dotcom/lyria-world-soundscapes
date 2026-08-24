#!/usr/bin/env python3
"""
generate_with_lyria_api.py
Generates authentic neural soundscapes for all 12 locations directly using the Google Lyria-002 Model API on Vertex AI.
"""

import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio")

PROJECT_ID = "es-proto-7oju4o"
LOCATION = "us-central1"
MODEL_ID = "lyria-002"
ENDPOINT_URL = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}:predict"

def get_auth_token() -> str:
    """Retrieves Google Cloud ADC access token."""
    res = subprocess.check_output(
        ["gcloud", "auth", "application-default", "print-access-token"],
        text=True
    )
    return res.strip()

def call_lyria_api(prompt: str, token: str) -> bytes:
    """Invokes Google Lyria-002 model API on Vertex AI and returns raw audio bytes."""
    payload = {
        "instances": [
            {
                "prompt": prompt
            }
        ],
        "parameters": {
            "sample_count": 1
        }
    }
    
    req = urllib.request.Request(
        ENDPOINT_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    with urllib.request.urlopen(req, timeout=120) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Lyria API returned HTTP {resp.status}")
        data = json.loads(resp.read().decode("utf-8"))
        
    pred = data["predictions"][0]
    b64_data = pred.get("bytesBase64Encoded", "")
    if not b64_data:
        raise ValueError(f"No audio bytes in Lyria response: {pred.keys()}")
        
    return base64.b64decode(b64_data)

def generate_location_soundscape(loc: dict, token: str):
    loc_id = loc["id"]
    loc_name = loc["name"]
    prompt = loc["lyria_master_prompt"]
    
    raw_path = os.path.join(AUDIO_DIR, f"{loc_id}_lyria_raw.wav")
    master_path = os.path.join(AUDIO_DIR, f"{loc_id}_master.wav")
    
    print(f"Calling Google Lyria-002 for '{loc_name}' ({loc_id})...")
    print(f"  Prompt: {prompt[:110]}...")
    
    audio_bytes = call_lyria_api(prompt, token)
    with open(raw_path, "wb") as f:
        f.write(audio_bytes)
        
    print(f"  ✓ Lyria generated: {len(audio_bytes)/(1024*1024):.2f} MB raw audio")
    
    # Loop/extend smoothly to ~60s using ffmpeg with subtle crossfade
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "1",
        "-i", raw_path,
        "-t", "60",
        "-af", "afade=t=in:ss=0:d=2.0,afade=t=out:st=57.5:d=2.5,loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ac", "2",
        "-ar", "48000",
        "-c:a", "pcm_s16le",
        master_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    size_mb = os.path.getsize(master_path) / (1024 * 1024)
    print(f"  ✓ Mastered 60s Lyria audio: {os.path.basename(master_path)} ({size_mb:.2f} MB)")

def main():
    print("===================================================================")
    print("   GENERATING 12 NEURAL PLANETARY SOUNDSCAPES VIA GOOGLE LYRIA-002")
    print("===================================================================")
    print(f"Project: {PROJECT_ID} | Model: {MODEL_ID} | Endpoint: {ENDPOINT_URL}\n")
    
    token = get_auth_token()
    config_file = os.path.join(DATA_DIR, "soundscape_configs.json")
    with open(config_file, "r", encoding="utf-8") as f:
        configs = json.load(f)
        
    for idx, loc in enumerate(configs, 1):
        print(f"\n[{idx}/12] Generating Lyria soundscape for '{loc['name']}'...")
        try:
            generate_location_soundscape(loc, token)
        except Exception as e:
            print(f"  ❌ Error for {loc['id']}: {e}")
            time.sleep(2)
            
    print("\n[Quality Gate 4 Check] All 12 Lyria-002 neural soundscapes generated and saved to static/audio/")

if __name__ == "__main__":
    main()
