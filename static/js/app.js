/**
 * EarthAI Soundscapes - Dual Player Application Logic
 * Supports dual immersive audio engines per location:
 *   1. Authentic Multi-Track Field Master (Wikimedia Commons Stems)
 *   2. Google DeepMind Lyria 2 Neural Soundscape (Vertex AI lyria-002)
 */

// Application State
const state = {
  locations: [],
  currentLoc: null,

  // Player 1: Authentic Field Master
  audio: new Audio(),
  audioCtx: null,
  analyser: null,
  sourceNode: null,
  isPlaying: false,
  isLooping: false,
  animationFrameId: null,

  // Player 2: Lyria 2 Neural Audio
  lyriaAudio: new Audio(),
  lyriaAudioCtx: null,
  lyriaAnalyser: null,
  lyriaSourceNode: null,
  isLyriaPlaying: false,
  isLyriaLooping: false,
  lyriaAnimationFrameId: null
};

// DOM Elements
const el = {
  locationSelect: document.getElementById('location-select'),
  prevLocBtn: document.getElementById('prev-location-btn'),
  nextLocBtn: document.getElementById('next-location-btn'),

  // Header Details
  locTitle: document.getElementById('loc-title'),
  locRegionBadge: document.getElementById('loc-region-badge'),
  locBiomeBadge: document.getElementById('loc-biome-badge'),
  locCoordsBadge: document.getElementById('loc-coords-badge'),
  locBiomeDesc: document.getElementById('loc-biome-desc'),
  locSoundscapeDesc: document.getElementById('loc-soundscape-desc'),
  locSoundscapeWhy: document.getElementById('loc-soundscape-why'),

  // Player 1: Field Master Audio & Waveform Visualizer
  waveformCanvas: document.getElementById('waveform-canvas'),
  waveformPlaceholder: document.getElementById('waveform-placeholder'),
  playBtn: document.getElementById('play-btn'),
  playIcon: document.getElementById('play-icon'),
  currentTime: document.getElementById('current-time'),
  totalDuration: document.getElementById('total-duration'),
  seekBar: document.getElementById('seek-bar'),
  muteBtn: document.getElementById('mute-btn'),
  volumeIcon: document.getElementById('volume-icon'),
  volumeBar: document.getElementById('volume-bar'),
  loopBtn: document.getElementById('loop-btn'),
  audioStatusTag: document.getElementById('audio-status-tag'),
  audioModeLabel: document.getElementById('audio-mode-label'),

  // Player 1: Audio Generation Provenance
  audioRecordingsUsed: document.getElementById('audio-recordings-used'),
  audioSourceAttribution: document.getElementById('audio-source-attribution'),
  audioDspProcessing: document.getElementById('audio-dsp-processing'),

  // Player 2: Lyria 2 Audio & Waveform Visualizer
  lyriaWaveformCanvas: document.getElementById('lyria-waveform-canvas'),
  lyriaWaveformPlaceholder: document.getElementById('lyria-waveform-placeholder'),
  lyriaPlayBtn: document.getElementById('lyria-play-btn'),
  lyriaPlayIcon: document.getElementById('lyria-play-icon'),
  lyriaCurrentTime: document.getElementById('lyria-current-time'),
  lyriaTotalDuration: document.getElementById('lyria-total-duration'),
  lyriaSeekBar: document.getElementById('lyria-seek-bar'),
  lyriaMuteBtn: document.getElementById('lyria-mute-btn'),
  lyriaVolumeIcon: document.getElementById('lyria-volume-icon'),
  lyriaVolumeBar: document.getElementById('lyria-volume-bar'),
  lyriaLoopBtn: document.getElementById('lyria-loop-btn'),
  lyriaAudioStatusTag: document.getElementById('lyria-audio-status-tag'),
  lyriaAudioModeLabel: document.getElementById('lyria-audio-mode-label'),

  // Player 2: Lyria Generation Provenance
  lyriaModelName: document.getElementById('lyria-model-name'),
  lyriaPromptUsed: document.getElementById('lyria-prompt-used'),
  lyriaProcessingDetails: document.getElementById('lyria-processing-details'),

  // Tier 1 Telemetry
  teleElev: document.getElementById('tele-elev'),
  teleCanopy: document.getElementById('tele-canopy'),
  teleWater: document.getElementById('tele-water'),
  teleTemp: document.getElementById('tele-temp'),
  telePrecip: document.getElementById('tele-precip'),
  teleWind: document.getElementById('tele-wind'),

  // Tier 2 Acoustics
  acousticsT60: document.getElementById('acoustics-t60'),
  acousticsBiophony: document.getElementById('acoustics-biophony'),
  acousticsGeophony: document.getElementById('acoustics-geophony'),
  acousticsProfileDesc: document.getElementById('acoustics-profile-desc'),

  // Tier 3 Translation Table & Prompts
  dataTranslationTable: document.getElementById('data-translation-table'),
  masterPromptDisplay: document.getElementById('master-prompt-display'),
  negativePromptDisplay: document.getElementById('negative-prompt-display'),

  // Indigenous Elements
  speciesTags: document.getElementById('species-tags'),
  geophonyTags: document.getElementById('geophony-tags')
};

