"""Small project logger helper.

Provides get_logger(name) which returns a logger that writes INFO+ to
logs/answers.log and also to console. Safe to import multiple times.
"""
import logging
import os
from logging.handlers import RotatingFileHandler


LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "answers.log")


def _ensure_log_dir():
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception:
        # best-effort; if creation fails we'll still try console logging
        pass


def get_logger(name: str = "taxmate") -> logging.Logger:
    """Return a configured logger for the project.

    This function is idempotent: calling it multiple times won't add
    duplicate handlers.
    """
    _ensure_log_dir()
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding handlers repeatedly
    if not getattr(logger, "_configured_for_taxmate", False):
        # File handler
        try:
            fh = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=2, encoding="utf-8")
            fh.setLevel(logging.INFO)
            fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
            logger.addHandler(fh)
        except Exception:
            # If file handler can't be created, continue with console only
            pass

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(ch)

        # Mark configured
        logger._configured_for_taxmate = True

    return logger
