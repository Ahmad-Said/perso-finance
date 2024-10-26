from datetime import datetime
import re

from frais.sncf.trip_extractor import TripExtractor, TripDetails


class TripAchatExtractor(TripExtractor):


    def is_supported(self, document_text: str) -> bool:
        return 'JUSTIFICATIF D\'ACHAT' in document_text.upper()

    # example of datetime: Aller 08/07/2024 à 16:59:00
    datetime_regex = r'Aller (\d{2}/\d{2}/\d{4}) à (\d{2}:\d{2}:\d{2})'
    # example: Montant total (TTC) : €16.10
    ammount_regex = r'Montant total \(TTC\) : €(\d+\.\d{2})'

    # example of document_text:
    # ....
    # Compiègne (FR)
    # Paris Gare du Nord
    # Montant total (TTC) : €16.10
    source_destination_regex = r'(.*)\n(.*)\nMontant total \(TTC\) : €\d+\.\d{2}'

    def extract_trip_details(self, document_text: str) -> TripDetails:
        trip_details = {
            'trip_date': None,
            'amount_paid': None,
            'start_destination': None,
            'end_destination': None
        }
        # Extract trip date
        match = re.search(self.datetime_regex, document_text)
        if match:
            day_date = match.group(1)
            hour_date = match.group(2)

            trip_details['trip_date'] = datetime.strptime(day_date + ' ' + hour_date, '%d/%m/%Y %H:%M:%S')

        # Extract amount paid
        match = re.search(self.ammount_regex, document_text)
        if match:
            trip_details['amount_paid'] = float(match.group(1))

        # Extract start and end destinations
        match = re.search(self.source_destination_regex, document_text)
        if match:
            trip_details['start_destination'] = match.group(1)
            trip_details['end_destination'] = match.group(2)

        return TripDetails(**trip_details)