// Initialize Application
async function init() {
  try {
    const res = await fetch('/api/locations');
    if (!res.ok) throw new Error(`HTTP ${res.status} fetching locations`);
    state.locations = await res.json();

    if (state.locations.length > 0) {
      populateLocationDropdown();
      selectLocation(state.locations[0].id);
    }

    setupEventListeners();
    setupLyriaEventListeners();
    resizeCanvases();
    window.addEventListener('resize', resizeCanvases);

    if (window.lucide) {
      window.lucide.createIcons();
    }
  } catch (err) {
    console.error('Error initializing soundscape studio:', err);
    if (el.locTitle) el.locTitle.textContent = `Error loading locations: ${err.message}`;
  }
}

// Populate Location Select
function populateLocationDropdown() {
  if (!el.locationSelect) return;
  el.locationSelect.innerHTML = '';
  state.locations.forEach((loc) => {
    const opt = document.createElement('option');
    opt.value = loc.id;
    opt.textContent = `${loc.name} (${loc.region.split(',')[0]})`;
    el.locationSelect.appendChild(opt);
  });
}

// Select Location
function selectLocation(locId) {
  const loc = state.locations.find((l) => l.id === locId);
  if (!loc) return;

  state.currentLoc = loc;
  if (el.locationSelect) el.locationSelect.value = locId;

  // Header Details
  if (el.locTitle) el.locTitle.textContent = loc.name;
  if (el.locRegionBadge) el.locRegionBadge.textContent = loc.region;
  if (el.locBiomeBadge) el.locBiomeBadge.textContent = loc.biome.split('&')[0].trim();
  if (el.locCoordsBadge) el.locCoordsBadge.textContent = `${loc.lat.toFixed(4)}°, ${loc.lng.toFixed(4)}°`;
  if (el.locBiomeDesc) el.locBiomeDesc.textContent = `${loc.biome}. Ecological analysis translates planetary climate, canopy density, and topographic resonance directly into authentic bioacoustic soundscapes.`;
  if (el.locSoundscapeDesc) el.locSoundscapeDesc.textContent = loc.soundscape_description || 'Authentic planetary field recording.';
  if (el.locSoundscapeWhy) el.locSoundscapeWhy.textContent = loc.soundscape_why_rationale || 'Driven by local climate and biophysical indicators.';

  // Telemetry Tier 1
  const t = loc.telemetry || {};
  if (el.teleElev) el.teleElev.textContent = `${Math.round(t.elevation_meters || 0)} m`;
  if (el.teleCanopy) el.teleCanopy.textContent = `${t.tree_canopy_percent || 0}%`;
  if (el.teleWater) el.teleWater.textContent = `${t.water_occurrence_percent || 0}%`;
  if (el.teleTemp) el.teleTemp.textContent = `${t.ambient_temp_celsius || 20}°C`;
  if (el.telePrecip) el.telePrecip.textContent = `${t.precipitation_rate_mm_h || 0} mm/h`;
  if (el.teleWind) el.teleWind.textContent = `${t.wind_speed_ms || 3.0} m/s`;

  // Acoustics Tier 2
  const a = loc.acoustic_derivation || {};
  if (el.acousticsT60) el.acousticsT60.textContent = `${a.reverberation_decay_t60_seconds || 1.2}s`;
  if (el.acousticsBiophony) el.acousticsBiophony.textContent = `${a.biophonic_density_score || 75} / 100`;
  if (el.acousticsGeophony) el.acousticsGeophony.textContent = `${a.geophonic_intensity_score || 50} / 100`;
  if (el.acousticsProfileDesc) el.acousticsProfileDesc.textContent = a.spatial_acoustic_profile || 'Balanced natural sound propagation.';

  // Translation Matrix Tier 3
  renderDataTranslationTable(loc);

  // Prompts Tier 3
  if (el.masterPromptDisplay) el.masterPromptDisplay.textContent = loc.lyria_master_prompt || '';
  if (el.negativePromptDisplay) el.negativePromptDisplay.textContent = loc.lyria_negative_prompt || '';

  // Tags
  if (el.speciesTags) {
    el.speciesTags.innerHTML = '';
    (loc.dominant_species || []).forEach((sp) => {
      const span = document.createElement('span');
      span.className = 'px-3 py-1.5 rounded-xl bg-white border border-emerald-200 text-emerald-950 font-semibold text-xs shadow-sm';
      span.textContent = sp;
      el.speciesTags.appendChild(span);
    });
  }

  if (el.geophonyTags) {
    el.geophonyTags.innerHTML = '';
    (loc.geophonic_elements || []).forEach((gp) => {
      const span = document.createElement('span');
      span.className = 'px-3 py-1.5 rounded-xl bg-white border border-blue-200 text-blue-950 font-semibold text-xs shadow-sm';
      span.textContent = gp;
      el.geophonyTags.appendChild(span);
    });
  }

  // Load Player 1: Authentic Field Recording Soundscape
  loadFieldAudioTrack(loc.audio_asset_url || `/api/audio/${loc.id}_master.wav`, 'Authentic Field Recording Soundscape');

  // Populate Player 1 Provenance Note
  const prov = loc.soundscape_generation_provenance || {};
  if (el.audioRecordingsUsed) el.audioRecordingsUsed.textContent = prov.recordings_used || 'Authentic regional field recordings.';
  if (el.audioSourceAttribution) el.audioSourceAttribution.textContent = prov.source || 'Wikimedia Commons Field Sound Database.';
  if (el.audioDspProcessing) el.audioDspProcessing.textContent = prov.processing || 'Multi-track spatial audio mix, bandpass filtering, EBU R128 loudness normalization.';

  // Load Player 2: Lyria 2 Neural Bioacoustic Soundscape
  const lyriaUrl = `/api/audio/${loc.id}_lyria.wav`;
  loadLyriaAudioTrack(lyriaUrl, 'Google Lyria 2 Neural Soundscape');

  // Populate Player 2 Provenance Note
  const lyriaMeta = loc.lyria_soundscape || {};
  if (el.lyriaModelName) el.lyriaModelName.textContent = lyriaMeta.model_name || 'Google DeepMind Lyria 2 (lyria-002)';
  if (el.lyriaPromptUsed) {
    const p = lyriaMeta.prompt_used || loc.lyria_master_prompt || 'Conditioned on planetary canopy, wind, and indigenous fauna telemetry.';
    el.lyriaPromptUsed.textContent = p;
    el.lyriaPromptUsed.title = p;
  }
  if (el.lyriaProcessingDetails) {
    el.lyriaProcessingDetails.textContent = lyriaMeta.processing || 'Direct neural synthesis via Lyria 2 API on Vertex AI, 60s seamless loop, EBU R128 (-16 LUFS) mastering.';
  }

  if (window.lucide) window.lucide.createIcons();
}

