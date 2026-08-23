// ADAPTIX-FARM — Interactive Client Application Engine with Dark Mode & Bilingual Voice

let currentFile = null;
let currentLanguage = 'en';
let isRecording = false;
let userUsedVoice = false;
let speechRecognition = null;
let currentExecutionState = null;
let costChartInstance = null;
let latencyChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  if (window.lucide) {
    lucide.createIcons();
  }
  setupDropzone();
  setupSpeechRecognition();
  loadDocumentList();
  loadHistory();
  loadMetrics();
});

// ==========================================
// DARK / LIGHT THEME TOGGLE & PERSISTENCE
// ==========================================
function initTheme() {
  const savedTheme = localStorage.getItem('adaptix_theme');
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
}

function toggleDarkMode() {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('adaptix_theme', isDark ? 'dark' : 'light');
  if (window.lucide) {
    lucide.createIcons();
  }
  // Re-render charts with updated theme colors if on metrics tab
  if (costChartInstance || latencyChartInstance) {
    renderMetricsCharts();
  }
}

// ==========================================
// TAB NAVIGATION
// ==========================================
function switchTab(tabId) {
  document.querySelectorAll('.tab-pane').forEach(el => {
    el.classList.add('hidden');
    el.classList.remove('active');
  });
  
  const target = document.getElementById(`tab-${tabId}`);
  if (target) {
    target.classList.remove('hidden');
    target.classList.add('active');
  }

  document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
  const activeBtn = Array.from(document.querySelectorAll('.nav-btn')).find(btn => 
    btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(tabId)
  );
  if (activeBtn) {
    activeBtn.classList.add('active');
  }

  if (tabId === 'metrics') {
    loadMetrics();
  } else if (tabId === 'history') {
    loadHistory();
  } else if (tabId === 'documents') {
    loadDocumentList();
  }

  if (window.lucide) lucide.createIcons();
}

// ==========================================
// IMAGE UPLOAD & DROPZONE
// ==========================================
function setupDropzone() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('image-input');

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('border-agri-500', 'bg-agri-50/50', 'dark:bg-agri-950/40');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('border-agri-500', 'bg-agri-50/50', 'dark:bg-agri-950/40');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('border-agri-500', 'bg-agri-50/50', 'dark:bg-agri-950/40');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files[0]) {
      handleFileSelection(fileInput.files[0]);
    }
  });
}

