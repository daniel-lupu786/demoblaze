import logging
import os
from datetime import datetime, UTC

def _configure_logging() -> None:
    os.makedirs("artifacts", exist_ok=True)

    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    log_path = f"artifacts/logs/test_run_{ts}.log"

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    root.handlers.clear()

    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    # File
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)

    root.addHandler(ch)
    root.addHandler(fh)

    logging.getLogger(__name__).info("Logging initialized -> %s", log_path)