// Render Data Translation Table
function renderDataTranslationTable(loc) {
  if (!el.dataTranslationTable) return;
  el.dataTranslationTable.innerHTML = '';
  const t = loc.telemetry || {};
  const a = loc.acoustic_derivation || {};

  const mappings = [
    {
      metric: 'Tree Canopy Cover',
      value: `${t.tree_canopy_percent || 0}%`,
      source: 'Hansen Global Forest Change (30m)',
      color: 'emerald',
      translation:
        (t.tree_canopy_percent || 0) > 75
          ? `Dense closed canopy (${t.tree_canopy_percent}%) acts as an acoustic absorption chamber (Reverb T60: ${a.reverberation_decay_t60_seconds || 0.8}s), heavily damping long-range echoes while amplifying rich multi-tier canopy biophony.`
          : (t.tree_canopy_percent || 0) < 15
            ? `Sparse vegetative cover (${t.tree_canopy_percent}%) exposes bare reflective rock and desert surfaces, maximizing reverberation decay (T60: ${a.reverberation_decay_t60_seconds || 4.2}s) and high-frequency sound propagation.`
            : `Moderate canopy cover (${t.tree_canopy_percent}%) provides balanced acoustic absorption with diffuse foliage scatter.`,
      promptImpact:
        (t.tree_canopy_percent || 0) > 75
          ? 'Dense biophonic choir, cicadas pulsing, high canopy moisture drip'
          : (t.tree_canopy_percent || 0) < 15
            ? 'Vast cavernous gorge acoustics, thermal updrafts whistling through rock crevices, red-tailed hawk echoes'
            : 'Balanced woodland chorus, leaf rustling, open glade acoustics'
    },
    {
      metric: 'Elevation & Relief',
      value: `${Math.round(t.elevation_meters || 0)} m (${Math.round(t.relief_meters || 0)}m relief, ${t.slope_degrees || 0}° slope)`,
      source: 'Copernicus GLO-30 DEM',
      color: 'slate',
      translation:
        (t.elevation_meters || 0) > 4000
          ? `Extreme high altitude (${Math.round(t.elevation_meters)}m) creates thin atmospheric air pressure (<350 hPa) that severely damps high frequencies, leaving an eerie dry isolation dominated by violent ridge turbulence.`
          : (t.slope_degrees || 0) > 20
            ? `Steep topography (${t.slope_degrees}° slope, ${Math.round(t.relief_meters || 0)}m vertical relief) creates multi-surface acoustic reflections and prolonged cavernous echoes.`
            : 'Low-elevation coastal/plains terrain maintains dense atmospheric acoustic coupling with wide spatial distribution.',
      promptImpact:
        (t.elevation_meters || 0) > 4000
          ? 'Violent jet stream wind roar, thin air acoustic damping, glacial serac calving booms'
          : (t.slope_degrees || 0) > 20
            ? 'Echoing raptor shrieks, multi-surface slapback echoes, resonant gorge wind'
            : 'Expansive natural stereo field, close-proximity bird calls'
    },
    {
      metric: 'Surface Water Permanence',
      value: `${t.water_occurrence_percent || 0}%`,
      source: 'EC JRC Global Surface Water',
      color: 'blue',
      translation:
        (t.water_occurrence_percent || 0) > 70
          ? `High surface water permanence (${t.water_occurrence_percent}%) shifts the acoustic medium to hydroacoustic dominance, where sound propagates 4.3x faster than in air.`
          : (t.water_occurrence_percent || 0) > 20
            ? `Adjacent riparian/estuarine surface water creates continuous bubbling, wave lap, and tidal current geophony.`
            : 'Arid desert substrate produces dry, crisp acoustic reflections with zero aquatic dampening.',
      promptImpact:
        (t.water_occurrence_percent || 0) > 70
          ? 'Hydroacoustic underwater crackle, deep tidal surge, rolling ocean swells'
          : (t.water_occurrence_percent || 0) > 20
            ? 'Rushing mountain river, cascading waterfalls, tidal marsh root slosh'
            : 'Dry desert wind whistling through stone, arid silence'
    },
    {
      metric: 'Hourly Precipitation Rate',
      value: `${t.precipitation_rate_mm_h || 0} mm/h`,
      source: 'ECMWF ERA5-Land Hourly',
      color: 'cyan',
      translation:
        (t.precipitation_rate_mm_h || 0) > 5.0
          ? `Heavy torrential rainfall (${t.precipitation_rate_mm_h} mm/h) generates dominant geophonic white noise (Score: ${a.geophonic_intensity_score || 90}/100) that masks low-amplitude biophony and forces fauna to vocalize at distinct frequencies.`
          : (t.precipitation_rate_mm_h || 0) > 0.5
            ? `Gentle precipitation (${t.precipitation_rate_mm_h} mm/h) produces rhythmic soothing droplets on foliage, elevating the natural ambient noise floor.`
            : 'Zero precipitation leaves biophonic signals unmasked and crystal-clear across the full spectrum.',
      promptImpact:
        (t.precipitation_rate_mm_h || 0) > 5.0
          ? 'Roaring monsoon downpour, thunder claps, heavy canopy deluge drops'
          : (t.precipitation_rate_mm_h || 0) > 0.5
            ? 'Steady light rain soaking needles, calming drip textures'
            : 'Crystal-clear avian calls, dry insect chirping'
    },
    {
      metric: 'Wind Velocity (10m)',
      value: `${t.wind_speed_ms || 0} m/s (${t.wind_direction_cardinal || 'W'})`,
      source: 'ECMWF ERA5 Reanalysis',
      color: 'amber',
      translation:
        (t.wind_speed_ms || 0) > 10.0
          ? `High wind speeds (${t.wind_speed_ms} m/s) generate strong turbulence and low-frequency aerodynamic rumble through ridges and canopies.`
          : 'Gentle breeze drives laminar foliage motion, generating soothing acoustic rustling.',
      promptImpact:
        (t.wind_speed_ms || 0) > 10.0
          ? 'Howling subzero gales, high-velocity gusts whistling through needles'
          : 'Gentle canopy sway, soft ocean breeze, tranquil air currents'
    }
  ];

  mappings.forEach((m) => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-50/80 transition';
    tr.innerHTML = `
      <td class="py-3.5 px-4 align-top">
        <div class="font-bold text-slate-900 flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-600"></span>
          <span>${m.metric}</span>
        </div>
        <span class="font-mono font-bold text-xs text-emerald-800 block mt-0.5">${m.value}</span>
        <span class="text-[10px] text-slate-400 font-mono">${m.source}</span>
      </td>
      <td class="py-3.5 px-4 align-top text-slate-700 leading-relaxed">
        ${m.translation}
      </td>
      <td class="py-3.5 px-4 align-top">
        <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 font-mono text-[11px] text-emerald-950 font-medium leading-relaxed">
          "${m.promptImpact}"
        </div>
      </td>
    `;
    el.dataTranslationTable.appendChild(tr);
  });
}

