from services.auth_service import AuthService
from services.resume_service import ResumeService
from utils.logger import setup_logger, log_step, log_message, LogType
import json

logger = setup_logger()

log_step(logger, 2, "Testing Resume Service")

try:
    # Create auth service and authenticate
    logger.info("Initializing authentication...")
    auth_service = AuthService()
    auth_service.authenticate()

    # Create resume service
    logger.info("\nInitializing resume service...")
    resume_service = ResumeService(auth_service)

    # Fetch resume data
    logger.info("\n--- Fetching Resume Data ---")
    resume_data = resume_service.fetch_resume_data()

    # Display resume structure
    logger.info("\nResume data structure:")
    logger.info(f"  Type: {type(resume_data)}")
    logger.info(f"  Top-level keys: {list(resume_data.keys())}")

    # Pretty print a sample of the data
    logger.info("\nSample of resume data (first 500 chars):")
    sample = json.dumps(resume_data, indent=2)[:500]
    logger.info(f"\n{sample}...")

    # Test stringification
    logger.info("\n--- Testing JSON Stringification ---")
    json_string = resume_service.stringify_resume_data(resume_data)
    logger.info(f"JSON string length: {len(json_string)} characters")
    logger.info(f"First 100 chars: {json_string[:100]}...")

    # Verify it can be parsed back
    logger.info("\n--- Verifying JSON is valid ---")
    parsed_back = json.loads(json_string)
    if parsed_back == resume_data:
        log_message(logger, "JSON stringification is reversible!", LogType.SUCCESS)
    else:
        log_message(logger, "JSON mismatch after parse!", LogType.ERROR)

    log_message(logger, "Resume service test completed!", LogType.SUCCESS)

except Exception as e:
    log_message(logger, f"Test failed: {e}", LogType.ERROR)
    import traceback
    traceback.print_exc()
    exit(1)