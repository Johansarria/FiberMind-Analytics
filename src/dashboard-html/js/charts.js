/**
 * Configuraciones de gráficos basados en Plotly.js
 *
 * Responsabilidad única: encapsular la configuración de Plotly.js y las funciones
 * de renderizado de gráficos. No conoce el estado de la aplicación ni el DOM
 * más allá del elemento contenedor que recibe como parámetro.
 *
 * Plotly.js se carga desde CDN y se expone globalmente como `window.Plotly`.
 * Paleta actual: light mode lavender/blue (ver CSS :root).
 */

/** Colores de la paleta light para gráficos */
const PALETTE = ['#8B7FCC', '#4A7BD4', '#5DB0A0', '#C9952E', '#D95C5C', '#7A6FBB', '#6D8FDC'];

const TEXT_COLOR = '#5C5278';
const GRID_COLOR = 'rgba(92, 82, 120, 0.1)';

/**
 * Gráfico de donut/torta para distribución de tipos de evento.
 * @param {string} elementId - ID del elemento contenedor
 * @param {Array<{label: string, value: number}>} data - Datos para el gráfico
 */
export async function createPieChart(elementId, data) {
  const element = document.getElementById(elementId);
  if (!element) return;

  const labels = data.map(d => d.label);
  const values = data.map(d => d.value);

  const trace = {
    type: 'pie',
    labels,
    values,
    hole: 0.55,
    marker: {
      colors: PALETTE,
      line: { color: '#FFFFFF', width: 3 },
    },
    textinfo: 'label+percent',
    textfont: { color: TEXT_COLOR, size: 11 },
    hoverinfo: 'label+value+percent',
    hovertemplate: '%{label}<br>%{value} eventos (%{percent})<extra></extra>',
  };

  const layout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: { t: 10, b: 10, l: 0, r: 0 },
    showlegend: false,
  };

  await Plotly.react(element, [trace], layout, { responsive: true, displayModeBar: false });
}

/**
 * Gráfico de barras para métricas comparativas.
 * @param {string} elementId - ID del elemento contenedor
 * @param {Array} data - Array de objetos con label y value
 * @param {string} labelKey - Campo usado como etiqueta en el eje X
 * @param {string} valueKey - Campo usado como valor en el eje Y
 * @param {Function} [labelFormatter] - Función para formatear etiquetas
 */
export async function createBarChart(elementId, data, labelKey, valueKey, labelFormatter) {
  const element = document.getElementById(elementId);
  if (!element) return;

  const labels = data.map(d => (labelFormatter ? labelFormatter(d[labelKey]) : d[labelKey]));
  const values = data.map(d => Number(d[valueKey]) || 0);

  const trace = {
    type: 'bar',
    x: labels,
    y: values,
    marker: {
      color: values.map(v => v > 0 ? '#8B7FCC' : '#E0D8EC'),
      line: { color: '#7A6FBB', width: 1 },
    },
    hovertemplate: '%{x}: %{y}<extra></extra>',
  };

  const layout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: { t: 10, b: 40, l: 40, r: 10 },
    font: { color: TEXT_COLOR, size: 11 },
    xaxis: {
      showgrid: false,
      tickfont: { color: TEXT_COLOR, size: 10 },
      tickangle: -30,
    },
    yaxis: {
      showgrid: true,
      gridcolor: GRID_COLOR,
      tickfont: { color: TEXT_COLOR, size: 10 },
    },
    showlegend: false,
  };

  await Plotly.react(element, [trace], layout, { responsive: true, displayModeBar: false });
}

/**
 * Gráfico de línea para traza OTDR (distancia vs atenuación).
 * @param {string} elementId - ID del elemento contenedor
 * @param {Array} eventos - Eventos OTDR con propiedades distancia_km y atenuacion_db
 */
export async function createTraceChart(elementId, eventos) {
  const element = document.getElementById(elementId);
  if (!element || !eventos || eventos.length === 0) return;

  const distances = eventos.map(e => e.distancia_km || 0);
  const attenuations = eventos.map(e => e.atenuacion_db || 0);
  const types = eventos.map(e => e.tipo_evento || '—');

  const trace = {
    type: 'scatter',
    mode: 'lines+markers',
    x: distances,
    y: attenuations,
    text: types,
    hovertemplate: '<b>%{text}</b><br>Distancia: %{x:.2f} km<br>Atenuación: %{y:.2f} dB<extra></extra>',
    line: { color: '#8B7FCC', width: 2, shape: 'spline' },
    marker: {
      size: 8,
      color: '#8B7FCC',
      line: { color: '#FFFFFF', width: 2 },
    },
  };

  const layout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: { t: 10, b: 50, l: 50, r: 20 },
    font: { color: TEXT_COLOR, size: 11 },
    xaxis: {
      title: { text: 'Distancia (km)', font: { color: TEXT_COLOR, size: 11 } },
      showgrid: true,
      gridcolor: GRID_COLOR,
      tickfont: { color: TEXT_COLOR, size: 10 },
    },
    yaxis: {
      title: { text: 'Atenuación (dB)', font: { color: TEXT_COLOR, size: 11 } },
      showgrid: true,
      gridcolor: GRID_COLOR,
      tickfont: { color: TEXT_COLOR, size: 10 },
    },
    showlegend: false,
  };

  await Plotly.react(element, [trace], layout, { responsive: true, displayModeBar: false });
}
