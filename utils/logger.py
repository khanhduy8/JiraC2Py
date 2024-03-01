import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_logger(name, level=logging.INFO, max_size=10485760, backup_count=5):
    """Function to setup rotating logger"""
    # Get the directory containing the logger utility module
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")

    # Create the logs directory if it does not exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Get current date for the log filename
    current_date = datetime.now().strftime("%m-%d-%Y")
    log_file = f"{name}-{current_date}.log"

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = RotatingFileHandler(
        os.path.join(log_dir, log_file), 
        maxBytes=max_size, 
        backupCount=backup_count
    )
    handler.setFormatter(formatter)
    
    # Setup stream handler for stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(stream_handler)

    return logger

