from pathlib import Path
from datetime import datetime
import pickle
from typing import Any


def save_image(receipts_dir: Path, image_data: bytes, file_name: str) -> Path:
    # Save image with timestamp and original filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = f"{timestamp}_{file_name}"
    image_path = receipts_dir / image_filename

    with open(image_path, "wb") as f:
        f.write(image_data)

    return image_path


def save_result(file_path: Path, result: Any) -> Path:
    pickle_filename = file_path.with_suffix(".pkl")
    with open(pickle_filename, "wb") as f:
        pickle.dump(result, f)

    return pickle_filename