function handleFileSelection(file) {
  currentFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    document.getElementById('preview-img').src = e.target.result;
    document.getElementById('image-filename').textContent = file.name;
    document.getElementById('dropzone-empty').classList.add('hidden');
    document.getElementById('dropzone-preview').classList.remove('hidden');
    
    // Show Pre-flight quality indicator
    const qBadge = document.getElementById('quality-status-badge');
    qBadge.classList.remove('hidden', 'bg-amber-50', 'dark:bg-amber-950/50', 'text-amber-800', 'dark:text-amber-300', 'border-amber-200');
    qBadge.classList.add('bg-emerald-50', 'dark:bg-emerald-950/50', 'text-emerald-800', 'dark:text-emerald-300', 'border', 'border-emerald-200', 'dark:border-emerald-800');
    qBadge.innerHTML = `
      <div class="flex items-center space-x-2">
        <i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-600 dark:text-emerald-400"></i>
        <span>Image loaded (${(file.size / 1024).toFixed(1)} KB). Quality gate ready.</span>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
  };
  reader.readAsDataURL(file);
}

function removeImage(e) {
  if (e) e.stopPropagation();
  currentFile = null;
  document.getElementById('image-input').value = '';
  document.getElementById('dropzone-empty').classList.remove('hidden');
  document.getElementById('dropzone-preview').classList.add('hidden');
  document.getElementById('quality-status-badge').classList.add('hidden');
}

// ==========================================
// VOICE SPEECH-TO-TEXT & LANGUAGE
// ==========================================
function setLanguage(lang) {
  currentLanguage = lang;
  
  const isEn = lang === 'en';
  document.getElementById('lang-en').className = isEn
    ? "px-2.5 py-1 text-xs font-bold rounded-lg bg-white dark:bg-slate-700 text-agri-800 dark:text-agri-300 shadow-sm"
    : "px-2.5 py-1 text-xs font-bold rounded-lg text-slate-600 dark:text-slate-400";
    
  document.getElementById('lang-ta').className = !isEn
    ? "px-2.5 py-1 text-xs font-bold rounded-lg bg-white dark:bg-slate-700 text-agri-800 dark:text-agri-300 shadow-sm"
    : "px-2.5 py-1 text-xs font-bold rounded-lg text-slate-600 dark:text-slate-400";
    
  const langLabel = document.getElementById('voice-listening-lang');
  if (langLabel) {
    langLabel.textContent = isEn ? "English" : "தமிழ்";
  }

  if (speechRecognition) {
    speechRecognition.lang = lang === 'ta' ? 'ta-IN' : 'en-US';
  }
}

function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    speechRecognition = new SpeechRecognition();
    speechRecognition.continuous = false;
    speechRecognition.interimResults = false;
    speechRecognition.lang = 'en-US';

    speechRecognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      document.getElementById('query-input').value = transcript;
      stopVoiceRecording();
    };

    speechRecognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      stopVoiceRecording();
    };

    speechRecognition.onend = () => {
      stopVoiceRecording();
    };
  }
}

function toggleVoiceRecording() {
  if (isRecording) {
    stopVoiceRecording();
  } else {
    startVoiceRecording();
  }
}

function startVoiceRecording() {
  isRecording = true;
  userUsedVoice = true;
  document.getElementById('voice-btn-label').textContent = 'Stop Recording';
  document.getElementById('voice-recording-indicator').classList.remove('hidden');
  document.getElementById('voice-recording-indicator').classList.add('flex');
  
  if (speechRecognition) {
    speechRecognition.lang = currentLanguage === 'ta' ? 'ta-IN' : 'en-US';
    try {
      speechRecognition.start();
    } catch (e) {
      console.warn(e);
    }
  } else {
    // Simulated voice recording if browser API unavailable
    setTimeout(() => {
      if (isRecording) {
        document.getElementById('query-input').value = currentLanguage === 'ta' 
          ? "இந்த தக்காளி இலையில் மஞ்சள் புள்ளிகள் மற்றும் கருகிய பகுதிகள் வருகிறது. என்ன பிரச்சனை?" 
          : "My tomato lower leaves have yellow rings with dark concentric spots.";
        stopVoiceRecording();
      }
    }, 2500);
  }
}

function stopVoiceRecording() {
  isRecording = false;
  document.getElementById('voice-btn-label').textContent = 'Record Voice (Speak Query)';
  document.getElementById('voice-recording-indicator').classList.add('hidden');
  document.getElementById('voice-recording-indicator').classList.remove('flex');
  if (speechRecognition) {
    try { speechRecognition.stop(); } catch(e) {}
  }
}

// ==========================================
// PRESET DEMO SCENARIOS
// ==========================================
function loadPreset(presetKey) {
  removeImage(null);
  
  if (presetKey === 'tomato_early_blight') {
    document.getElementById('context-crop').value = 'Tomato';
    document.getElementById('context-stage').value = 'Vegetative';
    document.getElementById('context-season').value = 'Kharif (Monsoon/Humid)';
    document.getElementById('context-location').value = 'Coimbatore, Tamil Nadu';
    document.getElementById('context-notes').value = 'Spots appeared after continuous 3 days drizzle.';
    document.getElementById('query-input').value = 'Lower leaves showing dark spots with concentric bullseye rings and yellow halo.';
    setLanguage('en');
    createSyntheticLeafImage("tomato_leaf_early_blight.png", "#2e7d32", "concentric_spots");
  } 
  else if (presetKey === 'chilli_leaf_curl') {
    document.getElementById('context-crop').value = 'Chilli';
    document.getElementById('context-stage').value = 'Flowering';
    document.getElementById('context-season').value = 'Zaid (Summer/Dry)';
    document.getElementById('context-location').value = 'Guntur, Andhra Pradesh';
    document.getElementById('context-notes').value = 'Whiteflies observed on leaf undersides.';
    document.getElementById('query-input').value = 'Top foliage curling upwards with puckered small leaves and stunted growth.';
    setLanguage('en');
    createSyntheticLeafImage("chilli_leaf_curl.png", "#388e3c", "upward_curl");
  } 
  else if (presetKey === 'unseen_query') {
    document.getElementById('context-crop').value = 'Chilli';
    document.getElementById('context-stage').value = 'Vegetative';
    document.getElementById('context-season').value = 'Kharif (Monsoon/Humid)';
    document.getElementById('context-location').value = 'Madurai, Tamil Nadu';
    document.getElementById('context-notes').value = 'Sudden occurrence in young plot.';
    document.getElementById('query-input').value = 'My chilli plant leaves are curling and showing pale patches. What should I check?';
    setLanguage('en');
    createSyntheticLeafImage("chilli_unseen_specimen.png", "#4caf50", "pale_patches");
  } 
  else if (presetKey === 'blurry_fallback') {
    document.getElementById('context-crop').value = 'Tomato';
    document.getElementById('query-input').value = 'Leaf problem please check.';
    createSyntheticBlurryImage("blurry_bad_photo.jpg");
  }
}

function createSyntheticLeafImage(filename, bgColor, pattern) {
  const canvas = document.createElement('canvas');
  canvas.width = 400;
  canvas.height = 400;
  const ctx = canvas.getContext('2d');
  
  // Background
  ctx.fillStyle = '#f8fafc';
  ctx.fillRect(0, 0, 400, 400);

  // Draw stylized leaf
  ctx.save();
  ctx.translate(200, 200);
  ctx.beginPath();
  ctx.moveTo(0, -140);
  ctx.bezierCurveTo(90, -100, 110, 80, 0, 150);
  ctx.bezierCurveTo(-110, 80, -90, -100, 0, -140);
  ctx.fillStyle = bgColor;
  ctx.fill();
  ctx.lineWidth = 3;
  ctx.strokeStyle = '#1b5e20';
  ctx.stroke();

  // Veins
  ctx.beginPath();
  ctx.moveTo(0, -140);
  ctx.lineTo(0, 145);
  ctx.strokeStyle = '#81c784';
  ctx.lineWidth = 2.5;
  ctx.stroke();

  if (pattern === 'concentric_spots') {
    // Bullseye spot 1
    ctx.beginPath();
    ctx.arc(35, -20, 22, 0, 2 * Math.PI);
    ctx.fillStyle = '#fbc02d';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(35, -20, 14, 0, 2 * Math.PI);
    ctx.fillStyle = '#4e342e';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(35, -20, 6, 0, 2 * Math.PI);
    ctx.fillStyle = '#212121';
    ctx.fill();

    // Bullseye spot 2
    ctx.beginPath();
    ctx.arc(-40, 40, 18, 0, 2 * Math.PI);
    ctx.fillStyle = '#fbc02d';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(-40, 40, 11, 0, 2 * Math.PI);
    ctx.fillStyle = '#4e342e';
    ctx.fill();
  }

  ctx.restore();

  canvas.toBlob((blob) => {
    const file = new File([blob], filename, { type: 'image/png' });
    handleFileSelection(file);
  });
}

function createSyntheticBlurryImage(filename) {
  const canvas = document.createElement('canvas');
  canvas.width = 120; // Intentionally small & blurry
  canvas.height = 120;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#2d5a27';
  ctx.fillRect(0, 0, 120, 120);
  ctx.filter = 'blur(12px)';
  ctx.fillStyle = '#888888';
  ctx.fillRect(20, 20, 80, 80);

  canvas.toBlob((blob) => {
    const file = new File([blob], filename, { type: 'image/jpeg' });
    handleFileSelection(file);
    
    // Update badge to alert user
    const qBadge = document.getElementById('quality-status-badge');
    qBadge.classList.remove('hidden', 'bg-emerald-50', 'dark:bg-emerald-950/50', 'text-emerald-800');
    qBadge.classList.add('bg-amber-50', 'dark:bg-amber-950/50', 'text-amber-800', 'dark:text-amber-300', 'border', 'border-amber-200', 'dark:border-amber-800');
    qBadge.innerHTML = `
      <div class="flex items-center space-x-2">
        <i data-lucide="alert-triangle" class="w-4 h-4 text-amber-600 dark:text-amber-400"></i>
        <span>Pre-flight check: Image resolution is low (120x120px). Quality gate test loaded.</span>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
  });
}

