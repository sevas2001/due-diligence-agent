# Due Diligence Agent

[![CI](https://github.com/sevas2001/due-diligence-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/sevas2001/due-diligence-agent/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11-blue)

Agente IA autónomo end-to-end para análisis de empresas españolas: búsqueda web en
tiempo real, extracción de datos financieros, generación de informes de due diligence
con LLM y memoria persistente en PostgreSQL.

**Stack:** LangGraph · FastAPI · PostgreSQL · Streamlit · Docker · yfinance · Tavily

---

## Casos de uso

- **"Analiza Iberdrola"** → busca, procesa y devuelve un informe de due diligence.
- **"Compara Iberdrola con Endesa"** → recupera ambas (o las analiza) y genera comparativa.
- **"¿Qué empresas del sector energético hemos analizado?"** → consulta la memoria.

---

## Arquitectura

```
Usuario (Streamlit) → FastAPI → Agente LangGraph → PostgreSQL (memoria)
```

**Flujo del agente (grafo LangGraph):**

```
check_memory → fetch_finance → fetch_corporate → fetch_news → analyze → assemble → persist
     │              │                │                │           │
  memoria        yfinance        scraper web        Tavily       LLM
```

El agente genera un informe estructurado: resumen ejecutivo, situación financiera,
noticias recientes con sentimiento, DAFO, indicadores de riesgo y fuentes.

**Separación datos / juicio (anti-alucinación):** las cifras vienen de las tools y el
LLM no las altera; el LLM solo produce el análisis (resumen, DAFO, sentimiento, riesgo).

---

## Endpoints API

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/analyze` | Analiza una empresa, devuelve el informe |
| POST | `/compare` | Compara dos empresas (usa memoria o las analiza) |
| GET | `/companies?sector=` | Empresas analizadas (filtro por sector) |
| GET | `/companies/{q}/latest` | Último informe de una empresa |
| GET | `/companies/{q}/history` | Histórico de informes |
| GET | `/health` | Healthcheck |

---

## Estructura

```
app/
├── config.py          # Settings desde .env (pydantic-settings)
├── llm/client.py      # Cliente LLM agnóstico (OpenRouter, OpenAI-compatible)
├── tools/             # finance (yfinance), web_search (Tavily), scraper (BeautifulSoup)
├── memory/            # models + db + repository (SQLAlchemy / PostgreSQL)
├── agent/             # state, prompts, nodes, graph (LangGraph) + compare
├── schemas/report.py  # Schemas Pydantic (informe + comparativa)
└── api/main.py        # FastAPI
frontend/              # App Streamlit (pestañas Analizar / Comparar)
scripts/               # Smoke tests: test_llm, test_agent, test_compare, test_memory
tests/                 # Tests CI-safe (pytest, sin red/keys)
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
python scripts/test_compare.py "Iberdrola" "Endesa"     # comparativa end-to-end
python scripts/test_memory.py                           # memoria (save/query)
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
- [x] Scraper cableado en el grafo (`fetch_corporate`)
- [x] Comparativa entre empresas (`/compare` + UI)
- [x] API FastAPI + frontend Streamlit
- [x] Docker + CI

**Brief cubierto al 100%:** 3 casos de uso + 3 tools (yfinance, Tavily, scraper).
