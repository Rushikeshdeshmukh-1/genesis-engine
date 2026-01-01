from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_reload: bool = True
    
    # Database Configuration (SQLite)
    database_url: str = "sqlite+aiosqlite:///./idea_engine.db"
    
    # Google Gemini API Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash"
    gemini_timeout: int = 90
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout: int = 120
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    
    # Research Agent Configuration (Simplified)
    scraper_max_retries: int = 3
    scraper_rate_limit_delay: int = 2
    
    # Web Search Configuration
    serpapi_api_key: Optional[str] = None
    
    # Scoring Configuration
    scoring_factors_config: str = "config/scoring_factors.yaml"
    scoring_batch_size: int = 10
    scoring_parallel_workers: int = 4
    
    # Report Generation
    report_output_dir: str = "./reports"
    report_formats: str = "pdf,markdown"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    jwt_secret: str = "your-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Feature Flags
    enable_idea_generation: bool = True
    enable_research_agent: bool = True
    enable_scoring_engine: bool = True
    enable_report_generation: bool = True
    
    # Performance Tuning
    max_concurrent_ideas: int = 50
    max_research_depth: int = 3
    cache_ttl_seconds: int = 3600
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def report_formats_list(self) -> list[str]:
        """Parse report formats into a list."""
        return [fmt.strip() for fmt in self.report_formats.split(",")]


# Global settings instance
settings = Settings()