// ==========================================
// PIPELINE EXECUTION
// ==========================================
async function executePipeline() {
  const btn = document.getElementById('analyze-btn');
  const btnText = document.getElementById('analyze-btn-text');
  const progress = document.getElementById('pipeline-progress');
  const progressFill = document.getElementById('progress-bar-fill');
  const progressTitle = document.getElementById('progress-step-title');
  const progressDesc = document.getElementById('progress-step-desc');
  const progressElapsed = document.getElementById('progress-elapsed');

  const queryText = document.getElementById('query-input').value.trim();
  const crop = document.getElementById('context-crop').value;
  const stage = document.getElementById('context-stage').value;
  const season = document.getElementById('context-season').value;
  const location = document.getElementById('context-location').value;
  const notes = document.getElementById('context-notes').value;

  if (!currentFile && !queryText) {
    alert("Please provide a crop photograph, voice recording, or text query to begin.");
    return;
  }

  btn.disabled = true;
  btn.classList.add('opacity-75');
  btnText.textContent = "EXECUTING AGENTIC PIPELINE...";
  progress.classList.remove('hidden');
  
  let startTime = Date.now();
  let timer = setInterval(() => {
    progressElapsed.textContent = ((Date.now() - startTime) / 1000).toFixed(1) + 's';
  }, 100);

  try {
    let resultData = null;

    if (currentFile) {
      // Multipart Form Analysis
      progressTitle.textContent = "Step 1/6: Pre-flight Image Quality Check...";
      progressDesc.textContent = "Calculating Laplacian variance, brightness histogram, and resolution";
      progressFill.style.width = "20%";

      const formData = new FormData();
      formData.append('image', currentFile);
      if (crop) formData.append('crop', crop);
      if (stage) formData.append('growth_stage', stage);
      if (season) formData.append('season', season);
      if (location) formData.append('location', location);
      if (notes) formData.append('notes', notes);
      if (queryText) formData.append('user_query', queryText);
      formData.append('language', currentLanguage);

      const res = await fetch('/api/analyze', {
        method: 'POST',
        body: formData
      });
      resultData = await res.json();
    } else {
      // Text-only Analysis
      progressTitle.textContent = "Step 1/5: Agronomic Intent Decomposition...";
      progressFill.style.width = "30%";

      const res = await fetch('/api/analyze/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: queryText,
          crop: crop || undefined,
          growth_stage: stage || undefined,
          season: season || undefined,
          location: location || undefined,
          notes: notes || undefined,
          language: currentLanguage
        })
      });
      resultData = await res.json();
    }

    clearInterval(timer);
    progressFill.style.width = "100%";
    progressTitle.textContent = "Pipeline Execution Complete!";
    progressDesc.textContent = "Synthesizing multi-evidence fusion and verified advisory";

    currentExecutionState = resultData;
    renderResults(resultData);
    renderRouteTrace(resultData);
    renderEvidence(resultData);

    setTimeout(() => {
      progress.classList.add('hidden');
      switchTab('results');
    }, 500);

  } catch (err) {
    clearInterval(timer);
    console.error("Pipeline error:", err);
    alert("Error executing pipeline: " + err.message);
  } finally {
    btn.disabled = false;
    btn.classList.remove('opacity-75');
    btnText.textContent = "RUN ADAPTIX PIPELINE";
  }
}

