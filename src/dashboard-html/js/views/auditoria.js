/**
 * Vista: Auditoría de Red
 *
 * Responsabilidad: mostrar el listado completo de eventos OTDR del ISP activo,
 * con indicadores de severidad y resumen general.
 */

import { errorState, emptyState, eventTable, kpiCard } from '../html-templates.js';

/**
 * @param {HTMLElement} container
 * @param {import('../api-client.js').ApiClient} api
 * @param {import('../application-state.js').ApplicationState} state
 * @param {import('../charts.js')} charts
 */
export async function render(container, api, state, charts) {
  container.innerHTML = `
    <div class="fade-in">
      <!-- KPI Grid -->
      <div class="metric-grid cols-6" id="audit-kpis"></div>

      <!-- Tabla de eventos -->
      <div class="table-card">
        <div class="table-header">
          <div class="table-title">Todos los Eventos</div>
        </div>
        <div id="audit-eventos"></div>
      </div>
    </div>
  `;

  const kpisEl = document.getElementById('audit-kpis');
  const eventosEl = document.getElementById('audit-eventos');

  try {
    const data = await api.get('/stats');

    const totalEventos = state.totalEvents;
    const totalHilos = data.total_hilos ?? '—';
    const tiposCount = (data.por_tipo || []).length;
    const criticos = (data.eventos_recientes || []).filter(
      e => (e.atenuacion_db || 0) > 25
    ).length;

    kpisEl.innerHTML = [
      kpiCard('Total Eventos', totalEventos.toLocaleString(), '📡', 'blue'),
      kpiCard('Hilos', totalHilos, '🔗', 'lavender'),
      kpiCard('Tipos Detectados', tiposCount, '📊', 'amber'),
      kpiCard('Críticos', criticos, '🚨', criticos > 0 ? 'red' : 'green'),
    ].join('');

    // Si hay eventos recientes, mostrarlos; si no, intentar /traces
    let eventos = data.eventos_recientes || [];
    if (eventos.length === 0) {
      // Fallback: cargar primeros 20 eventos del cable 1
      const fallback = await api.get('/traces/1/1').catch(
        (/** @type {Error} */ err) => {
          console.warn('[Auditoría] Sin datos de fallback:', err.message);
          return null;
        }
      );
      if (fallback?.eventos) {
        eventos = fallback.eventos;
      }
    }

    if (eventos.length > 0) {
      eventosEl.innerHTML = eventTable(eventos.slice(0, 50), 'critical');
    } else {
      eventosEl.innerHTML = emptyState('📊', 'Sin eventos registrados',
        'No hay datos disponibles para el ISP seleccionado');
    }
  } catch (/** @type {Error} */ error) {
    kpisEl.innerHTML = '';
    eventosEl.innerHTML = errorState(`Error al cargar auditoría: ${error.message}`);
  }
}
