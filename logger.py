import logging


class SimpleLogger:
    def __init__(self, name, log_file, level=logging.INFO):
        """
        Initializes the simple logger.

        Args:
            name (str): Name of the logger.
            log_file (str): File to which logs will be written.
            level (int): Logging level (default is logging.INFO).
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        """
        Returns the logger instance.

        Returns:
            logging.Logger: Configured logger instance.
        """
        return self.logger

    def set_level(self, level):
        """
        Sets the logging level for the logger and its handlers.

        Args:
            level (int): Logging level.
        """
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)

