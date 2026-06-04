# FiberMind Analytics 🔬📡

Plataforma de analítica e inteligencia artificial para inspección y mantenimiento de infraestructura **FTTH** (Fiber To The Home). Decodifica trazas OTDR, detecta fallas críticas automáticamente y permite consultas en lenguaje natural vía IA local.

---

## 🎯 Para quién es

- **ISPs y operadores FTTH** que quieren automatizar el análisis de trazas OTDR
- **Técnicos en campo** que necesitan diagnósticos rápidos desde su celular
- **NOCs** que requieren integración REST con dashboards existentes

---

## ✨ Capacidades

| Característica | Descripción |
|:--|:--|
| 📡 **Decodificación OTDR** | Analiza archivos .sor y extrae eventos ópticos |
| ⚠️ **Detección de Fallas** | Identifica empalmes, curvaturas y splits con pérdida crítica |
| 📊 **Visualización** | Trazas estimadas de potencia óptica con umbrales |
| 🤖 **IA Local (Text-to-SQL)** | Consulta la red en lenguaje natural vía Ollama (privacidad total) |
| 🗺️ **Inventario Geográfico** | Localiza empalmes, CTOs y mufas en planos |
| 🤖 **Bot de Telegram** | Técnicos consultan desde el celular |
| 🔌 **API REST** | Integración con cualquier dashboard o NOC |
| 🔌 **Servidor MCP** | Integración con asistentes IA (Claude, Cursor, etc.) |
| 🐳 **Docker** | Despliegue en 1 comando |

---

## 📂 Estructura

```
fibermind-analytics/
├── src/
│   ├── core/domain/          # Modelos de dominio (OTDREvent, InventoryElement)
│   │   services/             # Lógica de negocio (AI, Network)
│   ├── infrastructure/
│   │   ├── database/         # Repositorio SQLite
│   │   ├── ai/               # Cliente Ollama
│   │   ├── telegram/         # Bot de Telegram
│   │   └── mcp/              # Servidor MCP
│   ├── api/                  # API REST (FastAPI)
│   ├── dashboard/            # Dashboard web (Streamlit)
│   ├── config/               # Prompts y configuración
│   └── utils/                # Plotting y utilidades
├── scripts/                  # ETL, setup, diagnóstico
├── tests/                    # Pruebas unitarias
├── pyproject.toml            # Paquete Python
├── Dockerfile                # Imagen Docker
├── docker-compose.yml        # Stack completo
└── AGENTES.md                # Guía para asistentes IA
```

---

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado)

```bash
# Clonar
git clone https://github.com/Johansarria/FiberMind-Analytics.git
cd FiberMind-Analytics

# Copiar configuración
cp .env.example .env
# Edita TELEGRAM_BOT_TOKEN si quieres el bot

# Iniciar todo el stack
docker compose --profile all up -d
```

Servicios:
| Puerto | Servicio | URL |
|:--|:--|:--|
| 8000 | API REST | http://localhost:8000/docs |
| 8501 | Dashboard | http://localhost:8501 |
| 11435 | Ollama | http://localhost:11435 |
| 5432 | PostgreSQL | localhost:5432 |

### Opción 2: Local (Desarrollo)

```bash
# Instalar
python3 -m venv venv && source venv/bin/activate
pip install -e .
pip install -e ".[web,dashboard]"

# Configurar
cp .env.example .env

# Iniciar base de datos
python scripts/setup_db.py

# API REST
uvicorn src.api.main:app --reload --port 8000

# Dashboard
streamlit run src/dashboard/app.py

# Bot de Telegram (requiere token)
python -m src.infrastructure.telegram.bot

# Servidor MCP
python -m src.infrastructure.mcp.server
```

---

## 🔌 API REST

| Método | Endpoint | Descripción |
|:--|:--|:--|
| GET | `/health` | Health check |
| GET | `/traces/{id_cable}/{id_hilo}` | Eventos OTDR de un hilo |
| GET | `/traces/{id_cable}/{id_hilo}/plot` | Gráfico de traza OTDR |
| POST | `/audit` | Auditoría de empalmes críticos |
| GET | `/infrastructure` | Listar infraestructura |
| GET | `/infrastructure/search?q=` | Buscar elemento geográfico |
| POST | `/query` | Consulta en lenguaje natural (requiere Ollama) |
| GET | `/stats` | Estadísticas de la red |

Documentación interactiva: http://localhost:8000/docs

---

## 🤖 Bot de Telegram

```
/start        → Info y bienvenida
/auditar      → Auditoría de empalmes críticos
/hilo <c> <h> → Radiografía de un hilo específico
```

Configura en `.env`:
```
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_AUTHORIZED_CHAT_ID=tu_chat_id
```

---

## 🛠️ Stack Tecnológico

- **Python 3.12+** · FastAPI · Streamlit · Pydantic
- **SQLite** (dev) / **PostgreSQL** (prod)
- **Ollama** (qwen2.5-coder:1.5b) · **MCP Protocol**
- **python-telegram-bot** · **matplotlib**
- **Docker** · **Docker Compose**

---

## 📄 Licencia

MIT © 2026 Johan Sarria

---

> 🔬 *De técnicos para técnicos — análisis FTTH con privacidad e inteligencia local.*
