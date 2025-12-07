from services.notification_service import NotificationService
from utils.logger import setup_logger, log_step, log_message, LogType
import time

logger = setup_logger()

log_step(logger, 5, "Testing Notification Service")

try:
    # Create notification service
    notification_service = NotificationService()

    # Test 1: Pipeline start notification
    logger.info("\n--- Test 1: Pipeline Start Notification ---")
    success = notification_service.send_pipeline_start_notification(mode="generic")
    if success:
        log_message(logger, "Pipeline start notification sent", LogType.SUCCESS)
    else:
        log_message(logger, "Failed to send pipeline start notification", LogType.ERROR)

    # Wait a bit to avoid rate limits
    time.sleep(2)

    # Test 2: Success notification
    logger.info("\n--- Test 2: Success Notification ---")
    test_url = "https://example.com/test_resume.pdf"
    success = notification_service.send_success_notification(
        pdf_url=test_url,
        mode="generic"
    )
    if success:
        log_message(logger, "Success notification sent", LogType.SUCCESS)
    else:
        log_message(logger, "Failed to send success notification", LogType.ERROR)

    # Wait a bit
    time.sleep(2)

    # Test 3: Failure notification
    logger.info("\n--- Test 3: Failure Notification ---")
    success = notification_service.send_failure_notification(
        error="Test error message",
        mode="generic"
    )
    if success:
        log_message(logger, "Failure notification sent", LogType.SUCCESS)
    else:
        log_message(logger, "Failed to send failure notification", LogType.ERROR)

    # Wait a bit
    time.sleep(2)

    # Test 4: Custom message
    logger.info("\n--- Test 4: Custom Message ---")
    success = notification_service.send_message(
        "🧪 This is a test message from the Resume Automation Pipeline!"
    )
    if success:
        log_message(logger, "Custom message sent", LogType.SUCCESS)
    else:
        log_message(logger, "Failed to send custom message", LogType.ERROR)

    log_message(logger, "Notification service test completed!", LogType.SUCCESS)
    logger.info("\n📱 Check your Telegram to see the messages!")

except Exception as e:
    log_message(logger, f"Test failed: {e}", LogType.ERROR)
    import traceback
    traceback.print_exc()
    exit(1)