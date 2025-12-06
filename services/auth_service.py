import requests
from typing import Optional
from config.settings import settings
from utils.logger import setup_logger, log_message, LogType

logger = setup_logger(__name__)

class AuthService:
  def __init__(self):
    self.access_token: Optional[str] = None
    self._authenticated = False

  def authenticate(self) -> str:
    if self._authenticated and self.access_token:
      log_message(logger, "Using cached access token.")
      return self.access_token

    log_message(logger, "Fetching access token....")

    url = f"{settings.RESUME_API_BASE_URL}/auth/login"
    payload = {
      "username": settings.RESUME_API_USERNAME,
      "password": settings.RESUME_API_PASSWORD
    }

    try:
      response = requests.post(url, json=payload, timeout=30)
      response.raise_for_status()

      data = response.json()
      self.access_token = data["token"]["accessToken"]
      self._authenticated = True

      log_message(logger, "Access token fetched successfully.", LogType.SUCCESS)
      return self.access_token

    except requests.exceptions.HTTPError as e:
      log_message(logger, f"HTTP error while fetching access token: {e}", LogType.ERROR)
      if e.response is not None:
        logger.error(f"Response: {e.response.text}")
      raise
    except requests.exceptions.RequestException as e:
      log_message(logger, f"Network error while fetching access token: {e}", LogType.ERROR)
      raise
    except KeyError as e:
      log_message(logger, f"Unexpected response format: missing key {e}", LogType.ERROR)
      raise
    except Exception as e:
      log_message(logger, f"Unexpected error while fetching access token: {e}", LogType.ERROR)
      raise

  def get_auth_headers(self) -> dict:
    if not self._authenticated or not self.access_token:
      self.authenticate()

    return {
      "Authorization": f"Bearer {self.access_token}",
      "Content-Type": "application/json"
    }

  def is_authenticated(self) -> bool:
    return self._authenticated and self.access_token is not None

  def logout(self):
    log_message(logger, "Clearing access token.")
    self.access_token = None
    self._authenticated = False