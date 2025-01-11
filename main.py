import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from app.backend.flask_app import create_app  # noqa: E402
from app.backend.config import Config  # noqa: E402

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))

if __name__ == "__main__":
    app = create_app(Config)
    port_raw = os.getenv("FLASK_PORT")
    if isinstance(port_raw, str):
        port = int(port_raw)
        app.run(port=port, host=os.getenv("FLASK_HOST"))
