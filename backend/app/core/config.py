import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR.parent / "data"
UPLOAD_DIR = DATA_DIR / "images"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

class ModelSettings(BaseModel):
    provider: str = os.getenv("OPEN_MODEL_PROVIDER", "mock")
    name: str = os.getenv("OPEN_MODEL_NAME", "qwen-vl-small")
    api_key: str = os.getenv("OPEN_MODEL_API_KEY", "")
    base_url: str = os.getenv("OPEN_MODEL_BASE_URL", "")

class CommercialModelASettings(BaseModel):
    provider: str = os.getenv("COMMERCIAL_MODEL_A_PROVIDER", "mock")
    name: str = os.getenv("COMMERCIAL_MODEL_A_NAME", "gpt-4o-mini")
    api_key: str = os.getenv("COMMERCIAL_MODEL_A_API_KEY", "")
    base_url: str = os.getenv("COMMERCIAL_MODEL_A_BASE_URL", "")

class CommercialModelBSettings(BaseModel):
    provider: str = os.getenv("COMMERCIAL_MODEL_B_PROVIDER", "mock")
    name: str = os.getenv("COMMERCIAL_MODEL_B_NAME", "claude-3-5-sonnet")
    api_key: str = os.getenv("COMMERCIAL_MODEL_B_API_KEY", "")
    base_url: str = os.getenv("COMMERCIAL_MODEL_B_BASE_URL", "")

class Settings(BaseModel):
    app_name: str = "ADAPTIX-FARM"
    app_env: str = os.getenv("APP_ENV", "development")
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "127.0.0.1")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'adaptix_farm.db'}")
    
    # AI Models
    open_model: ModelSettings = ModelSettings()
    commercial_a: CommercialModelASettings = CommercialModelASettings()
    commercial_b: CommercialModelBSettings = CommercialModelBSettings()
    
    # RAG Settings
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "local_semantic")
    vector_db_path: str = str(VECTORSTORE_DIR)
    
    # Image Quality Thresholds
    min_blur_variance: float = 60.0      # Below this indicates blur
    min_brightness: float = 35.0         # Below this indicates underexposed
    max_brightness: float = 230.0        # Above this indicates overexposed
    min_contrast: float = 25.0           # Below this indicates low contrast
    min_resolution: int = 150            # Minimum width/height in px

settings = Settings()