// ==========================================
// RENDER ASSESSMENT RESULTS
// ==========================================
function renderResults(state) {
  document.getElementById('no-results-view').classList.add('hidden');
  document.getElementById('results-view').classList.remove('hidden');

  document.getElementById('result-req-id').textContent = state.request_id || 'REQ-001';
  
  const finalRes = state.final_result || {};
  const conf = state.confidence || {};
  const verif = state.verification_results || {};
  const quality = state.quality_check;

  document.getElementById('result-condition-title').textContent = finalRes.possible_condition || 'Crop Assessment';
  document.getElementById('result-crop-name').textContent = finalRes.crop || state.context?.crop || 'Crop';
  document.getElementById('result-safety-disclaimer').textContent = ' ' + (finalRes.safety_disclaimer || '');

  // Confidence Badge
  const confBadge = document.getElementById('result-confidence-badge');
  const confScore = Math.round((conf.score || 0.85) * 100);
  const confLevel = conf.level || 'Moderate';
  confBadge.textContent = `${confLevel.toUpperCase()} (${confScore}%)`;
  confBadge.className = `text-lg font-heading font-extrabold mt-0.5 ${
    confLevel === 'High' ? 'text-agri-700 dark:text-agri-400' : confLevel === 'Moderate' ? 'text-blue-700 dark:text-blue-400' : 'text-amber-700 dark:text-amber-400'
  }`;

  // Verification Badge
  const verifBadge = document.getElementById('result-verification-badge');
  const isVerified = verif.verified;
  verifBadge.textContent = isVerified ? "✓ Verified" : "⚠️ Requires Review";
  verifBadge.className = `text-lg font-heading font-extrabold mt-0.5 ${isVerified ? 'text-emerald-700 dark:text-emerald-400' : 'text-amber-700 dark:text-amber-400'}`;

  // Quality Badge
  const qualBadge = document.getElementById('result-quality-badge');
  if (quality) {
    qualBadge.textContent = quality.passed ? `Passed (${quality.blur_score.toFixed(0)} var)` : `Issues Flagged`;
    qualBadge.className = `text-lg font-heading font-extrabold mt-0.5 ${quality.passed ? 'text-slate-700 dark:text-slate-300' : 'text-red-700 dark:text-red-400'}`;
  } else {
    qualBadge.textContent = "Text / No Image";
  }

  // Spoken Script Box
  const spokenTextEl = document.getElementById('result-spoken-script-text');
  if (spokenTextEl) {
    const spokenScript = finalRes.spoken_script || finalRes.assessment_summary || "Assessment complete.";
    spokenTextEl.textContent = `"${spokenScript}"`;
  }

  // Management Checklist
  const mList = document.getElementById('result-management-list');
  mList.innerHTML = '';
  (finalRes.management_advice || []).forEach(item => {
    const li = document.createElement('li');
    li.className = 'flex items-start space-x-2.5 bg-slate-50 dark:bg-slate-950/60 p-3 rounded-2xl border border-slate-100 dark:border-slate-800';
    li.innerHTML = `
      <i data-lucide="arrow-right-circle" class="w-4 h-4 text-agri-600 dark:text-agri-400 mt-0.5 shrink-0"></i>
      <span>${item}</span>
    `;
    mList.appendChild(li);
  });

  // Preventative List
  const pList = document.getElementById('result-preventative-list');
  pList.innerHTML = '';
  (finalRes.preventative_measures || []).forEach(item => {
    const li = document.createElement('li');
    li.className = 'flex items-start space-x-2.5 bg-slate-50 dark:bg-slate-950/60 p-3 rounded-2xl border border-slate-100 dark:border-slate-800';
    li.innerHTML = `
      <i data-lucide="shield-check" class="w-4 h-4 text-blue-600 dark:text-blue-400 mt-0.5 shrink-0"></i>
      <span>${item}</span>
    `;
    pList.appendChild(li);
  });

  if (window.lucide) lucide.createIcons();

  // If farmer used voice recording, automatically speak out the advice in selected language
  if (userUsedVoice) {
    setTimeout(() => {
      playRecommendationAudio(true);
      userUsedVoice = false;
    }, 600);
  }
}

