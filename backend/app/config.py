"""Application configuration settings and environment variable management."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecretKey(SecretStr):
    """SecretStr that evaluates truthiness on secret value and stringifies safely."""

    def __bool__(self) -> bool:
        return bool(self.get_secret_value())

    def __str__(self) -> str:
        return self.get_secret_value()


class Settings(BaseSettings):
    """Typed application configuration with environment variable resolution."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = Field(default="AuraPulse AI", description="Application service name")
    VERSION: str = Field(default="2.2.0", description="Semantic service version")
    API_V1_STR: str = Field(default="/api/v1", description="API v1 route prefix")

    # Gemini / GenAI Keys
    GEMINI_API_KEY: SecretKey | str = Field(default="", description="Gemini API Key for Flash generation and Copilot")
    GEMINI_FLASH_MODEL: str = Field(default="gemini-2.5-flash", description="Gemini Flash Model ID")

    # Google Services Keys
    GOOGLE_MAPS_API_KEY: SecretKey | str = Field(
        default="", description="Google Maps Places API key for verified vendor search"
    )
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(
        default="", description="Filesystem path to Google service account credentials JSON"
    )

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=10, ge=1, le=1000, description="Max requests per minute")
    RATE_LIMIT_PER_DAY: int = Field(default=100, ge=1, le=50000, description="Max requests per day")
    TRUSTED_PROXY_HOPS: int = Field(default=1, ge=0, le=10, description="Trusted reverse proxy hops")

    # HTTP Server Settings
    PORT: int = Field(default=8000, ge=1, le=65535, description="Port number to bind HTTP server")
    HOST: str = Field(default="0.0.0.0", description="Host interface address to bind HTTP server")
    ALLOWED_ORIGIN: str = Field(default="", description="Comma-separated custom allowed CORS origins")

    @property
    def gemini_api_key_str(self) -> str:
        return str(self.GEMINI_API_KEY)

    @property
    def google_maps_api_key_str(self) -> str:
        return str(self.GOOGLE_MAPS_API_KEY)


settings = Settings()
