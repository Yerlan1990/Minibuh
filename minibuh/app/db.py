from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, create_engine, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    sub = Column(String, unique=True, index=True, nullable=True)  # Google subject
    telegram_id = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, index=True, nullable=True)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    iin = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending -> approved -> active
    google_connected = Column(Boolean, default=False)
    drive_root_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FolderMap(Base):
    __tablename__ = "folder_map"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    path = Column(String)
    drive_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")

class CompanyProfile(Base):
    __tablename__ = "company_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    type = Column(String)  # ИП/ТОО
    tax_id = Column(String)  # БИН/ИИН
    address = Column(String)
    bank = Column(String)
    bik = Column(String)
    iik = Column(String)
    kbe = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    director = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User")
    __table_args__ = (UniqueConstraint('user_id', 'name'), )

class Counterparty(Base):
    __tablename__ = "counterparties"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    tax_id = Column(String)
    address = Column(String)
    bank = Column(String)
    bik = Column(String)
    iik = Column(String)
    kbe = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    director = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User")

class ServiceCatalog(Base):
    __tablename__ = "service_catalog"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    knp = Column(String, nullable=True)
    default_price = Column(Integer, default=0)
    vat_rate = Column(Integer, default=12)
    is_quick = Column(Boolean, default=False)  # для "быстрых 3"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
    __table_args__ = (UniqueConstraint('user_id', 'name'), )

class Numerator(Base):
    __tablename__ = "numerators"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("company_profiles.id"))
    doc_type = Column(String)  # contract|invoice|act|tax_invoice
    prefix = Column(String, default="DOC")
    year = Column(Integer, default=datetime.utcnow().year)
    counter = Column(Integer, default=0)
    user = relationship("User")
    company = relationship("CompanyProfile")
    __table_args__ = (UniqueConstraint('company_id', 'doc_type', 'year'), )

class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("company_profiles.id"))
    counterparty_id = Column(Integer, ForeignKey("counterparties.id"))
    number = Column(String, index=True)
    service_name = Column(String)
    knp = Column(String, nullable=True)
    vat_rate = Column(Integer, default=12)
    amount = Column(Integer)
    currency = Column(String, default="KZT")
    advance_percent = Column(Integer, default=0)
    status = Column(String, default="issued")
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
    company = relationship("CompanyProfile")
    counterparty = relationship("Counterparty")

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("company_profiles.id"))
    counterparty_id = Column(Integer, ForeignKey("counterparties.id"))
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)
    number = Column(String, index=True)
    service_name = Column(String)
    knp = Column(String, nullable=True)
    vat_rate = Column(Integer, default=12)
    amount = Column(Integer)
    due_days = Column(Integer, default=7)
    status = Column(String, default="issued")
    created_at = Column(DateTime, default=datetime.utcnow)

class Act(Base):
    __tablename__ = "acts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("company_profiles.id"))
    counterparty_id = Column(Integer, ForeignKey("counterparties.id"))
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    number = Column(String, index=True)
    amount = Column(Integer)
    period = Column(String)
    status = Column(String, default="issued")
    created_at = Column(DateTime, default=datetime.utcnow)

class TaxInvoice(Base):
    __tablename__ = "tax_invoices"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("company_profiles.id"))
    counterparty_id = Column(Integer, ForeignKey("counterparties.id"))
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    number = Column(String, index=True)
    vat_rate = Column(Integer, default=12)
    amount = Column(Integer)
    status = Column(String, default="issued")
    created_at = Column(DateTime, default=datetime.utcnow)

class DocumentFile(Base):
    __tablename__ = "document_files"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    doc_type = Column(String)
    entity_id = Column(Integer)
    drive_id = Column(String, nullable=True)
    path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