// ==========================================
// RENDER ROUTE TRACE
// ==========================================
function renderRouteTrace(state) {
  const container = document.getElementById('route-trace-timeline');
  container.innerHTML = '';

  document.getElementById('trace-total-latency').textContent = `${(state.total_latency_ms || 0).toFixed(0)} ms`;
  document.getElementById('trace-total-cost').textContent = `$${(state.total_estimated_cost || 0).toFixed(4)}`;

  const traceList = state.route_trace || [];
  traceList.forEach((ev, idx) => {
    const card = document.createElement('div');
    card.className = 'p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950/50 space-y-2 hover:border-agri-400 dark:hover:border-agri-600 transition';

    card.innerHTML = `
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div class="flex items-center space-x-2.5">
          <span class="w-6 h-6 rounded-full bg-agri-100 dark:bg-agri-950 text-agri-800 dark:text-agri-300 text-xs font-bold flex items-center justify-center">${ev.step_number || idx + 1}</span>
          <h4 class="text-sm font-heading font-bold text-slate-900 dark:text-white capitalize">${(ev.task_type || '').replace(/_/g, ' ')}</h4>
          <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300">${ev.provider}</span>
        </div>
        <div class="flex items-center space-x-3 text-xs font-mono text-slate-500 dark:text-slate-400">
          <span>⏱️ ${ev.latency_ms.toFixed(0)} ms</span>
          <span>💵 $${ev.estimated_cost.toFixed(4)}</span>
          <span class="px-2 py-0.5 rounded ${ev.status === 'success' ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300' : 'bg-red-100 dark:bg-red-950 text-red-800 dark:text-red-300'} text-[10px] font-bold uppercase">${ev.status}</span>
        </div>
      </div>
      <p class="text-xs text-slate-600 dark:text-slate-400 pl-8.5">${ev.reason}</p>
      <div class="pl-8.5 text-[11px] text-slate-400 dark:text-slate-500 flex items-center space-x-3">
        <span>Model: <strong class="text-slate-700 dark:text-slate-300">${ev.model_name}</strong></span>
        <span>Routing Score: <strong class="text-slate-700 dark:text-slate-300">${ev.routing_score.toFixed(2)}</strong></span>
      </div>
    `;
    container.appendChild(card);
  });

  if (window.lucide) lucide.createIcons();
}

