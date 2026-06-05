# FiberMind Analytics 🔬📡

**Plataforma de inteligencia de red FTTH — Decodifica, visualiza y audita tu infraestructura óptica.**

FiberMind transforma trazas OTDR en un dashboard NOC profesional con detección automática de fallas críticas, consultas multi-ISP y visualización en tiempo real. Diseñado para ISPs que quieren pasar de hojas de cálculo y archivos `.sor` sueltos a una plataforma centralizada.

---

## ✨ Panorama General

| Área | Descripción |
|:--|:--|
| 🎯 **Para quién** | ISPs FTTH, NOCs, técnicos en campo |
| 📡 **Qué hace** | Decodifica trazas OTDR, detecta fallas, audita empalmes críticos |
| 📊 **Dashboard** | SPA moderna modo claro, estilo NOC profesional (HTML/CSS/JS puro) |
| 🤖 **IA local** | Consultas en lenguaje natural vía Ollama (privacidad total) |
| 🔌 **API REST** | Integración con cualquier sistema existente |
| 🐳 **Despliegue** | Docker compose en 1 comando |

---

## 🖥️ Dashboard SPA

El nuevo dashboard es una **Single Page Application** hecha en HTML/CSS/JS puro:

- **Paleta clara profesional** — Fondo lavanda (#FDF8FE), sidebar lavanda (#DCD4F2), acentos azul-lavanda
- **5 tarjetas KPI** — Eventos OTDR, críticos, tipos detectados, cables, hilos monitoreados
- **Gráficos Plotly.js** — Donut de tipos de evento, barras de hilos por cable
- **Tabla de eventos** — Últimos eventos con badges de severidad
- **5 vistas** — Panel Principal, Consulta de Hilos, Auditoría, Infraestructura, Acerca de
- **Responsive** — Funciona en tablets y laptops
- **Servido por FastAPI** — Sin servidor web adicional, sin dependencias Node.js

![Dashboard](https://via.placeholder.com/800x400/FDF8FE/DCD4F2?text=FiberMind+Dashboard)

---

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado)

```bash
git clone https://github.com/Johansarria/FiberMind-Analytics.git
cd FiberMind-Analytics
cp .env.example .env
# Edita las variables de conexión a base de datos y Telegram

docker compose --profile all up -d
```

| Puerto | Servicio |
|:--|:--|
| `8000` | API REST + Dashboard web |
| `11435` | Ollama (modelos IA local) |
| `5432` | PostgreSQL |

### Opción 2: Desarrollo local

```bash
python3 -m venv venv && source venv/bin/activate
pip install -e ".[web]"

cp .env.example .env
python scripts/setup_db.py

# API + Dashboard
uvicorn src.api.main:app --reload --port 8000
```

Abrir en navegador: **http://localhost:8000**

---

## 🔌 API REST

| Método | Endpoint | Descripción |
|:--|:--|:--|
| `GET` | `/health` | Health check del sistema |
| `GET` | `/isps` | Listar ISPs configurados |
| `GET` | `/stats` | Estadísticas de la red activa |
| `GET` | `/traces/{cable}/{hilo}` | Eventos OTDR de un hilo |
| `GET` | `/traces/{cable}/{hilo}/plot` | Gráfico de traza OTDR |
| `POST` | `/audit` | Auditoría de empalmes críticos |
| `POST` | `/query` | Consulta en lenguaje natural |
| `GET` | `/infrastructure` | Inventario geográfico |
| `GET` | `/infrastructure/search?q=` | Búsqueda de infraestructura |

Documentación interactiva: **http://localhost:8000/docs**

---

## 🏗️ Stack Tecnológico

```
Frontend     HTML5 · CSS3 · JavaScript (ES Modules) · Plotly.js
Backend      Python 3.13+ · FastAPI · Pydantic v2
Base de datos SQLite (desarrollo) / PostgreSQL (producción)
IA Local     Ollama · qwen2.5-coder:1.5b
Bot          python-telegram-bot (opcional)
Despliegue   Docker · Docker Compose
```

---

## 🤖 Bot de Telegram

```text
/start        → Información del sistema
/auditar      → Auditoría de empalmes críticos
/hilo <c> <h> → Radiografía de un hilo
```

---

## 📁 Estructura del proyecto

```
├── src/
│   ├── api/                  # API REST FastAPI
│   ├── core/
│   │   ├── domain/           # Modelos (OTDREvent, Cable, Hilo)
│   │   └── services/         # Lógica de negocio (AI, Network)
│   ├── infrastructure/
│   │   ├── database/         # Repositorio SQLite/PostgreSQL
│   │   ├── ai/               # Cliente Ollama
│   │   ├── telegram/         # Bot de Telegram
│   │   └── mcp/              # Servidor MCP (protocolo IA)
│   ├── dashboard-html/       # Dashboard SPA (HTML/CSS/JS)
│   ├── config/               # Prompts y configuración multi-ISP
│   └── utils/                # Plotting y utilidades
├── scripts/                  # ETL, setup, diagnóstico
├── tests/                    # Pruebas unitarias
├── docs/                     # Documentación
├── Dockerfile                # Imagen Docker
├── docker-compose.yml        # Stack completo
└── pyproject.toml            # Paquete Python
```

---

## 📄 Licencia

MIT © 2026 Johan Sarria

> 🔬 *De técnicos para técnicos — análisis FTTH con privacidad e inteligencia local.*
