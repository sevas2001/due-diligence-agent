# Agente IA Autónomo para Análisis de Empresas — Project Brief

## Idea central

Un agente de IA autónomo que, dado el nombre de una empresa española, es capaz de buscar información actualizada de forma autónoma, analizar sus datos financieros públicos, generar un informe estructurado de due diligence básico y almacenar todo en memoria persistente para consultas y comparativas futuras.

El objetivo no es investigación académica sino una herramienta aplicada a negocio real, del tipo que usan equipos de M&A, consultoría estratégica y análisis financiero.

---

## Casos de uso

- Un analista escribe: "Analiza Iberdrola" → el agente busca, procesa y devuelve un informe estructurado
- "Compara Iberdrola con Endesa en los últimos 6 meses" → el agente recupera ambos de memoria y genera comparativa
- "¿Qué empresas del sector energético hemos analizado?" → el agente consulta su memoria persistente

---

## Stack técnico

**Orquestación del agente**
- LangChain + LangGraph — construcción del agente con grafo de estados y memoria

**Herramientas del agente (tools)**
- Tavily API o SerpAPI — búsqueda web en tiempo real de noticias y datos de la empresa
- Yahoo Finance API (yfinance) — datos financieros históricos y actuales
- Web scraping con BeautifulSoup — extracción de información de webs corporativas y registros públicos

**Backend y API**
- FastAPI — API REST que expone el agente al exterior
- PostgreSQL — base de datos relacional para memoria persistente del agente (historial de análisis, empresas procesadas, informes generados)

**Frontend**
- Streamlit — interfaz web simple donde el usuario introduce el nombre de la empresa y visualiza el informe generado

**Infraestructura**
- Docker + docker-compose — contenedorización de todos los servicios (agente, API, base de datos, frontend)
- GitHub Actions — CI/CD automático

**LLM**
- OpenAI GPT-4o o Claude claude-sonnet-4-6 vía API — generación del informe final estructurado

---

## Output del agente

El agente genera un informe estructurado con:

1. **Resumen ejecutivo** — quién es la empresa, sector, tamaño
2. **Situación financiera** — precio acción, capitalización, P/E ratio, variación 12 meses
3. **Noticias recientes** — últimas 5-10 noticias relevantes con análisis de sentimiento
4. **Análisis DAFO básico** — generado por el LLM a partir de la información recopilada
5. **Indicadores de riesgo** — volatilidad, tendencia, alertas
6. **Fecha del análisis y fuentes consultadas**

---

## Arquitectura del agente (flujo)

```
Usuario introduce empresa
        ↓
LangGraph inicializa el agente
        ↓
Tool 1: Búsqueda web (Tavily) → noticias y contexto
        ↓
Tool 2: Yahoo Finance → datos financieros
        ↓
Tool 3: PostgreSQL → ¿ya tenemos análisis previo? → recupera contexto histórico
        ↓
LLM genera informe estructurado
        ↓
PostgreSQL guarda el informe con timestamp
        ↓
FastAPI devuelve el informe
        ↓
Streamlit lo renderiza al usuario
```

---

## Por qué este proyecto para el mercado laboral

Conecta directamente con los sectores y roles más demandados en las ofertas revisadas:

- **KPMG Deal Advisory** — due diligence financiero es su negocio principal
- **EY wavespace** — IA aplicada a análisis de negocio
- **Accenture Data Scientist** — soluciones con LLMs orientadas a decisiones de negocio
- **E-Frontiers** — analítica financiera avanzada
- **NTT DATA Banking** — analítica en sector financiero
- **BBVA Be Talent** — modelos aplicados a datos financieros reales

Demuestra dominio de: agentes IA, LangGraph, memoria persistente con PostgreSQL, FastAPI, Docker, datos financieros reales y entrega de producto funcional end-to-end.

---

## Nombre sugerido para el repositorio

`company-intelligence-agent` o `due-diligence-agent`

---

## Lo que añade al CV

```
LangGraph · Agentes IA con memoria persistente · PostgreSQL · 
FastAPI · Docker · Streamlit · Yahoo Finance API · 
Análisis financiero automatizado · Due diligence con IA
```

Descripción para el CV:
*"Agente IA autónomo end-to-end para análisis de empresas: búsqueda web en tiempo real, extracción de datos financieros, generación de informes de due diligence con LLM y memoria persistente en PostgreSQL. Stack: LangGraph + FastAPI + Docker + Streamlit."*
