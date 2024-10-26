from datetime import datetime

from pydantic import BaseModel

from frais.model.frais_details import FraisDetails


class TripDetails(BaseModel):
    trip_date: datetime
    amount_paid: float
    start_destination: str
    end_destination: str

class TripExtractor:
    def is_supported(self, document_text: str) -> bool:
        raise NotImplementedError

    def extract_trip_details(self, document_text: str) -> TripDetails:
        raise NotImplementedError

    def get_frais_details(self, document_text: str, proof_doc: str) -> FraisDetails:
        trip_details = self.extract_trip_details(document_text)
        return FraisDetails(payment_date=trip_details.trip_date,
                            amount_paid=trip_details.amount_paid,
                            proof_document=proof_doc,
                            comment=f"De {trip_details.start_destination} à {trip_details.end_destination}")