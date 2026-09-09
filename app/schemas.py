
from pydantic import BaseModel, ConfigDict


class Invoice(BaseModel):
    id: str
    contact_name: str
    total_amount: float
    currency: str
    date: str
    due_date: str
    status: str

    model_config = ConfigDict(extra="ignore")

class ProviderResponse(BaseModel):
    invoices: list[Invoice]

    model_config = ConfigDict(extra="ignore")

class SyncResponse(BaseModel):
    status: str
    fetched_count: int
    invoices: list[Invoice]
