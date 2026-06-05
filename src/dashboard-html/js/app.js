/**
 * Bootstrap de FiberMind Analytics Dashboard
 *
 * Responsabilidad única: crear instancias, registrar dependencias,
 * e iniciar la aplicación. No contiene lógica de vistas ni de API.
 * Es el orquestador que conecta todos los módulos vía inyección de dependencias.
 */

import { ApiClient } from './api-client.js';
import { ApplicationState } from './application-state.js';
import { ViewRouter } from './view-router.js';
import * as templates from './html-templates.js';
import * as charts from './charts.js';

// Carga diferida de vistas — solo se importan al navegar
const viewModules = {
  panel: () => import('./views/panel.js'),
  consulta: () => import('./views/consulta.js'),
  auditoria: () => import('./views/auditoria.js'),
  infraestructura: () => import('./views/infraestructura.js'),
  acerca: () => import('./views/acerca.js'),
};

// --- Instancias (singletons) ---
const state = new ApplicationState();
const api = new ApiClient('');
const mainContent = document.getElementById('main-content');

if (!mainContent) {
  throw new Error('[FiberMind] #main-content no encontrado en el DOM');
}

const router = new ViewRouter(mainContent);

// --- Inicialización ---
async function initialize() {
  try {
    await loadAvailableIsps();
    await refreshSystemStatus();
  } catch (error) {
    console.warn('[FiberMind] Error en inicialización:', error.message);
  }

  setupSidebarNavigation();
  navigateToView('panel');
}

/**
 * Carga la lista de ISPs disponibles desde la API.
 */
async function loadAvailableIsps() {
  try {
    const isps = await api.get('/isps');
    if (Array.isArray(isps)) {
      state.setIsps(isps);
    }
  } catch (error) {
    console.warn('[FiberMind] No se pudieron cargar ISPs:', error.message);
  }
}

/**
 * Refresca el estado de salud del sistema y lo sincroniza con el ISP activo.
 */
async function refreshSystemStatus() {
  try {
    const health = await api.get('/health');
    state.updateHealth(health);
    if (state.activeIspId) {
      api.activeIspId = state.activeIspId;
    }
  } catch (error) {
    console.warn('[FiberMind] No se pudo obtener health:', error.message);
  }

  // Actualizar ISP selector en sidebar (si existe)
  updateIspBadge();
}

/**
 * Actualiza el indicador de ISP activo y estado de conexión en sidebar y header.
 */
function updateIspBadge() {
  const nameEl = document.getElementById('isp-name');
  const dotEl = document.getElementById('isp-dot');
  const headerDot = document.getElementById('header-dot');
  const headerStatus = document.getElementById('header-status-text');
  const headerTime = document.getElementById('header-time');

  if (nameEl && state.activeIspName) {
    nameEl.textContent = state.activeIspName;
  }

  const isOnline = state.healthStatus === 'ok';
  const statusText = isOnline ? 'Online' : 'Offline';
  const statusClass = isOnline ? 'online' : 'offline';

  if (dotEl) {
    dotEl.className = `isp-status-dot ${statusClass}`;
  }
  if (headerDot) {
    headerDot.className = `header-dot ${statusClass}`;
  }
  if (headerStatus) {
    headerStatus.textContent = statusText;
  }
  if (headerTime) {
    headerTime.textContent = `🕐 ${new Date().toLocaleTimeString('es-CO')}`;
  }
}

/**
 * Configura los eventos de navegación en la sidebar.
 * Open/Closed: agregar un nuevo item de navegación requiere:
 * 1) Registrar la vista en router.registerView()
 * 2) Agregar el <a> en index.html con data-view
 * El handler no necesita modificarse.
 */
function setupSidebarNavigation() {
  const navLinks = document.querySelectorAll('.nav-item');
  navLinks.forEach(link => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      const viewName = link.getAttribute('data-view');
      if (viewName) {
        navigateToView(viewName);
        updateActiveNav(link);
      }
    });
  });
}

/**
 * Actualiza el estado activo en la barra de navegación.
 * @param {HTMLElement} activeLink
 */
function updateActiveNav(activeLink) {
  document.querySelectorAll('.nav-item').forEach(l => l.classList.remove('active'));
  activeLink.classList.add('active');
}

/**
 * Navega a una vista, importándola bajo demanda y renderizándola.
 * @param {string} viewName - Identificador de la vista destino
 */
async function navigateToView(viewName) {
  const loader = viewModules[viewName];
  if (!loader) {
    mainContent.innerHTML = templates.errorState(`Vista desconocida: ${viewName}`);
    return;
  }

  try {
    // Loading state
    mainContent.innerHTML = templates.loadingOverlay('Cargando vista...');

    // Importación bajo demanda — cada vista es un chunk separado
    const viewModule = await loader();

    // Registrar en el router (Open/Closed: solo esto se necesita por vista nueva)
    router.registerView(viewName, viewModule.render);

    // Render via router
    router.navigate(viewName, api, state, charts, templates);
  } catch (error) {
    mainContent.innerHTML = templates.errorState(
      `Error al cargar "${viewName}": ${error.message}`
    );
    console.error(`[FiberMind] Error navegando a ${viewName}:`, error);
  }
}

// --- Arranque ---
initialize();
