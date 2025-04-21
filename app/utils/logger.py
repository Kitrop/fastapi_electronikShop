import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

file_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)
file_handler.setFormatter(log_format)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING) 