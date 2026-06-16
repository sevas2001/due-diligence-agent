"""Config de pytest: fuerza SQLite ANTES de importar la app.

`app.config.settings` se cachea en el primer import, así que la variable de
entorno debe estar puesta aquí, en el arranque de la sesión de tests.
"""
import os
import tempfile

# Backend SQLite temporal y aislado para los tests.
_tmp = os.path.join(tempfile.gettempdir(), "dd_agent_ci_test.db")
if os.path.exists(_tmp):
    os.remove(_tmp)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}"

# Keys vacías: ningún test CI debe tocar red/LLM.
os.environ.setdefault("LLM_API_KEY", "")
os.environ.setdefault("TAVILY_API_KEY", "")
