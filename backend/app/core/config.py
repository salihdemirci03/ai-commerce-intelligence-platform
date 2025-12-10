"""
Application configuration using Pydantic Settings.
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # ==========================================================================
    # APPLICATION
    # ==========================================================================
    APP_NAME: str = "Commerce Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # ==========================================================================
    # API
    # ==========================================================================
    API_BASE_URL: str = "http://localhost:8000"
    API_V1_PREFIX: str = "/api/v1"
    FRONTEND_URL: str = "http://localhost:3000"

    # ==========================================================================
    # DATABASE
    # ==========================================================================
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/commerce_intelligence"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_ECHO: bool = False

    # ==========================================================================
    # REDIS
    # ==========================================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    REDIS_MAX_CONNECTIONS: int = 50

    # ==========================================================================
    # SECURITY & AUTH
    # ==========================================================================
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

    # Password requirements
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # ==========================================================================
    # AI & LLM
    # ==========================================================================
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"

    # Alternative LLM
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"

    # Vector Store
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "commerce-intelligence"

    # Agent Configuration
    AGENT_TIMEOUT_SECONDS: int = 300
    AGENT_MAX_RETRIES: int = 3
    AGENT_CONCURRENT_LIMIT: int = 5

    # ==========================================================================
    # MARKETPLACE INTEGRATIONS
    # ==========================================================================
    # Amazon
    AMAZON_SP_API_ACCESS_KEY: Optional[str] = None
    AMAZON_SP_API_SECRET_KEY: Optional[str] = None
    AMAZON_SP_API_REFRESH_TOKEN: Optional[str] = None
    AMAZON_SP_API_REGION: str = "us-east-1"
    AMAZON_MARKETPLACE_ID: str = "ATVPDKIKX0DER"

    # Shopify
    SHOPIFY_API_KEY: Optional[str] = None
    SHOPIFY_API_SECRET: Optional[str] = None
    SHOPIFY_ACCESS_TOKEN: Optional[str] = None
    SHOPIFY_SHOP_NAME: Optional[str] = None
    SHOPIFY_API_VERSION: str = "2024-01"

    # Etsy
    ETSY_API_KEY: Optional[str] = None
    ETSY_API_SECRET: Optional[str] = None
    ETSY_ACCESS_TOKEN: Optional[str] = None
    ETSY_SHOP_ID: Optional[str] = None

    # ==========================================================================
    # PAYMENTS (STRIPE)
    # ==========================================================================
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # Subscription Plans
    STRIPE_BASIC_PRICE_ID: str = "price_basic_monthly"
    STRIPE_PRO_PRICE_ID: str = "price_pro_monthly"
    STRIPE_MASTER_PRICE_ID: str = "price_master_monthly"

    # Add-on Prices (in cents)
    DEEP_REPORT_STANDARD_PRICE: int = 1000  # $10
    DEEP_REPORT_PREMIUM_PRICE: int = 3000  # $30
    DEEP_REPORT_ENTERPRISE_PRICE: int = 5000  # $50

    # ==========================================================================
    # EXTERNAL DATA SOURCES
    # ==========================================================================
    SERPAPI_KEY: Optional[str] = None
    TIKTOK_API_KEY: Optional[str] = None
    TIKTOK_API_SECRET: Optional[str] = None
    WORLD_BANK_API_KEY: Optional[str] = None
    CENSUS_API_KEY: Optional[str] = None

    # ==========================================================================
    # CLOUD STORAGE
    # ==========================================================================
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "commerce-intelligence-reports"
    S3_ENDPOINT_URL: Optional[str] = None

    # Supabase (alternative)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None

    # ==========================================================================
    # EMAIL
    # ==========================================================================
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "noreply@commerce-intelligence.com"
    EMAIL_FROM_NAME: str = "Commerce Intelligence Platform"

    # Templates
    WELCOME_EMAIL_TEMPLATE_ID: Optional[str] = None
    FORECAST_COMPLETE_TEMPLATE_ID: Optional[str] = None
    SUBSCRIPTION_TEMPLATE_ID: Optional[str] = None

    # ==========================================================================
    # BACKGROUND JOBS
    # ==========================================================================
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True

    # Task Timeouts
    FORECAST_TASK_TIMEOUT: int = 600
    REPORT_GENERATION_TIMEOUT: int = 1800
    DATA_SYNC_TIMEOUT: int = 3600

    # ==========================================================================
    # RATE LIMITING
    # ==========================================================================
    RATE_LIMIT_BASIC: int = 100
    RATE_LIMIT_PRO: int = 500
    RATE_LIMIT_MASTER: int = 2000
    RATE_LIMIT_ADMIN: int = 10000
    RATE_LIMIT_ANONYMOUS: int = 10
    RATE_LIMIT_WINDOW: int = 60

    # ==========================================================================
    # MONITORING
    # ==========================================================================
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: Optional[str] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0

    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090

    # Logging
    LOG_FILE_PATH: str = "./logs/app.log"
    LOG_FILE_MAX_SIZE: int = 10485760  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5
    LOG_FORMAT: str = "json"

    # ==========================================================================
    # FEATURE FLAGS
    # ==========================================================================
    ENABLE_MARKETPLACE_INTEGRATIONS: bool = True
    ENABLE_DEEP_REPORTS: bool = True
    ENABLE_OAUTH: bool = True
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    ENABLE_WEBHOOKS: bool = True
    ENABLE_API_KEYS: bool = True
    ENABLE_ADMIN_PANEL: bool = True
    ENABLE_AI_CONTENT_GENERATION: bool = True
    ENABLE_PREDICTIVE_ANALYTICS: bool = True
    ENABLE_REALTIME_UPDATES: bool = False

    # ==========================================================================
    # CORS
    # ==========================================================================
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://your-domain.com"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # ==========================================================================
    # DATA PROCESSING
    # ==========================================================================
    CITY_DATA_UPDATE_INTERVAL: int = 86400  # 24 hours
    MIN_CITY_POPULATION: int = 50000
    MAX_CITIES_PER_FORECAST: int = 100

    # Forecast Configuration
    DEFAULT_FORECAST_HORIZON_MONTHS: int = 12
    MIN_DEMAND_SCORE_THRESHOLD: int = 30
    COMPETITION_WEIGHT: float = 0.3
    DEMAND_WEIGHT: float = 0.4
    PROFITABILITY_WEIGHT: float = 0.3

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("CELERY_ACCEPT_CONTENT", mode="before")
    @classmethod
    def parse_celery_content(cls, v):
        """Parse Celery accept content."""
        if isinstance(v, str):
            return [content.strip() for content in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        """Check if environment is production."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if environment is development."""
        return self.ENVIRONMENT == "development"


# Create global settings instance
settings = Settings()
