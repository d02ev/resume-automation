import os
from typing import Optional
from utils.logger import setup_logger, log_message, LogType

logger = setup_logger(__name__)

def read_file(file_path: str) -> str:
  log_message(logger, f"Reading JD from file: {file_path}")

  if not os.path.exists(file_path):
    log_message(logger, f"File not found: {file_path}", LogType.ERROR)
    raise FileNotFoundError(f"File not found: {file_path}")

  try:
    with open(file_path, 'r', encoding='utf-8') as f:
      content = f.read()

    log_message(logger, f"File read successfully ({len(content)} chars)", LogType.SUCCESS)
    return content

  except IOError as e:
    log_message(logger, f"Error reading file: {e}", LogType.ERROR)
    raise
  except Exception as e:
    log_message(logger, f"Unexpected error reading file: {e}", LogType.ERROR)
    raise

def is_file_path(value: str) -> bool:
  has_extension = '.' in os.path.basename(value)
  has_path_sep = '/' in value or '\\' in value
  exists = os.path.exists(value)

  return (has_extension or has_path_sep) and exists

def get_job_description(jd_input: Optional[str]) -> Optional[str]:
  if not jd_input:
    log_message(logger, "No job description provided")
    return None

  if jd_input.lower().strip() == "no":
    log_message(logger, "Job description explicitly set to 'no'")
    return None

  if is_file_path(jd_input):
    log_message(logger, f"Job description appears to be a file: {jd_input}")
    try:
      return read_file(jd_input)
    except Exception as e:
      log_message(logger, f"Failed to read JD file: {e}", LogType.ERROR)
      raise

  log_message(logger, f"Using job description as direct text ({len(jd_input)} chars)")
  return jd_input

def validate_template_id(template_id: str) -> bool:
  if not template_id:
    return False

  has_slash = '/' in template_id
  has_extension = template_id.endswith('.cshtml')

  return has_extension and has_slash

def validate_resume_name(resume_name: str) -> bool:
  if not resume_name:
    return False

  invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
  return not any(char in resume_name for char in invalid_chars)

def format_mode_name(mode: str) -> str:
  mode_map = {
    "generic": "Generic Optimisation",
    "jd-optimised": "JD-Optimised",
    "job-description": "JD-Optimised"
  }
  return mode_map.get(mode.lower(), mode.upper())