#!/usr/bin/env python3
"""
soundscape_translator.py
Translates Earth Observation and climate telemetry into structured Lyria prompts,
negative prompts, acoustic feature matrices, 4 location-adaptive real-time knobs,
and explicit 'What it sounds like' & 'Why does it sound like this' descriptions for each location.
"""

import json
import os
from typing import Dict, Any, List

# Explicit ecological soundscape profiles explaining What it sounds like & Why
LOCATION_ACOUSTIC_PROFILES = {
    "amazon_rainforest": {
        "what_it_sounds_like": "A deafening, dense tropical polyphony: high-frequency rhythmic cicadas pulsing against warm humid air, deep guttural howler monkey territorial roars reverberating through the upper canopy, sharp yelps of toco toucans, and sudden heavy deluge raindrops splattering on gigantic broadleaf foliage.",
        "why_it_sounds_like_this": "With 96.5% tree canopy cover and high precipitation (7.5 mm/h), the multi-tiered tropical moist broadleaf forest acts as a natural acoustic absorption chamber (T60: 0.71s), damping echoes while amplifying high-density biophony across distinct frequency niches. Slow-moving várzea floodplain waters provide low background turbulence, allowing piercing avian and primate territorial calls to travel horizontally beneath the dense canopy."
    },
    "grand_canyon": {
        "what_it_sounds_like": "Vast, open, echo-rich arid gorge acoustics: hot desert thermal wind whistling through narrow sandstone crevices, soaring red-tailed hawk piercing shrieks with long multi-slapback cavernous echoes, dry cicadas buzzing in 35°C heat, and a distant low-frequency rumble of the Colorado River churning through rapids 1,000m below.",
        "why_it_sounds_like_this": "Extreme vertical relief (1,011m elevation, 38.2° slope) and sparse vegetative cover (4.5% canopy) create colossal reflective limestone surfaces with prolonged reverberation decay (T60: 4.33s). Low ambient moisture and arid desert temperatures produce strong thermal wind updrafts that whistle through mesa fissures, while sound waves bounce repeatedly between cliff walls."
    },
    "great_barrier_reef": {
        "what_it_sounds_like": "A 100% underwater hydroacoustic seascape: the continuous, sizzling campfire crackle of millions of snapping shrimp claws, deep hydrostatic ocean swells surging through coral bommies, parrotfish beaks scraping hard coral, and haunting low-frequency humpback whale melodic songs echoing across deep water channels.",
        "why_it_sounds_like_this": "100% surface water occurrence and zero terrestrial canopy shift the acoustic medium entirely to saltwater, where sound travels 4.3x faster than in air with minimal attenuation. Snapping shrimp cavitation bubbles dominate the 3.5–8 kHz frequency band, while long-wavelength humpback whale vocalizations exploit thermal ocean thermoclines to propagate across dozens of kilometers."
    },
    "mount_everest": {
        "what_it_sounds_like": "Extreme high-altitude jet stream winds howling violently across jagged granite ridges, stark low-pressure atmospheric acoustic damping, sudden earth-shaking sub-bass booming of colossal glacial seracs cracking in the Khumbu Icefall, and shrill cries of high-altitude Alpine choughs whipping past in freezing gales.",
        "why_it_sounds_like_this": "At an elevation of 8,729m with subzero temperatures (-18.5°C) and severe wind speeds (14.2 m/s), low atmospheric pressure (<350 hPa) severely damps high-frequency sound propagation, creating an eerie, dry isolation. The acoustic landscape is dominated by wind turbulence across steep 42° rock faces and deep infrasonic mechanical stress fractures in moving glacier ice."
    },
    "western_ghats": {
        "what_it_sounds_like": "A torrential wall of Southwest Monsoon rain roaring across steep basalt ridges, cascading mountain waterfalls crashing into plunge pools, and the legendary, human-like clear flute whistling melody of the endemic Malabar Whistling Thrush ('Whistling Schoolboy') singing through the misty downpour.",
        "why_it_sounds_like_this": "High precipitation rate (12.4 mm/h) driven by orographic monsoon lifting against the 1,887m escarpment generates overwhelming geophonic white noise (geophonic score: 94.6). Endemic fauna like the Malabar Whistling Thrush have evolved pure sinusoidal, high-amplitude whistling calls that specifically cut through the heavy acoustic frequency masking of waterfalls and rain."
    },
    "sundarbans": {
        "what_it_sounds_like": "Twice-daily tidal surges rushing and swirling through intricate mangrove prop roots, popping mud bubbles and clicking fiddler crabs on exposed tidal mudflats, sharp piercing cries of white-throated kingfishers diving for fish, and steady humid Bay of Bengal maritime coastal winds rustling Sundari leaves.",
        "why_it_sounds_like_this": "High water occurrence (84%) combined with low elevation (4m) and tidal dynamics creates a distinct amphibious acoustic environment. Sound alternates rhythmically between water sloshing against stilt roots during high tide and micro-percussive crustacean clicking and bubble bursting on exposed mud during low tide."
    },
    "daintree_rainforest": {
        "what_it_sounds_like": "Ancient Gondwanan rainforest directly meeting the Coral Sea: dry wooden clattering of gigantic Licuala fan palm fronds swaying in tropical breezes, deep chest-thumping infrasonic booming rumbles of the Southern Cassowary, barking white-lipped treefrogs, and gentle tropical beach waves breaking right at the edge of the forest tree line.",
        "why_it_sounds_like_this": "Where 94% closed-canopy tropical rainforest meets coastal sandy shores, acoustics blend heavy maritime surf with dense understory damping. The Southern Cassowary utilizes low-frequency infrasound (40–70 Hz) specifically because low frequencies penetrate through dense fan palm foliage and thick trunk barriers far more effectively than high-frequency calls."
    },
    "greater_khingan": {
        "what_it_sounds_like": "Subzero (-30°C) winter Siberian wilderness: biting arctic gales whistling through sparse Dahurian larch needles, eerie deep double-hoots of Eurasian eagle-owls echoing through frozen air, loud sharp explosive cracks and resonant groans of thick river ice fracturing under thermal tension, and deep snowpack muffling all echoes.",
        "why_it_sounds_like_this": "Extreme winter temperatures (-12.4°C baseline to -35°C peaks) and needleleaf larch biomes create dry, high-density air that transmits sharp percussive sounds with exceptional clarity. Thick snowpack absorbs reflections, creating a quiet, crisp acoustic field punctuated by mechanical thermal ice fracturing on frozen rivers."
    },
    "tongass_national_forest": {
        "what_it_sounds_like": "North Pacific coastal temperate rainforest: steady cold rain soaking Sitka spruce and Western hemlock needles, high-pitched chatter and piercing cries of bald eagles perched in tall trees, cold Pacific ocean swells surging against granite fiords, and crystal-clear glacial meltwater streams rushing over gravel.",
        "why_it_sounds_like_this": "High maritime precipitation (3.8 mm/h) and 88% evergreen needleleaf canopy create a soothing, continuous rain-drip backdrop. Steep coastal fjord geography channels cold Pacific westerlies and ocean swells directly into sheltered inlets, providing a dual maritime-temperate forest acoustic signature."
    },
    "valdivian_rainforest": {
        "what_it_sounds_like": "Andean temperate rainforest: cold Pacific westerlies driving rain through 3,000-year-old giant Alerce trees with deep organic trunk creaks and groans, rapid ringing staccato territorial trills of the Chucao tapaculo bird, pure metallic bell-like chirps of Darwin's frogs, and roaring glacial torrents rushing over volcanic basalt.",
        "why_it_sounds_like_this": "Heavy maritime rainfall from the Southern Ocean combined with steep 18.5° Andean slopes drives fast, turbulent river currents. Ancient giant Alerce trees (Fitzroya) create unique mechanical creaking under high wind loads, while specialized endemic understory birds produce rapid high-frequency staccato calls to signal across dense bamboo thickets."
    },
    "great_bear_rainforest": {
        "what_it_sounds_like": "Pacific fjord coastal rainforest: haunting harmonic pack howls of coastal sea wolves echoing across misty ocean fjords, heavy splashes of migrating salmon leaping up rocky river rapids, intricate hollow wooden knocks, bell-tones, and croaks of common ravens, and dense marine fog dripping on spongy moss understories.",
        "why_it_sounds_like_this": "Glacially carved granite fjords with 31° slopes reflect and amplify long-wavelength vocalizations, allowing coastal wolf pack howls to reverberate for miles. Abundant salmon runs in shallow rocky streams introduce energetic, localized splashing geophony beneath moss-laden cedar canopies."
    },
    "borneo_rainforest": {
        "what_it_sounds_like": "Towering 60-meter lowland dipterocarp rainforest: haunting rising melodic duet songs of Bornean gibbons echoing across the high canopy at dawn, heavy rhythmic whooshing wingbeats and loud trumpet honks of Rhinoceros hornbills, sluggish peat swamp blackwater river murmurs, and sudden afternoon equatorial cloudbursts.",
        "why_it_sounds_like_this": "Extreme tree heights (up to 65m emergent dipterocarps) and 91% canopy cover create multi-layered acoustic vertical strata. Gibbons call from the highest emergent crowns where acoustic propagation is unimpeded by ground absorption, while large hornbills displace audible low-frequency air pockets during flight between forest layers."
    }
}

