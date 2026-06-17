"""Comparativa entre dos empresas (caso de uso "compara A con B").

Estrategia: reutiliza informes de memoria; si una empresa no está analizada,
la analiza al vuelo con el agente. Luego el LLM genera el juicio comparativo.
"""
from __future__ import annotations

import json

from app.agent.graph import run as run_agent
from app.agent.prompts import COMPARISON_SYSTEM, COMPARISON_USER_TEMPLATE
from app.llm.client import get_llm
from app.memory import repository as repo
from app.memory.db import get_session, init_db
from app.schemas.report import (
    ComparisonReport,
    DueDiligenceReport,
    FinancialSnapshot,
    LLMComparison,
)


def _get_or_analyze(company: str) -> DueDiligenceReport:
    """Devuelve el último informe de memoria; si no existe, lo genera."""
    init_db()
    with get_session() as s:
        prev = repo.get_latest_analysis(s, company)
        if prev:
            return DueDiligenceReport(**prev.report)
    # Sin análisis previo -> el agente lo crea (y lo persiste).
    return run_agent(company)


def _digest(report: DueDiligenceReport) -> str:
    """Resumen compacto de un informe para alimentar la comparación."""
    return json.dumps(
        {
            "empresa": report.company_name,
            "sector": report.sector,
            "financials": report.financials.model_dump(),
            "resumen": report.executive_summary,
            "riesgo": report.risk.model_dump(),
            "noticias_titulares": [n.title for n in report.news[:5]],
        },
        ensure_ascii=False,
        indent=2,
        default=str,
    )


def compare(company_a: str, company_b: str) -> ComparisonReport:
    """Compara dos empresas y devuelve un informe comparativo."""
    report_a = _get_or_analyze(company_a)
    report_b = _get_or_analyze(company_b)

    llm = get_llm().with_structured_output(LLMComparison)
    user = COMPARISON_USER_TEMPLATE.format(
        name_a=report_a.company_name,
        report_a=_digest(report_a),
        name_b=report_b.company_name,
        report_b=_digest(report_b),
    )
    comparison: LLMComparison = llm.invoke(
        [("system", COMPARISON_SYSTEM), ("human", user)]
    )

    return ComparisonReport(
        company_a=report_a.company_name,
        company_b=report_b.company_name,
        financials_a=report_a.financials or FinancialSnapshot(),
        financials_b=report_b.financials or FinancialSnapshot(),
        comparison=comparison,
        sources=["Yahoo Finance (yfinance)", "Tavily", "memoria"],
    )
