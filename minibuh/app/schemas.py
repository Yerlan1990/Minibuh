from pydantic import BaseModel
from typing import Optional

class CompanyIn(BaseModel):
    name: str
    type: str
    tax_id: str
    address: str
    bank: str
    bik: str
    iik: str
    kbe: Optional[str] = None
    phone: Optional[str] = None
    director: Optional[str] = None

class CounterpartyIn(CompanyIn):
    pass

class ContractIn(BaseModel):
    company_id: int
    counterparty_id: int
    service_name: str
    knp: Optional[str] = None
    vat_rate: int = 12
    amount: int
    currency: str = "KZT"
    advance_percent: int = 0
    reserve_number: bool = True

class InvoiceIn(BaseModel):
    company_id: int
    counterparty_id: int
    contract_id: Optional[int] = None
    service_name: str
    knp: Optional[str] = None
    vat_rate: int = 12
    amount: int
    due_days: int = 7
    reserve_number: bool = True

class ActIn(BaseModel):
    company_id: int
    counterparty_id: int
    contract_id: int
    amount: int
    period: str
    reserve_number: bool = True

class TaxInvoiceIn(BaseModel):
    company_id: int
    counterparty_id: int
    contract_id: Optional[int] = None
    invoice_id: Optional[int] = None
    amount: int
    vat_rate: int = 12
    reserve_number: bool = True
