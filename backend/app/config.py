from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ESI_BASE_URL: str = "https://esi.evetech.net/latest"
    REGION_ID: int = 10000002
    TAX_RATE: float = 0.08
    BROKER_FEE: float = 0.03
    VERTEX_PROJECT_ID: str = "your-gcp-project-id"
    VERTEX_ENDPOINT_ID: str = "your-model-endpoint-id"
    DATABASE_URL: str = "sqlite:////tmp/test.db"

    class Config:
        env_file = ".env"

settings = Settings()