// ==========================================
// RENDER EVIDENCE MATRIX
// ==========================================
function renderEvidence(state) {
  const fusion = state.evidence_fusion || {};
  const retrieved = state.retrieved_sources || [];

  // Visual
  const vBox = document.getElementById('evidence-visual-content');
  const vis = fusion.visual_evidence || {};
  vBox.innerHTML = `
    <p>• Condition: <span class="text-agri-800 dark:text-agri-300 font-semibold">${vis.possible_condition || vis.initial_assessment || 'N/A'}</span></p>
    <p>• Detected Crop: <span class="text-slate-800 dark:text-slate-200">${vis.detected_crop || vis.crop || 'N/A'}</span></p>
    <p>• Severity: <span class="text-slate-800 dark:text-slate-200">${vis.severity_level || 'Moderate'}</span></p>
  `;

  // RAG
  const rBox = document.getElementById('evidence-rag-content');
  rBox.innerHTML = `
    <p>• Matched Bulletins: <span class="text-blue-800 dark:text-blue-300 font-semibold">${retrieved.length}</span></p>
    <p>• Top Source: <span class="text-slate-800 dark:text-slate-200 truncate block">${retrieved[0]?.document_title || 'N/A'}</span></p>
  `;

  // Context
  const cBox = document.getElementById('evidence-context-content');
  const ctx = state.context || {};
  cBox.innerHTML = `
    <p>• Stated Crop: <span class="text-purple-800 dark:text-purple-300 font-semibold">${ctx.crop || 'Auto-Detected'}</span></p>
    <p>• Growth Stage: <span class="text-slate-800 dark:text-slate-200">${ctx.growth_stage || 'Not specified'}</span></p>
    <p>• Season: <span class="text-slate-800 dark:text-slate-200">${ctx.season || 'Not specified'}</span></p>
  `;

  // Citations list
  const citBox = document.getElementById('citations-container');
  citBox.innerHTML = '';
  if (retrieved.length === 0) {
    citBox.innerHTML = `<p class="text-xs text-slate-400">No extension citations retrieved.</p>`;
  } else {
    retrieved.forEach(src => {
      const card = document.createElement('div');
      card.className = 'p-3.5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/60 space-y-1.5';
      card.innerHTML = `
        <div class="flex items-center justify-between text-xs">
          <span class="font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-1.5">
            <i data-lucide="bookmark" class="w-3.5 h-3.5 text-agri-600 dark:text-agri-400"></i>
            <span>${src.document_title}</span>
          </span>
          <span class="bg-blue-100 dark:bg-blue-950 text-blue-800 dark:text-blue-300 px-2 py-0.5 rounded font-mono text-[10px]">Relevance: ${(src.relevance_score * 100).toFixed(0)}%</span>
        </div>
        <p class="text-xs text-slate-600 dark:text-slate-300 italic">"${src.matched_text}"</p>
        <p class="text-[10px] text-slate-400 dark:text-slate-500">Source: ${src.source_name} (Page ${src.page})</p>
      `;
      citBox.appendChild(card);
    });
  }

  if (window.lucide) lucide.createIcons();
}

