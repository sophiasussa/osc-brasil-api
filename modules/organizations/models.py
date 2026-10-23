from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base import Base


organization_areas = Table(
    "organization_areas",
    Base.metadata,
    Column(
        "organization_id",
        BigInteger,
        ForeignKey("organizations.id"),
        primary_key=True,
    ),
    Column(
        "area_id",
        Integer,
        ForeignKey("activity_areas.id"),
        primary_key=True,
    ),
)


organization_subareas = Table(
    "organization_subareas",
    Base.metadata,
    Column(
        "organization_id",
        BigInteger,
        ForeignKey("organizations.id"),
        primary_key=True,
    ),
    Column(
        "subarea_id",
        Integer,
        ForeignKey("activity_subareas.id"),
        primary_key=True,
    ),
)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cnpj: Mapped[str | None] = mapped_column(String(14), nullable=True)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    trade_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    legal_nature_code: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("legal_natures.code"),
        nullable=True,
    )
    
    matrix_or_branch: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    registration_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    removed_from_mosc: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    foundation_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    closing_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    closing_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    municipality_code: Mapped[str | None] = mapped_column(
        String(10),
        ForeignKey("municipalities.code"),
        nullable=True,
    )

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    municipality: Mapped["Municipality | None"] = relationship(
        back_populates="organizations",
    )

    areas: Mapped[list["ActivityArea"]] = relationship(
        secondary=organization_areas,
        back_populates="organizations",
    )

    subareas: Mapped[list["ActivitySubarea"]] = relationship(
        secondary=organization_subareas,
        back_populates="organizations",
    )

    legal_nature: Mapped["LegalNature | None"] = relationship(
        back_populates="organizations",
    )

    cnaes: Mapped[list["OrganizationCnae"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )


class ActivityArea(Base):
    __tablename__ = "activity_areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    organizations: Mapped[list["Organization"]] = relationship(
        secondary=organization_areas,
        back_populates="areas",
    )

    subareas: Mapped[list["ActivitySubarea"]] = relationship(
        back_populates="area",
    )


class ActivitySubarea(Base):
    __tablename__ = "activity_subareas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    area_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("activity_areas.id"),
        nullable=True,
    )

    area: Mapped["ActivityArea | None"] = relationship(
        back_populates="subareas",
    )

    organizations: Mapped[list["Organization"]] = relationship(
        secondary=organization_subareas,
        back_populates="subareas",
    )


class Municipality(Base):
    __tablename__ = "municipalities"

    code: Mapped[str] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    state_code: Mapped[str | None] = mapped_column(
        "uf",
        String(2),
        nullable=True,
    )

    organizations: Mapped[list["Organization"]] = relationship(
        back_populates="municipality",
    )


class LegalNature(Base):
    __tablename__ = "legal_natures"

    code: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(
        "name",
        String(255),
        nullable=False,
    )

    organizations: Mapped[list["Organization"]] = relationship(
        back_populates="legal_nature",
    )

class Cnae(Base):
    __tablename__ = "cnaes"

    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    organizations: Mapped[list["OrganizationCnae"]] = relationship(
        back_populates="cnae",
    )


class OrganizationCnae(Base):
    __tablename__ = "organization_cnaes"

    organization_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )

    cnae_code: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("cnaes.code", ondelete="RESTRICT"),
        primary_key=True,
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    organization: Mapped["Organization"] = relationship(
        back_populates="cnaes",
    )

    cnae: Mapped["Cnae"] = relationship(
        back_populates="organizations",
    )
