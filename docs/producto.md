# FiberMind Analytics — Documentación de Producto

> **Plataforma de inteligencia de red FTTH para ISPs y NOCs**
> Versión: 0.3.0 · Última actualización: Junio 2026

---

## 1. Propuesta de Valor

FiberMind Analytics permite a **ISPs y operadores FTTH** centralizar, analizar y auditar sus trazas OTDR desde un dashboard profesional, eliminando la dependencia de hojas de cálculo, archivos `.sor` dispersos y herramientas de escritorio obsoletas.

### Problema que resuelve

| Problema | Cómo lo soluciona FiberMind |
|:--|:--|
| Trazas OTDR dispersas en archivos `.sor` individuales | Base de datos centralizada multi-ISP con importación automatizada |
| Diagnóstico manual lento → técnicos pierden horas | Detección automática de fallas críticas con umbrales configurables |
| Sin visibilidad centralizada del estado de red | Dashboard NOC con KPIs, gráficos y tabla de eventos en tiempo real |
| Dificultad para auditar empalmes entre equipos | Auditoría programática vía API REST y bot de Telegram |
| Privacidad de datos de red → no pueden usar IA en la nube | IA local con Ollama — los datos nunca salen de la infraestructura del ISP |

### Mercado objetivo

- **ISPs FTTH pequeños y medianos** (500–50,000 clientes) en Latinoamérica
- **NOCs** que requieren integración REST con sistemas existentes
- **Técnicos en campo** que necesitan diagnósticos rápidos desde su celular (vía Telegram)
- **Empresas de consultoría** que auditan redes FTTH

---

## 2. Capacidades del Producto

### 2.1 Dashboard NOC (Web SPA)

| Característica | Detalle |
|:--|:--|
| **Tipo** | Single Page Application (HTML/CSS/JS puro — sin frameworks) |
| **KPIs** | 5 tarjetas: Eventos totales, críticos, tipos detectados, cables, hilos |
| **Gráficos** | Donut de tipos de evento, barras de hilos por cable (Plotly.js) |
| **Tabla** | Últimos eventos reportados con badges de severidad (crítico, mayor, menor, info) |
| **Vistas** | Panel Principal, Consulta de Hilos, Auditoría, Infraestructura, Acerca de |
| **Estilo** | Modo claro profesional (lavanda + azul pastel), tipografía Inter |
| **Rendimiento** | Carga diferida de vistas (dynamic imports), sin recarga de página |
| **Sin dependencias** | No requiere Node.js, npm, React, Vue — solo un navegador |

### 2.2 API REST

Documentación interactiva en `/docs` (OpenAPI/Swagger).

**Endpoints principales:**

| Endpoint | Uso |
|:--|:--|
| `GET /stats` | Estadísticas en tiempo real del ISP activo |
| `GET /traces/{cable}/{hilo}` | Eventos OTDR de un hilo específico |
| `POST /audit` | Auditoría de empalmes con pérdida crítica |
| `POST /query` | Consulta en lenguaje natural (requiere Ollama) |
| `GET /infrastructure/search?q=` | Búsqueda geoespacial de infraestructura |

### 2.3 Inteligencia Artificial Local

- Modelo: **qwen2.5-coder:1.5b** vía Ollama
- Text-to-SQL: consulta la red en lenguaje natural
- Privacidad total: los datos nunca salen del servidor del ISP
- Sin costos recurrentes de API — corre en CPU o GPU básica

### 2.4 Bot de Telegram

Comandos disponibles:

| Comando | Función |
|:--|:--|
| `/start` | Información del sistema y bienvenida |
| `/auditar` | Auditoría de todos los empalmes críticos |
| `/hilo <cable> <hilo>` | Radiografía completa de un hilo |

---

## 3. Arquitectura

```
┌──────────────┐     ┌───────────────────────┐     ┌──────────────┐
│   Telegram   │────▶│   FastAPI (Backend)    │◀────│   Dashboard  │
│    Bot       │     │  ┌─────────────────┐   │     │   Web SPA    │
└──────────────┘     │  │ Core de Dominio  │   │     └──────────────┘
                     │  │  (Servicios)     │   │
┌──────────────┐     │  └────────┬────────┘   │
│   Ollama IA  │◀────│───────────┘            │
│  (local)     │     │  ┌─────────────────┐   │
└──────────────┘     │  │  Infraestructura │   │
                     │  │  DB / MCP / AI   │   │
                     │  └─────────────────┘   │
                     └───────────────────────┘
                               │
                     ┌────────┴────────┐
                     │   PostgreSQL /  │
                     │    SQLite       │
                     └─────────────────┘
```

### Principios de diseño

- **Privacidad primero**: La IA corre localmente. No se envían datos a terceros.
- **Multi-ISP**: Un solo despliegue puede atender múltiples operadores de red.
- **Sin vendor lock-in**: API REST estándar, base de datos SQL, dashboard HTML puro.
- **Offline-first**: Funciona sin conexión a Internet (excepto el bot de Telegram).

---

## 4. Modelo de Licenciamiento

FiberMind Analytics se distribuye bajo **licencia MIT** – código abierto, uso comercial permitido.

**Opciones de soporte disponibles:**
- Despliegue y configuración asistida
- Personalización del dashboard con marca del ISP
- Integración con sistemas existentes (facturación, OSS/BSS)
- Capacitación para equipos NOC

---

## 5. Roadmap

| Versión | Hito | Estado |
|:--|:--|:--|
| v0.1 | Prototipo: decodificación .sor + API básica | ✅ Completado |
| v0.2 | Bot de Telegram + MCP Server + consultas IA | ✅ Completado |
| v0.3 | **Dashboard SPA profesional** + multi-ISP + modo claro | ✅ **Actual** |
| v0.4 | Autenticación multi-rol + usuarios | 🔜 Próximo |
| v0.5 | Alertas en tiempo real + notificaciones | 🔜 Planeado |
| v0.6 | Dashboard personalizable por ISP | 🔜 Planeado |

---

## 6. Competencia

| Herramienta | FiberMind | Excel/Hojas | Viavi/EXFO SW | PRTG/Zabbix |
|:--|:--|:--|:--|:--|
| Dashboard dedicado FTTH | ✅ | ❌ | ❌ | ❌ |
| IA local y privada | ✅ | ❌ | ❌ | ❌ |
| Bot Telegram | ✅ | ❌ | ❌ | ❌ |
| API REST abierta | ✅ | ❌ | ❌ | Parcial |
| Sin licencias costosas | ✅ | Parcial | ❌ (~$5K) | ❌ (~$2K) |
| Multi-ISP | ✅ | ❌ | ❌ | ❌ |
| Código abierto | ✅ | ❌ | ❌ | ❌ |

---

## 7. Casos de Uso

### ISP con 3,000 clientes en Cali, Colombia

> *"Antes revisábamos las trazas OTDR una por una en el software del fabricante. Con FiberMind centralized toda la red, detectamos empalmes críticos en segundos, y los técnicos consultan desde el celular por Telegram."*

### NOC con 5 operadores regionales

> *"Un solo dashboard para monitorear la salud de todos los ISP que administramos. Las alertas automáticas nos permiten prevenir fallas antes de que afecten a los clientes."*

---

> 📧 **Contacto:** johansarria59@gmail.com
> 🔗 **Repositorio:** [github.com/Johansarria/FiberMind-Analytics](https://github.com/Johansarria/FiberMind-Analytics)
