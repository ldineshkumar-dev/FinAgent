"""
Configuration settings for MFT Finance AI Assistant
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"
SRC_DIR = PROJECT_ROOT / "src"

# Database settings
DB_PATH = DATA_DIR / "finance_module.duckdb"
SCHEMA_PATH = DATA_DIR / "db_schema.txt"

# Model configurations - Optimized for CPU
class ModelConfig:
    # Local SLM for SQL generation - Use lightweight model
    SLM_MODEL = "distilbert-base-uncased"  # Much smaller fallback model
    SLM_DEVICE = "cpu"  # Force CPU usage
    SLM_MAX_TOKENS = 256
    SLM_TEMPERATURE = 0.1
    USE_FALLBACK_SQL = True  # Use template-based SQL generation primarily
    
    # Embedding model for semantic search - Lighter model
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE = "cpu"  # Force CPU
    EMBEDDING_BATCH_SIZE = 8  # Smaller batch for CPU

# Vector database settings - Optimized for column-based search
class VectorConfig:
    COLLECTION_NAME = "finance_schema"
    SIMILARITY_THRESHOLD = 0.3  # Lower threshold for better column matching
    MAX_RELEVANT_TABLES = 5
    MAX_RELEVANT_COLUMNS = 10  # Add column limit
    DISTANCE_METRIC = "cosine"
    PRIORITIZE_COLUMN_SEARCH = True  # Use column-first search strategy

# Query processing settings
class QueryConfig:
    MAX_SQL_LENGTH = 1000
    TIMEOUT_SECONDS = 30
    MAX_RESULT_ROWS = 1000

# UI settings
class UIConfig:
    PAGE_TITLE = "MFT Finance AI - Efficient Edition"
    PAGE_ICON = "🚀"
    THEME = "dark"
    
# Logging settings
class LogConfig:
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ENABLE_PERFORMANCE_LOGGING = True

# Performance settings
class PerformanceConfig:
    CACHE_EMBEDDINGS = True
    CACHE_MODELS = True
    BATCH_PROCESSING = True
    PARALLEL_PROCESSING = True

# Create directories if they don't exist
def ensure_directories():
    """Ensure all required directories exist"""
    for directory in [DATA_DIR, EMBEDDINGS_DIR]:
        directory.mkdir(exist_ok=True)

# Validation
def validate_config():
    """Validate configuration settings"""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    
    ensure_directories()
    return True

if __name__ == "__main__":
    validate_config()
    print("✅ Configuration validated successfully!")
