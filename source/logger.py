import logging
import sys
from logging import Logger


def get_logger() -> Logger:
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(funcName)s:%(lineno)s >>> %(message)s',
        level=logging.INFO,
        handlers=[logging.StreamHandler(stream=sys.stdout)],
    )

    return logging.getLogger()


logger = get_logger()
