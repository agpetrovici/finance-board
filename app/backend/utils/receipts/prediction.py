from pathlib import Path
from typing import Optional

from mindee import Client, PredictResponse, product


def make_receipt_prediction(mindee_client: Client, data_input: Path | bytes, file_name: Optional[str]) -> PredictResponse:
    match data_input:
        case Path():
            input_doc = mindee_client.source_from_path(data_input)
        case bytes():
            input_doc = mindee_client.source_from_bytes(
                input_bytes=data_input,
                filename=file_name,
            )
        case _:
            raise ValueError("Invalid input type")

    result: PredictResponse = mindee_client.parse(product.ReceiptV5, input_doc)

    return result
