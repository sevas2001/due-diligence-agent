"""Smoke test end-to-end del agente.

    set DATABASE_URL=sqlite:///./test_agent.db
    python scripts/test_agent.py "Iberdrola"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agent.graph import run  # noqa: E402


def main() -> int:
    company = sys.argv[1] if len(sys.argv) > 1 else "Iberdrola"
    print(f"Analizando: {company}\n" + "=" * 60)
    report = run(company)

    print(f"\nEMPRESA: {report.company_name} ({report.ticker}) | {report.sector}")
    print(f"\nRESUMEN EJECUTIVO:\n{report.executive_summary}")
    f = report.financials
    print(f"\nFINANZAS: precio={f.current_price}{f.currency} cap={f.market_cap} "
          f"PE={f.pe_ratio} var12m={f.change_12m_pct}%")
    print(f"\nNOTICIAS ({len(report.news)}):")
    for n in report.news[:5]:
        print(f"  [{n.sentiment}] {n.title}")
    print(f"\nDAFO:\n  F: {report.swot.fortalezas}\n  D: {report.swot.debilidades}"
          f"\n  O: {report.swot.oportunidades}\n  A: {report.swot.amenazas}")
    print(f"\nRIESGO: {report.risk.nivel} | {report.risk.tendencia}")
    print(f"  alertas: {report.risk.alertas}")
    print(f"\nFUENTES: {report.sources} | fecha: {report.analysis_date}")
    print("\nOK - agente end-to-end funcionando.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
