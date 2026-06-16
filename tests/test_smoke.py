"""Tests CI-safe: sin red, sin keys, sin LLM. Solo schema + memoria (SQLite).

CI fija DATABASE_URL a un SQLite temporal antes de importar la app.
"""
from app.memory import repository as repo
from app.memory.db import get_session, init_db
from app.schemas.report import (
    DueDiligenceReport,
    FinancialSnapshot,
    NewsItem,
    RiskIndicators,
    SwotAnalysis,
)


def _report(name: str, ticker: str, sector: str) -> DueDiligenceReport:
    return DueDiligenceReport(
        company_name=name,
        ticker=ticker,
        sector=sector,
        executive_summary="resumen de prueba",
        financials=FinancialSnapshot(symbol=ticker, current_price=10.0),
        news=[NewsItem(title="n", sentiment="positivo")],
        swot=SwotAnalysis(fortalezas=["f"]),
        risk=RiskIndicators(nivel="bajo"),
        sources=["test"],
    )


def test_report_schema_roundtrip():
    rep = _report("Acme", "ACM.MC", "Tech")
    dumped = rep.model_dump(mode="json")
    restored = DueDiligenceReport(**dumped)
    assert restored.company_name == "Acme"
    assert restored.news[0].sentiment == "positivo"


def test_memory_save_and_query():
    init_db()
    with get_session() as s:
        repo.save_report(s, _report("Iberdrola", "IBE.MC", "Utilities"))
        repo.save_report(s, _report("Endesa", "ELE.MC", "Utilities"))

    with get_session() as s:
        latest = repo.get_latest_analysis(s, "Iberdrola")
        assert latest is not None
        assert latest.report["company_name"] == "Iberdrola"

        utilities = repo.list_companies(s, sector="Utilities")
        assert {c.name for c in utilities} == {"Iberdrola", "Endesa"}
