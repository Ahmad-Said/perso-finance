import json
import os
from datetime import datetime
from typing import Optional

from const.const_gl import ConstGl
from frais.model.frais_details import FraisDetails, FraisDetailsList

def read_special_frais(special_frais_json: Optional[str] = None) -> FraisDetailsList:
    special_frais_json = special_frais_json or ConstGl.SPECIAL_FRAIS_JSON
    if not os.path.exists(special_frais_json):
        return FraisDetailsList(frais_details=[])
    with open(special_frais_json) as f:
        special_frais_data = json.load(f)
    return FraisDetailsList(**special_frais_data)

def write_special_frais(special_frais: FraisDetailsList, special_frais_json: Optional[str] = None):
    special_frais_json = special_frais_json or ConstGl.SPECIAL_FRAIS_JSON
    parent_dir = os.path.dirname(special_frais_json)
    os.makedirs(parent_dir, exist_ok=True)
    with open(special_frais_json, 'w') as f:
        f.write(special_frais.model_dump_json(indent=4))



def main_example():
    special_frais: FraisDetailsList = FraisDetailsList(
        frais_details = [
            # data/abonnement_ter_24_25.pdf
            FraisDetails(payment_date=datetime(2024, 8, 6),
                         amount_paid=30,
                         proof_document='/path/to/proof/abonnement.pdf',
                         comment='Abonnement TER'),
        ]
    )

    temp_json_file = os.path.join(ConstGl.TEMP_DIR, 'special_frais.json')

    write_special_frais(special_frais, temp_json_file)
    read_special_frais(temp_json_file)


if __name__ == '__main__':
    main_example()