"""
Enhanced Logging Configuration for Backend
Logs all events, errors, and API calls to both file and console
"""

import logging
import os
from pathlib import Path
from datetime import datetime
import json

# Create logs directory
LOG_DIR = Path(__file__).parent.parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Log file paths
LOG_FILE = LOG_DIR / 'bank_chatbot_backend.log'
ERROR_LOG_FILE = LOG_DIR / 'bank_chatbot_errors.log'
API_LOG_FILE = LOG_DIR / 'bank_chatbot_api.log'

# Log format
DETAILED_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
SIMPLE_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging():
    """Setup comprehensive logging for the backend"""
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(SIMPLE_FORMAT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs (DEBUG level)
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(DETAILED_FORMAT)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # File handler for errors only (ERROR level)
    error_handler = logging.FileHandler(ERROR_LOG_FILE, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # API logger
    api_logger = logging.getLogger('api')
    api_logger.setLevel(logging.DEBUG)
    api_file_handler = logging.FileHandler(API_LOG_FILE, encoding='utf-8')
    api_file_handler.setFormatter(logging.Formatter(DETAILED_FORMAT))
    api_logger.addHandler(api_file_handler)
    
    logging.info('=' * 80)
    logging.info('BANK TELLER CHATBOT - BACKEND SERVER STARTED')
    logging.info('=' * 80)
    logging.info(f'Log files:')
    logging.info(f'  - Main logs: {LOG_FILE}')
    logging.info(f'  - Error logs: {ERROR_LOG_FILE}')
    logging.info(f'  - API logs: {API_LOG_FILE}')
    logging.info('=' * 80)
    
    return root_logger, api_logger


# Setup logging when module is imported
root_logger, api_logger = setup_logging()


def log_api_request(method: str, path: str, data: dict = None):
    """Log API request"""
    api_logger.info(f'API REQUEST: {method} {path}', extra={'data': data})


def log_api_response(method: str, path: str, status_code: int, response_data: dict = None):
    """Log API response"""
    api_logger.info(f'API RESPONSE: {method} {path} - Status {status_code}', 
                   extra={'response': response_data})


def log_api_error(method: str, path: str, error: str, status_code: int = 500):
    """Log API error"""
    api_logger.error(f'API ERROR: {method} {path} - Status {status_code}: {error}')


def log_database_operation(operation: str, table: str, details: str = ''):
    """Log database operations"""
    logging.debug(f'DB OPERATION: {operation} on {table} - {details}')


def log_model_inference(intent: str, confidence: float, entities: dict = None):
    """Log model inference results"""
    logging.info(f'MODEL INFERENCE: Intent={intent}, Confidence={confidence:.2f}, Entities={entities}')


def log_dialogue_state(state: str, context: dict = None):
    """Log dialogue state changes"""
    logging.debug(f'DIALOGUE STATE: {state}', extra={'context': context})
