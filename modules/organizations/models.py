from datetime import date

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base import Base


organization_areas = Table(
    "organization_areas",
    Base.metadata,
    Column(
        "organization_id",
        BigInteger,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "area_id",
        BigInteger,
        ForeignKey("activity_areas.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)

organization_subareas = Table(
    "organization_subareas",
    Base.metadata,
    Column(
        "organization_id",
        BigInteger,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "subarea_id",
        BigInteger,
        ForeignKey("activity_subareas.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    cnpj: Mapped[str] = mapped_column(
        String(14), unique=True, nullable=False
    )
    legal_name: Mapped[str | None] = mapped_column(String, nullable=True)
    trade_name: Mapped[str | None] = mapped_column(String, nullable=True)
    legal_nature_code: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    matrix_or_branch: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    registration_status: Mapped[str] = mapped_column(
        String, nullable=False
    )
    removed_from_mosc: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )
    foundation_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    closing_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    closing_year: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    municipality_code: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    latitude: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    longitude: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    areas: Mapped[list["ActivityArea"]] = relationship(
        secondary=organization_areas,
        back_populates="organizations",
        order_by="ActivityArea.name",
    )

    subareas: Mapped[list["ActivitySubarea"]] = relationship(
        secondary=organization_subareas,
        back_populates="organizations",
        order_by="ActivitySubarea.name",
    )


class ActivityArea(Base):
    __tablename__ = "activity_areas"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(
        String(150), unique=True, nullable=False
    )

    organizations: Mapped[list["Organization"]] = relationship(
        secondary=organization_areas,
        back_populates="areas",
    )

    subareas: Mapped[list["ActivitySubarea"]] = relationship(
        back_populates="area",
        order_by="ActivitySubarea.name",
    )


class ActivitySubarea(Base):
    __tablename__ = "activity_subareas"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    area_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("activity_areas.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(200), nullable=False
    )

    area: Mapped["ActivityArea"] = relationship(
        back_populates="subareas"
    )

    organizations: Mapped[list["Organization"]] = relationship(
        secondary=organization_subareas,
        back_populates="subareas",
    )
