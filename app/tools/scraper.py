"""Tool de scraping ligero vía requests + BeautifulSoup.

Extrae texto limpio de una web corporativa o registro público. Best-effort:
ante fallo devuelve cadena vacía en vez de romper el agente.
"""
from __future__ import annotations

import requests
from bs4 import BeautifulSoup

# UA de navegador real: muchas webs corporativas devuelven 403 a UAs de bot.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}


def fetch_text(url: str, max_chars: int = 5000) -> str:
    """Descarga una URL y devuelve su texto visible, truncado a `max_chars`."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException:
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    text = " ".join(soup.get_text(separator=" ").split())
    return text[:max_chars]
