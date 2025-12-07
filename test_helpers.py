from utils.helpers import (
    read_file,
    is_file_path,
    get_job_description,
    validate_template_id,
    validate_resume_name,
    format_mode_name
)
from utils.logger import setup_logger, log_step, log_message, LogType
import os

logger = setup_logger()

log_step(logger, 6, "Testing Helper Utilities")

try:
    # Create test files
    logger.info("\n--- Creating Test Files ---")
    test_jd_file = "test_job_description.txt"
    test_jd_content = """
Software Engineer Position

We are looking for a skilled software engineer with experience in:
- Python programming
- REST APIs
- Cloud platforms (AWS/Azure)
- Docker and Kubernetes

Requirements:
- 3+ years of experience
- Bachelor's degree in Computer Science
- Strong problem-solving skills
    """.strip()

    with open(test_jd_file, 'w') as f:
        f.write(test_jd_content)

    log_message(logger, f"Created test file: {test_jd_file}", LogType.SUCCESS)

    # Test 1: is_file_path
    logger.info("\n--- Test 1: is_file_path() ---")
    tests = [
        (test_jd_file, True, "Existing file"),
        ("non_existent.txt", False, "Non-existent file"),
        ("just some text", False, "Plain text"),
        ("/path/to/file.txt", False, "Path that doesn't exist")
    ]

    for value, expected, description in tests:
        result = is_file_path(value)
        status = "✅" if result == expected else "❌"
        logger.info(f"  {status} {description}: is_file_path('{value}') = {result}")

    # Test 2: read_file
    logger.info("\n--- Test 2: read_file() ---")
    content = read_file(test_jd_file)
    logger.info(f"  Content length: {len(content)} characters")
    logger.info(f"  First 100 chars: {content[:100]}...")

    # Test 3: get_job_description
    logger.info("\n--- Test 3: get_job_description() ---")

    # Test with "no"
    jd = get_job_description("no")
    logger.info(f"  get_job_description('no') = {jd}")

    # Test with direct text
    jd = get_job_description("This is a direct job description")
    logger.info(f"  Direct text = {jd[:50]}...")

    # Test with file path
    jd = get_job_description(test_jd_file)
    logger.info(f"  File path = {jd[:50]}...")

    # Test 4: validate_template_id
    logger.info("\n--- Test 4: validate_template_id() ---")
    templates = [
        ("templates/resume_template.cshtml", True),
        ("templates/modern.cshtml", True),
        ("invalid_template", False),
        ("", False)
    ]

    for template, expected in templates:
        result = validate_template_id(template)
        status = "✅" if result == expected else "❌"
        logger.info(f"  {status} '{template}' = {result}")

    # Test 5: validate_resume_name
    logger.info("\n--- Test 5: validate_resume_name() ---")
    names = [
        ("Vikramaditya_Pratap_Singh", True),
        ("My_Resume_2024", True),
        ("Resume/with/slash", False),
        ("Resume:with:colon", False),
        ("", False)
    ]

    for name, expected in names:
        result = validate_resume_name(name)
        status = "✅" if result == expected else "❌"
        logger.info(f"  {status} '{name}' = {result}")

    # Test 6: format_mode_name
    logger.info("\n--- Test 6: format_mode_name() ---")
    modes = ["generic", "jd-optimized", "job-description", "unknown"]

    for mode in modes:
        formatted = format_mode_name(mode)
        logger.info(f"  '{mode}' → '{formatted}'")

    # Cleanup
    logger.info("\n--- Cleanup ---")
    os.remove(test_jd_file)
    log_message(logger, f"Removed test file: {test_jd_file}", LogType.SUCCESS)

    log_message(logger, "Helper utilities test completed!", LogType.SUCCESS)

except Exception as e:
    log_message(logger, f"Test failed: {e}", LogType.ERROR)
    import traceback
    traceback.print_exc()

    # Cleanup on error
    if os.path.exists(test_jd_file):
        os.remove(test_jd_file)

    exit(1)