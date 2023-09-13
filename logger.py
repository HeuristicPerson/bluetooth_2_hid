import logging

def get_logger() -> logging.Logger:
    # Create a logger
    logger = logging.getLogger('bluetooth_2_usb')

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Create a handler for writing log messages to a file
        file_handler = logging.FileHandler('/var/log/bluetooth_2_usb/bluetooth_2_usb.log')

        # Create a handler for writing log messages to stdout
        stdout_handler = logging.StreamHandler()

        # Create a formatter and set it for both handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stdout_handler.setFormatter(formatter)

        # Add both handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stdout_handler)

    return logger
