"""Modelos ORM (SQLAlchemy 2.0) de la memoria persistente.

Dos tablas:
- companies: una fila por empresa analizada (dedupe por symbol).
- analyses: histórico de informes; cada análisis guarda el informe completo en
  JSON + timestamp, para comparativas y consultas posteriores.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    sector: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="company", cascade="all, delete-orphan", order_by="Analysis.created_at.desc()"
    )


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    report: Mapped[dict] = mapped_column(JSON)  # DueDiligenceReport serializado
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    company: Mapped["Company"] = relationship(back_populates="analyses")