// ---------------------------------------------------------------------------
// Player 1 (Authentic Field Recording Master) Controls & Visualizer
// ---------------------------------------------------------------------------

function loadFieldAudioTrack(url, label = 'Authentic Field-Recorded Master') {
  state.audio.src = url;
  state.audio.load();
  if (el.audioModeLabel) el.audioModeLabel.textContent = label;
  if (el.audioStatusTag) el.audioStatusTag.textContent = 'Ready';
  if (el.seekBar) el.seekBar.value = 0;
  if (el.currentTime) el.currentTime.textContent = '0:00';
  state.isPlaying = false;
  updatePlayButtonUI();
}

function initFieldAudioContext() {
  if (state.audioCtx) return;
  try {
    const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
    state.audioCtx = new AudioCtxClass();
    state.analyser = state.audioCtx.createAnalyser();
    state.analyser.fftSize = 256;
    state.sourceNode = state.audioCtx.createMediaElementSource(state.audio);
    state.sourceNode.connect(state.analyser);
    state.analyser.connect(state.audioCtx.destination);
    startFieldVisualizerLoop();
  } catch (e) {
    console.warn('Field Web Audio API context init warning:', e);
  }
}

function startFieldVisualizerLoop() {
  const canvas = el.waveformCanvas;
  if (!canvas || !state.analyser) return;
  const ctx = canvas.getContext('2d');
  const bufferLength = state.analyser.frequencyBinCount;
  const freqData = new Uint8Array(bufferLength);
  const timeData = new Uint8Array(bufferLength);

  function draw() {
    state.animationFrameId = requestAnimationFrame(draw);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!state.isPlaying) {
      const w = canvas.width;
      const h = canvas.height;
      const t = Date.now() * 0.002;
      ctx.beginPath();
      ctx.lineWidth = 2 * window.devicePixelRatio;
      ctx.strokeStyle = 'rgba(27, 77, 62, 0.25)';
      for (let x = 0; x < w; x += 4) {
        const y = h / 2 + Math.sin(x * 0.015 + t) * (h * 0.08);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      return;
    }

    state.analyser.getByteFrequencyData(freqData);
    state.analyser.getByteTimeDomainData(timeData);

    const width = canvas.width;
    const height = canvas.height;
    const barWidth = (width / bufferLength) * 2.2;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const barHeight = (freqData[i] / 255.0) * height * 0.85;
      const grad = ctx.createLinearGradient(0, height, 0, height - barHeight);
      grad.addColorStop(0, '#1B4D3E');
      grad.addColorStop(0.6, '#059669');
      grad.addColorStop(1, '#06B6D4');
      ctx.fillStyle = grad;
      ctx.fillRect(x, height - barHeight, barWidth - 1.5, barHeight);
      x += barWidth;
    }

    ctx.beginPath();
    ctx.lineWidth = 2.5 * window.devicePixelRatio;
    ctx.strokeStyle = '#FFFFFF';
    ctx.shadowColor = 'rgba(6, 182, 212, 0.8)';
    ctx.shadowBlur = 8;
    const sliceWidth = width / bufferLength;
    let wx = 0;
    for (let i = 0; i < bufferLength; i++) {
      const v = timeData[i] / 128.0;
      const wy = (v * height) / 2;
      if (i === 0) ctx.moveTo(wx, wy);
      else ctx.lineTo(wx, wy);
      wx += sliceWidth;
    }
    ctx.stroke();
    ctx.shadowBlur = 0;
  }
  draw();
}