// ==========================================
// VOICE TEXT-TO-SPEECH PLAYBACK (ENGLISH & TAMIL)
// ==========================================
function playRecommendationAudio(autoTrigger = false) {
  if (!currentExecutionState) return;
  const finalRes = currentExecutionState.final_result || {};
  
  let textToSpeak = finalRes.spoken_script;
  if (!textToSpeak) {
    if (currentLanguage === 'ta') {
      textToSpeak = `வணக்கம் விவசாயி அவர்களே. பயிர்: ${finalRes.crop}. கண்டறியப்பட்ட பாதிப்பு: ${finalRes.possible_condition}. கணினி நம்பகத்தன்மை: ${currentExecutionState.confidence?.level || 'உயர் நிலை'}. மேலதிக விவரங்களுக்கு வேளாண் அதிகாரியை அணுகவும்.`;
    } else {
      textToSpeak = `${finalRes.crop}. Possible condition is ${finalRes.possible_condition}. ${finalRes.assessment_summary}`;
    }
  }

  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    const targetLang = currentLanguage === 'ta' ? 'ta-IN' : 'en-US';
    utterance.lang = targetLang;
    utterance.rate = currentLanguage === 'ta' ? 0.90 : 0.96;
    utterance.pitch = 1.0;

    // Pick best available voice for language
    const voices = window.speechSynthesis.getVoices();
    if (voices && voices.length > 0) {
      if (currentLanguage === 'ta') {
        const tamilVoice = voices.find(v => v.lang === 'ta-IN' || v.lang === 'ta' || (v.name && v.name.toLowerCase().includes('tamil')));
        if (tamilVoice) utterance.voice = tamilVoice;
      } else {
        const engVoice = voices.find(v => (v.lang === 'en-US' || v.lang === 'en-IN' || v.lang.startsWith('en')) && (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Desktop')));
        if (engVoice) utterance.voice = engVoice;
      }
    }

    const btnText = document.getElementById('tts-btn-text');
    if (btnText) {
      btnText.textContent = currentLanguage === 'ta' ? "🔊 குரல் வழிகாட்டல் ஒலிக்கிறது..." : "🔊 Playing Spoken Reply...";
    }
    
    utterance.onend = () => {
      if (btnText) {
        btnText.textContent = currentLanguage === 'ta' ? "🔊 தமிழில் கேட்க (Listen)" : "🔊 Listen to Advice";
      }
    };
    utterance.onerror = () => {
      if (btnText) {
        btnText.textContent = currentLanguage === 'ta' ? "🔊 தமிழில் கேட்க (Listen)" : "🔊 Listen to Advice";
      }
    };

    window.speechSynthesis.speak(utterance);
  }
}

// ==========================================
// ADVISORY DOCUMENTS & RAG
// ==========================================
async function uploadAdvisoryDoc(e) {
  e.preventDefault();
  const fileInput = document.getElementById('doc-file-input');
  const titleInput = document.getElementById('doc-title-input');
  const cropSelect = document.getElementById('doc-crop-select');
  const btn = document.getElementById('doc-upload-btn');

  if (!fileInput.files[0]) return;

  btn.disabled = true;
  btn.textContent = "Extracting & Indexing Chunks...";

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('title', titleInput.value);
  formData.append('crop', cropSelect.value);

  try {
    const res = await fetch('/api/documents/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    alert(data.message || "Document indexed successfully!");
    fileInput.value = '';
    titleInput.value = '';
    loadDocumentList();
  } catch (err) {
    alert("Error uploading document: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Index Document Chunks";
  }
}

async function loadDocumentList() {
  const container = document.getElementById('doc-chunks-list');
  if (!container) return;

  try {
    const res = await fetch('/api/documents/list');
    const data = await res.json();
    container.innerHTML = '';

    (data.chunks || []).forEach(chk => {
      const card = document.createElement('div');
      card.className = 'p-3.5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/60 text-xs space-y-1.5';
      card.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-bold text-slate-800 dark:text-slate-200">${chk.document_title || chk.document_name}</span>
          <span class="bg-agri-100 dark:bg-agri-950 text-agri-800 dark:text-agri-300 px-2 py-0.5 rounded text-[10px] font-semibold">${chk.crop}</span>
        </div>
        <p class="text-slate-600 dark:text-slate-400 line-clamp-3">${chk.content}</p>
        <p class="text-[10px] text-slate-400 dark:text-slate-500">Page ${chk.page_number} • Chunk ID: ${chk.chunk_id}</p>
      `;
      container.appendChild(card);
    });
  } catch (e) {
    console.warn("Failed to load documents:", e);
  }
}

async function testRAGQuery() {
  const query = document.getElementById('rag-test-query').value.trim();
  const resBox = document.getElementById('rag-test-results');
  if (!query) return;

  resBox.innerHTML = '<p class="text-slate-400">Searching vector store...</p>';
  
  const formData = new FormData();
  formData.append('query', query);

  try {
    const res = await fetch('/api/documents/query', { method: 'POST', body: formData });
    const data = await res.json();
    resBox.innerHTML = '';
    
    (data.results || []).forEach(r => {
      const item = document.createElement('div');
      item.className = 'p-2.5 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700';
      item.innerHTML = `
        <div class="flex justify-between font-semibold text-slate-700 dark:text-slate-300">
          <span>${r.document_title}</span>
          <span class="text-blue-700 dark:text-blue-400 font-mono">${(r.relevance_score * 100).toFixed(0)}%</span>
        </div>
        <p class="text-slate-600 dark:text-slate-400 mt-1 line-clamp-2">${r.matched_text}</p>
      `;
      resBox.appendChild(item);
    });
  } catch (err) {
    resBox.innerHTML = '<p class="text-red-500">Search error</p>';
  }
}

// ==========================================
// HISTORY
// ==========================================
async function loadHistory() {
  const tbody = document.getElementById('history-table-body');
  if (!tbody) return;

  try {
    const res = await fetch('/api/history');
    const list = await res.json();
    tbody.innerHTML = '';

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="py-6 text-center text-slate-400">No previous analyses recorded.</td></tr>`;
      return;
    }

    list.forEach(row => {
      const tr = document.createElement('tr');
      tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/60 transition cursor-pointer';
      tr.onclick = () => loadHistoricalAnalysis(row.request_id);

      tr.innerHTML = `
        <td class="py-3.5 px-4 font-mono font-semibold text-slate-800 dark:text-slate-200">${row.request_id}</td>
        <td class="py-3.5 px-4">${row.crop || 'General'}</td>
        <td class="py-3.5 px-4 font-medium text-slate-800 dark:text-slate-200">${row.possible_condition || 'N/A'}</td>
        <td class="py-3.5 px-4 font-bold ${row.confidence_level === 'High' ? 'text-agri-700 dark:text-agri-400' : 'text-blue-700 dark:text-blue-400'}">${row.confidence_level}</td>
        <td class="py-3.5 px-4">${row.verification_status || 'Verified'}</td>
        <td class="py-3.5 px-4 font-mono">${(row.total_latency_ms || 0).toFixed(0)} ms</td>
        <td class="py-3.5 px-4 font-mono">$${(row.total_estimated_cost || 0).toFixed(4)}</td>
        <td class="py-3.5 px-4 text-right">
          <button class="px-2.5 py-1 bg-slate-100 dark:bg-slate-800 hover:bg-agri-100 dark:hover:bg-agri-900 text-slate-700 dark:text-slate-200 rounded-lg font-semibold text-[10px]">View</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.warn("Failed to load history:", e);
  }
}

async function loadHistoricalAnalysis(requestId) {
  try {
    const res = await fetch(`/api/analysis/${requestId}`);
    const state = await res.json();
    currentExecutionState = state;
    renderResults(state);
    renderRouteTrace(state);
    renderEvidence(state);
    switchTab('results');
  } catch (err) {
    alert("Could not load historical analysis: " + err.message);
  }
}

// ==========================================
// METRICS & CHARTS (DARK/LIGHT AWARE)
// ==========================================
async function loadMetrics() {
  try {
    const res = await fetch('/api/metrics');
    const data = await res.json();

    document.getElementById('metric-total-requests').textContent = data.total_requests || 0;
    document.getElementById('metric-avg-latency').textContent = `${data.average_latency_ms || 0} ms`;
    document.getElementById('metric-total-cost').textContent = `$${(data.total_estimated_cost_usd || 0).toFixed(4)}`;
    document.getElementById('metric-rag-chunks').textContent = data.indexed_rag_documents || 5;

    renderMetricsCharts();
  } catch (e) {
    console.warn("Failed to load metrics:", e);
  }
}

function renderMetricsCharts() {
  const isDark = document.documentElement.classList.contains('dark');
  const textColor = isDark ? '#94a3b8' : '#64748b';
  const gridColor = isDark ? 'rgba(51, 65, 85, 0.4)' : 'rgba(226, 232, 240, 0.8)';

  const ctxCost = document.getElementById('costChart')?.getContext('2d');
  const ctxLat = document.getElementById('latencyChart')?.getContext('2d');

  if (ctxCost) {
    if (costChartInstance) costChartInstance.destroy();
    costChartInstance = new Chart(ctxCost, {
      type: 'doughnut',
      data: {
        labels: ['Open-Weight ($0.00)', 'Commercial A (~$0.015)', 'Commercial B (~$0.009)', 'RAG Engine ($0.0005)'],
        datasets: [{
          data: [0.000, 0.015, 0.009, 0.0005],
          backgroundColor: ['#4ade80', '#38bdf8', '#c084fc', '#fbbf24'],
          borderColor: isDark ? '#0f172a' : '#ffffff',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: textColor, font: { family: 'Inter', size: 11 } }
          }
        }
      }
    });
  }

  if (ctxLat) {
    if (latencyChartInstance) latencyChartInstance.destroy();
    latencyChartInstance = new Chart(ctxLat, {
      type: 'bar',
      data: {
        labels: ['Quality Check', 'Crop ID (Open)', 'Pathology (Comm A)', 'RAG Retrieval', 'Verification (Comm B)'],
        datasets: [{
          label: 'Latency (ms)',
          data: [120, 280, 1450, 180, 920],
          backgroundColor: isDark ? '#22c55e' : '#15803d',
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: { color: textColor, font: { family: 'Inter', size: 10 } },
            grid: { display: false }
          },
          y: {
            beginAtZero: true,
            ticks: { color: textColor, font: { family: 'Inter', size: 10 } },
            grid: { color: gridColor }
          }
        }
      }
    });
  }
}
