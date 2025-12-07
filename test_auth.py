from services.auth_service import AuthService
from utils.logger import setup_logger, log_step, log_message, LogType

logger = setup_logger()

log_step(logger, 1, "Testing Authentication Service")

try:
    # Create auth service instance
    auth_service = AuthService()

    logger.info("Initial authentication state:")
    logger.info(f"  Is authenticated: {auth_service.is_authenticated()}")
    logger.info(f"  Access token: {auth_service.access_token}")

    # First authentication
    logger.info("\n--- First Authentication Attempt ---")
    token1 = auth_service.authenticate()
    logger.info(f"Token received: {token1[:20]}...")
    logger.info(f"Is authenticated: {auth_service.is_authenticated()}")

    # Second authentication (should use cached token)
    logger.info("\n--- Second Authentication Attempt (should use cache) ---")
    token2 = auth_service.authenticate()
    logger.info(f"Token received: {token2[:20]}...")

    # Verify same token
    if token1 == token2:
        log_message(logger, "Token persistence working! Same token reused.", LogType.SUCCESS)
    else:
        log_message(logger, "Token mismatch! Persistence not working.", LogType.ERROR)

    # Test get_auth_headers
    logger.info("\n--- Testing get_auth_headers() ---")
    headers = auth_service.get_auth_headers()
    logger.info(f"Headers: {headers}")

    # Test logout
    logger.info("\n--- Testing logout() ---")
    auth_service.logout()
    logger.info(f"Is authenticated after logout: {auth_service.is_authenticated()}")

    log_message(logger, "Authentication service test completed!", LogType.SUCCESS)

except Exception as e:
    log_message(logger, f"Test failed: {e}", LogType.ERROR)
    import traceback
    traceback.print_exc()
    exit(1)