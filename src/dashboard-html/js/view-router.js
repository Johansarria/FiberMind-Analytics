/**
 * Router de vistas (View Router)
 *
 * Responsabilidad única: navegar entre vistas de la SPA.
 * Abierto a extensión (registrar nuevas vistas vía registerView) sin modificar
 * el código del router. Cada vista es una función que recibe el contenedor.
 */

export class ViewRouter {
  /**
   * @param {HTMLElement} container - Elemento DOM donde se renderizan las vistas
   */
  constructor(container) {
    /** @type {HTMLElement} Contenedor raíz de vistas */
    this.container = container;
    /**
     * Registro de vistas: { nombre: renderFn(container, api, state, charts, templates) }
     * @type {Record<string, Function>}
     */
    this.views = {};
  }

  /**
   * Registra una vista en el router.
   * Open/Closed: agregar vistas = llamar a registerView, no modificar el router.
   *
   * @param {string} name - Identificador único de la vista
   * @param {Function} renderFn - Función que renderiza la vista:
   *   renderFn(container, api, state, charts, templates)
   */
  registerView(name, renderFn) {
    if (this.views[name]) {
      console.warn(`[ViewRouter] Sobrescribiendo vista existente: ${name}`);
    }
    this.views[name] = renderFn;
  }

  /**
   * Navega a una vista registrada.
   * @param {string} name - Identificador de la vista destino
   * @param {object} api - Instancia de ApiClient
   * @param {object} state - Instancia de ApplicationState
   * @param {object} charts - Módulo de gráficos
   * @param {object} templates - Módulo de templates HTML
   */
  navigate(name, api, state, charts, templates) {
    const renderFn = this.views[name];
    if (!renderFn) {
      console.error(`[ViewRouter] Vista no encontrada: ${name}`);
      this.container.innerHTML =
        `<div class="error-state">Vista no encontrada: ${this._escapeHtml(name)}</div>`;
      return;
    }

    state.currentView = name;
    renderFn(this.container, api, state, charts, templates);
  }

  /**
   * Escapa HTML para prevenir XSS en mensajes de error.
   * @param {string} text
   * @returns {string}
   */
  _escapeHtml(text) {
    const element = document.createElement('div');
    element.appendChild(document.createTextNode(text));
    return element.innerHTML;
  }
}
