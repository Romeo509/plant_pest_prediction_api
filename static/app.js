// app.js — handles drag/drop, uploads, UI updates and logs

const dropZone = document.getElementById('dropZone');
const imageInput = document.getElementById('imageInput');
const previewImage = document.getElementById('previewImage');
const dropHint = document.getElementById('dropHint');
const predictBtn = document.getElementById('predictBtn');
const clearBtn = document.getElementById('clearBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const detailedOutput = document.getElementById('detailedOutput');
const finalPrediction = document.getElementById('finalPrediction');
const confidenceBar = document.getElementById('confidenceBar');
const confidencePct = document.getElementById('confidencePct');
const confidenceLabel = document.getElementById('confidenceLabel');
const healthStatus = document.getElementById('healthStatus');
const logsArea = document.getElementById('logsArea');
const clearLogs = document.getElementById('clearLogs');
const errorBox = document.getElementById('error');
const themeToggleBtn = document.getElementById('themeToggle'); // legacy, may not exist
const themeSelect = document.getElementById('themeSelect');
const kpiRequests = document.getElementById('kpiRequests');
const kpiLatency = document.getElementById('kpiLatency');
const kpiModel = document.getElementById('kpiModel');
const kpiUptime = document.getElementById('kpiUptime');

let currentFile = null;
let startTime = Date.now();
let totalRequests = 0;
let totalLatencyMs = 0;

// Drag & drop handlers
['dragenter','dragover'].forEach(evt => {
  dropZone.addEventListener(evt, e => {
    e.preventDefault(); e.stopPropagation();
    dropZone.classList.add('dragover');
  });
});
['dragleave','drop'].forEach(evt => {
  dropZone.addEventListener(evt, e => {
    e.preventDefault(); e.stopPropagation();
    dropZone.classList.remove('dragover');
  });
});

dropZone.addEventListener('drop', e => {
  const dt = e.dataTransfer;
  if (!dt) return;
  const file = dt.files[0];
  handleFile(file);
});

// file chooser
imageInput.addEventListener('change', e => {
  const file = e.target.files[0];
  handleFile(file);
});

// clicking the label should trigger file input — label has for attribute

// clear and predict
clearBtn.addEventListener('click', clearSelection);
predictBtn.addEventListener('click', uploadImage);
clearLogs.addEventListener('click', () => { logsArea.innerHTML = ''; addLog('Logs cleared by user'); });

function handleFile(file) {
  if (!file) return;
  if (!file.type.startsWith('image/')) {
    alert('Please upload an image file');
    return;
  }
  currentFile = file;
  const url = URL.createObjectURL(file);
  previewImage.src = url;
  previewImage.style.display = 'block';
  dropHint.style.display = 'none';
  results.style.display = 'none';
  errorBox.style.display = 'none';
  addLog(`File selected: ${file.name} (${Math.round(file.size/1024)} KB)`);
}

function clearSelection() {
  currentFile = null;
  imageInput.value = '';
  previewImage.src = '';
  previewImage.style.display = 'none';
  dropHint.style.display = 'block';
  results.style.display = 'none';
  addLog('Selection cleared');
}

async function uploadImage() {
  if (!currentFile) {
    alert('Select an image first (drag or tap)');
    return;
  }
  // UI updates
  loading.style.display = 'block';
  results.style.display = 'none';
  errorBox.style.display = 'none';
  healthStatus.textContent = 'Analyzing';
  addLog('INFO: Starting upload to /api/predict');

  const formData = new FormData();
  formData.append('file', currentFile);

  try {
    const t0 = performance.now();
    const resp = await fetch('/api/predict', { method: 'POST', body: formData });
    const t1 = performance.now();
    const latency = Math.max(0, t1 - t0);
    totalRequests += 1;
    totalLatencyMs += latency;
    const now = new Date().toISOString();
    addLog(`INFO: ${resp.status} ${resp.statusText} — POST /api/predict (${now}) • ${latency.toFixed(0)}ms`);
    updateKpis();
    const data = await resp.json().catch(() => null);

    if (!resp.ok) {
      const msg = data?.detail || `Server returned ${resp.status}`;
      throw new Error(msg);
    }

    displayResults(data);
  } catch (err) {
    loading.style.display = 'none';
    errorBox.style.display = 'block';
    errorBox.textContent = '❌ Error: ' + (err.message || err);
    healthStatus.textContent = 'Error';
    addLog('ERROR: ' + (err.message || String(err)));
  }
}

function displayResults(data) {
  loading.style.display = 'none';
  results.style.display = 'block';
  // expected fields: disease, confidence (0-1 or percent), all_probs, final_prediction
  const confidence = normalizeConfidence(data.confidence);
  finalPrediction.textContent = `🎯 ${data.final_prediction || data.disease || 'Unknown'}`;
  confidenceLabel.textContent = `Confidence: ${Math.round(confidence*100)}%`;
  confidenceBar.style.width = `${Math.round(confidence*100)}%`;
  confidencePct.textContent = `${Math.round(confidence*100)}%`;
  healthStatus.textContent = 'Ready';
  detailedOutput.textContent = JSON.stringify({ disease: data.disease, confidence: data.confidence, all_probs: data.all_probs }, null, 2);

  addLog(`INFO: Prediction complete — ${data.final_prediction || data.disease} (${Math.round(confidence*100)}%)`);
  // update charts with the prediction
  recordPrediction(data.final_prediction || data.disease || 'unknown');
}

function normalizeConfidence(v) {
  if (v == null) return 0;
  if (v > 1) return Math.min(1, v / 100);
  return Math.max(0, Math.min(1, v));
}

function addLog(msg) {
  const time = new Date().toLocaleTimeString();
  const line = document.createElement('div');
  const level = msg.startsWith('ERROR') ? 'log-error' : 'log-info';
  line.className = level;
  line.textContent = `${time} — ${msg}`;
  logsArea.appendChild(line);
  // keep scroll to bottom
  logsArea.scrollTop = logsArea.scrollHeight;
}

// add initial messages
addLog('UI ready');
addLog('Tip: drag an image into the left panel or click to choose');

// accessibility: clicking the dropZone label should open file picker
const fileLabel = document.querySelector('.file-label');
if (fileLabel) fileLabel.addEventListener('click', (e) => { imageInput.click(); });

// Theme toggle
function applyThemeClass(name) {
  document.body.classList.remove('theme-dark', 'theme-forest');
  if (name === 'dark') document.body.classList.add('theme-dark');
  if (name === 'forest') document.body.classList.add('theme-forest');
}

function setThemeByName(name) {
  const valid = ['light','dark','forest'];
  const theme = valid.includes(name) ? name : 'light';
  applyThemeClass(theme);
  localStorage.setItem('themeName', theme);
  if (themeSelect) themeSelect.value = theme;
}

// Legacy toggle (kept for compatibility if present)
if (themeToggleBtn) {
  themeToggleBtn.addEventListener('click', () => {
    const isDark = document.body.classList.contains('theme-dark');
    setThemeByName(isDark ? 'light' : 'dark');
  });
}

if (themeSelect) {
  themeSelect.addEventListener('change', (e) => setThemeByName(e.target.value));
}

// KPIs
function updateKpis() {
  if (kpiRequests) kpiRequests.textContent = String(totalRequests);
  const avg = totalRequests ? (totalLatencyMs / totalRequests) : 0;
  if (kpiLatency) kpiLatency.textContent = totalRequests ? `${avg.toFixed(0)} ms` : '—';
  if (kpiModel && kpiModel.textContent.trim() === '') kpiModel.textContent = 'maize-disease-v1';
}
function tickUptime() {
  const sec = Math.floor((Date.now() - startTime) / 1000);
  const hh = String(Math.floor(sec/3600)).padStart(2,'0');
  const mm = String(Math.floor((sec%3600)/60)).padStart(2,'0');
  const ss = String(sec%60).padStart(2,'0');
  if (kpiUptime) kpiUptime.textContent = `${hh}:${mm}:${ss}`;
}

// --- Charts logic ---
let requestsChart = null;
let diseasesChart = null;
const maxPoints = 20;
let chartLabels = [];
let cumulativeRequests = 0;
const diseaseCounts = {}; // name -> cumulative count

function initCharts() {
  const reqCtx = document.getElementById('requestsChart').getContext('2d');
  const disCtx = document.getElementById('diseasesChart').getContext('2d');

  requestsChart = new Chart(reqCtx, {
    type: 'line',
    data: { labels: chartLabels, datasets: [{ label: 'Total Requests', data: [], borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.08)', tension: 0.3 }] },
    options: { responsive: true, maintainAspectRatio: false, scales: { x: { display: true }, y: { beginAtZero: true } } }
  });

  diseasesChart = new Chart(disCtx, {
    type: 'line',
    data: { labels: chartLabels, datasets: [] },
    options: { responsive: true, maintainAspectRatio: false, scales: { x: { display: true }, y: { beginAtZero: true } } }
  });
}

function recordPrediction(disease) {
  const timeLabel = new Date().toLocaleTimeString();
  // push label
  chartLabels.push(timeLabel);
  if (chartLabels.length > maxPoints) chartLabels.shift();

  // requests: cumulative
  cumulativeRequests += 1;
  const reqDataset = requestsChart.data.datasets[0].data;
  reqDataset.push(cumulativeRequests);
  if (reqDataset.length > maxPoints) reqDataset.shift();
  requestsChart.data.labels = chartLabels.slice();

  // diseases: update counts
  if (!diseaseCounts[disease]) {
    diseaseCounts[disease] = 0;
    // create new dataset for this disease, initialize previous points to zero
    const color = randomColor();
    const newDs = { label: disease, data: Array(chartLabels.length-1).fill(0).concat([0]), borderColor: color, backgroundColor: color+'22', tension: 0.3 };
    diseasesChart.data.datasets.push(newDs);
  }
  diseaseCounts[disease] += 1;

  // ensure each dataset has value for this new label
  diseasesChart.data.datasets.forEach(ds => {
    if (ds.label === disease) {
      const last = ds.data.length ? ds.data[ds.data.length-1] : 0;
      ds.data.push((last || 0) + 1);
    } else {
      const last = ds.data.length ? ds.data[ds.data.length-1] : 0;
      ds.data.push(last || 0);
    }
    if (ds.data.length > maxPoints) ds.data.shift();
  });

  // trim labels on both charts
  if (requestsChart.data.labels.length > maxPoints) requestsChart.data.labels.shift();
  if (diseasesChart.data.labels.length > maxPoints) diseasesChart.data.labels.shift();

  // sync labels
  diseasesChart.data.labels = chartLabels.slice();

  requestsChart.update();
  diseasesChart.update();
}

function randomColor() {
  const r = Math.floor(Math.random()*180)+50;
  const g = Math.floor(Math.random()*180)+50;
  const b = Math.floor(Math.random()*180)+50;
  return `rgb(${r}, ${g}, ${b})`;
}

// Initialize charts when DOM is ready (canvas elements exist)
window.addEventListener('load', () => {
  // theme preference
  const savedName = localStorage.getItem('themeName');
  if (savedName) {
    setThemeByName(savedName);
  } else {
    // migrate old boolean if exists
    const saved = localStorage.getItem('themeDark');
    if (saved === '1') setThemeByName('dark');
    else setThemeByName('light');
  }
  initCharts();
  updateKpis();
  tickUptime();
  setInterval(tickUptime, 1000);
});

