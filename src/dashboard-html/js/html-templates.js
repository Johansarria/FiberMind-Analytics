/**
 * Templates HTML reutilizables
 *
 * Responsabilidad única: generar fragmentos HTML consistentes para toda la SPA.
 * DRY: cada patrón visual (loading, error, empty, badges, event rows) vive aquí
 * y se importa donde se necesite, no se duplica inline.
 */

/**
 * Indicador de carga con spinner.
 * @returns {string}
 */
export function loadingOverlay(text = 'Cargando...') {
  return `<div class="loading-overlay">
    <div class="loading-spinner"></div>
    <span>${escHtml(text)}</span>
  </div>`;
}

/**
 * Estado de error con mensaje.
 * @param {string} message - Descripción del error
 * @returns {string}
 */
export function errorState(message) {
  return `<div class="empty-state">⚠️ <span>${escHtml(message)}</span></div>`;
}

/**
 * Estado vacío (sin datos) contextual.
 * @param {string} icon - Emoji o icono
 * @param {string} title - Título del estado vacío
 * @param {string} [description] - Descripción opcional
 * @returns {string}
 */
export function emptyState(icon, title, description = '') {
  return `<div class="empty-state">
    <div class="empty-state-icon">${escHtml(icon)}</div>
    <div class="empty-state-text"><strong>${escHtml(title)}</strong></div>
    ${description ? `<p style="color:var(--text-dim);font-size:0.82rem;">${escHtml(description)}</p>` : ''}
  </div>`;
}

/**
 * Badge de severidad con color.
 * @param {'badge-red'|'badge-amber'|'badge-green'|'badge-blue'|'badge-accent'|'badge-purple'} colorClass
 * @param {string} text
 * @returns {string}
 */
export function badge(colorClass, text) {
  return `<span class="badge ${colorClass}">${escHtml(text)}</span>`;
}

/**
 * Estado de éxito con mensaje.
 * @param {string} text
 * @returns {string}
 */
export function successState(text) {
  return `<div class="empty-state">✅ <span>${escHtml(text)}</span></div>`;
}

/**
 * Fila de tabla para un evento OTDR.
 * @param {object} evento - { id_cable, id_hilo, distancia_km, tipo_evento, atenuacion_db }
 * @param {string} severityClass - 'critical' | 'major' | 'minor' | 'info' | 'ok'
 * @returns {string}
 */
export function eventTableRow(evento, severityClass = 'info') {
  const distance = evento.distancia_km
    ? evento.distancia_km.toFixed(2) + ' km'
    : '—';
  const attenuation = evento.atenuacion_db
    ? evento.atenuacion_db.toFixed(2) + ' dB'
    : '—';

  const badgeTextMap = { critical: 'Crítico', major: 'Mayor', minor: 'Menor', info: 'Info', ok: 'OK' };
  const badgeText = badgeTextMap[severityClass] || 'Info';

  return `<tr>
    <td>${escHtml(String(evento.id_cable || '—'))}</td>
    <td>${escHtml(String(evento.id_hilo || '—'))}</td>
    <td>${distance}</td>
    <td>${escHtml(evento.tipo_evento || '—')}</td>
    <td>${attenuation}</td>
    <td>${badge(severityClass, badgeText)}</td>
  </tr>`;
}

/**
 * Tabla completa de eventos a partir de un array.
 * DRY: evita que cada vista duplique el markup de la tabla.
 * @param {Array} eventos - Array de objetos event
 * @param {'critical'|'major'|'minor'|'info'|'ok'} severityClass
 * @returns {string}
 */
export function eventTable(eventos, severityClass = 'info') {
  if (!eventos || eventos.length === 0) {
    return emptyState('📡', 'Sin eventos', 'No hay registros para mostrar');
  }

  return `<table class="data-table">
    <thead>
      <tr>
        <th>Cable</th>
        <th>Hilo</th>
        <th>Distancia</th>
        <th>Tipo</th>
        <th>Atenuación</th>
        <th>Severidad</th>
      </tr>
    </thead>
    <tbody>
      ${eventos.map(e => eventTableRow(e, severityClass)).join('')}
    </tbody>
  </table>`;
}

/**
 * Tarjeta KPI con título, valor, icono y color de acento.
 * @param {string} title - Etiqueta del KPI
 * @param {string|number} value - Valor principal
 * @param {string} icon - Emoji o icono
 * @param {string} iconColorClass - Clase CSS: 'blue' | 'green' | 'red' | 'amber' | 'lavender' | 'teal'
 * @param {object} [opts] - Opciones adicionales
 * @param {string} [opts.trend] - 'up' | 'down' | 'flat'
 * @param {string} [opts.trendText] - Texto de tendencia
 * @returns {string}
 */
export function kpiCard(title, value, icon, iconColorClass = 'blue', opts = {}) {
  const trend = opts.trend || '';
  const trendText = opts.trendText || '';
  const trendHtml = trend
    ? `<span class="metric-card-trend ${trend}">${trend === 'up' ? '↑' : '↓'} ${escHtml(trendText)}</span>`
    : '';

  return `<div class="metric-card">
    <div class="metric-card-header">
      <div class="metric-card-icon ${iconColorClass}">${icon}</div>
      ${trendHtml}
    </div>
    <div class="metric-card-label">${escHtml(title)}</div>
    <div class="metric-card-value">${escHtml(String(value))}</div>
  </div>`;
}

/**
 * Escapa HTML para prevenir XSS.
 * @param {*} text
 * @returns {string}
 */
export function escHtml(text) {
  if (typeof text !== 'string') {
    return String(text);
  }
  const element = document.createElement('div');
  element.appendChild(document.createTextNode(text));
  return element.innerHTML;
}
