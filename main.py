#!/usr/bin/env python

import argparse
import sys
from typing import Optional

from config.settings import settings
from services.auth_service import AuthService
from services.resume_service import ResumeService
from services.ai_service import AiService
from services.generator_service import GeneratorService
from services.notification_service import NotificationService
from utils.helpers import get_job_description, validate_resume_name, validate_template_id, format_mode_name
from utils.logger import setup_logger, log_message, log_step, LogType

def parse_args():
  parser = argparse.ArgumentParser(
    description="Resume automation pipeline - optimise and generate resumes using AI.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  # Generic optimisation
  python main.py --mode generic

  # JD-optimised with direct text
  python main.py --mode job-description --jd "Software Engineer position..."

  # JD-optimised with file
  python main.py --mode job-description --jd job_description.txt

  # Custom template and name
  python main.py --mode generic --template-id templates/modern.cshtml --resume-name John_Doe_2024
    """
  )

  parser.add_argument(
    "--mode",
    type=str,
    choices=["generic", "job-description"],
    default="generic",
    help="Optimisation mode: 'generic' for general optimisation, 'job-description' for JD-tailored."
  )
  parser.add_argument(
    "--jd",
    type=str,
    default="no",
    help="Job description (text or file path). Default: 'no' (generic mode)"
  )

  parser.add_argument(
    "--template-id",
    type=str,
    default=settings.DEFAULT_TEMPLATE_ID,
    help=f"Template ID for resume generation. Default: {settings.DEFAULT_TEMPLATE_ID}"
  )

  parser.add_argument(
    "--resume-name",
    type=str,
    default=settings.DEFAULT_RESUME_NAME,
    help=f"Output resume filename. Default: {settings.DEFAULT_RESUME_NAME}"
  )

  parser.add_argument(
    "--debug",
    action="store_true",
    help="Enable debug logging"
  )

  return parser.parse_args()

def validate_args(args):
  logger = setup_logger()

  if not validate_template_id(args.template_id):
    log_message(logger, f"Invalid template ID: {args.template_id}", LogType.ERROR)
    log_message(logger, "Template ID must be in format: templates/name.cshtml", LogType.ERROR)
    sys.exit(1)

  if not validate_resume_name(args.resume_name):
    log_message(logger, f"Invalid resume name: {args.resume_name}", LogType.ERROR)
    log_message(logger, "Resume name cannot contain: / \\ : * ? \" < > |", LogType.ERROR)
    sys.exit(1)

  if args.mode == "job-description" and args.jd.lower() == "no":
    log_message(logger, "Job description mode requires --jd to be provided", LogType.ERROR)
    log_message(logger, "Either provide a job description or use --mode generic", LogType.ERROR)
    sys.exit(1)

def run_pipeline(mode: str, jd_input: Optional[str], template_id: str, resume_name: str, debug: bool = False):
  import logging
  logger = setup_logger(level=logging.DEBUG if debug else logging.INFO)

  print("\n" + "=" * 70)
  print(" " * 20 + "RESUME AUTOMATION PIPELINE")
  print("=" * 70 + "\n")

  logger.info(f"Mode: {format_mode_name(mode)}")
  logger.info(f"Template: {template_id}")
  logger.info(f"Resume Name: {resume_name}")

  auth_service = None
  notification_service = NotificationService()

  try:
    log_step(logger, 0, "Validating config")
    settings.validate()
    log_message(logger, "Configs validated", LogType.SUCCESS)

    notification_service.send_pipeline_start_notification(mode=mode)

    # Step#01: auth
    log_step(logger, 1, "Authentication")
    auth_service = AuthService()
    auth_service.authenticate()

    # Step#02: fetch resume data
    log_step(logger, 2, "Fetching resume data")
    resume_service = ResumeService(auth_service)
    resume_data = resume_service.fetch_resume_data()

    # Step#03: AI P1
    log_step(logger, 3, "AI P1")
    ai_service = AiService()
    optimised_data = ai_service.optimise_generic(resume_data)

    # Step#04 AI P2 (if jd provided)
    if mode == "job-description":
      log_step(logger, 4, "AI P2")
      job_description = get_job_description(jd_input)

      if not job_description:
        log_message(logger, "Failed to get job description", LogType.ERROR)
        raise ValueError("Job description is required for job-description mode")

      logger.info(f"Job description length: {len(job_description)} chars")

      optimised_data = ai_service.optimise_with_jd(optimised_data, job_description)
    else:
      logger.info("Skipping AI P2")

    # Step#05: resume generation
    log_step(logger, 5, "Generating resume PDF")
    generator_service = GeneratorService(auth_service)
    job_id = generator_service.generate_resume(
      resume_data=optimised_data,
      template_id=template_id,
      resume_name=resume_name
    )

    # Step#06: polling
    log_step(logger, 6, "Polling")
    result = generator_service.poll_job_status(job_id)

    # Step#07: handle result
    log_step(logger, 7, "Processing result")

    if result.get("status") == "success":
      pdf_url = result.get("pdfUrl", "No URL provided")

      log_message(logger, "Resume generated successfully", LogType.SUCCESS)
      logger.info(f"\n{'=' * 70}")
      logger.info(f"PDF URL: {pdf_url}")
      logger.info(f"{'=' * 70}\n")

      notification_service.send_success_notification(pdf_url=pdf_url, mode=mode)

      print("\n SUCCESS! your resume is ready!")
      print(f"Download: {pdf_url}\n")

    else:
      error = result.get("error", "Unknown error")
      log_message(logger, f"Resume generation failed: {error}", LogType.ERROR)

      notification_service.send_failure_notification(error=error, mode=mode)

      print("\n FAILED! resume generation unsuccessful!")
      print(f"Error: {error}\n")
      sys.exit(1)

  except KeyboardInterrupt:
    log_message(logger, "Pipeline interrupted by user", LogType.WARNING)
    notification_service.send_message("Pipeline interrupted by user")
    print("\n\nPipeline interrupted by user\n")
    sys.exit(1)
  except Exception as e:
    log_message(logger, f"Pipeline failed: {e}")

    if debug:
      import traceback
      traceback.print_exc()

    error_msg = str(e)
    notification_service.send_failure_notification(error=error_msg, mode=mode)

    print(f"\n pipeline failed: {e}\n")
    sys.exit(1)

  finally:
    if auth_service:
      logger.debug("Cleaning up access token....")

def main():
  args = parse_args()

  validate_args(args)

  run_pipeline(
    mode=args.mode,
    jd_input=args.jd,
    template_id=args.template_id,
    resume_name=args.resume_name,
    debug=args.debug
  )

if __name__ == "__main__":
  main()