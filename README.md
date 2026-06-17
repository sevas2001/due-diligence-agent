# Due Diligence Agent

[![CI](https://github.com/sevas2001/due-diligence-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/sevas2001/due-diligence-agent/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11-blue)

Agente IA autónomo end-to-end para análisis de empresas españolas: búsqueda web en
tiempo real, extracción de datos financieros, generación de informes de due diligence
con LLM y memoria persistente en PostgreSQL.

**Stack:** LangGraph · FastAPI · PostgreSQL · Streamlit · Docker · yfinance · Tavily

---

## Arquitectura

```
Usuario (Streamlit) → FastAPI → Agente LangGraph
                                      │
        ┌─────────────────┬──────────┴──────────┬─────────────────┐
        ▼                 ▼                      ▼                 ▼
   Tavily (web)     yfinance (finanzas)   PostgreSQL (memoria)   LLM (informe)
```

El agente genera un informe estructurado: resumen ejecutivo, situación financiera,
noticias recientes con sentimiento, DAFO, indicadores de riesgo y fuentes.

---

## Estructura

```
app/
├── config.py          # Settings desde .env (pydantic-settings)
├── llm/               # Cliente LLM agnóstico (OpenRouter, OpenAI-compatible)
├── tools/             # yfinance, Tavily, scraper
├── memory/            # Modelos SQLAlchemy + repositorio (PostgreSQL)
├── agent/             # Grafo de estados LangGraph
├── schemas/           # Schemas Pydantic del informe
└── api/               # FastAPI
frontend/              # App Streamlit
tests/
```

---

## Arranque local (dev)

```bash
python -m venv .venv
.venv\Scripts\activate           # Windows
pip install -r requirements.txt

copy .env.example .env           # Windows — rellena tus keys
```

LLM vía **OpenRouter** (OpenAI-compatible): consigue key en https://openrouter.ai/keys
y ponla en `LLM_API_KEY`. Cambia de modelo solo editando `LLM_MODEL` en `.env`.

### Probar por capas (smoke tests)

```bash
python scripts/test_llm.py                              # capa LLM
python scripts/test_agent.py "Iberdrola"                # agente end-to-end (SQLite)
pytest -q                                               # tests CI-safe
```

### Levantar todo (Docker)

```bash
docker compose up --build
# API:      http://localhost:8000/docs
# Frontend: http://localhost:8501
```

### Sin Docker (dev)

```bash
uvicorn app.api.main:app --reload          # terminal 1
streamlit run frontend/streamlit_app.py    # terminal 2
```

---

## Estado del proyecto

- [x] Estructura base + config
- [x] Capa LLM (OpenRouter)
- [x] Tools (yfinance, Tavily, scraper)
- [x] Memoria PostgreSQL
- [x] Agente LangGraph + prompt del informe
- [x] API FastAPI + frontend Streamlit
- [x] Docker + CI