function setupEventListeners() {
  if (el.locationSelect) {
    el.locationSelect.addEventListener('change', (e) => selectLocation(e.target.value));
  }
  if (el.prevLocBtn) {
    el.prevLocBtn.addEventListener('click', () => {
      const idx = state.locations.findIndex((l) => l.id === state.currentLoc.id);
      const prevIdx = (idx - 1 + state.locations.length) % state.locations.length;
      selectLocation(state.locations[prevIdx].id);
    });
  }
  if (el.nextLocBtn) {
    el.nextLocBtn.addEventListener('click', () => {
      const idx = state.locations.findIndex((l) => l.id === state.currentLoc.id);
      const nextIdx = (idx + 1) % state.locations.length;
      selectLocation(state.locations[nextIdx].id);
    });
  }

  // Player 1 Play / Pause
  if (el.playBtn) {
    el.playBtn.addEventListener('click', () => {
      // Pause Lyria if playing
      if (state.isLyriaPlaying) {
        state.lyriaAudio.pause();
      }

      initFieldAudioContext();
      if (state.audioCtx && state.audioCtx.state === 'suspended') {
        state.audioCtx.resume();
      }
      if (state.isPlaying) {
        state.audio.pause();
      } else {
        state.audio.play().catch((e) => console.warn('Field play interrupted:', e));
      }
    });
  }

  state.audio.addEventListener('play', () => {
    state.isPlaying = true;
    if (el.waveformPlaceholder) el.waveformPlaceholder.classList.add('hidden');
    if (el.audioStatusTag) {
      el.audioStatusTag.textContent = 'Streaming 48kHz Stereo';
      el.audioStatusTag.className = 'text-xs font-mono font-medium px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-300';
    }
    updatePlayButtonUI();
  });

  state.audio.addEventListener('pause', () => {
    state.isPlaying = false;
    if (el.audioStatusTag) {
      el.audioStatusTag.textContent = 'Paused';
      el.audioStatusTag.className = 'text-xs font-mono font-medium px-2.5 py-1 rounded-full bg-slate-100 text-slate-700';
    }
    updatePlayButtonUI();
  });

  state.audio.addEventListener('timeupdate', () => {
    if (!state.audio.duration) return;
    const cur = state.audio.currentTime;
    const dur = state.audio.duration;
    if (el.currentTime) el.currentTime.textContent = formatTime(cur);
    if (el.totalDuration) el.totalDuration.textContent = formatTime(dur);
    if (el.seekBar) el.seekBar.value = (cur / dur) * 100;
  });

  state.audio.addEventListener('ended', () => {
    if (!state.isLooping) {
      state.isPlaying = false;
      updatePlayButtonUI();
    }
  });

  if (el.seekBar) {
    el.seekBar.addEventListener('input', (e) => {
      if (!state.audio.duration) return;
      const pct = parseFloat(e.target.value);
      state.audio.currentTime = (pct / 100) * state.audio.duration;
    });
  }

  if (el.volumeBar) {
    el.volumeBar.addEventListener('input', (e) => {
      state.audio.volume = parseFloat(e.target.value);
      updateVolumeIcon();
    });
  }

  if (el.muteBtn) {
    el.muteBtn.addEventListener('click', () => {
      state.audio.muted = !state.audio.muted;
      updateVolumeIcon();
    });
  }

  if (el.loopBtn) {
    el.loopBtn.addEventListener('click', () => {
      state.isLooping = !state.isLooping;
      state.audio.loop = state.isLooping;
      el.loopBtn.classList.toggle('bg-emerald-100', state.isLooping);
      el.loopBtn.classList.toggle('text-emerald-800', state.isLooping);
      el.loopBtn.classList.toggle('border-emerald-300', state.isLooping);
    });
  }
}

