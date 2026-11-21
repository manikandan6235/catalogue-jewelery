
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    ARRAY,
    Boolean,
    UniqueConstraint,
    CheckConstraint
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.database.base import Base


class Product(Base):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    # Product identification
    product_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    # Master references
    metal_id: Mapped[int] = mapped_column(
        ForeignKey("metals.id"),
        nullable=False
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False
    )

    product_type_id: Mapped[int] = mapped_column(
        ForeignKey("product_types.id"),
        nullable=False
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False
    )

    subcategory_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collections.id"),
        nullable=False
    )

    subcollection_id: Mapped[int] = mapped_column(
        ForeignKey("subcollections.id"),
        nullable=False
    )

    gender_id: Mapped[int] = mapped_column(
        ForeignKey("genders.id"),
        nullable=False
    )

    uom_id: Mapped[int] = mapped_column(
        ForeignKey("uoms.id"),
        nullable=False
    )

    # Default attributes
    default_carat_id: Mapped[int | None] = mapped_column(
        ForeignKey("carats.id"),
        nullable=True
    )

    default_color_id: Mapped[int | None] = mapped_column(
        ForeignKey("colors.id"),
        nullable=True
    )

    default_size_id: Mapped[int | None] = mapped_column(
        ForeignKey("sizes.id"),
        nullable=True
    )

    default_style_id: Mapped[int | None] = mapped_column(
        ForeignKey("styles.id"),
        nullable=True
    )

    # Default weights
    default_gross_weight: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False
    )

    default_net_weight: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False
    )

    # Wastage
    wastage: Mapped[Decimal] = mapped_column(
        Numeric(8, 3),
        default=0,
        nullable=False
    )

    # Keywords
    keywords: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list,
        nullable=False
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Database constraints
    __table_args__ = (

        UniqueConstraint(
            "product_id",
            name="uq_products_product_code"
        ),

        ForeignKeyConstraint(
            ["category_id", "subcategory_id"],
            ["subcategories.category_id", "subcategories.id"],
            name="fk_products_category_subcategory"
        ),

        CheckConstraint(
            "default_gross_weight > 0 AND "
            "default_net_weight > 0 AND "
            "default_gross_weight >= default_net_weight",
            name="chk_product_default_weights"
        ),
    )

    # Product variants
    variants = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    # Master relationships
    metal = relationship("Metal")
    project = relationship("Project")
    product_type = relationship("ProductType")

    category = relationship(
        "Category",
        foreign_keys=[category_id]
    )

    subcategory = relationship(
    "Subcategory",
    foreign_keys="[Product.category_id, Product.subcategory_id]",
    viewonly=True
)

    collection = relationship("Collection")
    subcollection = relationship("Subcollection")
    gender = relationship("Gender")
    uom = relationship("UOM")

    # Default attribute relationships
    default_carat = relationship(
        "Carat",
        foreign_keys=[default_carat_id]
    )

    default_color = relationship(
        "Color",
        foreign_keys=[default_color_id]
    )

    default_size = relationship(
        "Size",
        foreign_keys=[default_size_id]
    )

    default_style = relationship(
        "Style",
        foreign_keys=[default_style_id]
    )
