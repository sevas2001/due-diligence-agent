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


def _financials_metrics(f: dict) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Precio", _fmt(f.get("current_price"), f" {f.get('currency') or ''}"))
    c2.metric("Cap. mercado", _fmt(f.get("market_cap")))
    c3.metric("P/E", _fmt(f.get("pe_ratio")))
    c4.metric("Var. 12m", _fmt(f.get("change_12m_pct"), " %"))


def render_report(rep: dict) -> None:
    """Renderiza un informe de due diligence completo."""
    st.subheader(f"{rep['company_name']}  ·  {rep.get('ticker') or ''}")
    st.caption(f"Sector: {rep.get('sector') or '—'} · Fecha: {rep['analysis_date']}")

    st.markdown("### Resumen ejecutivo")
    st.write(rep["executive_summary"])

    st.markdown("### Situación financiera")
    _financials_metrics(rep["financials"])

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
    with d1:
        st.markdown("**Fortalezas**")
        st.write(sw["fortalezas"])
        st.markdown("**Oportunidades**")
        st.write(sw["oportunidades"])
    with d2:
        st.markdown("**Debilidades**")
        st.write(sw["debilidades"])
        st.markdown("**Amenazas**")
        st.write(sw["amenazas"])

    rk = rep["risk"]
    st.markdown("### Indicadores de riesgo")
    color = {"bajo": "🟢", "medio": "🟡", "alto": "🔴"}.get(rk["nivel"], "⚪")
    st.write(f"{color} Nivel: **{rk['nivel']}** · Tendencia: {rk.get('tendencia') or '—'}")
    for a in rk.get("alertas", []):
        st.write(f"- ⚠️ {a}")

    st.caption(f"Fuentes: {', '.join(rep.get('sources', []))}")


# --- Sidebar: consulta de memoria ---
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


tab_analizar, tab_comparar = st.tabs(["🔍 Analizar", "⚖️ Comparar"])

# --- Pestaña: Analizar una empresa ---
with tab_analizar:
    company = st.text_input("Nombre de la empresa", placeholder="Ej: Iberdrola")
    if st.button("Analizar", type="primary") and company.strip():
        with st.spinner(f"Analizando {company}… (web + finanzas + LLM)"):
            try:
                r = requests.post(
                    f"{API_URL}/analyze", json={"company": company}, timeout=180
                )
                r.raise_for_status()
                render_report(r.json())
            except requests.RequestException as e:
                st.error(f"Error: {e}")

# --- Pestaña: Comparar dos empresas ---
with tab_comparar:
    col_a, col_b = st.columns(2)
    company_a = col_a.text_input("Empresa A", placeholder="Ej: Iberdrola")
    company_b = col_b.text_input("Empresa B", placeholder="Ej: Endesa")
    if st.button("Comparar", type="primary") and company_a.strip() and company_b.strip():
        with st.spinner(f"Comparando {company_a} vs {company_b}… (puede tardar)"):
            try:
                r = requests.post(
                    f"{API_URL}/compare",
                    json={"company_a": company_a, "company_b": company_b},
                    timeout=300,
                )
                r.raise_for_status()
                rep = r.json()
            except requests.RequestException as e:
                st.error(f"Error: {e}")
                st.stop()

        cmp = rep["comparison"]
        st.subheader(f"{rep['company_a']}  ⚖️  {rep['company_b']}")

        st.markdown("### Resumen comparativo")
        st.write(cmp["resumen"])

        ca, cb = st.columns(2)
        with ca:
            st.markdown(f"**{rep['company_a']}**")
            _financials_metrics(rep["financials_a"])
        with cb:
            st.markdown(f"**{rep['company_b']}**")
            _financials_metrics(rep["financials_b"])

        st.markdown("### Diferencias clave")
        for d in cmp.get("diferencias_clave", []):
            st.write(f"- {d}")

        if cmp.get("ganador_financiero"):
            st.success(f"🏆 Mejor perfil financiero ahora: **{cmp['ganador_financiero']}**")

        st.markdown("### Recomendación")
        st.info(cmp["recomendacion"])

        st.caption(f"Fuentes: {', '.join(rep.get('sources', []))}")
