
from sqlalchemy import (
    Integer,
    ForeignKey,
    Numeric,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    carat_id: Mapped[int] = mapped_column(
        ForeignKey("carats.id"), nullable=False
    )

    color_id: Mapped[int] = mapped_column(
        ForeignKey("colors.id"), nullable=False
    )

    size_id: Mapped[int] = mapped_column(
        ForeignKey("sizes.id"), nullable=False
    )

    style_id: Mapped[int] = mapped_column(
        ForeignKey("styles.id"), nullable=False
    )

    weight: Mapped[float] = mapped_column(
        Numeric(12, 3), nullable=False
    )

    product = relationship(
        "Product",
        back_populates="variants"
    )

    carat = relationship("Carat")
    color = relationship("Color")
    size = relationship("Size")
    style = relationship("Style")

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "carat_id",
            "color_id",
            "size_id",
            "style_id",
            name="uq_product_variant_combination"
        ),
    )
