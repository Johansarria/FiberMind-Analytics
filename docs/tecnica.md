# FiberMind Analytics — Documentación Técnica

> **Arquitectura, despliegue y API del sistema de inteligencia de red FTTH**
> Versión: 0.3.0 · Junio 2026

---

## Índice

1. [Arquitectura del Sistema](#1-arquitectura-del-sistema)
2. [Estructura del Proyecto](#2-estructura-del-proyecto)
3. [Dashboard SPA](#3-dashboard-spa)
4. [API REST](#4-api-rest)
5. [Despliegue](#5-despliegue)
6. [Configuración Multi-ISP](#6-configuración-multi-isp)
7. [Modelo de Datos](#7-modelo-de-datos)
8. [Autenticación y Seguridad](#8-autenticación-y-seguridad)

---

## 1. Arquitectura del Sistema

```
┌────────────────────────────────────────────────────────────────┐
│                     CLIENTE (Navegador)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Dashboard SPA (HTML/CSS/JS puro)                │   │
│  │  view-router.js  →  charts.js  →  api-client.js  → fetch │   │
│  │  app.js (bootstrap)   views/*.js (carga diferida)         │   │
│  └─────────────────────────┬────────────────────────────────┘   │
│                            │ HTTP (fetch)                        │
└────────────────────────────┼────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                    SERVIDOR (FastAPI)                            │
│  ┌─────────────────────────┴──────────────────────────────────┐  │
│  │  src/api/main.py                                           │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │  │
│  │  │ /stats   │ │ /traces  │ │ /audit   │ │ /health      │  │  │
│  │  │ /isps    │ │ /query   │ │ /infra.. │ │ / → static   │  │  │
│  │  └─────┬────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘  │  │
│  │        └────────────┼────────────┼──────────────┘           │  │
│  │                     ▼            ▼                           │  │
│  │  ┌────────────────────────────────────────────────────┐     │  │
│  │  │        Core de Dominio (src/core/)                   │     │  │
│  │  │  services/network_service.py   → lógica FTTH         │     │  │
│  │  │  services/ai_service.py        → Ollama integración  │     │  │
│  │  │  domain/models.py             → OTDREvent, Cable     │     │  │
│  │  └───────────────────┬─────────────────────────────────┘     │  │
│  │                      ▼                                       │  │
│  │  ┌────────────────────────────────────────────────────┐     │  │
│  │  │       Infraestructura (src/infrastructure/)          │     │  │
│  │  │  database/repository.py    → SQLite / PostgreSQL      │     │  │
│  │  │  ai/ollama_client.py       → Modelo IA local          │     │  │
│  │  │  telegram/bot.py           → Bot de Telegram          │     │  │
│  │  │  mcp/server.py             → Protocolo MCP            │     │  │
│  │  └───────────────────┬─────────────────────────────────┘     │  │
│  └──────────────────────┼──────────────────────────────────────┘  │
│                         ▼                                         │
└─────────────────────────┼─────────────────────────────────────────┘
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
       ┌──────────────┐       ┌──────────────┐
       │  PostgreSQL   │       │    Ollama    │
       │  / SQLite     │       │  (localhost  │
       │               │       │   :11435)    │
       └──────────────┘       └──────────────┘
```

### Capas

| Capa | Directorio | Responsabilidad |
|:--|:--|:--|
| **Presentación** | `src/dashboard-html/` | Dashboard SPA (navegador) |
| **API** | `src/api/` | Endpoints REST (FastAPI) |
| **Aplicación** | `src/core/services/` | Lógica de negocio (NetworkService, AIService) |
| **Dominio** | `src/core/domain/` | Modelos de datos (OTDREvent, Cable, Hilo) |
| **Infraestructura** | `src/infrastructure/` | DB, IA, Telegram, MCP |

---

## 2. Estructura del Proyecto

```
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI app, rutas, CORS, montaje estático
│   │   └── __init__.py
│   ├── core/
│   │   ├── domain/
│   │   │   └── models.py        # OTDREvent, Cable, Hilo, Splitter
│   │   ├── services/
│   │   │   ├── network_service.py  # Lógica FTTH: consultas, stats, auditoría
│   │   │   └── ai_service.py       # Text-to-SQL vía Ollama
│   │   └── __init__.py
│   ├── infrastructure/
│   │   ├── database/
│   │   │   └── repository.py    # CRUD SQLite/PostgreSQL (DatabaseRepository)
│   │   ├── ai/
│   │   │   └── ollama_client.py # Cliente HTTP para Ollama API
│   │   ├── telegram/
│   │   │   └── bot.py            # Bot de Telegram (comandos /hilo, /auditar)
│   │   └── mcp/
│   │       └── server.py         # Servidor MCP (Model Context Protocol)
│   ├── config/
│   │   ├── prompts.py            # Prompts para consultas IA
│   │   └── isp_config.py         # Configuración multi-ISP
│   ├── utils/
│   │   └── plotting.py           # Generación de gráficos (matplotlib)
│   ├── dashboard-html/           # Dashboard SPA completo
│   │   ├── index.html            # Punto de entrada
│   │   ├── css/
│   │   │   └── style.css         # 850 líneas — diseño modo claro
│   │   ├── js/
│   │   │   ├── app.js            # Bootstrap + lazy loading de vistas
│   │   │   ├── api-client.js     # Cliente HTTP con X-ISP-ID
│   │   │   ├── application-state.js # Estado global de la app
│   │   │   ├── charts.js         # Gráficos Plotly.js (pie, bar, trace)
│   │   │   ├── html-templates.js # Templates reutilizables (KPI, tabla, badges)
│   │   │   ├── view-router.js    # Router SPA inyectado con dependencias
│   │   │   └── views/
│   │   │       ├── panel.js         # Dashboard principal con KPIs + gráficos
│   │   │       ├── consulta.js      # Consulta de trazas por cable/hilo
│   │   │       ├── auditoria.js     # Auditoría de empalmes críticos
│   │   │       ├── infraestructura.js # Salud del sistema + stack info
│   │   │       └── acerca.js        # Info del producto + selector ISP
│   ├── cli.py                     # CLI para scripts y diagnóstico
│   └── config/
├── scripts/                     # ETL, importación, setup de BD
├── tests/                       # Pruebas unitarias (pytest)
├── docs/                        # Documentación
├── pyproject.toml               # Configuración del paquete
├── Dockerfile                   # Imagen multi-etapa
├── docker-compose.yml           # Stack con PostgreSQL + Ollama
├── AGENTES.md                   # Guía de desarrollo para asistentes IA
└── ftth_glossary.md             # Glosario técnico FTTH
```

---

## 3. Dashboard SPA

### 3.1 Principios de diseño

- **SPA pura**: Sin frameworks (React, Vue, Angular). JavaScript nativo con módulos ES.
- **Carga diferida**: Cada vista se importa bajo demanda (`import('./views/panel.js')`).
- **Inyección de dependencias**: El router pasa `api`, `state`, `charts`, `templates` a cada vista.
- **DRY estricto**: Los templates HTML reutilizables (`kpiCard`, `eventTable`, `badge`) viven en `html-templates.js`.
- **SRP**: Cada archivo JS tiene una responsabilidad única y documentada.

### 3.2 Flujo de carga

```
index.html
  └─ <script type="module" src="/app/js/app.js">
       ├── Carga ISPs desde API (/isps)
       ├── Health check (/health)
       ├── Inicializa sidebar navigation
       └── Navega a 'panel'
            ├── Importa views/panel.js (lazy)
            ├── Router registra y navega
            ├── panel.js renderiza estructura HTML
            ├── API /stats → KPIs + gráficos + tabla
            └── Plotly.js renderiza donut y barras
```

### 3.3 Clases CSS principales

| Clase | Uso |
|:--|:--|
| `.app-layout` | Contenedor grid: sidebar + main |
| `.sidebar` | Panel lateral lavanda (~205px) |
| `.nav-item` | Items de navegación con icono |
| `.metric-grid` | Grid de tarjetas KPI (cols-5) |
| `.metric-card` | Card individual con icono + valor + label |
| `.chart-grid` | Grid de gráficos (cols-2) |
| `.chart-card` | Contenedor de gráfico Plotly.js |
| `.table-card` | Contenedor de tabla de eventos |
| `.status-grid` | Grid de estado (2 columnas) |
| `.badge` | Badge de severidad (red, amber, green, blue) |
| `.btn` | Botón genérico |
| `.btn-primary` | Botón primario azul |

### 3.4 Sistema de colores (variables CSS)

```css
:root {
  --bg: #FDF8FE;           /* Fondo principal */
  --sidebar: #DCD4F2;       /* Sidebar lavanda */
  --sidebar-hover: #C8BCE8; /* Sidebar hover */
  --card-bg: #F4F0FA;       /* Fondo de tarjetas */
  --accent: #8B7FCC;        /* Acento lavanda */
  --accent-blue: #4A7BD4;   /* Acento azul */
  --text: #3A3355;          /* Texto principal */
  --text-dim: #8A7FA8;      /* Texto secundario */
  --border: #D8D0EB;        /* Bordes */
  --red: #D95C5C;           /* Severidad crítica */
  --green: #4CAF84;         /* OK */
  --amber: #C9952E;         /* Severidad media */
}
```

---

## 4. API REST

### 4.1 Endpoints

```
GET  /health                    → { status, version, db_connected, ... }
GET  /isps                      → [{ id: "isp1", name: "ISP 1" }, ...]
GET  /stats                     → { total_eventos, por_tipo[], hilos_por_cable[], eventos_criticos }
GET  /traces/{cable}/{hilo}     → { cable, hilo, eventos: [{ id, distancia_km, atenuacion_db, tipo_evento }] }
GET  /traces/{cable}/{hilo}/plot → PNG imagen de traza OTDR
POST /audit                     → { header: { ... }, body: { criticos: [...], ... } }
POST /query (body: { query })   → { respuesta: "..." }
GET  /infrastructure            → [{ id, tipo, lat, lon, ... }]
GET  /infrastructure/search?q=  → [{ ...matches... }]
```

### 4.2 Respuesta de /stats

```json
{
  "isp": "chiminangos",
  "isp_name": "Red Chiminangos",
  "total_eventos": 11,
  "por_tipo": [
    { "tipo_evento": "Splitter 1x8 (2do Nivel CTO)", "count": 2 },
    { "tipo_evento": "Salida ODF (Conector)", "count": 2 }
  ],
  "hilos_por_cable": [
    { "id_cable": 8, "hilos": 2 }
  ],
  "eventos_criticos": 6
}
```

### 4.3 Header de ISP

Todas las rutas que dependen del ISP activo aceptan el header:

```
X-ISP-ID: chiminangos
```

Si no se envía, se usa el ISP configurado por defecto.

### 4.4 CORS

En desarrollo, CORS está abierto (`allow_origins=["*"]`). En producción, restringir al origen del dashboard.

---

## 5. Despliegue

### 5.1 Docker (producción)

```bash
docker compose --profile all up -d
```

Variables de entorno requeridas:

| Variable | Descripción |
|:--|:--|
| `DATABASE_URL` | PostgreSQL URL (default: `postgresql+asyncpg://user:pass@localhost/fibermind`) |
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram (opcional) |
| `TELEGRAM_AUTHORIZED_CHAT_ID` | Chat autorizado (opcional) |
| `OLLAMA_BASE_URL` | URL de Ollama (default: `http://host.docker.internal:11435`) |
| `DEFAULT_ISP_ID` | ISP por defecto |

### 5.2 Desarrollo local

```bash
# Dependencias
pip install -e ".[web]"

# Base de datos SQLite
python scripts/setup_db.py

# Iniciar API + Dashboard
uvicorn src.api.main:app --reload --port 8000
```

### 5.3 Health check

```bash
curl http://localhost:8000/health
# → {"status":"ok","version":"0.3.0","db_connected":true,...}
```

---

## 6. Configuración Multi-ISP

Los ISP se configuran en `src/config/isp_config.py`:

```python
ISPS = {
    "chiminangos": ISPConfig(
        name="Red Chiminangos",
        db_path="data/chiminangos.db",
        olt_power_dbm=3.0,
        splitter_config=[
            SplitterConfig(type="1x8", loss_db=10.5),
            SplitterConfig(type="1x8", loss_db=10.5),
        ],
    ),
}
```

Cada ISP tiene su propia base de datos SQLite (o esquema en PostgreSQL), configuración de potencia OLT y topología de splitters.

---

## 7. Modelo de Datos

### Entidades principales

```python
class OTDREvent:
    id: int
    id_cable: int
    id_hilo: int
    distancia_km: float
    atenuacion_db: float
    tipo_evento: str       # Splitter, Empalme, Curvatura, etc.
    timestamp: datetime

class Cable:
    id: int
    nombre: str
    capacidad_hilos: int

class Hilo:
    id: int
    id_cable: int
    numero: int
    estado: str            # activo, dañado, en_mantenimiento
```

### Base de datos

| Entorno | Motor | Conexión por defecto |
|:--|:--|:--|
| Desarrollo | SQLite | `data/{isp_id}.db` |
| Producción | PostgreSQL | `DATABASE_URL` (variable de entorno) |

---

## 8. Autenticación y Seguridad

### Estado actual (v0.3)

- **Sin autenticación interna**: El dashboard y la API son accesibles sin login.
- **Aislamiento de red**: Se recomienda ejecutar detrás de un reverse proxy (nginx, Caddy) con autenticación básica o VPN.
- **X-ISP-ID**: El header de ISP permite multi-tenencia a nivel de datos, no de autenticación.

### Próximas versiones (v0.4+)

- Autenticación JWT multi-rol (admin, técnico, lector)
- Sesiones por ISP
- HTTPS forzado vía reverse proxy
- Rate limiting en endpoints públicos

---

> **Repositorio:** [github.com/Johansarria/FiberMind-Analytics](https://github.com/Johansarria/FiberMind-Analytics)
> **Documentación API:** `http://localhost:8000/docs`
> **Dashboard:** `http://localhost:8000`
