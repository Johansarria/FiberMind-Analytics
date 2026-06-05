/**
 * Estado global de la aplicación (Application State)
 *
 * Responsabilidad única: mantener el estado compartido entre vistas.
 * No maneja UI, no hace peticiones HTTP, no conoce el DOM.
 * Las vistas leen/escriben estado a través de métodos públicos.
 */

export class ApplicationState {
  constructor() {
    /** @type {string} Vista actualmente activa */
    this.currentView = 'panel';
    /** @type {Array<{id: string, name: string}>} Lista de ISPs disponibles */
    this.isps = [];
    /** @type {string|null} ISP activo seleccionado */
    this.activeIspId = null;
    /** @type {string|null} Nombre del ISP activo */
    this.activeIspName = null;
    /** @type {number} Total de eventos OTDR del ISP activo */
    this.totalEvents = 0;
    /** @type {boolean} Indica si la DB está conectada */
    this.dbConnected = false;
    /** @type {object|null} Último snapshot de salud del sistema */
    this.healthData = null;
    /** @type {string|null} Estado de salud: 'ok' | null */
    this.healthStatus = null;
  }

  /**
   * Cambia el ISP activo y propaga el ID al ApiClient.
   * @param {string} ispId - Nuevo ID de ISP
   * @param {string} ispName - Nombre del ISP
   */
  setActiveIsp(ispId, ispName) {
    this.activeIspId = ispId;
    this.activeIspName = ispName;
  }

  /**
   * Actualiza los datos de salud del sistema.
   * @param {object} health - Respuesta del endpoint /health
   */
  updateHealth(health) {
    this.healthData = health;
    this.healthStatus = health.status;
    this.dbConnected = health.db_connected;
    this.totalEvents = health.total_events || 0;
    if (health.isp_name) {
      this.activeIspName = health.isp_name;
    }
    if (health.isp) {
      this.activeIspId = health.isp;
    }
  }

  /**
   * Establece la lista de ISPs disponibles.
   * @param {Array} ispList
   */
  setIsps(ispList) {
    this.isps = ispList;
  }
}
