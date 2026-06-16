"""Tool de datos financieros vía Yahoo Finance (yfinance).

Dos pasos:
1. Resolver nombre de empresa -> ticker (búsqueda Yahoo). Empresas españolas
   cotizan con sufijo `.MC` (Madrid), ej. Iberdrola -> IBE.MC.
2. Obtener datos financieros del ticker.
"""
from __future__ import annotations

import requests
import yfinance as yf

_YAHOO_SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DueDiligenceAgent/0.1)"}


def resolve_ticker(name: str) -> dict | None:
    """Resuelve un nombre de empresa al mejor ticker de Yahoo Finance.

    Devuelve {symbol, name, exchange} o None si no hay resultado.
    """
    try:
        resp = requests.get(
            _YAHOO_SEARCH_URL,
            params={"q": name, "quotesCount": 6, "newsCount": 0},
            headers=_HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        quotes = resp.json().get("quotes", [])
    except (requests.RequestException, ValueError):
        return None

    equities = [q for q in quotes if q.get("quoteType") == "EQUITY" and q.get("symbol")]
    if not equities:
        return None

    # Preferir bolsa de Madrid (.MC) para empresas españolas.
    preferred = next((q for q in equities if q["symbol"].endswith(".MC")), equities[0])
    return {
        "symbol": preferred["symbol"],
        "name": preferred.get("shortname") or preferred.get("longname") or name,
        "exchange": preferred.get("exchDisp", ""),
    }


def get_financials(name_or_ticker: str) -> dict:
    """Datos financieros estructurados para una empresa.

    Acepta nombre ("Iberdrola") o ticker directo ("IBE.MC"). Devuelve dict con
    métricas clave + variación 12 meses. Campos faltantes quedan en None.
    """
    resolved = resolve_ticker(name_or_ticker)
    symbol = resolved["symbol"] if resolved else name_or_ticker

    ticker = yf.Ticker(symbol)
    info = getattr(ticker, "info", {}) or {}

    # Variación 12 meses desde el histórico (más fiable que campos sueltos).
    change_12m_pct = None
    try:
        hist = ticker.history(period="1y")
        if not hist.empty:
            first, last = hist["Close"].iloc[0], hist["Close"].iloc[-1]
            if first:
                change_12m_pct = round((last - first) / first * 100, 2)
    except Exception:  # noqa: BLE001
        pass

    return {
        "symbol": symbol,
        "company_name": info.get("longName") or (resolved or {}).get("name"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "currency": info.get("currency"),
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "dividend_yield": info.get("dividendYield"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "beta": info.get("beta"),
        "change_12m_pct": change_12m_pct,
        "website": info.get("website"),
        "long_business_summary": info.get("longBusinessSummary"),
    }
