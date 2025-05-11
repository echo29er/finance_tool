"""
Logging configuration module
"""
import os
import logging

def setup_logging(log_to_file=False, log_level=logging.INFO):
    """
    Set up logging configuration
    
    Args:
        log_to_file (bool): Whether to log to a file
        log_level (int): Logging level to use
    """
    # Create logs directory if it doesn't exist
    if log_to_file and not os.path.exists("../logs"):
        os.makedirs("../logs")
    
    handlers = [logging.StreamHandler()]  # Always log to console
    
    if log_to_file:
        handlers.append(logging.FileHandler("../logs/chards_scraper.log"))
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    # Return the logger
    return logging.getLogger()