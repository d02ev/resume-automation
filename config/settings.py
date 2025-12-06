import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
  RESUME_API_BASE_URL: str = os.getenv("RESUME_API_BASE_URL", "https://portfolio-api-oo25.onrender.com/api")
  RESUME_API_USERNAME: str = os.getenv("RESUME_API_USERNAME")
  RESUME_API_PASSWORD: str = os.getenv("RESUME_API_PASSWORD")
  GITHUB_PAT: str = os.getenv("GITHUB_PAT")
  OPENAI_BASE_URL: str = "https://models.github.ai/inference/chat/completions"
  OPENAI_MODEL: str = "openai/gpt-4.1"
  TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
  TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID")
  POLL_INTERVAL_SECONDS: int = os.getenv("POLL_INTERVAL_SECONDS", 30)
  MAX_POLL_ATTEMPTS: int = os.getenv("MAX_POLL_ATTEMPTS", 20)
  DEFAULT_TEMPLATE_ID: str = os.getenv("DEFAULT_TEMPLATE_ID", "templates/resume_template.cshtml")
  DEFAULT_RESUME_NAME: str = os.getenv("DEFAULT_RESUME_NAME", "Vikramaditya_Pratap_Singh")

  @classmethod
  def validate(cls) -> bool:
    required_vars = {
      "RESUME_API_USERNAME": cls.RESUME_API_USERNAME,
      "RESUME_API_PASSWORD": cls.RESUME_API_PASSWORD,
      "GITHUB_PAT": cls.GITHUB_PAT,
      "TELEGRAM_BOT_TOKEN": cls.TELEGRAM_BOT_TOKEN,
      "TELEGRAM_CHAT_ID": cls.TELEGRAM_CHAT_ID
    }

    missing = [key for key, value in required_vars.items() if not value]
    if missing:
      raise ValueError(
        f"Missing required env vars: {', '.join(missing)}\n"
        f"Please check your .env file."
      )

    return True

settings = Settings()