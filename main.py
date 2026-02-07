import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import uvicorn  # noqa: E402

from app.backend.app import create_app  # noqa: E402

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))

app = create_app()

if __name__ == "__main__":
    port_raw = os.getenv("FASTAPI_PORT")
    host = os.getenv("FASTAPI_HOST", "localhost")
    port = int(port_raw) if port_raw else 8000
    ssl_certfile = "cert.pem" if Path("cert.pem").exists() else None
    ssl_keyfile = "key.pem" if Path("key.pem").exists() else None
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
        reload=True,
    )