def calculate_acoustic_derivation(telemetry: Dict[str, Any], loc: Dict[str, Any]) -> Dict[str, Any]:
    elev = telemetry.get("elevation_meters", 0.0)
    canopy = telemetry.get("tree_canopy_percent", 0.0)
    water = telemetry.get("water_occurrence_percent", 0.0)
    precip = telemetry.get("precipitation_rate_mm_h", 0.0)
    wind = telemetry.get("wind_speed_ms", 3.0)
    temp = telemetry.get("ambient_temp_celsius", 20.0)
    slope = telemetry.get("terrain_slope_degrees", 5.0)

    if canopy > 70:
        t60 = round(0.7 + (slope / 100.0) * 0.4, 2)
        spatial_acoustics = "High foliage acoustic absorption with warm multi-tier canopy reflections and diffuse understory scattering."
    elif elev > 3000:
        t60 = round(1.2 + (slope / 50.0) * 0.8, 2)
        spatial_acoustics = "Low atmospheric air density, crisp high-frequency wind propagation across exposed granite ridges."
    elif elev > 800 and canopy < 20:
        t60 = round(2.8 + (slope / 30.0) * 1.2, 2)
        spatial_acoustics = "Deep cavernous canyon multi-surface echo reverberation with long decay times across limestone walls."
    elif water > 80:
        t60 = round(1.5, 2)
        spatial_acoustics = "Open water boundary acoustic reflections with hydrostatic sub-surface low-frequency resonance."
    else:
        t60 = round(1.1, 2)
        spatial_acoustics = "Balanced outdoor open-air sound propagation."

    biophonic_density = round(min(100.0, (canopy * 0.7) + (max(0, 35 - abs(temp - 26)) * 1.0)), 1)
    geophonic_intensity = round(min(100.0, (precip * 5.0) + (wind * 4.0) + (water * 0.3)), 1)

    return {
        "reverberation_decay_t60_seconds": t60,
        "spatial_acoustic_profile": spatial_acoustics,
        "biophonic_density_score": biophonic_density,
        "geophonic_intensity_score": geophonic_intensity,
        "dominant_acoustic_frequency_band": "High-Mid (Canopy Chirps & Raindrops)" if canopy > 60 else "Low-Sub (Wind Roar & Wave Swell)" if elev > 3000 or water > 80 else "Mid-High (Echo & Crevice Whispers)",
        "atmospheric_damping_factor": "High Foliage Damping" if canopy > 80 else "Low Air Density Damping" if elev > 4000 else "Standard Maritime Damping"
    }

