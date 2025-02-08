import logging
from pathlib import Path

import colorlog


def setup_logger(log_file: str) -> logging.Logger:
    """Set up a logger with a file handler and a stream handler."""
    # Create the log file directory
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    color_formatter = colorlog.ColoredFormatter(
        "%(asctime)s - %(log_color)s%(levelname)s%(reset)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )

    # Create a file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Create a stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(color_formatter)
    logger.addHandler(stream_handler)

    return logger


LOG = setup_logger("logs/deepseek_fin_qa.log")
