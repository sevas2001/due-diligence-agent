"""Grafo del agente (LangGraph).

Flujo:
    check_memory -> fetch_finance -> fetch_news -> analyze -> assemble -> persist

check_memory recupera contexto previo; las tools recopilan datos; el LLM analiza;
assemble construye el informe; persist lo guarda en memoria.
"""
from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.agent import nodes
from app.agent.state import AgentState
from app.schemas.report import DueDiligenceReport


@lru_cache
def build_graph():
    """Compila el grafo una vez (cacheado)."""
    g = StateGraph(AgentState)

    g.add_node("check_memory", nodes.check_memory)
    g.add_node("fetch_finance", nodes.fetch_finance)
    g.add_node("fetch_news", nodes.fetch_news)
    g.add_node("analyze", nodes.analyze)
    g.add_node("assemble", nodes.assemble)
    g.add_node("persist", nodes.persist)

    g.add_edge(START, "check_memory")
    g.add_edge("check_memory", "fetch_finance")
    g.add_edge("fetch_finance", "fetch_news")
    g.add_edge("fetch_news", "analyze")
    g.add_edge("analyze", "assemble")
    g.add_edge("assemble", "persist")
    g.add_edge("persist", END)

    return g.compile()


def run(company: str) -> DueDiligenceReport:
    """Ejecuta el agente para una empresa y devuelve el informe."""
    graph = build_graph()
    final = graph.invoke({"company_query": company, "errors": []})
    if errs := final.get("errors"):
        # No abortamos: informe puede ser parcial. Solo dejamos traza.
        print(f"[agente] avisos: {errs}")
    return final["report"]
