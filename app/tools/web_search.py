"""Tool de búsqueda web en tiempo real vía Tavily.

Devuelve noticias / contexto reciente de la empresa. Requiere TAVILY_API_KEY.
"""
from __future__ import annotations

from functools import lru_cache

from tavily import TavilyClient

from app.config import settings


@lru_cache
def _client() -> TavilyClient:
    if not settings.tavily_api_key:
        raise RuntimeError("TAVILY_API_KEY vacía. Rellena tu key de Tavily en .env.")
    return TavilyClient(api_key=settings.tavily_api_key)


def search_news(company: str, max_results: int = 8) -> list[dict]:
    """Busca noticias recientes de la empresa.

    Devuelve lista de {title, url, content, published_date, score}.
    """
    query = f"noticias recientes {company} empresa resultados financieros"
    resp = _client().search(
        query=query,
        search_depth="advanced",
        topic="news",
        max_results=max_results,
        days=180,
    )
    results = resp.get("results", [])
    return [
        {
            "title": r.get("title"),
            "url": r.get("url"),
            "content": r.get("content"),
            "published_date": r.get("published_date"),
            "score": r.get("score"),
        }
        for r in results
    ]
