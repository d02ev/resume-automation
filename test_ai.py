from services.auth_service import AuthService
from services.resume_service import ResumeService
from services.ai_service import AiService
from utils.logger import setup_logger, log_step, log_message, LogType
import json

logger = setup_logger()

log_step(logger, 3, "Testing AI Service")

try:
    # Setup services
    logger.info("Setting up services...")
    auth_service = AuthService()
    auth_service.authenticate()

    resume_service = ResumeService(auth_service)
    ai_service = AiService()

    # Fetch resume data
    logger.info("\n--- Fetching Resume Data ---")
    resume_data = resume_service.fetch_resume_data()
    logger.info(f"Original resume size: {len(json.dumps(resume_data))} characters")

    # Test generic optimization
    logger.info("\n--- Testing Generic Optimization ---")
    optimized_data = ai_service.optimise_generic(resume_data)
    logger.info(f"Optimized resume size: {len(optimized_data)} characters")

    # Verify it's valid JSON
    logger.info("\n--- Validating Optimized JSON ---")
    try:
        parsed = json.loads(optimized_data)
        logger.info(f"Parsed successfully! Top-level keys: {list(parsed.keys())}")

        # Check for _issues
        if "_issues" in parsed:
            if parsed["_issues"]:
                log_message(logger, f"AI reported issues: {parsed['_issues']}", LogType.ERROR)
            else:
                log_message(logger, "No issues reported by AI", LogType.SUCCESS)

        log_message(logger, "Optimized data is valid JSON", LogType.SUCCESS)

    except json.JSONDecodeError as e:
        log_message(logger, f"Optimized data is not valid JSON: {e}", LogType.ERROR)
        logger.error(f"First 500 chars: {optimized_data[:500]}")
        raise

    log_message(logger, "AI service test completed!", LogType.SUCCESS)

except Exception as e:
    log_message(logger, f"Test failed: {e}", LogType.ERROR)
    import traceback
    traceback.print_exc()
    exit(1)