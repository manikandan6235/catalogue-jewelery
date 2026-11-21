
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CategoryAttributeConfig(Base):

    __tablename__ = "category_attribute_config"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False
    )

    attribute_name: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Product default configuration

    product_default_applicable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    product_default_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Variant configuration

    variant_applicable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    variant_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    __table_args__ = (

        UniqueConstraint(
            "category_id",
            "attribute_name",
            name="uq_category_attribute"
        ),

        CheckConstraint(
            "attribute_name IN "
            "('CARAT', 'COLOR', 'SIZE', 'STYLE')",
            name="chk_category_attribute_name"
        ),

        CheckConstraint(
            "NOT product_default_required "
            "OR product_default_applicable",
            name="chk_product_default_required"
        ),

        CheckConstraint(
            "NOT variant_required OR variant_applicable",
            name="chk_variant_required"
        ),
    )
