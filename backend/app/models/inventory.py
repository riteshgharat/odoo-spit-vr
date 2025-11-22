from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Boolean,
    DECIMAL,
    Date,
    ForeignKey,
    TIMESTAMP
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    address = Column(Text)
    is_active = Column(Boolean, default=True)

    locations = relationship("Location", back_populates="warehouse")


class Location(Base):
    __tablename__ = "locations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    warehouse_id = Column(BigInteger, ForeignKey("warehouses.id"), nullable=False)
    name = Column(String(150), nullable=False)
    code = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)

    warehouse = relationship("Warehouse", back_populates="locations")


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=False, unique=True)
    category = Column(String(100))
    uom = Column(String(20), nullable=False)  # e.g. "pcs", "kg"
    description = Column(Text)
    reorder_level = Column(DECIMAL(18, 4), default=0)
    reorder_qty = Column(DECIMAL(18, 4), default=0)
    is_active = Column(Boolean, default=True)


class StockLevel(Base):
    __tablename__ = "stock_levels"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    location_id = Column(BigInteger, ForeignKey("locations.id"), nullable=False)
    quantity = Column(DECIMAL(18, 4), default=0)

    product = relationship("Product")
    location = relationship("Location")


class InventoryDocument(Base):
    __tablename__ = "inventory_documents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    document_no = Column(String(50), nullable=False, unique=True)
    doc_type = Column(String(20), nullable=False)  # RECEIPT / DELIVERY / TRANSFER / ADJUSTMENT
    status = Column(String(20), nullable=False)    # draft / waiting / ready / done / canceled
    warehouse_id = Column(BigInteger, ForeignKey("warehouses.id"), nullable=False)
    counterparty_name = Column(String(255))
    doc_date = Column(Date, nullable=False)

    warehouse = relationship("Warehouse")
    items = relationship("InventoryDocumentItem", back_populates="document")


class InventoryDocumentItem(Base):
    __tablename__ = "inventory_document_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    document_id = Column(BigInteger, ForeignKey("inventory_documents.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    from_location_id = Column(BigInteger, ForeignKey("locations.id"))
    to_location_id = Column(BigInteger, ForeignKey("locations.id"))
    quantity = Column(DECIMAL(18, 4), default=0)
    system_qty = Column(DECIMAL(18, 4))
    counted_qty = Column(DECIMAL(18, 4))
    difference = Column(DECIMAL(18, 4))
    uom = Column(String(20), nullable=False)

    document = relationship("InventoryDocument", back_populates="items")
    product = relationship("Product")
    from_location = relationship("Location", foreign_keys=[from_location_id])
    to_location = relationship("Location", foreign_keys=[to_location_id])


class StockLedger(Base):
    __tablename__ = "stock_ledger"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    location_id = Column(BigInteger, ForeignKey("locations.id"), nullable=False)
    warehouse_id = Column(BigInteger, ForeignKey("warehouses.id"), nullable=False)
    quantity_change = Column(DECIMAL(18, 4), nullable=False)
    doc_type = Column(String(20), nullable=False)       # RECEIPT / DELIVERY / TRANSFER / ADJUSTMENT
    document_id = Column(BigInteger, ForeignKey("inventory_documents.id"), nullable=False)
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    product = relationship("Product")
    location = relationship("Location")
    warehouse = relationship("Warehouse")
    document = relationship("InventoryDocument")
    user = relationship("User")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    otp_code = Column(String(10), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)

    user = relationship("User")