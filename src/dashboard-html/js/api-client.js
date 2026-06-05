/**
 * API Client para FiberMind Analytics
 *
 * Responsabilidad única: gestionar comunicación HTTP con la API REST.
 * Inyecta el header X-ISP-ID desde el estado de la aplicación.
 * No conoce el DOM, ni el router, ni las vistas.
 */

export class ApiClient {
  /**
   * @param {string} baseUrl - URL base del API (ej: '' para mismo origen)
   */
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
    /** @type {string|null} identificador del ISP activo */
    this.activeIspId = null;
  }

  /**
   * Construye headers estándar para cada petición.
   * @returns {Record<string, string>}
   */
  _buildHeaders() {
    const headers = { 'Accept': 'application/json' };
    if (this.activeIspId) {
      headers['X-ISP-ID'] = this.activeIspId;
    }
    return headers;
  }

  /**
   * Petición HTTP genérica — núcleo compartido por get/post/getBlob.
   * @param {string} path - Ruta del endpoint (ej: /stats)
   * @param {object} [options] - Opciones fetch adicionales
   * @returns {Promise<any>}
   */
  async _request(path, options = {}) {
    const url = `${this.baseUrl}${path}`;
    const headers = { ...this._buildHeaders(), ...options.headers };
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      const errorBody = await response.text().catch(
      () => ''  // Si no se puede leer el body del error, se omite
    );
      throw new ApiError(
        `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorBody
      );
    }
    return response;
  }

  /**
   * Petición GET que retorna JSON.
   * @param {string} path - Ruta del endpoint
   * @returns {Promise<any>}
   */
  async get(path) {
    const response = await this._request(path);
    return response.json();
  }

  /**
   * Petición POST que envía y recibe JSON.
   * @param {string} path - Ruta del endpoint
   * @param {object} body - Cuerpo de la petición (se serializa a JSON)
   * @returns {Promise<any>}
   */
  async post(path, body) {
    const response = await this._request(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return response.json();
  }

  /**
   * Obtiene un blob (ej: imagen PNG de traza) desde el API.
   * @param {string} path - Ruta del endpoint
   * @returns {Promise<Blob>}
   */
  async getBlob(path) {
    const response = await this._request(path);
    return response.blob();
  }
}

/**
 * Error tipado para fallos de API.
 * Permite a los handlers distinguir errores de red de errores HTTP.
 */
export class ApiError extends Error {
  /**
   * @param {string} message - Mensaje descriptivo
   * @param {number} statusCode - Código HTTP
   * @param {string} body - Cuerpo de la respuesta de error
   */
  constructor(message, statusCode, body = '') {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.body = body;
  }
}
