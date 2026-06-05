/**
 * Vista: Infraestructura
 *
 * Responsabilidad: mostrar el estado de salud del sistema, conectividad
 * con bases de datos y metadatos del stack tecnológico.
 */

import { errorState, badge } from '../html-templates.js';

/**
 * @param {HTMLElement} container
 * @param {import('../api-client.js').ApiClient} api
 * @param {import('../application-state.js').ApplicationState} state
 * @param {import('../charts.js')} charts
 */
export async function render(container, api, state, charts) {
  container.innerHTML = `
    <div class="fade-in">
      <!-- Salud del sistema -->
      <div class="table-card">
        <div class="table-header">
          <div class="table-title">Estado del Sistema</div>
        </div>
        <div id="infra-health"></div>
      </div>

      <!-- Stack tecnológico -->
      <div class="table-card" style="margin-top:16px;">
        <div class="table-header">
          <div class="table-title">Stack Tecnológico</div>
        </div>
        <div id="infra-stack"></div>
      </div>
    </div>
  `;

  const healthEl = document.getElementById('infra-health');
  const stackEl = document.getElementById('infra-stack');

  try {
    const health = await api.get('/health');

    healthEl.innerHTML = `
      <div class="status-grid">
        <div class="status-card">
          <span class="status-card-indicator ${health.status === 'ok' ? 'green' : 'red'}"></span>
          <div class="status-card-info">
            <div class="status-card-name">API</div>
            <div class="status-card-detail">${health.status === 'ok' ? 'Online' : 'Offline'}</div>
          </div>
          ${health.status === 'ok' ? badge('ok', 'Online') : badge('critical', 'Offline')}
        </div>
        <div class="status-card">
          <span class="status-card-indicator ${health.db_connected ? 'green' : 'red'}"></span>
          <div class="status-card-info">
            <div class="status-card-name">Base de Datos</div>
            <div class="status-card-detail">${health.db_connected ? 'Conectada' : 'Desconectada'}</div>
          </div>
          ${health.db_connected ? badge('ok', 'Online') : badge('critical', 'Offline')}
        </div>
        <div class="status-card">
          <span class="status-card-indicator ${state.activeIspName ? 'green' : 'amber'}"></span>
          <div class="status-card-info">
            <div class="status-card-name">ISP Activo</div>
            <div class="status-card-detail">${state.activeIspName || '—'}</div>
          </div>
        </div>
        <div class="status-card">
          <span class="status-card-indicator green"></span>
          <div class="status-card-info">
            <div class="status-card-name">DB Time</div>
            <div class="status-card-detail">${health.db_time_ms ? `${health.db_time_ms.toFixed(1)} ms` : '—'}</div>
          </div>
        </div>
        <div class="status-card">
          <span class="status-card-indicator green"></span>
          <div class="status-card-info">
            <div class="status-card-name">Eventos Totales</div>
            <div class="status-card-detail">${(health.total_events || 0).toLocaleString()}</div>
          </div>
        </div>
        <div class="status-card">
          <span class="status-card-indicator green"></span>
          <div class="status-card-info">
            <div class="status-card-name">Versión API</div>
            <div class="status-card-detail">${health.version || 'v1'}</div>
          </div>
        </div>
      </div>
    `;

    stackEl.innerHTML = `
      <div class="status-grid">
        <div class="status-card">
          <span class="status-card-indicator green"></span>
          <div class="status-card-info">
            <div class="status-card-name">Backend</div>
            <div class="status-card-detail">Python 3.12+ · FastAPI</div>
          </div>
        </div>
        <div class="status-card">
          <span class="status-card-indicator green"></span>
          <div class="status-card-info">
            <div class="status-card-name">Frontend</div>
            <div class="status-card-detail">HTML5 · CSS3 · ES Modules · Plotly.js</div>
          </div>
        </div>
        <div class="status-card">
          <span class="status-card-indicator green"></span>
          <div class="status-card-info">
            <div class="status-card-name">Base de Datos</div>
            <div class="status-card-detail">PostgreSQL 15+</div>
          </div>
        </div>
        <div class="status-card">
          <span class="status-card-indicator green"></span>
          <div class="status-card-info">
            <div class="status-card-name">Infraestructura</div>
            <div class="status-card-detail">Docker · Contenedor Linux</div>
          </div>
        </div>
        <div class="status-card">
          <span class="status-card-indicator green"></span>
          <div class="status-card-info">
            <div class="status-card-name">OTDR Engine</div>
            <div class="status-card-detail">PyOTDR</div>
          </div>
        </div>
      </div>
    `;
  } catch (/** @type {Error} */ error) {
    healthEl.innerHTML = errorState(`Error al conectar con API: ${error.message}`);
    stackEl.innerHTML = errorState('No se pudo cargar información del stack');
  }
}
