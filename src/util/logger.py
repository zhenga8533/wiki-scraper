import logging
import os


class Logger:
    def __init__(self, name: str, path: str, log: bool):
        """
        Initialize a logger object.

        :param: name - Name of the logger
        :param: path - Path to the log file
        :param: log - Whether to log to file or not
        :return: None
        """

        self.logging = log
        self.logger = self.setup_logger(name, path)
        self.info(f"Logger.__init__: Logger initialized with name '{name}' and path '{path}'")

    def setup_logger(self, name: str, path: str) -> logging.Logger:
        """
        Setup a logger with a file and stream handler.

        :param: name - Name of the logger
        :param: path - Path to the log file
        :return: Logger object
        """

        # Create log directory if it doesn't exist
        log_dir = "/".join(path.split("/")[:-1])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Setup logger
        logger = logging.getLogger(name)
        if not logger.hasHandlers():
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

            # File handler
            file_handler = logging.FileHandler(path, mode="w", encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # Stream handler
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        return logger

    def set_logging(self, logging: bool) -> None:
        """
        Set the logging attribute.

        :param: logging - Whether to log or not
        :return: None
        """

        self.logging = logging

    def log(self, level: int, message: str) -> None:
        """
        Log a message to the logger.

        :param: level - Logging level
        :param: message - Message to log
        :return: None
        """

        if self.logging:
            if type(level) is str:
                level = getattr(logging, level.upper())
                if not isinstance(level, int):
                    raise ValueError(f"Invalid log level: {level}")
            self.logger.log(level, message)

    def info(self, message: str) -> None:
        """
        Log an info message to the logger.

        :param: message - Message to log
        :return: None
        """

        if self.logging:
            self.log(logging.INFO, message)

    def warning(self, message: str) -> None:
        """
        Log a warning message to the logger.

        :param: message - Message to log
        :return: None
        """

        if self.logging:
            self.log(logging.WARNING, message)

    def error(self, message: str) -> None:
        """
        Log an error message to the logger.

        :param: message - Message to log
        :return: None
        """

        if self.logging:
            self.log(logging.ERROR, message)

    def critical(self, message: str) -> None:
        """
        Log a critical message to the logger.

        :param: message - Message to log
        :return: None
        """

        if self.logging:
            self.log(logging.CRITICAL, message)

    def debug(self, message: str) -> None:
        """
        Log a debug message to the logger.

        :param: message - Message to log
        :return: None
        """

        if self.logging:
            self.log(logging.DEBUG, message)
