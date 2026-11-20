
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Numeric,
    ARRAY,
    Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    # Product identification
    product_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    # Master references
    metal_id: Mapped[int] = mapped_column(
        ForeignKey("metals.id"), nullable=False
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )

    product_type_id: Mapped[int] = mapped_column(
        ForeignKey("product_types.id"), nullable=False
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )

    subcategory_id: Mapped[int] = mapped_column(
        ForeignKey("subcategories.id"), nullable=False
    )

    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collections.id"), nullable=False
    )

    subcollection_id: Mapped[int] = mapped_column(
        ForeignKey("subcollections.id"), nullable=False
    )

    gender_id: Mapped[int] = mapped_column(
        ForeignKey("genders.id"), nullable=False
    )

    uom_id: Mapped[int] = mapped_column(
        ForeignKey("uoms.id"), nullable=False
    )

    # Default attributes
    default_carat_id: Mapped[int] = mapped_column(
        ForeignKey("carats.id"), nullable=False
    )

    default_color_id: Mapped[int] = mapped_column(
        ForeignKey("colors.id"), nullable=False
    )

    default_size_id: Mapped[int] = mapped_column(
        ForeignKey("sizes.id"), nullable=False
    )

    default_style_id: Mapped[int] = mapped_column(
        ForeignKey("styles.id"), nullable=False
    )

    # Weight and wastage
    default_weight: Mapped[float] = mapped_column(
        Numeric(12, 3), nullable=False
    )

    wastage: Mapped[float] = mapped_column(
        Numeric(8, 3), default=0, nullable=False
    )

    # Keywords
    keywords: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Relationships
    variants = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    metal = relationship("Metal")
    project = relationship("Project")
    product_type = relationship("ProductType")
    category = relationship("Category")
    subcategory = relationship("Subcategory")
    collection = relationship("Collection")
    subcollection = relationship("Subcollection")
    gender = relationship("Gender")
    uom = relationship("UOM")

    default_carat = relationship(
        "Carat", foreign_keys=[default_carat_id]
    )
    default_color = relationship(
        "Color", foreign_keys=[default_color_id]
    )
    default_size = relationship(
        "Size", foreign_keys=[default_size_id]
    )
    default_style = relationship(
        "Style", foreign_keys=[default_style_id]
    )
