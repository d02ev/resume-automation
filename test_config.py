from config.settings import settings
from utils.logger import setup_logger, log_step, log_message, LogType

# Create logger
logger = setup_logger()

# Test logging
log_step(logger, 0, "Testing Configuration & Logging")

# Test configuration loading
try:
    log_message(logger, "Loading configuration...")

    logger.info(f"Resume API URL: {settings.RESUME_API_BASE_URL}")
    logger.info(f"Username: {settings.RESUME_API_USERNAME}")
    logger.info(f"Password: {'*' * len(settings.RESUME_API_PASSWORD or '')}")
    logger.info(f"GitHub PAT: {settings.GITHUB_PAT[:10] if settings.GITHUB_PAT else 'NOT SET'}...")
    logger.info(f"Telegram Token: {settings.TELEGRAM_BOT_TOKEN[:10] if settings.TELEGRAM_BOT_TOKEN else 'NOT SET'}...")
    logger.info(f"Chat ID: {settings.TELEGRAM_CHAT_ID}")
    logger.info(f"Default Template: {settings.DEFAULT_TEMPLATE_ID}")
    logger.info(f"Default Resume Name: {settings.DEFAULT_RESUME_NAME}")
    logger.info(f"Poll Interval: {settings.POLL_INTERVAL_SECONDS}s")
    logger.info(f"Max Poll Attempts: {settings.MAX_POLL_ATTEMPTS}")

    log_message(logger, "Configuration loaded successfully", LogType.SUCCESS)

    # Validate required variables
    log_message(logger, "Validating required environment variables...")
    settings.validate()
    log_message(logger, "All required environment variables are set", LogType.SUCCESS)

except ValueError as e:
    log_message(logger, str(e), LogType.ERROR)
    exit(1)
except Exception as e:
    log_message(logger, f"Unexpected error: {e}", LogType.ERROR)
    exit(1)

log_message(logger, "Configuration and logging test completed!", LogType.SUCCESS)