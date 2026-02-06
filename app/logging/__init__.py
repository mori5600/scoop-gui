from pathlib import Path
from typing import Final

from logly import _LoggerProxy, logger

LOG_DIR_PATH: Final[Path] = Path(__file__).parent.parent / "logs"


def init_logger() -> _LoggerProxy:
    """Initialize the logger.

    This function initializes the logger by configuring it with the desired settings.

    """
    LOG_DIR_PATH = Path(__file__).parent.parent / "logs"

    logger.configure(
        level="INFO",
        color=True,
        console=True,
        auto_sink=True,
    )

    logger.add(f"{LOG_DIR_PATH}/app.log", size_limit="10MB", retention=3)

    logger.success("logger initialized!")

    return logger
