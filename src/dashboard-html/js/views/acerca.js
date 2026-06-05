/**
 * Vista: Acerca de / Configuración
 *
 * Responsabilidad: mostrar información del producto, selector de ISP,
 * y acceso a documentación técnica.
 */

/**
 * @param {HTMLElement} container
 * @param {import('../api-client.js').ApiClient} api
 * @param {import('../application-state.js').ApplicationState} state
 * @param {import('../charts.js')} charts
 * @param {import('../html-templates.js')} templates
 */
export async function render(container, api, state, charts, templates) {
  const ispOptions = state.isps.map(isp =>
    `<option value="${templates.escHtml(String(isp.id))}" ${isp.id === state.activeIspId ? 'selected' : ''}>
      ${templates.escHtml(isp.name)}
    </option>`
  ).join('');

  container.innerHTML = `
    <div class="fade-in">
      <!-- Configuración ISP -->
      <div class="search-form">
        <div class="section-title">Configuración</div>
        <div class="form-group" style="max-width:400px;">
          <label for="isp-selector">ISP Activo</label>
          <select id="isp-selector">
            ${ispOptions}
          </select>
        </div>
        <button id="change-isp-btn" class="btn btn-primary" style="margin-top:12px;">
          Cambiar ISP
        </button>
        <div id="isp-result" style="margin-top:12px;"></div>
      </div>

      <!-- Acerca de -->
      <div class="table-card" style="margin-top:16px;">
        <div class="table-header">
          <div class="table-title">Acerca de FiberMind Analytics</div>
        </div>
        <p style="color:var(--text-secondary); line-height:1.6; padding: 0 4px;">
          FiberMind Analytics es una plataforma de monitoreo de redes de fibra óptica
          que utiliza tecnología OTDR para detectar, analizar y visualizar eventos
          en la infraestructura de red de los ISP.
        </p>
        <div class="info-list" style="margin-top:12px;">
          <div class="info-item">
            <span class="info-item-label">Versión</span>
            <span class="info-item-value">1.0.0</span>
          </div>
          <div class="info-item">
            <span class="info-item-label">Stack</span>
            <span class="info-item-value">FastAPI + PostgreSQL + HTML/CSS/JS SPA</span>
          </div>
          <div class="info-item">
            <span class="info-item-label">Motor OTDR</span>
            <span class="info-item-value">PyOTDR</span>
          </div>
        </div>
      </div>
    </div>
  `;

  const ispSelector = document.getElementById('isp-selector');
  const changeButton = document.getElementById('change-isp-btn');
  const resultEl = document.getElementById('isp-result');

  changeButton.addEventListener('click', async () => {
    const selectedId = ispSelector.value;
    const selectedName = ispSelector.options[ispSelector.selectedIndex]?.text || selectedId;

    state.setActiveIsp(selectedId, selectedName);
    api.activeIspId = selectedId;

    resultEl.innerHTML = templates.successState(
      `ISP cambiado a: ${templates.escHtml(selectedName)}`
    );
  });
}
