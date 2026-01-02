const MOLSTAR_CDN = 'https://cdn.jsdelivr.net/npm/molstar/build/viewer/molstar.min.js';
const MOLSTAR_CSS = 'https://cdn.jsdelivr.net/npm/molstar/build/viewer/molstar.css';

const container = document.getElementById('molstar-container');
const selectEl = document.getElementById('trajectory-select');
const sliderEl = document.getElementById('frame-slider');
const frameValueEl = document.getElementById('frame-value');
const statusEl = document.getElementById('status');

let viewer = null;
let loading = false;

function logStatus(message, detail) {
  const label = detail ? `${message} (${detail})` : message;
  console.log('[molstar-webapp]', label);
  statusEl.textContent = label;
}

function ensureStyle() {
  if (document.querySelector('link[data-molstar-css="true"]')) return;
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = MOLSTAR_CSS;
  link.dataset.molstarCss = 'true';
  document.head.appendChild(link);
}

function loadScript(url) {
  if (window.molstar) return Promise.resolve();
  return new Promise((resolve, reject) => {
    let script = document.querySelector(`script[src="${url}"]`);
    if (script) {
      script.addEventListener('load', () => resolve());
      script.addEventListener('error', () => reject(new Error('Mol* script failed to load')));
      return;
    }
    script = document.createElement('script');
    script.src = url;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Mol* script failed to load'));
    document.head.appendChild(script);
  });
}

async function createViewer() {
  ensureStyle();
  await loadScript(MOLSTAR_CDN);
  logStatus('Creating viewer');
  viewer = await window.molstar.Viewer.create(container, {
    layoutShowControls: false,
    layoutShowRemoteState: false,
    layoutShowLog: true,
    layoutIsExpanded: false,
    showWelcomeMessage: false,
    viewportShowExpand: true,
    viewportShowControls: true,
    collapseLeftPanel: true,
    illumination: false,
  });
}

async function updateModelIndex(plugin, frameIndex) {
  if (!plugin?.state?.data) return;
  const state = plugin.state.data;
  const builder = state.build();
  const modelIndex = Math.max(
    Math.round(Number.isFinite(frameIndex) ? frameIndex : 0),
    0,
  );
  let updated = false;
  state.cells.forEach((cell, ref) => {
    const params = cell?.transform?.params;
    if (!params) return;
    if (Object.prototype.hasOwnProperty.call(params, 'modelIndex')) {
      if (params.modelIndex !== modelIndex) {
        builder.to(ref).update({ modelIndex });
        updated = true;
      }
      return;
    }
    if (Object.prototype.hasOwnProperty.call(params, 'frameIndex')) {
      if (params.frameIndex !== modelIndex) {
        builder.to(ref).update({ frameIndex: modelIndex });
        updated = true;
      }
    }
  });
  if (!updated) return;
  await builder.commit();
}

async function loadTrajectory(trajId) {
  if (!trajId) return;
  if (loading) return;
  loading = true;
  try {
    logStatus('Loading trajectory', trajId);
    const response = await fetch(`/api/mvsx/${trajId}`);
    if (!response.ok) {
      throw new Error(`Failed to load MVSX (${response.status})`);
    }
    const buffer = await response.arrayBuffer();
    const bytes = new Uint8Array(buffer);
    await viewer.loadMvsData(bytes, 'mvsx');
    logStatus('Rendered MolViewSpec', trajId);
    sliderEl.max = '99';
  } catch (error) {
    console.error('[molstar-webapp] Failed to load trajectory', error);
    logStatus('Failed to load trajectory');
  } finally {
    loading = false;
  }
}

async function init() {
  logStatus('Fetching trajectories');
  const response = await fetch('/api/trajectories');
  if (!response.ok) {
    logStatus('Failed to load trajectories');
    return;
  }
  const items = await response.json();
  selectEl.innerHTML = '';
  items.forEach((entry) => {
    const option = document.createElement('option');
    option.value = entry.id;
    option.textContent = entry.label;
    selectEl.appendChild(option);
  });
  if (!viewer) {
    await createViewer();
  }
  const initial = selectEl.value;
  await loadTrajectory(initial);
}

selectEl.addEventListener('change', (event) => {
  const next = event.target.value;
  loadTrajectory(next);
});

sliderEl.addEventListener('input', (event) => {
  const value = Number(event.target.value);
  frameValueEl.textContent = String(value);
  if (!viewer || loading) return;
  updateModelIndex(viewer.plugin, value).catch((error) => {
    console.error('[molstar-webapp] Failed to update frame', error);
  });
});

init().catch((error) => {
  console.error('[molstar-webapp] Failed to initialize', error);
  logStatus('Initialization failed');
});
