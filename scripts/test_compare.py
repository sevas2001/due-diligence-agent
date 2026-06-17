"""Smoke test de comparativa.

    set DATABASE_URL=sqlite:///./test_compare.db
    python scripts/test_compare.py "Iberdrola" "Endesa"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agent.compare import compare  # noqa: E402


def main() -> int:
    a = sys.argv[1] if len(sys.argv) > 1 else "Iberdrola"
    b = sys.argv[2] if len(sys.argv) > 2 else "Endesa"
    print(f"Comparando: {a} vs {b}\n" + "=" * 60)
    rep = compare(a, b)

    fa, fb = rep.financials_a, rep.financials_b
    print(f"\n{rep.company_a}: precio={fa.current_price} PE={fa.pe_ratio} var12m={fa.change_12m_pct}%")
    print(f"{rep.company_b}: precio={fb.current_price} PE={fb.pe_ratio} var12m={fb.change_12m_pct}%")
    c = rep.comparison
    print(f"\nRESUMEN:\n{c.resumen}")
    print("\nDIFERENCIAS CLAVE:")
    for d in c.diferencias_clave:
        print(f"  - {d}")
    print(f"\nGANADOR FINANCIERO: {c.ganador_financiero}")
    print(f"\nRECOMENDACION:\n{c.recomendacion}")
    print("\nOK - comparativa funcionando.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
