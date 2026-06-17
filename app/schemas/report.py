"""Schema Pydantic del informe de due diligence.

Es el contrato de salida del agente y la forma en que se persiste en memoria.
El LLM genera (vía structured output) las partes analíticas: resumen ejecutivo,
DAFO, sentimiento de noticias y riesgo. Los datos duros vienen de las tools.
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

Sentiment = Literal["positivo", "neutral", "negativo"]


class NewsItem(BaseModel):
    title: str
    url: str | None = None
    published_date: str | None = None
    sentiment: Sentiment = "neutral"
    summary: str | None = Field(default=None, description="Resumen 1 línea de la noticia")


class FinancialSnapshot(BaseModel):
    symbol: str | None = None
    currency: str | None = None
    current_price: float | None = None
    market_cap: float | None = None
    pe_ratio: float | None = None
    forward_pe: float | None = None
    dividend_yield: float | None = None
    beta: float | None = None
    change_12m_pct: float | None = None
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None


class SwotAnalysis(BaseModel):
    fortalezas: list[str] = Field(default_factory=list)
    debilidades: list[str] = Field(default_factory=list)
    oportunidades: list[str] = Field(default_factory=list)
    amenazas: list[str] = Field(default_factory=list)


class RiskIndicators(BaseModel):
    nivel: Literal["bajo", "medio", "alto"] = "medio"
    volatilidad: str | None = Field(default=None, description="Lectura de beta/volatilidad")
    tendencia: str | None = Field(default=None, description="Tendencia 12m")
    alertas: list[str] = Field(default_factory=list)


class DueDiligenceReport(BaseModel):
    company_name: str
    ticker: str | None = None
    sector: str | None = None
    executive_summary: str
    financials: FinancialSnapshot
    news: list[NewsItem] = Field(default_factory=list)
    swot: SwotAnalysis
    risk: RiskIndicators
    sources: list[str] = Field(default_factory=list)
    analysis_date: date = Field(default_factory=date.today)


# --- Sub-schema que el LLM rellena (solo las partes analíticas) ---
# Separamos lo que genera el LLM de los datos duros (tools) para un structured
# output más fiable y barato.
class LLMAnalysis(BaseModel):
    executive_summary: str
    news_sentiment: list[NewsItem]
    swot: SwotAnalysis
    risk: RiskIndicators


# --- Comparativa entre dos empresas (caso de uso "compara A con B") ---
class LLMComparison(BaseModel):
    """Juicio comparativo generado por el LLM a partir de dos informes."""

    resumen: str = Field(description="Comparación global en 3-5 frases")
    diferencias_clave: list[str] = Field(
        default_factory=list, description="Diferencias relevantes (finanzas, riesgo, momentum)"
    )
    ganador_financiero: str | None = Field(
        default=None, description="Empresa con mejor perfil financiero ahora, con motivo"
    )
    recomendacion: str = Field(description="Conclusión accionable para un analista")


class ComparisonReport(BaseModel):
    company_a: str
    company_b: str
    financials_a: FinancialSnapshot
    financials_b: FinancialSnapshot
    comparison: LLMComparison
    sources: list[str] = Field(default_factory=list)
    analysis_date: date = Field(default_factory=date.today)