// ---------------------------------------------------------------------------
// Player 2 (Google DeepMind Lyria 2 Neural Bioacoustics) Controls & Visualizer
// ---------------------------------------------------------------------------

function loadLyriaAudioTrack(url, label = 'Google Lyria 2 Neural Soundscape') {
  state.lyriaAudio.src = url;
  state.lyriaAudio.load();
  if (el.lyriaAudioModeLabel) el.lyriaAudioModeLabel.textContent = label;
  if (el.lyriaAudioStatusTag) el.lyriaAudioStatusTag.textContent = 'Ready';
  if (el.lyriaSeekBar) el.lyriaSeekBar.value = 0;
  if (el.lyriaCurrentTime) el.lyriaCurrentTime.textContent = '0:00';
  state.isLyriaPlaying = false;
  updateLyriaPlayButtonUI();
}

function initLyriaAudioContext() {
  if (state.lyriaAudioCtx) return;
  try {
    const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
    state.lyriaAudioCtx = new AudioCtxClass();
    state.lyriaAnalyser = state.lyriaAudioCtx.createAnalyser();
    state.lyriaAnalyser.fftSize = 256;
    state.lyriaSourceNode = state.lyriaAudioCtx.createMediaElementSource(state.lyriaAudio);
    state.lyriaSourceNode.connect(state.lyriaAnalyser);
    state.lyriaAnalyser.connect(state.lyriaAudioCtx.destination);
    startLyriaVisualizerLoop();
  } catch (e) {
    console.warn('Lyria Web Audio API context init warning:', e);
  }
}

