import logging
import sys
from datetime import datetime
from enum import Enum

class LogType(Enum):
  INFO = 0
  SUCCESS = 1
  WARNING = 2
  ERROR = 3

def setup_logger(name: str = "Resume Automation", level: int = logging.INFO) -> logging.Logger:
  logger = logging.getLogger(name)
  logger.setLevel(level)

  if logger.handlers:
    return logger

  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setLevel(level)

  formatter = logging.Formatter(
    fmt='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
  )

  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)

  return logger

def log_step(logger: logging.Logger, step_number: int, desc: str):
  logger.info("=" * 60)
  logger.info(f"STEP {step_number}: {desc}")
  logger.info("=" * 60)

def log_message(logger: logging.Logger, message:str, log_type: LogType=LogType.INFO):
  if log_type.value == 1:
    logger.info(f"{message}")
  elif log_type.value == 2:
    logger.warning(f"{message}")
  elif log_type.value == 3:
    logger.error(f"{message}")
  else:
    logger.info(f"{message}")

default_logger = setup_logger()