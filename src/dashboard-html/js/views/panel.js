/**
 * Vista: Dashboard Principal (Panel)
 *
 * Responsabilidad: renderizar el panel principal con KPI cards, gráficos
 * y tabla de últimos eventos del ISP activo.
 *
 * API /stats devuelve:
 *   { total_eventos, por_tipo: [{tipo_evento, count}],
 *     hilos_por_cable: [{id_cable, hilos}], eventos_criticos }
 */

import { errorState, kpiCard, eventTable, emptyState, loadingOverlay } from '../html-templates.js';

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
      <div class="metric-grid cols-5" id="panel-kpis"></div>

      <!-- Charts Row -->
      <div class="chart-grid cols-2">
        <div class="chart-card">
          <div class="chart-card-header">
            <div class="chart-card-title">Tipos de Evento</div>
          </div>
          <div class="chart-container" id="pie-tipos"></div>
        </div>
        <div class="chart-card">
          <div class="chart-card-header">
            <div class="chart-card-title">Hilos por Cable (Top 6)</div>
          </div>
          <div class="chart-container" id="bar-hilos"></div>
        </div>
      </div>

      <!-- Últimos eventos -->
      <div class="table-card">
        <div class="table-header">
          <div class="table-title">Últimos Eventos Reportados</div>
        </div>
        <div id="panel-eventos"></div>
      </div>
    </div>
  `;

  const kpisEl = document.getElementById('panel-kpis');
  const eventosEl = document.getElementById('panel-eventos');
  const pieEl = document.getElementById('pie-tipos');
  const barEl = document.getElementById('bar-hilos');

  try {
    const stats = await api.get('/stats');
    const totalEventos = Number(stats.total_eventos) || 0;

    // KPI cards
    kpisEl.innerHTML = [
      kpiCard('Eventos OTDR', totalEventos.toLocaleString(), '📡', 'blue'),
      kpiCard('Críticos', String(Number(stats.eventos_criticos) || 0), '🚨', 'red'),
      kpiCard('Tipos Detectados', String((stats.por_tipo || []).length), '📊', 'amber'),
      kpiCard('Cables', String((stats.hilos_por_cable || []).length), '📦', 'teal'),
      kpiCard('Hilos Monitoreados', String(
        (stats.hilos_por_cable || []).reduce((s, c) => s + Number(c.hilos || 0), 0)
      ), '🔗', 'lavender'),
    ].join('');

    // Gráfico de tipos — API usa .count
    const tiposData = (stats.por_tipo || []).map(t => ({
      label: t.tipo_evento || 'Desconocido',
      value: Number(t.count || 0),
    }));

    if (tiposData.length > 0) {
      await charts.createPieChart('pie-tipos', tiposData);
    } else {
      pieEl.innerHTML = emptyState('📊', 'Sin datos', 'No hay tipos de evento registrados');
    }

    // Gráfico de hilos por cable — API usa .hilos
    const hilosData = (stats.hilos_por_cable || []).slice(0, 6).map(h => ({
      label: `Cable ${h.id_cable}`,
      value: Number(h.hilos || 0),
    }));

    if (hilosData.length > 0) {
      await charts.createBarChart('bar-hilos', hilosData, 'label', 'value');
    } else {
      barEl.innerHTML = emptyState('📊', 'Sin datos', 'No hay cables monitoreados');
    }

    // Últimos eventos desde /health o consulta directa
    try {
      const healthData = await api.get('/health');
      const evData = await api.get('/traces/1/1');
      const eventos = (evData.eventos || evData || []).slice(0, 10);
      if (Array.isArray(eventos) && eventos.length > 0) {
        eventosEl.innerHTML = eventTable(eventos, 'critical');
      } else {
        eventosEl.innerHTML = emptyState('📡', 'Sin datos recientes',
          'No hay eventos registrados para este ISP');
      }
    } catch (/** @type {Error} */ _err) {
      eventosEl.innerHTML = emptyState('📡', 'Sin datos recientes',
        'Prueba seleccionando un cable/hilo en la vista Consulta');
    }
  } catch (/** @type {Error} */ error) {
    kpisEl.innerHTML = '';
    eventosEl.innerHTML = errorState(`Error al cargar dashboard: ${error.message}`);
  }
}