function startLyriaVisualizerLoop() {
  const canvas = el.lyriaWaveformCanvas;
  if (!canvas || !state.lyriaAnalyser) return;
  const ctx = canvas.getContext('2d');
  const bufferLength = state.lyriaAnalyser.frequencyBinCount;
  const freqData = new Uint8Array(bufferLength);
  const timeData = new Uint8Array(bufferLength);

  function draw() {
    state.lyriaAnimationFrameId = requestAnimationFrame(draw);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!state.isLyriaPlaying) {
      const w = canvas.width;
      const h = canvas.height;
      const t = Date.now() * 0.002;
      ctx.beginPath();
      ctx.lineWidth = 2 * window.devicePixelRatio;
      ctx.strokeStyle = 'rgba(126, 34, 206, 0.25)';
      for (let x = 0; x < w; x += 4) {
        const y = h / 2 + Math.sin(x * 0.015 + t) * (h * 0.08);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      return;
    }

    state.lyriaAnalyser.getByteFrequencyData(freqData);
    state.lyriaAnalyser.getByteTimeDomainData(timeData);

    const width = canvas.width;
    const height = canvas.height;
    const barWidth = (width / bufferLength) * 2.2;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const barHeight = (freqData[i] / 255.0) * height * 0.85;
      const grad = ctx.createLinearGradient(0, height, 0, height - barHeight);
      grad.addColorStop(0, '#581C87');
      grad.addColorStop(0.6, '#9333EA');
      grad.addColorStop(1, '#06B6D4');
      ctx.fillStyle = grad;
      ctx.fillRect(x, height - barHeight, barWidth - 1.5, barHeight);
      x += barWidth;
    }

    ctx.beginPath();
    ctx.lineWidth = 2.5 * window.devicePixelRatio;
    ctx.strokeStyle = '#FFFFFF';
    ctx.shadowColor = 'rgba(168, 85, 247, 0.85)';
    ctx.shadowBlur = 8;
    const sliceWidth = width / bufferLength;
    let wx = 0;
    for (let i = 0; i < bufferLength; i++) {
      const v = timeData[i] / 128.0;
      const wy = (v * height) / 2;
      if (i === 0) ctx.moveTo(wx, wy);
      else ctx.lineTo(wx, wy);
      wx += sliceWidth;
    }
    ctx.stroke();
    ctx.shadowBlur = 0;
  }
  draw();
}

