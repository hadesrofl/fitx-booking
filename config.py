import os

RUN_TEST = os.environ.get("RUN_TEST", "false").lower() == "true"

AUTH_USERNAME = os.environ.get("FITX_USERNAME", "")
AUTH_PASSWORD = os.environ.get("FITX_PASSWORD", "")
STUDIO_ID = os.environ.get("FITX_STUDIO_ID", "1293643060")
COURSE_NAME = os.environ.get("FITX_COURSE_NAME", "functional x")
