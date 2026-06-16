"""Smoke test de la memoria persistente.

Corre contra el DATABASE_URL configurado. Para probar sin Postgres:
    set DATABASE_URL=sqlite:///./test_memory.db   (Windows)
    python scripts/test_memory.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.memory.db import get_session, init_db  # noqa: E402
from app.memory import repository as repo  # noqa: E402
from app.schemas.report import (  # noqa: E402
    DueDiligenceReport,
    FinancialSnapshot,
    NewsItem,
    RiskIndicators,
    SwotAnalysis,
)


def _sample(name: str, ticker: str, sector: str, price: float) -> DueDiligenceReport:
    return DueDiligenceReport(
        company_name=name,
        ticker=ticker,
        sector=sector,
        executive_summary=f"{name}: empresa del sector {sector}.",
        financials=FinancialSnapshot(symbol=ticker, currency="EUR", current_price=price),
        news=[NewsItem(title="Noticia demo", sentiment="positivo")],
        swot=SwotAnalysis(fortalezas=["Líder de mercado"], amenazas=["Regulación"]),
        risk=RiskIndicators(nivel="medio", tendencia="alcista"),
        sources=["yfinance", "tavily"],
    )


def main() -> int:
    print(f"Backend: {settings.database_url}\n")
    init_db()

    with get_session() as s:
        repo.save_report(s, _sample("Iberdrola", "IBE.MC", "Utilities", 20.53))
        repo.save_report(s, _sample("Endesa", "ELE.MC", "Utilities", 24.10))

    with get_session() as s:
        latest = repo.get_latest_analysis(s, "Iberdrola")
        print("get_latest('Iberdrola') ->", latest.report["company_name"],
              "| precio", latest.report["financials"]["current_price"])

        companies = repo.list_companies(s, sector="Utilities")
        print("list_companies(sector=Utilities) ->", [c.name for c in companies])

        hist = repo.get_company_history(s, "Endesa")
        print("history('Endesa') -> analisis:", len(hist))

    print("\nOK - memoria persistente funcionando.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
