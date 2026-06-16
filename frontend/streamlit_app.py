"""Frontend Streamlit del agente de due diligence.

Habla con la API FastAPI. Arranca la API primero:
    uvicorn app.api.main:app --reload
    streamlit run frontend/streamlit_app.py
"""
from __future__ import annotations

import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Due Diligence Agent", page_icon="📊", layout="wide")
st.title("📊 Due Diligence Agent")
st.caption("Análisis autónomo de empresas españolas · LangGraph + LLM + memoria")


def _fmt(v, suffix=""):
    return f"{v:,}{suffix}" if isinstance(v, (int, float)) else "—"


with st.sidebar:
    st.header("Memoria")
    sector = st.text_input("Filtrar por sector", "")
    if st.button("Ver empresas analizadas"):
        try:
            params = {"sector": sector} if sector else {}
            r = requests.get(f"{API_URL}/companies", params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
            st.write(f"{len(data)} empresas") if data else st.info("Memoria vacía")
            for c in data:
                st.write(f"- **{c['name']}** ({c['symbol']}) · {c.get('sector') or '—'}")
        except requests.RequestException as e:
            st.error(f"API no disponible: {e}")

company = st.text_input("Nombre de la empresa", placeholder="Ej: Iberdrola")
go = st.button("Analizar", type="primary")

if go and company.strip():
    with st.spinner(f"Analizando {company}… (búsqueda web + finanzas + LLM)"):
        try:
            r = requests.post(f"{API_URL}/analyze", json={"company": company}, timeout=180)
            r.raise_for_status()
            rep = r.json()
        except requests.RequestException as e:
            st.error(f"Error: {e}")
            st.stop()

    st.subheader(f"{rep['company_name']}  ·  {rep.get('ticker') or ''}")
    st.caption(f"Sector: {rep.get('sector') or '—'} · Fecha: {rep['analysis_date']}")

    st.markdown("### Resumen ejecutivo")
    st.write(rep["executive_summary"])

    f = rep["financials"]
    st.markdown("### Situación financiera")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Precio", _fmt(f.get("current_price"), f" {f.get('currency') or ''}"))
    c2.metric("Cap. mercado", _fmt(f.get("market_cap")))
    c3.metric("P/E", _fmt(f.get("pe_ratio")))
    c4.metric("Var. 12m", _fmt(f.get("change_12m_pct"), " %"))

    st.markdown("### Noticias recientes")
    for n in rep.get("news", []):
        emoji = {"positivo": "🟢", "negativo": "🔴"}.get(n["sentiment"], "⚪")
        line = f"{emoji} **{n['title']}**"
        if n.get("url"):
            line += f" — [fuente]({n['url']})"
        st.markdown(line)
        if n.get("summary"):
            st.caption(n["summary"])

    st.markdown("### Análisis DAFO")
    sw = rep["swot"]
    d1, d2 = st.columns(2)
    d1.markdown("**Fortalezas**");  d1.write(sw["fortalezas"])
    d1.markdown("**Oportunidades**"); d1.write(sw["oportunidades"])
    d2.markdown("**Debilidades**"); d2.write(sw["debilidades"])
    d2.markdown("**Amenazas**");   d2.write(sw["amenazas"])

    rk = rep["risk"]
    st.markdown("### Indicadores de riesgo")
    color = {"bajo": "🟢", "medio": "🟡", "alto": "🔴"}.get(rk["nivel"], "⚪")
    st.write(f"{color} Nivel: **{rk['nivel']}** · Tendencia: {rk.get('tendencia') or '—'}")
    for a in rk.get("alertas", []):
        st.write(f"- ⚠️ {a}")

    st.caption(f"Fuentes: {', '.join(rep.get('sources', []))}")
