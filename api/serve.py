# -*- coding: utf-8 -*-
"""
CLI entry point: mgvaovao-serve
  Starts the FastAPI server via uvicorn with settings from the environment.
"""
import uvicorn
from mgvaovao.core.config import Settings

def main() -> None:
    cfg = Settings()
    uvicorn.run(
        "api.main:app",
        host=cfg.api_host,
        port=cfg.api_port,
        workers=cfg.api_workers,
        log_level="info",
    )

if __name__ == "__main__":
    main()
