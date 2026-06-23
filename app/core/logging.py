import logging
import sys

def setup_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # Configure fastAPI/Uvicorn loggers if necessary
    logging.getLogger("uvicorn.access").handlers = logging.getLogger().handlers
