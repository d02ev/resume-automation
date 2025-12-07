import time
import requests
import json
from typing import Dict
from config.settings import settings
from services.auth_service import AuthService
from utils.logger import setup_logger, log_message, LogType

logger = setup_logger(__name__)

class GeneratorService:
  def __init__(self, auth_service: AuthService):
    self.auth_service = auth_service

  def generate_resume(self, resume_data: str, template_id: str, resume_name: str) -> str:
    log_message(logger, "Generating resume....")
    logger.info(f"Template ID: {template_id}")
    logger.info(f"Resume Name: {resume_name}")

    url = f"{settings.RESUME_API_BASE_URL}/resume/generate"
    headers = self.auth_service.get_auth_headers()

    try:
      resume_dict = json.loads(resume_data)
    except json.JSONDecodeError:
      log_message(logger, "Resume data is not a valid JSON")
      raise

    payload = {
      "resumeData": resume_dict,
      "templateId": template_id,
      "resumeName": resume_name
    }

    try:
      logger.debug(f"Sending POST to {url}")

      response = requests.post(url, headers=headers, json=payload, timeout=30)
      response.raise_for_status()

      data = response.json()
      job_id = data["data"]["jobId"]

      if not job_id:
        raise ValueError("No 'jobId' field in API response")

      log_message(logger, "Resume data sent for generation successfully.", LogType.SUCCESS)
      logger.debug(f"Resume generation job id: {job_id}")

      return job_id

    except requests.exceptions.HTTPError as e:
      log_message(logger, f"HTTP error while generating resume: {e}", LogType.ERROR)
      if e.response is not None:
        logger.error(f"Response: {e.response.text}")
      raise
    except requests.exceptions.RequestException as e:
      log_message(logger, f"Network error while generating resume: {e}", LogType.ERROR)
      raise
    except (KeyError, ValueError) as e:
      log_message(logger, f"Unexpected response format: {e}", LogType.ERROR)
      raise
    except Exception as e:
      log_message(logger, f"Unexpected error while generating resume: {e}", LogType.ERROR)
      raise

  def poll_job_status(self, job_id: str, max_attempts: int = None, interval: int = None) -> Dict:
    if max_attempts is None:
      max_attempts = settings.MAX_POLL_ATTEMPTS
    if interval is None:
      interval = settings.POLL_INTERVAL_SECONDS

    log_message(logger, f"Polling job status (every {interval}s, max {max_attempts} attempts)...")

    url = f"{settings.RESUME_API_BASE_URL}/resume/status/{job_id}"
    headers = self.auth_service.get_auth_headers()

    for attempt in range(1, max_attempts + 1):
      try:
        logger.info(f"Attempt {attempt}/{max_attempts}...")

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()
        status = result.get("status")

        logger.info(f"Status: {status}")

        if status not in ["pending", "processing"]:
          if status == "success":
            log_message(logger, "Job completed successfully.", LogType.SUCCESS)
            return result
          elif status == "failed":
            log_message(logger, f"Job failed: {result.get('error', 'Unknown error')}", LogType.ERROR)
            return result
          else:
            log_message(logger, f"Unknown status: {status}", LogType.WARNING)
            return result

        if attempt < max_attempts:
          time.sleep(interval)

      except requests.exceptions.RequestException as e:
        log_message(logger, f"Error polling job status: {e}", LogType.ERROR)
        if attempt < max_attempts:
          log_message(logger, f"Retrying in {interval}s", LogType.WARNING)
          time.sleep(interval)
        else:
          raise

    raise TimeoutError(
      f"Job {job_id} did not complete after {max_attempts} attempts"
      f"({max_attempts * interval} seconds)"
    )