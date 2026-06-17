"""Nodos del grafo. Cada función recibe el estado y devuelve un parche parcial.
"""
from __future__ import annotations

import json

from app.agent.prompts import ANALYST_SYSTEM, ANALYST_USER_TEMPLATE
from app.agent.state import AgentState
from app.llm.client import get_llm
from app.memory import repository as repo
from app.memory.db import get_session, init_db
from app.schemas.report import (
    DueDiligenceReport,
    FinancialSnapshot,
    LLMAnalysis,
)
from app.tools.finance import get_financials
from app.tools.scraper import fetch_text
from app.tools.web_search import search_news


def check_memory(state: AgentState) -> AgentState:
    """Recupera el último análisis previo de la empresa, si existe."""
    init_db()
    query = state["company_query"]
    try:
        with get_session() as s:
            prev = repo.get_latest_analysis(s, query)
            if prev:
                r = prev.report
                return {
                    "prior_summary": (
                        f"Análisis previo ({r.get('analysis_date')}): "
                        f"{r.get('executive_summary', '')}"
                    )
                }
    except Exception as exc:  # noqa: BLE001
        return {"prior_summary": None, "errors": [f"memoria: {exc}"]}
    return {"prior_summary": None}


def fetch_finance(state: AgentState) -> AgentState:
    """Obtiene datos financieros vía yfinance."""
    try:
        return {"financials": get_financials(state["company_query"])}
    except Exception as exc:  # noqa: BLE001
        return {"financials": {}, "errors": [f"finance: {exc}"]}


def fetch_corporate(state: AgentState) -> AgentState:
    """Scrapea la web corporativa (de los datos de yfinance) para contexto extra.

    Best-effort: muchas webs corporativas bloquean bots (403) -> devuelve "".
    """
    website = (state.get("financials") or {}).get("website")
    if not website:
        return {"corporate_text": ""}
    try:
        return {"corporate_text": fetch_text(website, max_chars=3000)}
    except Exception as exc:  # noqa: BLE001
        return {"corporate_text": "", "errors": [f"scraper: {exc}"]}


def fetch_news(state: AgentState) -> AgentState:
    """Obtiene noticias recientes vía Tavily."""
    try:
        return {"news": search_news(state["company_query"], max_results=8)}
    except Exception as exc:  # noqa: BLE001
        return {"news": [], "errors": [f"news: {exc}"]}


def analyze(state: AgentState) -> AgentState:
    """Llama al LLM con structured output para las partes analíticas."""
    llm = get_llm().with_structured_output(LLMAnalysis)
    fin = state.get("financials", {})
    news = state.get("news", [])

    user = ANALYST_USER_TEMPLATE.format(
        company_query=state["company_query"],
        financials=json.dumps(fin, ensure_ascii=False, indent=2, default=str),
        news=json.dumps(
            [{"title": n.get("title"), "published_date": n.get("published_date"),
              "content": (n.get("content") or "")[:500], "url": n.get("url")}
             for n in news],
            ensure_ascii=False, indent=2, default=str,
        ),
        corporate_text=state.get("corporate_text") or "(no disponible)",
        prior_summary=state.get("prior_summary") or "(sin análisis previo)",
    )
    analysis: LLMAnalysis = llm.invoke(
        [("system", ANALYST_SYSTEM), ("human", user)]
    )
    return {"llm_analysis": analysis}


def assemble(state: AgentState) -> AgentState:
    """Combina datos duros (tools) + juicio (LLM) en el informe final."""
    fin = state.get("financials", {})
    analysis: LLMAnalysis = state["llm_analysis"]

    sources = ["Yahoo Finance (yfinance)", "Tavily"]
    if state.get("corporate_text"):
        sources.append(f"Web corporativa ({fin.get('website')})")

    report = DueDiligenceReport(
        company_name=fin.get("company_name") or state["company_query"],
        ticker=fin.get("symbol"),
        sector=fin.get("sector"),
        executive_summary=analysis.executive_summary,
        financials=FinancialSnapshot(**{
            k: fin.get(k) for k in FinancialSnapshot.model_fields if k in fin
        }),
        news=analysis.news_sentiment,
        swot=analysis.swot,
        risk=analysis.risk,
        sources=sources,
    )
    return {"report": report}


def persist(state: AgentState) -> AgentState:
    """Guarda el informe final en memoria persistente."""
    try:
        with get_session() as s:
            repo.save_report(s, state["report"])
    except Exception as exc:  # noqa: BLE001
        return {"errors": [f"persist: {exc}"]}
    return {}