function setupLyriaEventListeners() {
  if (el.lyriaPlayBtn) {
    el.lyriaPlayBtn.addEventListener('click', () => {
      // Pause Field Master if playing
      if (state.isPlaying) {
        state.audio.pause();
      }

      initLyriaAudioContext();
      if (state.lyriaAudioCtx && state.lyriaAudioCtx.state === 'suspended') {
        state.lyriaAudioCtx.resume();
      }
      if (state.isLyriaPlaying) {
        state.lyriaAudio.pause();
      } else {
        state.lyriaAudio.play().catch((e) => console.warn('Lyria play interrupted:', e));
      }
    });
  }

  state.lyriaAudio.addEventListener('play', () => {
    state.isLyriaPlaying = true;
    if (el.lyriaWaveformPlaceholder) el.lyriaWaveformPlaceholder.classList.add('hidden');
    if (el.lyriaAudioStatusTag) {
      el.lyriaAudioStatusTag.textContent = 'Streaming Lyria 2 48kHz';
      el.lyriaAudioStatusTag.className = 'text-xs font-mono font-medium px-2.5 py-1 rounded-full bg-purple-100 text-purple-900 border border-purple-300';
    }
    updateLyriaPlayButtonUI();
  });

  state.lyriaAudio.addEventListener('pause', () => {
    state.isLyriaPlaying = false;
    if (el.lyriaAudioStatusTag) {
      el.lyriaAudioStatusTag.textContent = 'Paused';
      el.lyriaAudioStatusTag.className = 'text-xs font-mono font-medium px-2.5 py-1 rounded-full bg-slate-100 text-slate-700';
    }
    updateLyriaPlayButtonUI();
  });

  state.lyriaAudio.addEventListener('timeupdate', () => {
    if (!state.lyriaAudio.duration) return;
    const cur = state.lyriaAudio.currentTime;
    const dur = state.lyriaAudio.duration;
    if (el.lyriaCurrentTime) el.lyriaCurrentTime.textContent = formatTime(cur);
    if (el.lyriaTotalDuration) el.lyriaTotalDuration.textContent = formatTime(dur);
    if (el.lyriaSeekBar) el.lyriaSeekBar.value = (cur / dur) * 100;
  });

  state.lyriaAudio.addEventListener('ended', () => {
    if (!state.isLyriaLooping) {
      state.isLyriaPlaying = false;
      updateLyriaPlayButtonUI();
    }
  });

  if (el.lyriaSeekBar) {
    el.lyriaSeekBar.addEventListener('input', (e) => {
      if (!state.lyriaAudio.duration) return;
      const pct = parseFloat(e.target.value);
      state.lyriaAudio.currentTime = (pct / 100) * state.lyriaAudio.duration;
    });
  }

  if (el.lyriaVolumeBar) {
    el.lyriaVolumeBar.addEventListener('input', (e) => {
      state.lyriaAudio.volume = parseFloat(e.target.value);
      updateLyriaVolumeIcon();
    });
  }

  if (el.lyriaMuteBtn) {
    el.lyriaMuteBtn.addEventListener('click', () => {
      state.lyriaAudio.muted = !state.lyriaAudio.muted;
      updateLyriaVolumeIcon();
    });
  }

  if (el.lyriaLoopBtn) {
    el.lyriaLoopBtn.addEventListener('click', () => {
      state.isLyriaLooping = !state.isLyriaLooping;
      state.lyriaAudio.loop = state.isLyriaLooping;
      el.lyriaLoopBtn.classList.toggle('bg-purple-100', state.isLyriaLooping);
      el.lyriaLoopBtn.classList.toggle('text-purple-800', state.isLyriaLooping);
      el.lyriaLoopBtn.classList.toggle('border-purple-300', state.isLyriaLooping);
    });
  }
}

// ---------------------------------------------------------------------------
// Helpers & Resize
// ---------------------------------------------------------------------------

function resizeCanvases() {
  [el.waveformCanvas, el.lyriaWaveformCanvas].forEach((canvas) => {
    if (!canvas) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
  });
}

function formatTime(sec) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}

function updatePlayButtonUI() {
  if (!el.playBtn) return;
  if (state.isPlaying) {
    el.playBtn.innerHTML = `<i data-lucide="pause" class="w-6 h-6 fill-current"></i>`;
  } else {
    el.playBtn.innerHTML = `<i data-lucide="play" class="w-6 h-6 fill-current ml-0.5"></i>`;
  }
  if (window.lucide) window.lucide.createIcons();
}

function updateVolumeIcon() {
  if (!el.muteBtn) return;
  let iconName = 'volume-2';
  if (state.audio.muted || state.audio.volume === 0) {
    iconName = 'volume-x';
  } else if (state.audio.volume < 0.5) {
    iconName = 'volume-1';
  }
  el.muteBtn.innerHTML = `<i data-lucide="${iconName}" class="w-5 h-5"></i>`;
  if (window.lucide) window.lucide.createIcons();
}

function updateLyriaPlayButtonUI() {
  if (!el.lyriaPlayBtn) return;
  if (state.isLyriaPlaying) {
    el.lyriaPlayBtn.innerHTML = `<i data-lucide="pause" class="w-6 h-6 fill-current"></i>`;
  } else {
    el.lyriaPlayBtn.innerHTML = `<i data-lucide="play" class="w-6 h-6 fill-current ml-0.5"></i>`;
  }
  if (window.lucide) window.lucide.createIcons();
}

function updateLyriaVolumeIcon() {
  if (!el.lyriaMuteBtn) return;
  let iconName = 'volume-2';
  if (state.lyriaAudio.muted || state.lyriaAudio.volume === 0) {
    iconName = 'volume-x';
  } else if (state.lyriaAudio.volume < 0.5) {
    iconName = 'volume-1';
  }
  el.lyriaMuteBtn.innerHTML = `<i data-lucide="${iconName}" class="w-5 h-5"></i>`;
  if (window.lucide) window.lucide.createIcons();
}

// Start App on DOM Ready
document.addEventListener('DOMContentLoaded', init);
