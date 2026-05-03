# FiberMind Analytics 🤖📊

Un sistema inteligente, autónomo y privado diseñado para transformar datos crudos de hardware en diagnósticos accionables utilizando **Modelos de Lenguaje Locales (LLMs)**. 

Este proyecto implementa una arquitectura **Text-to-SQL** y análisis de datos en lenguaje natural para optimizar las operaciones de mantenimiento preventivo (O&M). Basado en los principios de **Clean Architecture**, el sistema separa el dominio, la infraestructura y los servicios para garantizar mantenibilidad y escalabilidad.

---

## 🌟 Características Principales

### 1. Motor Analítico Asistido por LLM (Soberanía de Datos)
- **Razonamiento Local (Costo $0):** Impulsado por **Ollama** (`qwen2.5-coder:1.5b`), garantizando que los datos de infraestructura nunca salgan hacia APIs de terceros.
- **Text-to-SQL Dinámico:** Traducción de intenciones operativas complejas a consultas SQL precisas.
- **Análisis de Fallas (Fault Analysis):** Cruce de atenuaciones y distancias para diagnósticos técnicos.

### 2. Arquitectura de Software (AGENTES.md Compliant)
- **Modularidad Total:** Capas de Dominio, Infraestructura y Aplicación claramente separadas.
- **Patrón Repository:** Centralización del acceso a datos en SQLite.
- **Tipado Fuerte:** Implementación extensiva de Type Hints en Python para robustez.

### 3. Interfaz Agéntica Multicanal
- **Telegram Bot:** Interacción fluida para técnicos de campo (Auditoría, Radiografía de Hilos).
- **Servidor MCP:** Herramientas de diagnóstico integradas para ecosistemas de Agentes IA.
- **Visualización:** Generación automatizada de trazas OTDR estimadas mediante `matplotlib`.

---

## 📂 Estructura del Proyecto

```text
C:\MLpractica3\
├── src/
│   ├── core/                # Lógica pura y reglas de negocio
│   │   ├── domain/          # Entidades (OTDREvent, InventoryElement)
│   │   └── services/        # Casos de uso (AI Service, Network Service)
│   ├── infrastructure/      # Implementaciones de servicios externos
│   │   ├── database/        # Repositorio SQLite
│   │   ├── ai/              # Clientes de IA (Ollama)
│   │   ├── telegram/        # Lógica del Bot de Telegram
│   │   └── mcp/             # Servidor de herramientas MCP
│   ├── utils/               # Plotting, Strings, Utilidades comunes
│   └── config/              # Prompts y configuraciones del sistema
├── scripts/                 # Ingesta ETL, Setup y Diagnóstico
├── tests/                   # Suite de pruebas unitarias
├── data/                    # Almacenamiento de DB y trazas raw
└── .env                     # Configuración de credenciales y rutas
```

---

## 🚀 Instalación y Despliegue

### 1. Preparar Entorno
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install pyotdr python-telegram-bot matplotlib requests mcp python-dotenv
```

### 2. Configurar IA Local
```bash
ollama run qwen2.5-coder:1.5b
```

### 3. Ejecución
1. Configura el archivo `.env` con tus tokens y rutas.
2. Inicia el bot de Telegram:
   ```bash
   python -m src.infrastructure.telegram.bot
   ```
3. O inicia el servidor MCP:
   ```bash
   python -m src.infrastructure.mcp.server
   ```

---

## 🛠️ Tecnologías Utilizadas
- **Python 3.10+** (Core)
- **SQLite** (Data Warehouse)
- **Ollama** (LLM Engine)
- **FastMCP** (Integración de Herramientas)
- **Python Telegram Bot** (Interfaz)
- **Matplotlib** (Visualización)

---
*Optimizado bajo los estándares de **FiberMind Analytics** para la excelencia en O&M.*
