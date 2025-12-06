import requests
import json
import re
from typing import Dict, Optional
from config.settings import settings
from utils.logger import setup_logger, log_message, LogType

logger = setup_logger(__name__)

class AiService:
  def __init__(self):
    self.base_url = settings.OPENAI_BASE_URL
    self.model = settings.OPENAI_MODEL
    self.headers = {
      "Authorization": f"Bearer {settings.GITHUB_PAT}",
      "Content-Type": "application/json"
    }

  def _escape_percent_hash(self, value):
    if isinstance(value, list):
      return [self._escape_percent_hash(v) for v in value]
    if isinstance(value, dict):
      return { k: self._escape_percent_hash(v) for k, v in value.items() }
    if isinstance(value, str):
      return value.replace('%', '\\\\%').replace('#', '\\\\#')

    return value

  def _clean_json_response(self, content: str) -> str:
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```\s*', '', content)
    content = content.strip()

    return content

  def optimise_generic(self, resume_data: Dict) -> str:
    log_message(logger, "Starting AI P1 optimisation....")

    system_prompt = (
      "Task: Rewrite values in the provided resume JSON to improve grammar, "
      "clarity, technical impact, action verbs, and ATS strength. Keep exact JSON "
      "structure and keys. Do NOT change metrics, numbers, dates, fabricate achievements, "
      "modify fields with null dates, or add/remove keys. Output only valid JSON. "
      "Allowed: add relevant keywords, rewrite bullets, and enhance clarity while keeping "
      "meaning. If issues: include a top-level _issues array listing them (empty if none)."
    )
    payload = {
      "model": self.model,
      "temperature": 0,
      "messages": [
        { "role": "system", "content": system_prompt },
        { "role": "user", "content": json.dumps(resume_data) }
      ]
    }

    try:
      logger.debug(f"Sending request to {self.base_url}")
      logger.debug(f"Model: {self.model}")

      response = requests.post(
        self.base_url,
        json=payload,
        headers=self.headers,
        timeout=120
      )
      response.raise_for_status()

      result = response.json()
      content = result["choices"][0]["message"]["content"]
      clean_content = self._clean_json_response(content)

      try:
        json.loads(clean_content)
      except json.JSONDecodeError as e:
        log_message(logger, f"AI return invalid JSON: {e}", LogType.ERROR)
        logger.error(f"Content (first 500 chars): {clean_content[:500]}")
        raise

      optimised_data = self._escape_percent_hash(clean_content)

      log_message(logger, "AI P1 optimisation completed.", LogType.SUCCESS)
      logger.debug(f"Optimised data length: {len(optimised_data)} characters")

      return optimised_data

    except requests.exceptions.HTTPError as e:
      log_message(logger, f"HTTP error during AI P1 optimisation: {e}", LogType.ERROR)
      if e.response is not None:
        logger.error(f"Response: {e.response.text}")
      raise
    except requests.exceptions.RequestException as e:
      log_message(logger, f"Network error during AI P1 optimisation: {e}", LogType.ERROR)
      raise
    except KeyError as e:
      log_message(logger, f"Unexpected API response format: missing key {e}", LogType.ERROR)
      raise
    except Exception as e:
      log_message(logger, f"Unexpected error during AI P1 optimisation: {e}", LogType.ERROR)
      raise

  def optimise_with_jd(self, resume_data: str, job_description: str) -> str:
    log_message(logger, "Starting AI P2 optimisation....")
    logger.info(f"Job description length: {len(job_description)} characters.")

    system_prompt = (
      "Task: Rewrite values in the provided resume JSON so they align strongly with "
      "the supplied Job Description (JD) and maximize ATS relevance. Preserve exact JSON "
      "structure and keys. Do NOT change metrics, numbers, dates, fabricate achievements, "
      "modify null-date fields, or add/remove keys (except _issues and score). "
      "Output only valid JSON.\n\n"
      "Allowed: rewrite bullet points for JD alignment; add JD-relevant keywords, skills, "
      "and terminology; improve clarity and technical impact while preserving factual meaning.\n\n"
      "ATS Score: after optimization, output a numeric field named \"score\" (0-100) "
      "representing the resume's relevance to the JD.\n\n"
      "If issues arise (unclear or missing fields), include a top-level _issues array (empty if none)."
    )

    try:
      resume_dict = json.loads(resume_data)
    except json.JSONDecodeError:
      resume_dict = resume_data

    user_content = {
      "jd": job_description,
      "resume": resume_data
    }
    payload = {
      "model": self.model,
      "temperature": 0,
      "messages": [
        { "role": "system", "content": system_prompt },
        { "role": "user", "content": json.dumps(user_content) }
      ]
    }

    try:
      logger.debug(f"Sending request to {self.base_url}")
      logger.debug(f"Model: {self.model}")

      response = requests.post(
        self.base_url,
        json=payload,
        headers=self.headers,
        timeout=120
      )
      response.raise_for_status()

      result = response.json()
      content = result["choices"][0]["message"]["content"]
      cleaned_content = self._clean_json_response(content)

      try:
        parsed = json.loads(cleaned_content)
        if "score" in parsed:
          logger.info(f"ATS Score: {parsed['score']}/100")
        else:
          log_message(logger, "No ATS score generated", LogType.WARNING)

      except json.JSONDecodeError as e:
        log_message(logger, f"AI returned invalid JSON: {e}", LogType.ERROR)
        logger.error(f"Content (first 500 chars): {cleaned_content[:500]}")
        raise

      optimised_data = self._escape_percent_hash(cleaned_content)

      log_message(logger, "AI P2 optimisations completed", LogType.SUCCESS)
      logger.debug(f"Optimised data length: {len(optimised_data)} characters")

      return optimised_data
    except requests.exceptions.HTTPError as e:
      log_message(logger, f"HTTP error during AI P2 optimization: {e}", LogType.ERROR)
      if e.response is not None:
        logger.error(f"Response: {e.response.text}")
      raise
    except requests.exceptions.RequestException as e:
      log_message(logger, f"Network error during AI P2 optimization: {e}", LogType.ERROR)
      raise
    except KeyError as e:
      log_message(logger, f"Unexpected API response format: missing key {e}", LogType.ERROR)
      raise
    except Exception as e:
      log_message(logger, f"Unexpected error during AI P2 optimization: {e}", LogType.ERROR)
      raise