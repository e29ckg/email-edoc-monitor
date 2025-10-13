# utils/logger.py
import os
from datetime import datetime

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LEVELS = ["DEBUG", "INFO", "WARN", "ERROR"]

def log(message: str, level: str = "INFO"):
    if LEVELS.index(level.upper()) >= LEVELS.index(LOG_LEVEL):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level.upper()}] {message}")