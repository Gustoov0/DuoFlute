from typing import Any, Optional

from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Note(Base):
    """Nota musical da flauta doce soprano em dó.

    scientific_name: nota ESCRITA na partitura (ex.: B4).
    frequency_hz: frequência do som REAL. A flauta soprano soa uma oitava acima
    do que se escreve, então o Si escrito (B4) soa como B5 (~987,77 Hz).
    """

    __tablename__ = "notes"
    __table_args__ = (UniqueConstraint("name_pt", name="uq_notes_name_pt"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    introduced_in_unit_id: Mapped[int | None] = mapped_column(
        ForeignKey("units.id", ondelete="SET NULL")
    )
    name_pt: Mapped[str] = mapped_column(String(50))
    scientific_name: Mapped[str] = mapped_column(String(10))
    frequency_hz: Mapped[float] = mapped_column(Float)
    # Posição na pauta (clave de sol): 0 = 1ª linha (Mi), 1 = Fá, 2 = Sol, 3 = Lá, 4 = Si...
    staff_position: Mapped[int]

    fingering: Mapped[Optional["Fingering"]] = relationship(
        back_populates="note", uselist=False, cascade="all, delete-orphan"
    )


class Fingering(Base):
    """Digitação de uma nota na flauta doce soprano barroca.

    holes é um JSON com as chaves thumb, h1 ... h7.
    Valores: 0 = aberto, 1 = fechado, 2 = meio furo.
    """

    __tablename__ = "fingerings"
    __table_args__ = (UniqueConstraint("note_id", name="uq_fingerings_note_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id", ondelete="CASCADE"))
    holes: Mapped[dict[str, Any]] = mapped_column(JSONB)

    note: Mapped["Note"] = relationship(back_populates="fingering")