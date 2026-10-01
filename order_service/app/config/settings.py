from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_NAME: str
    # Log every SQL statement (very noisy; queries are visible as spans in traces).
    DB_ECHO: bool = False

    AMQP_URI: str
    RABBITMQ_HOST: str
    EXCHANGE: str
    EXCHANGE_TYPE: str
    ROUTING_KEY: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str

    USER_SERVICE_URL: str
    PRODUCT_SERVICE_URL: str

    SENTRY_DSN: str | None = None


settings = Settings()
