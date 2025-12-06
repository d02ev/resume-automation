import requests
import json
from typing import Dict
from config.settings import settings
from services.auth_service import AuthService
from utils.logger import setup_logger, log_message, LogType

logger = setup_logger(__name__)

class ResumeService:
  def __init__(self, auth_service: AuthService):
    self.auth_service = auth_service

  def fetch_resume_data(self) -> Dict:
    log_message(logger, "Fetching resume data....")

    url = f"{settings.RESUME_API_BASE_URL}/resume"
    headers = self.auth_service.get_auth_headers()

    try:
      response = requests.get(url, headers=headers, timeout=30)
      response.raise_for_status()

      data = response.json()
      resume_data = data.get("data")

      if not resume_data:
        raise ValueError("No 'data' field in API response")

      log_message(logger, "Resume data fetched successfully.", LogType.SUCCESS)
      logger.debug(f"Resume data keys: {list(resume_data.key())}")

      return resume_data

    except requests.exceptions.HTTPError as e:
      log_message(logger, f"HTTP error while fetching resume data: {e}", LogType.ERROR)
      if e.response is not None:
        logger.error(f"Response: {e.response.text}")
      raise
    except requests.exceptions.RequestException as e:
      log_message(logger, f"Network error while fetching resume data: {e}", LogType.ERROR)
      raise
    except (KeyError, ValueError) as e:
      log_message(logger, f"Unexpected response format: {e}", LogType.ERROR)
      raise
    except Exception as e:
      log_message(logger, f"Unexpected error while fetching resume data: {e}", LogType.ERROR)
      raise

  def stringify_resume_data(self, resume_data: Dict) -> str:
    log_message(logger, "Stringification of resume data....")

    try:
      json_string = json.dumps(resume_data)

      log_message(logger, f"Stringification successful ({len(json_string)} characters)", LogType.SUCCESS)

      return json_string

    except (TypeError, ValueError) as e:
      log_message(logger, f"Failed to stringify resume data: {e}", LogType.ERROR)
      raise
