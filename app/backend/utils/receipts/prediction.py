from pathlib import Path
from typing import Optional

from mindee import ClientV2, InferenceParameters, PathInput, BytesInput
from mindee.parsing.v2.field.inference_fields import InferenceFields


def make_receipt_prediction(model_id: str, mindee_client: ClientV2, data_input: Path | bytes, file_name: Optional[str]) -> InferenceFields:
    # Set inference parameters
    params = InferenceParameters(
        # ID of the model, required.
        model_id=model_id,
        # Options: set to `True` or `False` to override defaults
        # Enhance extraction accuracy with Retrieval-Augmented Generation.
        rag=None,
        # Extract the full text content from the document as strings.
        raw_text=None,
        # Calculate bounding box polygons for all fields.
        polygon=True,
        # Boost the precision and accuracy of all extractions.
        # Calculate confidence scores for all fields.
        confidence=None,
    )

    # Load a file from disk
    match data_input:
        case Path():
            input_source = PathInput(data_input)

        case bytes():
            input_source = BytesInput(
                raw_bytes=data_input,
                filename=file_name,
            )
        case _:
            raise ValueError("Invalid input type")

    # Send for processing using polling
    response = mindee_client.enqueue_and_get_inference(input_source, params)
    fields = response.inference.result.fields

    return fields
