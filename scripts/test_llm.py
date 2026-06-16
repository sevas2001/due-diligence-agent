"""Smoke test de la capa LLM. Verifica key + modelo + endpoint OpenRouter.

Uso:
    python scripts/test_llm.py
"""
import sys
from pathlib import Path

# Permite ejecutar el script sin instalar el paquete.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.llm.client import healthcheck  # noqa: E402


def main() -> int:
    print(f"Modelo:   {settings.llm_model}")
    print(f"Endpoint: {settings.llm_base_url}")
    print(f"Key:      {'sí' if settings.llm_api_key else 'NO (rellena .env)'}\n")
    try:
        out = healthcheck()
    except Exception as exc:  # noqa: BLE001
        print(f"FALLO: {type(exc).__name__}: {exc}")
        return 1
    print(f"Respuesta LLM: {out!r}")
    print("OK — capa LLM funcionando." if "OK" in out.upper() else "Respuesta inesperada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
