from services.auth_service import AuthService
from services.resume_service import ResumeService
from services.ai_service import AiService
from services.generator_service import GeneratorService
from utils.logger import setup_logger, log_step, log_message, LogType
from config.settings import settings

logger = setup_logger()

log_step(logger, 4, "Testing Generator Service")

try:
    # Setup services
    logger.info("Setting up services...")
    auth_service = AuthService()
    auth_service.authenticate()

    resume_service = ResumeService(auth_service)
    ai_service = AiService()
    generator_service = GeneratorService(auth_service)

    # Fetch and optimize resume
    logger.info("\n--- Fetching & Optimizing Resume ---")
    resume_data = resume_service.fetch_resume_data()
    optimized_data = ai_service.optimise_generic(resume_data)

    # Generate resume
    logger.info("\n--- Generating Resume PDF ---")
    job_id = generator_service.generate_resume(
        resume_data=optimized_data,
        template_id=settings.DEFAULT_TEMPLATE_ID,
        resume_name=settings.DEFAULT_RESUME_NAME
    )

    logger.info(f"\nJob ID: {job_id}")

    # Poll for completion
    logger.info("\n--- Polling for Completion ---")
    result = generator_service.poll_job_status(job_id)

    # Display result
    logger.info("\n--- Final Result ---")
    logger.info(f"Status: {result.get('status')}")

    if result.get("status") == "success":
        pdf_url = result.get("pdfUrl", "No URL provided")
        logger.info(f"PDF URL: {pdf_url}")
        log_message(logger, "Resume generated successfully!", LogType.SUCCESS)
    else:
        error = result.get("error", "Unknown error")
        logger.info(f"Error: {error}")
        log_message(logger, "Resume generation failed", LogType.ERROR)

    log_message(logger, "Generator service test completed!", LogType.SUCCESS)

except TimeoutError as e:
    log_message(logger, f"Timeout: {e}", LogType.ERROR)
    exit(1)
except Exception as e:
    log_message(logger, f"Test failed: {e}", LogType.ERROR)
    import traceback
    traceback.print_exc()
    exit(1)