# ─────────────────────────────────────────────
# FiberMind Analytics - Multi-ISP Configuration
# ─────────────────────────────────────────────
# Permite que una sola instancia sirva a múltiples
# ISPs con sus propias bases de datos, modelos de IA,
# bots de Telegram y configuraciones regionales.
# ─────────────────────────────────────────────

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from src.infrastructure.database.repository import FTTHRepository
from src.core.services.network_service import NetworkService

# ─── Constants ───
DEFAULT_CONFIG_PATHS = [
    "fibermind.yml",
    "~/.fibermind/config.yml",
    "/etc/fibermind/config.yml",
    os.environ.get("FIBERMIND_CONFIG", ""),
]


@dataclass
class ISPConfig:
    """Configuración individual de un ISP/cliente."""
    id: str
    name: str = ""
    db_path: str = "ftth_mantenimiento.db"
    ollama_url: str = "http://localhost:11434/api/generate"
    ollama_model: str = "qwen2.5-coder:1.5b"
    telegram_token: str = ""
    city: str = ""
    lat: float = 0.0
    lon: float = 0.0
    timezone: str = "America/Bogota"

    def __post_init__(self):
        if not self.name:
            self.name = self.id.capitalize()


@dataclass
class FiberMindConfig:
    """Gestor de configuración multi-ISP.

    Carga un archivo YAML y provee acceso a la config
    de cada ISP. Soporta herencia de valores globales.
    """

    default_isp: str = ""
    isps: dict[str, ISPConfig] = field(default_factory=dict)
    _loaded_path: str = ""

    @classmethod
    def load(cls, path: Optional[str] = None) -> "FiberMindConfig":
        """Carga configuración desde un archivo YAML.

        Busca en orden: path explícito → DEFAULT_CONFIG_PATHS.
        Si no encuentra ningún archivo, retorna config por defecto.
        """
        search_paths = [path] if path else DEFAULT_CONFIG_PATHS

        for path in search_paths:
            if not path:
                continue
            resolved = Path(path).expanduser()
            if resolved.exists():
                with open(resolved) as f:
                    raw = yaml.safe_load(f)
                if raw is None:
                    raw = {}
                return cls._from_dict(raw, str(resolved))

        print(f"[FiberMind] No config file found. Using defaults.")
        return cls._default()

    @classmethod
    def _from_dict(cls, raw: dict, source: str = "") -> "FiberMindConfig":
        default_isp = raw.get("default_isp", "")
        global_defaults = raw.get("globals", {})
        isps = {}

        for isp_id, isp_raw in raw.get("isps", {}).items():
            merged = {**global_defaults, **isp_raw}
            isps[isp_id] = ISPConfig(
                id=isp_id,
                name=merged.get("name", isp_id),
                db_path=merged.get("db", {}).get("path", "ftth_mantenimiento.db"),
                ollama_url=merged.get("ollama", {}).get("url", "http://localhost:11434/api/generate"),
                ollama_model=merged.get("ollama", {}).get("model", "qwen2.5-coder:1.5b"),
                telegram_token=merged.get("telegram", {}).get("token", ""),
                city=merged.get("location", {}).get("city", ""),
                lat=merged.get("location", {}).get("lat", 0.0),
                lon=merged.get("location", {}).get("lon", 0.0),
                timezone=merged.get("location", {}).get("timezone", "America/Bogota"),
            )

        return cls(default_isp=default_isp, isps=isps, _loaded_path=source)

    @classmethod
    def _default(cls) -> "FiberMindConfig":
        """Config por defecto (compatible con versión anterior)."""
        return cls(
            default_isp="default",
            isps={
                "default": ISPConfig(
                    id="default",
                    name="Local Development",
                    db_path=os.getenv("DB_PATH", "ftth_mantenimiento.db"),
                    ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate"),
                    ollama_model=os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b"),
                    telegram_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
                )
            },
        )

    def get_isp(self, isp_id: Optional[str] = None) -> ISPConfig:
        """Obtiene la config de un ISP. Usa default o el primero si no se especifica."""
        if not isp_id:
            isp_id = self.default_isp

        if not isp_id and self.isps:
            isp_id = list(self.isps.keys())[0]

        isp = self.isps.get(isp_id)
        if not isp:
            available = ", ".join(self.isps.keys()) if self.isps else "(none)"
            raise KeyError(f"ISP '{isp_id}' not found. Available: {available}")

        return isp

    def list_isps(self) -> list[dict]:
        """Lista todos los ISPs disponibles con info básica."""
        return [
            {
                "id": isp.id,
                "name": isp.name,
                "city": isp.city,
                "db_exists": Path(isp.db_path).expanduser().exists(),
            }
            for isp in self.isps.values()
        ]

    def get_repo(self, isp_id: Optional[str] = None) -> FTTHRepository:
        """Crea un repositorio para el ISP especificado."""
        isp = self.get_isp(isp_id)
        return FTTHRepository(isp.db_path)

    def get_network_service(self, isp_id: Optional[str] = None) -> NetworkService:
        """Crea un NetworkService para el ISP especificado."""
        return NetworkService(self.get_repo(isp_id))

    def get_available_isps(self) -> list[str]:
        """Retorna lista de IDs de ISP disponibles."""
        return list(self.isps.keys())

    def to_dict(self) -> dict:
        """Exporta la config como dict para la API."""
        return {
            "default_isp": self.default_isp,
            "loaded_from": self._loaded_path or "defaults (env vars)",
            "isps": {
                isp_id: {
                    "name": isp.name,
                    "city": isp.city,
                    "db_path": isp.db_path,
                    "ollama_model": isp.ollama_model,
                }
                for isp_id, isp in self.isps.items()
            },
        }


# ─── Singleton global ───
_config_instance: Optional[FiberMindConfig] = None


def get_config(path: Optional[str] = None) -> FiberMindConfig:
    """Singleton: carga la config una sola vez."""
    global _config_instance
    if _config_instance is None:
        _config_instance = FiberMindConfig.load(path)
    return _config_instance


def reload_config(path: Optional[str] = None) -> FiberMindConfig:
    """Recarga la config (útil para hot-reload)."""
    global _config_instance
    _config_instance = FiberMindConfig.load(path)
    return _config_instance
