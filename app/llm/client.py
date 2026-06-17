"""Capa LLM agnóstica.

Todo va vía OpenRouter (endpoint OpenAI-compatible). Cambiar de modelo = cambiar
`LLM_MODEL` en `.env`, sin tocar código. Usamos `ChatOpenAI` de langchain-openai
porque LangGraph se integra de forma nativa con los chat models de LangChain.
"""
from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.config import settings

# Headers recomendados por OpenRouter para atribución (opcionales).
_OPENROUTER_HEADERS = {
    "HTTP-Referer": "https://github.com/sevas/due-diligence-agent",
    "X-Title": "Due Diligence Agent",
}


@lru_cache
def get_llm(model: str | None = None, temperature: float | None = None) -> ChatOpenAI:
    """Devuelve un chat model configurado contra OpenRouter.

    Args:
        model: override del modelo (por defecto `settings.llm_model`).
        temperature: override de temperatura (por defecto `settings.llm_temperature`).

    Cacheado por (model, temperature) para reutilizar conexiones.
    """
    if not settings.llm_api_key:
        raise RuntimeError(
            "LLM_API_KEY vacía. Rellena tu key de OpenRouter en .env "
            "(copia .env.example a .env)."
        )

    return ChatOpenAI(
        model=model or settings.llm_model,
        temperature=temperature if temperature is not None else settings.llm_temperature,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        default_headers=_OPENROUTER_HEADERS,
        # Margen alto de salida: structured output del informe es grande; con un
        # límite bajo el JSON se trunca y falla el parseo (EOF while parsing).
        max_tokens=4096,
        timeout=90,
        max_retries=2,
    )


def healthcheck() -> str:
    """Llamada mínima para verificar que la key + modelo + endpoint funcionan."""
    llm = get_llm()
    resp = llm.invoke("Responde solo con la palabra: OK")
    return resp.content
