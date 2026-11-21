
from decimal import Decimal

from sqlalchemy import (
    Integer,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    CheckConstraint
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.database.base import Base


class ProductVariant(Base):

    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Variant attributes

    carat_id: Mapped[int | None] = mapped_column(
        ForeignKey("carats.id"),
        nullable=True
    )

    color_id: Mapped[int | None] = mapped_column(
        ForeignKey("colors.id"),
        nullable=True
    )

    size_id: Mapped[int | None] = mapped_column(
        ForeignKey("sizes.id"),
        nullable=True
    )

    style_id: Mapped[int | None] = mapped_column(
        ForeignKey("styles.id"),
        nullable=True
    )

    # Weight details

    gross_weight: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False
    )

    net_weight: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False
    )

    # Relationships

    product = relationship(
        "Product",
        back_populates="variants"
    )

    carat = relationship("Carat")
    color = relationship("Color")
    size = relationship("Size")
    style = relationship("Style")

    # Database constraints

    __table_args__ = (

        UniqueConstraint(
            "product_id",
            "carat_id",
            "color_id",
            "size_id",
            "style_id",
            name="uq_product_variant_combination",
            postgresql_nulls_not_distinct=True
        ),

        CheckConstraint(
            "gross_weight > 0 AND "
            "net_weight > 0 AND "
            "gross_weight >= net_weight",
            name="chk_variant_weights"
        ),
    )
