import requests
from typing import Optional
from config.settings import settings
from utils.logger import setup_logger, log_message, LogType

logger = setup_logger(__name__)

class NotificationService:
  def __init__(self):
    self.bot_token = settings.TELEGRAM_BOT_TOKEN
    self.chat_id = settings.TELEGRAM_CHAT_ID
    self.base_url = f"https://api.telegram.org/bit{self.bot_token}"

  def send_message(self, message: str, parse_mode: Optional[str] = None) -> bool:
    log_message(logger, "Sending telegram notification....")

    url = f"{self.base_url}/sendMessage"
    payload = {
      "chat_id": self.chat_id,
      "text": message
    }

    if parse_mode:
      payload["parse_mode"] = parse_mode

    try:
      logger.debug(f"Sending to chat ID: {self.chat_id}")

      response = requests.post(url, json=payload, timeout=30)
      response.raise_for_status()

      result = response.json()

      if result.get("ok"):
        log_message(logger, "Telegram notification sent successfully.", LogType.SUCCESS)
        return True
      else:
        log_message(logger, f"Telegram API returned ok=false: {result}", LogType.ERROR)
        return False

    except requests.exceptions.HTTPError as e:
      log_message(logger, f"HTTP error sending telegram notification: {e}", LogType.ERROR)
      if e.response is not None:
        logger.error(f"Response: {e.response.text}")
      return False
    except requests.exceptions.RequestException as e:
      log_message(logger, f"Network error while sending telegram notification: {e}", LogType.ERROR)
      return False
    except Exception as e:
      log_message(logger, f"Unexpected error while sending telegram notifications: {e}", LogType.ERROR)
      return False

  def send_success_notification(self, pdf_url: str, mode: str = "generic") -> bool:
    message = (
      f"Resume generation successful!\n\n"
      f"Mode: {mode.upper()}\n"
      f"PDF URL: {pdf_url}\n\n"
      f"Your resume is ready!"
    )
    return self.send_message(message)

  def send_failure_notification(self, error: str, mode: str = "generic") -> bool:
    message = (
      f"Resume generation failed!\n\n"
      f"Mode: {mode.upper()}\n"
      f"Error: {error}\n\n"
    )
    return self.send_message(message)

  def send_pipeline_start_notification(self, mode: str = "generic") -> bool:
    message = (
      f"Resume optimisation pipeline started\n\n"
      f"Mode: {mode.upper()}\n"
      f"Processing your resume...."
    )
    return self.send_message(message)