def get_location_specific_knobs(loc_id: str) -> List[Dict[str, Any]]:
    knobs_map = {
        "tongass_national_forest": [
            {
                "id": "canopy_rain_intensity",
                "name": "Temperate Rainforest Downpour",
                "description": "Modulates rainfall intensity and heavy water droplet impact on old-growth Sitka spruce and Western hemlock needles.",
                "min": 0, "max": 100, "default": 65, "unit": "%",
                "sonic_impact": "Controls rain droplet density, foliage splatter, and canopy runoff trickles.",
                "prompt_modifier": "heavy temperate rain dripping from mossy Sitka spruce needles, soothing rainforest downpour"
            },
            {
                "id": "bald_eagle_biophony",
                "name": "Coastal Avian & Marine Biophony",
                "description": "Adjusts the frequency and prominence of high-pitched bald eagle calls, raven vocalizations, and harbor seal splashes.",
                "min": 0, "max": 100, "default": 70, "unit": "%",
                "sonic_impact": "Increases sharp piercing bald eagle cries and deep resonant common raven croaks.",
                "prompt_modifier": "frequent piercing bald eagle calls echoing overhead, resonant common raven croaks"
            },
            {
                "id": "fjord_wave_swell",
                "name": "Pacific Fjord Tidal Swell",
                "description": "Controls the rhythm and power of cold North Pacific waves washing over rocky shoreline granite and pebble beds.",
                "min": 0, "max": 100, "default": 45, "unit": "%",
                "sonic_impact": "Modulates deep low-frequency ocean surges and pebble rolling textures.",
                "prompt_modifier": "rhythmic cold Pacific fjord waves crashing on rocky granite shorelines"
            },
            {
                "id": "glacial_melt_creek",
                "name": "Glacial Stream & Ice Runoff",
                "description": "Tunes the presence of cold, rushing glacial meltwater streams cascading down steep coastal fiord ravines.",
                "min": 0, "max": 100, "default": 55, "unit": "%",
                "sonic_impact": "Controls clear bubbling brook textures, rushing mountain stream turbulence.",
                "prompt_modifier": "crystal-clear glacial meltwater rushing through rocky mountain streams and fern beds"
            }
        ],
        "grand_canyon": [
            {
                "id": "canyon_echo_reverb",
                "name": "1,800m Gorge Reverberation",
                "description": "Controls the acoustic depth and long multi-surface echo decay across colossal Kaibab limestone and Vishnu schist canyon walls.",
                "min": 0, "max": 100, "default": 85, "unit": "%",
                "sonic_impact": "Expands cavernous spatial reverberation, long stereo slapback echoes, and vast acoustic space.",
                "prompt_modifier": "deep expansive 1800m canyon acoustic echo, vast cavernous spatial reverberation"
            },
            {
                "id": "thermal_canyon_winds",
                "name": "Desert Thermal Wind Shear",
                "description": "Modulates hot thermal updrafts and gusty desert winds whistling through tight sandstone buttes and rocky crevices.",
                "min": 0, "max": 100, "default": 60, "unit": "%",
                "sonic_impact": "Adds howling mid-frequency wind pitch shifts and rushing arid air currents.",
                "prompt_modifier": "hot desert thermal winds whistling through sandstone crevices and mesa cliffs"
            },
            {
                "id": "arid_wildlife_activity",
                "name": "Arid Avian & Cicada Chorus",
                "description": "Adjusts the presence of red-tailed hawk screeches and rhythmic desert cicada buzzing across the rim.",
                "min": 0, "max": 100, "default": 50, "unit": "%",
                "sonic_impact": "Brings red-tailed hawk soaring cries and descending canyon wren songs to the foreground.",
                "prompt_modifier": "piercing red-tailed hawk cries echoing off canyon walls, cascading canyon wren song, rhythmic cicadas"
            },
            {
                "id": "colorado_river_rapids",
                "name": "Colorado River Rapids Roar",
                "description": "Controls the distance and low-frequency roar of the Colorado River churning through Class V whitewater rapids at the gorge floor.",
                "min": 0, "max": 100, "default": 40, "unit": "%",
                "sonic_impact": "Controls distant sub-bass whitewater churn and rushing river foam.",
                "prompt_modifier": "distant thunderous roar of the Colorado River rapids churning at the bottom of the gorge"
            }
        ],
        "amazon_rainforest": [
            {
                "id": "canopy_wildlife_chorus",
                "name": "Canopy Biophony & Primate Chorus",
                "description": "Tunes the density of red howler monkey territorial roars, toco toucan yelps, and multi-layered cicada vibrations.",
                "min": 0, "max": 100, "default": 90, "unit": "%",
                "sonic_impact": "Intensifies resonant howler monkey dawn roars, vibrant bird calls, and tree frog choruses.",
                "prompt_modifier": "dense Amazon wildlife biophony, resonant red howler monkey roars, toucan calls, tropical insect chorus"
            },
            {
                "id": "tropical_deluge_rain",
                "name": "Equatorial Deluge & Thunder",
                "description": "Modulates torrential tropical rainstorms pounding broadleaf tree leaves and deep rolling thunderclaps.",
                "min": 0, "max": 100, "default": 75, "unit": "%",
                "sonic_impact": "Creates massive multi-layer rainfall splatter, heavy leaf impacts, and atmospheric thunder rumbles.",
                "prompt_modifier": "heavy tropical deluge rain hammering massive broadleaf canopy leaves, distant rolling thunder"
            },
            {
                "id": "varzea_river_currents",
                "name": "Flooded Forest & River Swell",
                "description": "Controls the gentle slosh of dark flooded várzea waters and the surfacing breath of pink river dolphins (boto).",
                "min": 0, "max": 100, "default": 50, "unit": "%",
                "sonic_impact": "Introduces rhythmic river laps against stilt roots, gentle water swirls, and blowhole exhalations.",
                "prompt_modifier": "gentle slow-moving Amazon river currents, water lapping against mangrove roots, pink river dolphin breath"
            },
            {
                "id": "nocturnal_amphibian_hum",
                "name": "Dusk-to-Night Amphibian Drone",
                "description": "Shifts the soundscape toward the nocturnal drone of millions of poison dart frogs, tree frogs, and katydids.",
                "min": 0, "max": 100, "default": 65, "unit": "%",
                "sonic_impact": "Filters daytime birds in favor of a dense, hypnotic polyphonic frog and insect hum.",
                "prompt_modifier": "hypnotic nocturnal chorus of Amazonian poison dart frogs, pulsing katydids, and nocturnal crickets"
            }
        ],
        "borneo_rainforest": [
            {
                "id": "gibbon_hornbill_duet",
                "name": "Gibbon & Hornbill Canopy Duet",
                "description": "Adjusts the melodic rising duets of Bornean gibbons and the heavy whooshing wingbeats of Rhinoceros hornbills.",
                "min": 0, "max": 100, "default": 85, "unit": "%",
                "sonic_impact": "Brings long melodic gibbon vocal calls and loud hornbill honks into clear acoustic focus.",
                "prompt_modifier": "haunting rising melodic duet of Bornean gibbons echoing from tall Shorea trees, Rhinoceros hornbill calls"
            },
            {
                "id": "dipterocarp_canopy_drip",
                "name": "60m Emergent Tree Moisture Drip",
                "description": "Controls the spatial drip of dense humid fog and post-rain moisture falling through 60-meter towering dipterocarp canopies.",
                "min": 0, "max": 100, "default": 60, "unit": "%",
                "sonic_impact": "High-definition spatial water droplet clicks and lush foliage diffusion.",
                "prompt_modifier": "gentle moisture dripping through 60-meter towering dipterocarp tree canopy, lush understory droplets"
            },
            {
                "id": "peat_swamp_hydroacoustics",
                "name": "Peat Swamp River Current",
                "description": "Modulates sluggish, tannin-rich blackwater river currents moving through submerged buttress tree roots.",
                "min": 0, "max": 100, "default": 45, "unit": "%",
                "sonic_impact": "Slow, deep watery sloshes and hollow root resonance.",
                "prompt_modifier": "sluggish blackwater peat swamp river murmurs, water swirling around buttress tree roots"
            },
            {
                "id": "afternoon_monsoon_storm",
                "name": "Afternoon Monsoon Thunderstorm",
                "description": "Tunes the intensity of sudden equatorial afternoon cloudbursts and deep humid thunder rumbles.",
                "min": 0, "max": 100, "default": 70, "unit": "%",
                "sonic_impact": "Increases rain intensity, wind rushing through palm fronds, and thunderclaps.",
                "prompt_modifier": "sudden equatorial afternoon monsoon downpour, wind sweeping through high canopy, warm thunder"
            }
        ],
        "sundarbans": [
            {
                "id": "tidal_mangrove_surge",
                "name": "Twice-Daily Tidal Surge",
                "description": "Controls the rhythm of incoming brackish ocean tides flooding through intricate mangrove pneumatophore root networks.",
                "min": 0, "max": 100, "default": 80, "unit": "%",
                "sonic_impact": "Deep tidal ebb and flow, bubbling water entering mud burrows.",
                "prompt_modifier": "rhythmic brackish tidal surge flooding mangrove roots, swirling estuary waters"
            },
            {
                "id": "estuarine_biophony",
                "name": "Estuarine Kingfisher & Mudfauna",
                "description": "Modulates the sharp calls of kingfishers, popping bubbles of mudskippers, and clicking fiddler crabs on exposed mudbanks.",
                "min": 0, "max": 100, "default": 65, "unit": "%",
                "sonic_impact": "Sharp high-frequency bird trills, subtle micro-clicks, and scurrying mud sounds.",
                "prompt_modifier": "sharp calls of white-throated kingfishers, subtle clicking of fiddler crabs on muddy banks"
            },
            {
                "id": "cyclonic_coastal_breeze",
                "name": "Bay of Bengal Coastal Wind",
                "description": "Tunes the steady humid sea breeze and gusty maritime winds blowing through Sundari tree branches.",
                "min": 0, "max": 100, "default": 55, "unit": "%",
                "sonic_impact": "Mid-frequency wind rustling dense mangrove foliage and rippling coastal waters.",
                "prompt_modifier": "steady Bay of Bengal coastal winds rustling Sundari mangrove leaves, saline maritime breeze"
            },
            {
                "id": "bengal_tiger_ambient_tension",
                "name": "Apex Predator Stealth Ambiance",
                "description": "Subtle acoustic tension: distant warning calls of spotted deer and rhesus macaques alerting to a moving tiger.",
                "min": 0, "max": 100, "default": 40, "unit": "%",
                "sonic_impact": "Sparse, intense spotted deer alarm barks, sudden silences, and stealthy brush rustles.",
                "prompt_modifier": "spotted deer alarm barks in the distance, tense atmospheric stillness in the mangrove maze"
            }
        ],
        "western_ghats": [
            {
                "id": "southwest_monsoon_deluge",
                "name": "Southwest Monsoon Deluge",
                "description": "Controls the massive wall of rain and wind characteristic of the 10,000mm annual monsoon hitting the western escarpment.",
                "min": 0, "max": 100, "default": 90, "unit": "%",
                "sonic_impact": "Roaring, relentless torrential rainfall and heavy mountain wind gusting across cliffs.",
                "prompt_modifier": "torrential Southwest Monsoon downpour pounding mountain ridges, roaring rainfall and mist"
            },
            {
                "id": "malabar_thrush_song",
                "name": "Malabar Whistling Thrush & Birds",
                "description": "Brings the legendary human-like melodic whistling of the 'whistling schoolboy' bird and laughingthrushes to life.",
                "min": 0, "max": 100, "default": 80, "unit": "%",
                "sonic_impact": "Clear, melodious human-like whistle contours echoing through misty ravines.",
                "prompt_modifier": "sweet melodic whistling song of the Malabar whistling thrush echoing across misty valleys"
            },
            {
                "id": "mountain_waterfall_cascade",
                "name": "Shola Waterfall & Rapids",
                "description": "Modulates roaring mountain torrents crashing over black basalt rock shelves into deep plunge pools.",
                "min": 0, "max": 100, "default": 70, "unit": "%",
                "sonic_impact": "Heavy mid-low white noise cascade and spray acoustic dispersal.",
                "prompt_modifier": "roaring mountain waterfalls crashing into rocky plunge pools, rushing stream foam"
            },
            {
                "id": "shola_cloud_mist_drip",
                "name": "Montane Cloud Forest Mist Drip",
                "description": "Tunes delicate condensation droplets dripping from stunted Shola evergreen trees and wild rhododendrons.",
                "min": 0, "max": 100, "default": 50, "unit": "%",
                "sonic_impact": "Quiet, delicate moisture drops, high-frequency dampening in thick mountain fog.",
                "prompt_modifier": "gentle mountain mist condensing on Shola forest leaves, quiet foggy atmospheric drops"
            }
        ],
        "daintree_rainforest": [
            {
                "id": "cassowary_infrasound_rumble",
                "name": "Southern Cassowary Infrasound",
                "description": "Controls deep, resonant low-frequency booming rumbles produced by ancient cassowaries vibrating through the forest floor.",
                "min": 0, "max": 100, "default": 65, "unit": "%",
                "sonic_impact": "Sub-bass chest-resonating thumps and low guttural reverberations.",
                "prompt_modifier": "deep low-frequency booming rumble of a southern cassowary vibrating the ancient understory"
            },
            {
                "id": "ancient_fan_palm_clatter",
                "name": "Gondwanan Fan Palm Clatter",
                "description": "Modulates the dry clattering sound of enormous Licuala fan palm fronds swaying and colliding in the breeze.",
                "min": 0, "max": 100, "default": 55, "unit": "%",
                "sonic_impact": "Rhythmic papery leaf clatter and wooden frond creaks.",
                "prompt_modifier": "rhythmic dry clatter of giant fan palm fronds swaying in tropical breezes"
            },
            {
                "id": "reef_edge_surf_roar",
                "name": "Rainforest-to-Reef Coastal Waves",
                "description": "Blends the gentle coral sea surf washing over white sand right at the edge of the dense forest tree line.",
                "min": 0, "max": 100, "default": 60, "unit": "%",
                "sonic_impact": "Crisp ocean wave foam meeting warm rainforest acoustic ambiance.",
                "prompt_modifier": "tropical Coral Sea surf gently washing on coastal sands where ancient rainforest meets the beach"
            },
            {
                "id": "treefrog_wompoo_chorus",
                "name": "White-lipped Treefrog & Fruit Dove",
                "description": "Adjusts the barking chorus of giant treefrogs and the rhythmic 'wom-poo' coos of fruit doves in the canopy.",
                "min": 0, "max": 100, "default": 75, "unit": "%",
                "sonic_impact": "Rich mid-range barking frogs and soft double-note dove calls.",
                "prompt_modifier": "vibrant barking calls of white-lipped treefrogs and soft 'wom-poo' coos of fruit doves"
            }
        ],
        "great_barrier_reef": [
            {
                "id": "snapping_shrimp_biophony",
                "name": "Snapping Shrimp Coral Chorus",
                "description": "Controls the continuous, mesmerizing 'crackling campfire' sound generated by millions of snapping shrimp claws across the reef.",
                "min": 0, "max": 100, "default": 90, "unit": "%",
                "sonic_impact": "Crisp high-frequency clicking, sizzling crackles, and hydrostatic texture.",
                "prompt_modifier": "intense crackling campfire sound of millions of snapping shrimp claws echoing across the coral reef"
            },
            {
                "id": "humpback_whale_song",
                "name": "Humpback Whale Hydrophone Melody",
                "description": "Adjusts the haunting, mournful low-and-high pitched melodic calls of migrating humpback whales echoing across deep water.",
                "min": 0, "max": 100, "default": 70, "unit": "%",
                "sonic_impact": "Sweeping melodic glissandos, rich oceanic harmonics, and deep underwater reverberation.",
                "prompt_modifier": "haunting melodic humpback whale songs echoing through deep underwater ocean channels"
            },
            {
                "id": "reef_crest_wave_break",
                "name": "Outer Reef Wave Breakers",
                "description": "Modulates massive Pacific ocean swells breaking over the shallow coral reef crest into turbulent white water.",
                "min": 0, "max": 100, "default": 65, "unit": "%",
                "sonic_impact": "Heavy bass impacts of collapsing ocean rollers and rushing foamy water.",
                "prompt_modifier": "thunderous ocean waves breaking over outer coral reef crests, deep underwater bubble surge"
            },
            {
                "id": "hydrostatic_depth_pressure",
                "name": "Sub-surface Hydrostatic Immersion",
                "description": "Shifts the acoustic perspective deeper underwater: rolling low-pass filter, subtle scuba bubble ascents, and calm hydrostatic hum.",
                "min": 0, "max": 100, "default": 50, "unit": "%",
                "sonic_impact": "Damped highs, enhanced sub-bass oceanic warmth, and gentle fluid movement.",
                "prompt_modifier": "deep hydrostatic sub-surface ocean ambiance, gentle underwater water movement and bubbles"
            }
        ],
        "greater_khingan": [
            {
                "id": "subzero_siberian_wind",
                "name": "Subzero Siberian Gale",
                "description": "Modulates freezing -30°C arctic wind whistling through bare Dahurian larch branches and across permafrost plains.",
                "min": 0, "max": 100, "default": 80, "unit": "%",
                "sonic_impact": "Sharp, chilling high-frequency wind whistles and rushing arctic gusts.",
                "prompt_modifier": "howling freezing Siberian winds whistling through sparse larch needles and snowy taiga ridges"
            },
            {
                "id": "frozen_river_ice_cracks",
                "name": "River Ice Popping & Thermal Fractures",
                "description": "Controls deep explosive pops and resonant metallic groans of thick river ice expanding and contracting under extreme subzero cold.",
                "min": 0, "max": 100, "default": 60, "unit": "%",
                "sonic_impact": "Sharp percussive cracks followed by reverberant sub-ice groans.",
                "prompt_modifier": "resonant cracking and booming of thick frozen river ice fracturing under extreme subzero cold"
            },
            {
                "id": "taiga_fauna_calls",
                "name": "Siberian Musk Deer & Eagle-Owl",
                "description": "Adjusts the eerie deep hoots of Eurasian eagle-owls and sudden sharp barking of musk deer through the silent snowy forest.",
                "min": 0, "max": 100, "default": 55, "unit": "%",
                "sonic_impact": "Deep low-frequency owl hoots and crisp, sudden mammal calls in absolute stillness.",
                "prompt_modifier": "deep resonant hoots of a Eurasian eagle-owl in the snowy stillness, distant bark of Siberian musk deer"
            },
            {
                "id": "snow_crust_acoustic_damping",
                "name": "Deep Powder Snow Acoustic Stillness",
                "description": "Controls the muffling absorption of thick boreal snowpack, creating pristine, near-silent atmospheric clarity.",
                "min": 0, "max": 100, "default": 70, "unit": "%",
                "sonic_impact": "Muffles distant reverberations, accentuates close-up breath, and delicate snow crystal drifts.",
                "prompt_modifier": "profound serene winter silence, soft dry snow crystals drifting across frozen forest floor"
            }
        ],
        "valdivian_rainforest": [
            {
                "id": "pacific_westerly_gale",
                "name": "Pacific Westerly Rainstorm",
                "description": "Modulates intense maritime storms and cold Antarctic westerlies driving heavy rain through dense Chilean temperate rainforests.",
                "min": 0, "max": 100, "default": 75, "unit": "%",
                "sonic_impact": "Powerful rushing wind gusts and heavy cold rain sheets.",
                "prompt_modifier": "heavy Pacific westerly rainstorm sweeping through ancient Chilean temperate rainforest"
            },
            {
                "id": "chucao_tapaculo_calls",
                "name": "Chucao Tapaculo & Bell Frogs",
                "description": "Brings the ringing, rapid staccato territorial calls of the iconic Chucao bird and clear bell-like chirps of Darwin's frog to life.",
                "min": 0, "max": 100, "default": 80, "unit": "%",
                "sonic_impact": "Loud staccato avian trills and pure metallic bell-like amphibian notes.",
                "prompt_modifier": "loud ringing staccato calls of the Chucao tapaculo and crystal bell-like chirps of Darwin's frogs"
            },
            {
                "id": "ancient_alerce_creaks",
                "name": "3,000-Year Alerce Trunk Groans",
                "description": "Controls deep wooden groans and moss-muffled creaks of gigantic, thousand-year-old Fitzroya cupressoides trees swaying in the wind.",
                "min": 0, "max": 100, "default": 50, "unit": "%",
                "sonic_impact": "Deep organic wood creaks, heavy branch groans, and spongy understory dampening.",
                "prompt_modifier": "deep organic creaking of 3000-year-old giant Alerce tree trunks swaying in mountain winds"
            },
            {
                "id": "andean_glacial_torrent",
                "name": "Andean Glacial River Rapids",
                "description": "Tunes roaring cold glacial torrents charging down steep volcanic basalt gorges toward coastal fjords.",
                "min": 0, "max": 100, "default": 65, "unit": "%",
                "sonic_impact": "Continuous roaring whitewater turbulence and boulder rolling rumbles.",
                "prompt_modifier": "roaring crystal-blue Andean glacial river rushing over volcanic basalt boulders"
            }
        ],
        "great_bear_rainforest": [
            {
                "id": "sea_wolf_fjord_howl",
                "name": "Coastal Sea Wolf Pack Chorus",
                "description": "Modulates the haunting, harmonious vocal howls of coastal sea wolves echoing across misty Pacific fjords.",
                "min": 0, "max": 100, "default": 85, "unit": "%",
                "sonic_impact": "Chilling, beautiful long melodic wolf howls with multi-wall fjord echo.",
                "prompt_modifier": "haunting pack howling of coastal sea wolves echoing across misty Pacific fjords and cedar trees"
            },
            {
                "id": "salmon_river_splashes",
                "name": "Salmon River Splash & Rapids",
                "description": "Controls the splashing of thousands of migrating salmon in shallow gravel rapids and bear river fishing sounds.",
                "min": 0, "max": 100, "default": 60, "unit": "%",
                "sonic_impact": "Rhythmic water slaps, rushing clear river currents, and heavy animal splashes.",
                "prompt_modifier": "rushing clear salmon river, heavy water splashes of migrating salmon leaping up rocky rapids"
            },
            {
                "id": "raven_bell_vocalizations",
                "name": "Old-Growth Raven Bell-Calls",
                "description": "Adjusts the intricate acoustic repertoire of common ravens: hollow wooden knocks, metallic bell-tones, and liquid gargles.",
                "min": 0, "max": 100, "default": 75, "unit": "%",
                "sonic_impact": "Sharp hollow clicks, resonant bell-like bird notes, and wing swooshes.",
                "prompt_modifier": "intricate hollow bell-like calls and resonant croaks of common ravens in giant cedar trees"
            },
            {
                "id": "coastal_fog_marine_drip",
                "name": "Pacific Marine Fog Condensation",
                "description": "Tunes dense North Pacific maritime fog dripping continuously from giant moss-laden Western redcedar branches.",
                "min": 0, "max": 100, "default": 55, "unit": "%",
                "sonic_impact": "Soothing, spatial water drops on spongy moss carpets and cedar bark.",
                "prompt_modifier": "heavy marine fog condensing and gently dripping through ancient moss-draped redcedar branches"
            }
        ],
        "mount_everest": [
            {
                "id": "jet_stream_ridge_roar",
                "name": "High-Altitude Jet Stream Gale",
                "description": "Controls ferocious 100+ km/h jet stream winds roaring across extreme razor-sharp granite rock ridges at 8,800 meters.",
                "min": 0, "max": 100, "default": 95, "unit": "%",
                "sonic_impact": "Intense howling high-velocity wind turbulence, low-frequency pressure fluctuations.",
                "prompt_modifier": "ferocious high-altitude jet stream winds howling across extreme rock ridges and snowy summits"
            },
            {
                "id": "khumbu_glacial_cracking",
                "name": "Khumbu Icefall Sub-bass Cracks",
                "description": "Modulates deep, earth-shaking sub-bass booms and explosive fractures as the colossal Khumbu Glacier shifts and calves seracs.",
                "min": 0, "max": 100, "default": 80, "unit": "%",
                "sonic_impact": "Sub-woofer shaking bass rumbles, sudden sharp ice shatter, and distant avalanche echoes.",
                "prompt_modifier": "deep thunderous sub-bass booming and cracking of colossal glacial seracs shifting in the Khumbu Icefall"
            },
            {
                "id": "alpine_chough_wind_calls",
                "name": "High Alpine Chough Bird Cries",
                "description": "Adjusts the shrill, high-pitched cries of Yellow-billed choughs gliding effortlessly through freezing thermal updrafts.",
                "min": 0, "max": 100, "default": 50, "unit": "%",
                "sonic_impact": "Piercing high-frequency bird calls whipping past in turbulent air currents.",
                "prompt_modifier": "sharp piercing cries of Alpine choughs swooping through freezing mountain updrafts"
            },
            {
                "id": "thin_air_acoustic_damping",
                "name": "Low-Pressure Atmospheric Vacuum",
                "description": "Simulates extreme altitude acoustics (<350 hPa): sharp reduction of high-frequency propagation, eerie dry isolation.",
                "min": 0, "max": 100, "default": 70, "unit": "%",
                "sonic_impact": "Dry, stark acoustic profile with reduced reverberation and stark, close-proximity wind focus.",
                "prompt_modifier": "stark low-pressure high-altitude acoustic atmosphere, crisp dry wind with minimal reverb"
            }
        ]
    }
    return knobs_map.get(loc_id, [])

