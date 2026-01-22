"""
Configuration file for Bank Teller Chatbot
Centralized settings with environment variable support
"""
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# Directory Configuration
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"
TESTS_DIR = BASE_DIR / "tests"

# ============================================================================
# Model Paths
# ============================================================================
INTENT_MODEL_PATH = MODELS_DIR / "intent_classifier.h5"
VECTORIZER_PATH = MODELS_DIR / "vectorizer.pkl"
LABEL_ENCODER_PATH = MODELS_DIR / "label_encoder.pkl"
INTENT_MAPPING_PATH = DATA_DIR / "intent_mapping.json"

# Training data paths
TRAIN_DATA_PATH = PROCESSED_DATA_DIR / "train.csv"
VAL_DATA_PATH = PROCESSED_DATA_DIR / "val.csv"
TEST_DATA_PATH = PROCESSED_DATA_DIR / "test.csv"

# ============================================================================
# Database Configuration
# ============================================================================
DATABASE_PATH = DATA_DIR / "bank_demo.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"

# ============================================================================
# ML Model Configuration
# ============================================================================
# TF-IDF Settings
MAX_FEATURES = 5000
NGRAM_RANGE = (1, 2)  # Unigrams and bigrams
MIN_DF = 2  # Minimum document frequency
MAX_DF = 0.95  # Maximum document frequency

# Neural Network Architecture
EMBEDDING_DIM = 128
HIDDEN_UNITS = [256, 128]
DROPOUT_RATE = 0.3
ACTIVATION = 'relu'
OUTPUT_ACTIVATION = 'softmax'

# Training Configuration
LEARNING_RATE = 0.001
BATCH_SIZE = 32
EPOCHS = 50
VALIDATION_SPLIT = 0.15
EARLY_STOPPING_PATIENCE = 5
REDUCE_LR_PATIENCE = 3
REDUCE_LR_FACTOR = 0.5

# ============================================================================
# Intent Classification Settings
# ============================================================================
CONFIDENCE_THRESHOLD = 0.60  # Main threshold for accepting predictions
LOW_CONFIDENCE_THRESHOLD = 0.40  # Below this, trigger fallback
MAX_INFERENCE_TIME_MS = 100  # Maximum allowed inference time

# ============================================================================
# Entity Extraction Patterns
# ============================================================================
# Regex patterns for Pakistani banking context
ENTITY_PATTERNS = {
    # Amount: 5000, 5,000, 5000.50, 5,000.50
    'amount': r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b',
    
    # Pakistani IBAN: PK36SCBL0000001123456702
    'account_number': r'\bPK\d{2}[A-Z]{4}\d{16}\b',
    
    # Pakistani mobile: 03001234567
    'phone': r'\b03\d{9}\b',
    
    # Date patterns: DD/MM/YYYY, DD-MM-YYYY
    'date': r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b',
    
    # Name extraction (after common prepositions)
    'recipient': r'(?:to|for|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
}

# Bill types (predefined list)
VALID_BILL_TYPES = [
    'electricity', 'gas', 'water', 'internet', 'mobile', 
    'phone', 'cable', 'utility', 'utilities'
]

# Account types
VALID_ACCOUNT_TYPES = ['savings', 'current', 'salary', 'checking']

# ============================================================================
# Banking Business Rules
# ============================================================================
MIN_TRANSFER_AMOUNT = 1
MAX_TRANSFER_AMOUNT = 1_000_000
MIN_BILL_AMOUNT = 1
MAX_BILL_AMOUNT = 500_000
CURRENCY = "PKR"

# Transaction types
TRANSACTION_TYPES = ['transfer', 'withdrawal', 'deposit', 'bill_payment']

# ============================================================================
# Session Management
# ============================================================================
SESSION_TIMEOUT_MINUTES = 30
MAX_CONVERSATION_TURNS = 10
MAX_FAILED_ATTEMPTS = 3
SESSION_CLEANUP_INTERVAL = 300  # seconds (5 minutes)

# ============================================================================
# API Configuration
# ============================================================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "True").lower() == "true"

# CORS settings
CORS_ORIGINS: List[str] = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# ============================================================================
# Logging Configuration
# ============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "chatbot.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_MAX_BYTES = 10_485_760  # 10MB
LOG_BACKUP_COUNT = 5

# ============================================================================
# Dataset Configuration
# ============================================================================
DATASET_NAME = "bitext/Bitext-retail-banking-llm-chatbot-training-dataset"
DATASET_SPLIT_RATIOS = {
    'train': 0.70,
    'val': 0.15,
    'test': 0.15
}

# ============================================================================
# NLP Settings (for future spaCy integration)
# ============================================================================
SPACY_MODEL = "en_core_web_sm"
USE_SPACY = False  # Set to True when spaCy is installed and needed

# ============================================================================
# Helper Functions
# ============================================================================

def create_directories():
    """Create all necessary directories if they don't exist"""
    directories = [
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        MODELS_DIR,
        LOGS_DIR,
        TESTS_DIR / "unit",
        TESTS_DIR / "integration",
        TESTS_DIR / "fixtures",
    ]
    
    created = []
    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(str(directory.relative_to(BASE_DIR)))
    
    # Create .gitkeep files to preserve empty directories in git
    for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
        gitkeep = directory / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
    
    if created:
        print(f"✅ Created {len(created)} directories:")
        for dir_path in created:
            print(f"   - {dir_path}/")
    else:
        print("✅ All directories already exist")
    
    return created

def verify_configuration():
    """Verify that all critical paths exist"""
    issues = []
    
    if not BASE_DIR.exists():
        issues.append(f"Base directory not found: {BASE_DIR}")
    
    if not BACKEND_DIR.exists():
        issues.append(f"Backend directory not found: {BACKEND_DIR}")
    
    if issues:
        print("❌ Configuration issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    print("✅ Configuration verified successfully")
    return True

def print_configuration():
    """Print current configuration summary"""
    print("\n" + "="*60)
    print("BANK TELLER CHATBOT - CONFIGURATION SUMMARY")
    print("="*60)
    print(f"\n📁 Base Directory: {BASE_DIR}")
    print(f"📊 Dataset: {DATASET_NAME}")
    print(f"🤖 Model Architecture: {HIDDEN_UNITS}")
    print(f"🎯 Confidence Threshold: {CONFIDENCE_THRESHOLD}")
    print(f"💾 Database: {DATABASE_PATH}")
    print(f"🌐 API: http://{API_HOST}:{API_PORT}")
    print(f"📝 Logs: {LOG_FILE}")
    print("="*60 + "\n")

if __name__ == "__main__":
    print_configuration()
    create_directories()
    verify_configuration()