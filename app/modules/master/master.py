
from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


# Common fields for master tables
class MasterMixin:
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )


# 1. Metal Master
class Metal(Base, MasterMixin):
    __tablename__ = "metals"


# 2. Project Master
class Project(Base, MasterMixin):
    __tablename__ = "projects"


# 3. Product Type Master
class ProductType(Base, MasterMixin):
    __tablename__ = "product_types"


# 4. Category Master
class Category(Base, MasterMixin):
    __tablename__ = "categories"

    subcategories = relationship(
        "Subcategory",
        back_populates="category"
    )


# 5. Subcategory Master
class Subcategory(Base):
    __tablename__ = "subcategories"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        index=True
    )

    code: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    category = relationship(
        "Category",
        back_populates="subcategories"
    )

    __table_args__ = (
        UniqueConstraint(
            "category_id",
            "code",
            name="uq_subcategory_category_code"
        ),
    )


# 6. Collection Master
class Collection(Base, MasterMixin):
    __tablename__ = "collections"

    subcollections = relationship(
        "Subcollection",
        back_populates="collection"
    )


# 7. Subcollection Master
class Subcollection(Base):
    __tablename__ = "subcollections"

    id: Mapped[int] = mapped_column(primary_key=True)

    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collections.id"),
        nullable=False,
        index=True
    )

    code: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    collection = relationship(
        "Collection",
        back_populates="subcollections"
    )

    __table_args__ = (
        UniqueConstraint(
            "collection_id",
            "code",
            name="uq_subcollection_collection_code"
        ),
    )


# 8. UOM Master
class UOM(Base, MasterMixin):
    __tablename__ = "uoms"


# 9. Carat Master
class Carat(Base, MasterMixin):
    __tablename__ = "carats"


# 10. Color Master
class Color(Base, MasterMixin):
    __tablename__ = "colors"


# 11. Size Master
class Size(Base, MasterMixin):
    __tablename__ = "sizes"


# 12. Style Master
class Style(Base, MasterMixin):
    __tablename__ = "styles"


# 13. Gender Master
class Gender(Base, MasterMixin):
    __tablename__ = "genders"
