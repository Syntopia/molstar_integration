const MOLSTAR_CDN = 'https://cdn.jsdelivr.net/npm/molstar/build/viewer/molstar.min.js';
const MOLSTAR_CSS = 'https://cdn.jsdelivr.net/npm/molstar/build/viewer/molstar.css';
const MVS_LABEL = 'MolViewSpec';

function ensureStyle(targetRoot) {
  const root = targetRoot || document;
  const existing = root.querySelector
    ? root.querySelector('link[data-molstar-css="true"]')
    : document.querySelector('link[data-molstar-css="true"]');
  if (existing) return;
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = MOLSTAR_CSS;
  link.dataset.molstarCss = 'true';
  const host = root && root.host ? root : document.head;
  host.appendChild(link);
}

function loadScript(url) {
  if (window.molstar) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const existing = document.querySelector(`script[src="${url}"]`);
    if (existing) {
      existing.addEventListener('load', () => resolve());
      existing.addEventListener('error', () => reject(new Error('Mol* script failed to load.')));
      return;
    }
    const script = document.createElement('script');
    script.src = url;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Mol* script failed to load.'));
    document.head.appendChild(script);
  });
}

function logInfo(message, detail) {
  console.log('[molstar-widget]', message, detail || '');
}

function logError(message, detail) {
  console.error('[molstar-widget]', message, detail || '');
}

function getBool(model, key, fallback) {
  const value = model.get(key);
  return typeof value === 'boolean' ? value : fallback;
}

async function createViewer(host, model, rootNode) {
  ensureStyle(rootNode);
  await loadScript(MOLSTAR_CDN);
  if (!window.molstar || !window.molstar.Viewer) {
    throw new Error('Mol* viewer bundle missing.');
  }
  logInfo(`Creating Mol* viewer (${MVS_LABEL})`);
  return window.molstar.Viewer.create(host, {
    layoutShowControls: getBool(model, 'layout_show_controls', false),
    layoutShowRemoteState: getBool(model, 'layout_show_remote_state', false),
    layoutShowLog: getBool(model, 'layout_show_log', true),
    layoutIsExpanded: getBool(model, 'layout_is_expanded', false),
    showWelcomeMessage: getBool(model, 'show_welcome_message', false),
    viewportShowExpand: getBool(model, 'viewport_show_expand', true),
    viewportShowControls: getBool(model, 'viewport_show_controls', true),
    collapseLeftPanel: getBool(model, 'collapse_left_panel', true),
    illumination: false,
  });
}

function decodeBase64(data) {
  if (!data) return new Uint8Array();
  const binary = atob(data);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

function applyShadowDomEventPatch(widgetElement) {
  const eventTypes = ['mousemove', 'mousedown', 'mouseup', 'click', 'wheel'];
  const captureHandler = (event) => {
    const path = event.composedPath && event.composedPath();
    if (!path || !path.includes(widgetElement)) return;
    const canvas = path.find((node) => node && node.tagName === 'CANVAS');
    if (!canvas) return;
    try {
      Object.defineProperty(event, 'target', {
        value: canvas,
        enumerable: true,
        configurable: true,
      });
    } catch (error) {
      // Ignore if the event target cannot be overridden.
    }
  };
  eventTypes.forEach((type) => {
    window.addEventListener(type, captureHandler, { capture: false });
  });
  return () => {
    eventTypes.forEach((type) => {
      window.removeEventListener(type, captureHandler, { capture: false });
    });
  };
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
  if (!updated) {
    logInfo('Frame index already applied.', `modelIndex=${modelIndex}`);
    return;
  }
  await builder.commit();
  logInfo('Updated Mol* trajectory frame', `modelIndex=${modelIndex}`);
}


export function render({ model, el }) {
  el.classList.add('molstar-widget');
  el.innerHTML = '';
  const rootNode = el.getRootNode ? el.getRootNode() : document;
  const cleanupEventPatch = applyShadowDomEventPatch(el);

  const viewerHost = document.createElement('div');
  viewerHost.className = 'molstar-host';
  el.appendChild(viewerHost);

  let disposed = false;
  const state = {
    viewer: null,
    loading: false,
    lastMvsx: null,
  };

  function setStatus(text) {
    logInfo(text);
  }

  async function refresh() {
    if (disposed) return;
    const mvsxBase64 = model.get('mvsx_base64');
    if (!mvsxBase64) {
      setStatus('Awaiting MolViewSpec MVSX payload.');
      return;
    }
    if (state.loading || mvsxBase64 === state.lastMvsx) {
      return;
    }
    state.loading = true;
    state.lastMvsx = mvsxBase64;
    try {
      setStatus('Loading Mol*...');
      if (!state.viewer) {
        const viewer = await createViewer(viewerHost, model, rootNode);
        if (disposed) {
          viewer.dispose();
          return;
        }
        state.viewer = viewer;
      }
      if (typeof state.viewer.loadMvsData !== 'function') {
        throw new Error('Mol* viewer does not expose loadMvsData.');
      }
      const bytes = decodeBase64(mvsxBase64);
      logInfo(`Loading ${MVS_LABEL} MVSX payload`, `bytes=${bytes.length}`);
      await state.viewer.loadMvsData(bytes, 'mvsx');
      setStatus('MolViewSpec rendered.');
      const currentIndex = model.get('frame_index');
      if (Number.isFinite(currentIndex)) {
        await updateModelIndex(state.viewer.plugin, currentIndex);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      logError('MolViewSpec error', message);
      logError('Failed to render MolViewSpec', message);
    } finally {
      state.loading = false;
    }
  }

  model.on('change:mvsx_base64', refresh);
  model.on('change:frame_index', () => {
    logInfo('frame_index changed', model.get('frame_index'));
    if (!state.viewer) return;
    if (state.loading) return;
    updateModelIndex(state.viewer.plugin, model.get('frame_index')).catch((error) => {
      const message = error instanceof Error ? error.message : String(error);
      logError('Failed to update Mol* trajectory frame', message);
    });
  });
  refresh();
  return () => {
    disposed = true;
    cleanupEventPatch?.();
    if (state.viewer) {
      logInfo('Disposing Mol* viewer');
      state.viewer.dispose();
      state.viewer = null;
    }
  };
}

export default { render };
