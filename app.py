"""
FinLing — Financial intelligence in African languages.
Entry point: runs the FastAPI server.
"""
import uvicorn
from finling.api.routes import app  # noqa: F401


def main() -> None:
    uvicorn.run(
        "finling.api.routes:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
