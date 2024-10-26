from datetime import datetime

from pydantic import BaseModel


class FraisDetails(BaseModel):
    payment_date: datetime
    amount_paid: float
    proof_document: str
    comment: str


class FraisDetailsList(BaseModel):
    frais_details: list[FraisDetails]