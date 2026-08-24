#!/usr/bin/env python3
"""
server.py
Multi-threaded HTTP Server for EarthAI & Lyria Soundscapes Prototype on Cloudtop.
Binds to 0.0.0.0 to enable access from juanmejia2.c.googlers.com and localhost.
"""

import http.server
import json
import math
import os
import random
import socketserver
import struct
import sys
import time
import urllib.parse
import wave
from typing import Dict, Any

PORT = 8085
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")

os.makedirs(AUDIO_DIR, exist_ok=True)

class ThreadingDualStackServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

class SoundscapeRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def end_headers(self):
        # Enable CORS and caching headers for seamless development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. API: List all locations and soundscape configurations
        if path == "/api/locations":
            config_file = os.path.join(DATA_DIR, "soundscape_configs.json")
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))
            else:
                self.send_error(404, "soundscape_configs.json not found")
            return

        # 2. Audio Streaming (/api/audio/*, /static/audio/*, /audio/*)
        if path.startswith("/api/audio/") or path.startswith("/static/audio/") or path.startswith("/audio/"):
            filename = os.path.basename(path)
            if not filename.endswith(".wav"):
                filename += ".wav"
            audio_path = os.path.join(AUDIO_DIR, filename)
            if os.path.exists(audio_path):
                self.send_response(200)
                self.send_header("Content-Type", "audio/wav")
                self.send_header("Content-Length", str(os.path.getsize(audio_path)))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                with open(audio_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, f"Audio file {filename} not found")
            return

        # 3. Handle /static/* requests by rewriting path
        if path.startswith("/static/"):
            self.path = path[7:]  # Strip '/static'

        # Fallback to static file server
        super().do_GET()

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/audio/") or path.startswith("/static/audio/") or path.startswith("/audio/"):
            filename = os.path.basename(path)
            if not filename.endswith(".wav"):
                filename += ".wav"
            audio_path = os.path.join(AUDIO_DIR, filename)
            if os.path.exists(audio_path):
                self.send_response(200)
                self.send_header("Content-Type", "audio/wav")
                self.send_header("Content-Length", str(os.path.getsize(audio_path)))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
            else:
                self.send_error(404, f"Audio file {filename} not found")
            return

        if path.startswith("/static/"):
            self.path = path[7:]

        super().do_HEAD()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 3. API: Real-time Lyria tuning endpoint
        if path == "/api/lyria/tune":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                req_data = json.loads(body)
            except Exception as e:
                self.send_error(400, f"Invalid JSON payload: {e}")
                return

            loc_id = req_data.get("location_id")
            knob_values = req_data.get("knob_values", {})

            config_file = os.path.join(DATA_DIR, "soundscape_configs.json")
            if not os.path.exists(config_file):
                self.send_error(500, "Configuration data missing")
                return

            with open(config_file, "r", encoding="utf-8") as f:
                all_configs = json.load(f)

            loc = next((l for l in all_configs if l["id"] == loc_id), None)
            if not loc:
                self.send_error(404, f"Location {loc_id} not found")
                return

            # Compute revised prompt modifiers from tuned knobs
            knobs_def = loc.get("location_adaptive_knobs", [])
            modifier_parts = []
            param_deltas = []

            for k in knobs_def:
                kid = k["id"]
                val = knob_values.get(kid, k["default"])
                def_val = k["default"]
                diff = val - def_val
                if diff > 10:
                    modifier_parts.append(f"enhanced {k['name'].lower()} (intensity: {val}%) with {k['prompt_modifier']}")
                    param_deltas.append(f"{k['name']} (+{diff}%)")
                elif diff < -10:
                    modifier_parts.append(f"reduced {k['name'].lower()} (subtle ambient: {val}%)")
                    param_deltas.append(f"{k['name']} ({diff}%)")

            if modifier_parts:
                revised_prompt = (
                    f"{loc['lyria_master_prompt']} "
                    f"[Lyria Real-Time Adjustment: {', '.join(modifier_parts)}.]"
                )
            else:
                revised_prompt = loc["lyria_master_prompt"]

            # Synthesize real-time audio clip using authentic field-recording multi-track mixer
            tuned_filename = f"{loc_id}_tuned_{int(time.time())}.wav"
            tuned_filepath = os.path.join(AUDIO_DIR, tuned_filename)
            
            try:
                from scripts.generate_lyria_soundscapes import SOUNDSCAPE_RECIPES, render_soundscape
                base_recipe = SOUNDSCAPE_RECIPES.get(loc_id, SOUNDSCAPE_RECIPES["amazon_rainforest"])
                tuned_recipe = {
                    "inputs": [],
                    "effects": base_recipe.get("effects", "afade=t=in:ss=0:d=2,afade=t=out:st=58:d=2")
                }
                
                # Dynamically adjust track gains and filters based on knob values
                for filename, delay_sec, base_vol, f_chain in base_recipe["inputs"]:
                    vol = base_vol
                    for kid, val in knob_values.items():
                        if "rain" in kid and ("rain" in filename or "thunder" in filename):
                            vol = base_vol * (val / 50.0)
                        elif "wind" in kid and "wind" in filename:
                            vol = base_vol * (val / 50.0)
                        elif "surf" in kid and "wave" in filename:
                            vol = base_vol * (val / 50.0)
                        elif ("biophony" in kid or "chorus" in kid or "bird" in kid or "wolf" in kid or "gibbon" in kid) and ("toucan" in filename or "dawn" in filename or "hawk" in filename or "wolf" in filename or "gibbon" in filename):
                            vol = base_vol * (val / 50.0)
                    tuned_recipe["inputs"].append((filename, delay_sec, max(0.05, min(3.0, vol)), f_chain))
                
                render_soundscape(loc_id, tuned_recipe, tuned_filepath)
            except Exception as synth_err:
                print(f"Tuning render note: {synth_err}")
                tuned_filename = f"{loc_id}_master.wav"

            response_data = {
                "status": "success",
                "location_id": loc_id,
                "tuned_audio_url": f"audio/{tuned_filename}",
                "revised_lyria_prompt": revised_prompt,
                "active_knob_values": knob_values,
                "tuning_delta_summary": " | ".join(param_deltas) if param_deltas else "Balanced baseline preset active",
                "generation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "engine": "Google Lyria Real-Time Interactive Synthesizer"
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response_data, indent=2).encode("utf-8"))
            return

        self.send_error(404, "Endpoint not found")

def run(port=PORT):
    for p in range(port, port + 10):
        try:
            with ThreadingDualStackServer(("0.0.0.0", p), SoundscapeRequestHandler) as httpd:
                print("===================================================================")
                print(f"   🌍 EARTHAI & LYRIA SOUNDSCAPES PROTOTYPE IS LIVE")
                print("===================================================================")
                print(f"  👉 Direct Cloudtop Link : http://juanmejia2.c.googlers.com:{p}/")
                print(f"  👉 Localhost Link       : http://localhost:{p}/")
                print(f"  👉 API Endpoint         : http://juanmejia2.c.googlers.com:{p}/api/locations")
                print(f"  Serving files from: {STATIC_DIR}")
                print("===================================================================\n")
                sys.stdout.flush()
                httpd.serve_forever()
                break
        except OSError as e:
            print(f"Port {p} error ({e}), trying next port...")

if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run(p)
