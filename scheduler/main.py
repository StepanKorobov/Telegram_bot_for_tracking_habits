import logging

import config
from scheduler import start_scheduler

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("main: scheduler service starting")
    start_scheduler()
    logger.info("main: scheduler service stopped")
