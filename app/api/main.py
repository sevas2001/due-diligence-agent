"""API REST que expone el agente de due diligence.

Endpoints:
    POST /analyze                      -> ejecuta el agente y devuelve el informe
    GET  /companies?sector=            -> empresas analizadas (memoria)
    GET  /companies/{query}/latest     -> último informe de una empresa
    GET  /companies/{query}/history    -> histórico de informes
    GET  /health
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.agent.compare import compare as compare_companies
from app.agent.graph import run as run_agent
from app.memory import repository as repo
from app.memory.db import get_session, init_db
from app.schemas.report import ComparisonReport, DueDiligenceReport


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # crea tablas al arrancar (dev)
    yield


app = FastAPI(
    title="Due Diligence Agent API",
    version="0.1.0",
    description="Agente IA autónomo de análisis de empresas españolas.",
    lifespan=lifespan,
)


class AnalyzeRequest(BaseModel):
    company: str


class CompanyOut(BaseModel):
    symbol: str
    name: str
    sector: str | None


class CompareRequest(BaseModel):
    company_a: str
    company_b: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze", response_model=DueDiligenceReport)
def analyze(req: AnalyzeRequest) -> DueDiligenceReport:
    if not req.company.strip():
        raise HTTPException(status_code=400, detail="company vacío")
    return run_agent(req.company.strip())


@app.post("/compare", response_model=ComparisonReport)
def compare(req: CompareRequest) -> ComparisonReport:
    a, b = req.company_a.strip(), req.company_b.strip()
    if not a or not b:
        raise HTTPException(status_code=400, detail="company_a y company_b requeridos")
    return compare_companies(a, b)


@app.get("/companies", response_model=list[CompanyOut])
def companies(sector: str | None = None) -> list[CompanyOut]:
    with get_session() as s:
        rows = repo.list_companies(s, sector=sector)
        return [CompanyOut(symbol=c.symbol, name=c.name, sector=c.sector) for c in rows]


@app.get("/companies/{query}/latest", response_model=DueDiligenceReport)
def latest(query: str) -> DueDiligenceReport:
    with get_session() as s:
        a = repo.get_latest_analysis(s, query)
        if a is None:
            raise HTTPException(status_code=404, detail="sin análisis para esa empresa")
        return DueDiligenceReport(**a.report)


@app.get("/companies/{query}/history", response_model=list[DueDiligenceReport])
def history(query: str) -> list[DueDiligenceReport]:
    with get_session() as s:
        rows = repo.get_company_history(s, query)
        return [DueDiligenceReport(**a.report) for a in rows]