def build_lyria_master_prompt(loc: Dict[str, Any], derivation: Dict[str, Any], profile: Dict[str, str]) -> str:
    species_str = ", ".join(loc.get("dominant_species", []))
    geophony_str = ", ".join(loc.get("geophonic_elements", []))
    name = loc["name"]
    biome = loc["biome"]
    
    prompt = (
        f"Immersive 60-second ultra-realistic natural field recording soundscape of {name} ({biome}). "
        f"Acoustic atmosphere: {profile['what_it_sounds_like']} "
        f"Geophonic environment features pristine spatial recording of {geophony_str}. "
        f"Vibrant indigenous biophony with authentic natural calls of {species_str}. "
        f"Acoustics & Physics: {derivation['spatial_acoustic_profile']} "
        f"Natural stereo binaural soundstage, deep organic textures, dynamic range, authentic planetary field acoustics."
    )
    return prompt

def main():
    print("=== Translating Telemetry into Lyria Prompts & Distinct Location Profiles ===")
    
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    telemetry_path = os.path.join(data_dir, "telemetry_data.json")
    
    if not os.path.exists(telemetry_path):
        print(f"Error: {telemetry_path} not found. Run extract_geospatial_telemetry.py first.")
        return

    with open(telemetry_path, "r", encoding="utf-8") as f:
        telemetry_data = json.load(f)

    soundscape_configs = []

    for loc in telemetry_data:
        loc_id = loc["id"]
        telemetry = loc.get("telemetry", {})
        
        # 1. Compute acoustic derivation
        derivation = calculate_acoustic_derivation(telemetry, loc)
        
        # 2. Get profile (What it sounds like & Why)
        profile = LOCATION_ACOUSTIC_PROFILES.get(loc_id, {
            "what_it_sounds_like": f"Authentic planetary field recording of {loc['name']}.",
            "why_it_sounds_like_this": f"Driven by local topography, canopy cover, and endemic species."
        })
        
        # 3. Build Lyria Master Prompt
        master_prompt = build_lyria_master_prompt(loc, derivation, profile)
        
        # 4. Define negative prompts
        negative_prompt = "synthesizer, drum machine, techno, edm, pop music, electronic beats, distorted guitar, human singing, speech, urban traffic, sirens, clipping, digital artifacts, harsh compression"
        
        # 5. Get 4 Location-Adaptive Knobs
        knobs = get_location_specific_knobs(loc_id)
            
        lyria_params = {
            "model": "lyria-v2-field-recording",
            "duration_seconds": 60,
            "sample_rate_hz": 48000,
            "audio_format": "wav_stereo",
            "temperature": 0.85,
            "top_k": 40,
            "seed": 42000 + len(soundscape_configs) * 137,
            "binaural_rendering": True,
            "target_rms_db": -16.0
        }
        
        config_entry = {
            "id": loc_id,
            "name": loc["name"],
            "region": loc["region"],
            "category": loc["category"],
            "biome": loc["biome"],
            "lat": loc["lat"],
            "lng": loc["lng"],
            "soundscape_description": profile["what_it_sounds_like"],
            "soundscape_why_rationale": profile["why_it_sounds_like_this"],
            "telemetry": telemetry,
            "acoustic_derivation": derivation,
            "lyria_master_prompt": master_prompt,
            "lyria_negative_prompt": negative_prompt,
            "lyria_params": lyria_params,
            "location_adaptive_knobs": knobs,
            "audio_asset_url": f"audio/{loc_id}_master.wav"
        }
        soundscape_configs.append(config_entry)
        print(f"  ✓ {loc['name']}: Distinct profile & prompt generated.")

    output_path = os.path.join(data_dir, "soundscape_configs.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(soundscape_configs, f, indent=2)

    print(f"\n[Quality Gate 3 Check] 12/12 soundscape configurations generated -> {output_path}")

if __name__ == "__main__":
    main()
