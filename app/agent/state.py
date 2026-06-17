"""Estado compartido del grafo del agente.

Cada nodo lee y escribe sobre este estado. LangGraph lo pasa entre nodos.
"""
from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from app.schemas.report import DueDiligenceReport, LLMAnalysis


class AgentState(TypedDict, total=False):
    # Entrada
    company_query: str

    # Datos recopilados por las tools
    financials: dict
    news: list[dict]
    corporate_text: str  # texto scrapeado de la web corporativa
    prior_summary: str | None  # contexto de análisis previo (memoria)

    # Salida del LLM y informe final
    llm_analysis: LLMAnalysis
    report: DueDiligenceReport

    # Diagnóstico (reducer: acumula errores de todos los nodos)
    errors: Annotated[list[str], operator.add]
