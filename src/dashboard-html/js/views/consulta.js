/**
 * Vista: Consulta de Trazas (Consulta)
 *
 * Responsabilidad: permitir al usuario consultar eventos OTDR por cable/hilo
 * específico y visualizar la traza gráfica.
 */

import { loadingOverlay, errorState, emptyState, eventTable, escHtml } from '../html-templates.js';

/** @type {string|null} Cable activo en el formulario */
let currentCable = null;
/** @type {string|null} Hilo activo en el formulario */
let currentHilo = null;

/**
 * @param {HTMLElement} container
 * @param {import('../api-client.js').ApiClient} api
 * @param {import('../application-state.js').ApplicationState} state
 * @param {import('../charts.js')} charts
 */
export async function render(container, api, state, charts) {
  container.innerHTML = `
    <div class="fade-in">
      <!-- Formulario de consulta -->
      <div class="search-form">
        <div class="section-title">Consultar Eventos por Cable/Hilo</div>
        <div class="form-row">
          <div class="form-group">
            <label for="consult-cable">Cable</label>
            <input type="number" id="consult-cable"
                   placeholder="ej: 8" value="${escHtml(currentCable || '')}" min="1">
          </div>
          <div class="form-group">
            <label for="consult-hilo">Hilo</label>
            <input type="number" id="consult-hilo"
                   placeholder="ej: 285" value="${escHtml(currentHilo || '')}" min="1">
          </div>
          <div class="form-group" style="align-self:flex-end;">
            <button id="consult-btn" class="btn btn-primary">Consultar</button>
          </div>
        </div>
      </div>

      <!-- Resultados: gráfico + tabla -->
      <div class="chart-grid cols-2" id="consult-results">
        <div class="chart-card">
          <div class="chart-card-header">
            <div class="chart-card-title">Traza OTDR</div>
          </div>
          <div class="chart-container tall" id="trace-chart"></div>
        </div>
        <div class="chart-card">
          <div class="chart-card-header">
            <div class="chart-card-title">Eventos en Línea</div>
          </div>
          <div id="trace-eventos"></div>
        </div>
      </div>
    </div>
  `;

  const cableInput = document.getElementById('consult-cable');
  const hiloInput = document.getElementById('consult-hilo');
  const consultButton = document.getElementById('consult-btn');

  consultButton.addEventListener('click', async () => {
    const cable = cableInput.value.trim();
    const hilo = hiloInput.value.trim();
    if (!cable || !hilo) {
      document.getElementById('trace-eventos').innerHTML =
        errorState('Debes ingresar número de cable e hilo');
      return;
    }
    currentCable = cable;
    currentHilo = hilo;
    await loadTrace(api, charts, cable, hilo);
  });

  // Auto-carga si hay valores previos
  if (currentCable && currentHilo) {
    document.getElementById('trace-eventos').innerHTML = loadingOverlay();
    await loadTrace(api, charts, currentCable, currentHilo);
  } else {
    document.getElementById('trace-chart').innerHTML =
      emptyState('🔍', 'Selecciona cable e hilo', 'Ingresa los valores y presiona Consultar');
    document.getElementById('trace-eventos').innerHTML = '';
  }
}

/**
 * Carga datos de traza y renderiza gráfico + tabla.
 * @param {import('../api-client.js').ApiClient} api
 * @param {import('../charts.js')} charts
 * @param {string} cable
 * @param {string} hilo
 */
async function loadTrace(api, charts, cable, hilo) {
  const eventosEl = document.getElementById('trace-eventos');
  const chartEl = document.getElementById('trace-chart');

  try {
    const data = await api.get(`/traces/${cable}/${hilo}`);
    const eventos = data.eventos || data || [];
    if (!Array.isArray(eventos) || eventos.length === 0) {
      chartEl.innerHTML = emptyState('📈', 'Sin datos de traza',
        `No hay eventos registrados para Cable ${cable} / Hilo ${hilo}`);
      eventosEl.innerHTML = '';
      return;
    }

    eventosEl.innerHTML = eventTable(eventos, 'info');
    await charts.createTraceChart('trace-chart', eventos);
  } catch (/** @type {Error} */ error) {
    chartEl.innerHTML = errorState(`Error al cargar traza: ${error.message}`);
    eventosEl.innerHTML = '';
  }
}
