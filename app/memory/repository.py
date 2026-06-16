"""Repositorio: única puerta de acceso a la memoria persistente.

El agente no toca el ORM directamente; usa estas funciones.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.memory.models import Analysis, Company
from app.schemas.report import DueDiligenceReport


def get_or_create_company(
    session: Session, symbol: str, name: str, sector: str | None
) -> Company:
    """Devuelve la empresa por symbol; la crea si no existe. Actualiza sector/nombre."""
    company = session.scalar(select(Company).where(Company.symbol == symbol))
    if company is None:
        company = Company(symbol=symbol, name=name, sector=sector)
        session.add(company)
        session.flush()  # asigna id sin cerrar la transacción
    else:
        company.name = name or company.name
        company.sector = sector or company.sector
    return company


def save_report(session: Session, report: DueDiligenceReport) -> Analysis:
    """Persiste un informe completo como nuevo Analysis ligado a su Company."""
    symbol = report.ticker or report.company_name
    company = get_or_create_company(session, symbol, report.company_name, report.sector)
    analysis = Analysis(company_id=company.id, report=report.model_dump(mode="json"))
    session.add(analysis)
    session.flush()
    return analysis


def get_latest_analysis(session: Session, company_query: str) -> Analysis | None:
    """Último análisis de una empresa, buscando por symbol o nombre (parcial)."""
    stmt = (
        select(Analysis)
        .join(Company)
        .where(
            (Company.symbol == company_query)
            | (Company.name.ilike(f"%{company_query}%"))
        )
        .order_by(Analysis.created_at.desc())
        .limit(1)
    )
    return session.scalar(stmt)


def get_company_history(session: Session, company_query: str) -> list[Analysis]:
    """Histórico completo de análisis de una empresa (más reciente primero)."""
    stmt = (
        select(Analysis)
        .join(Company)
        .where(
            (Company.symbol == company_query)
            | (Company.name.ilike(f"%{company_query}%"))
        )
        .order_by(Analysis.created_at.desc())
    )
    return list(session.scalars(stmt))


def list_companies(session: Session, sector: str | None = None) -> list[Company]:
    """Lista empresas analizadas, opcionalmente filtradas por sector (parcial)."""
    stmt = select(Company).order_by(Company.name)
    if sector:
        stmt = stmt.where(Company.sector.ilike(f"%{sector}%"))
    return list(session.scalars(stmt))
