import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_NAME: str = os.getenv("DB_NAME")

    AMQP_URI: str = os.getenv("AMQP_URI")
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST")
    EXCHANGE: str = os.getenv("EXCHANGE")
    EXCHANGE_TYPE: str = os.getenv("EXCHANGE_TYPE")
    ROUTING_KEY: str = os.getenv("ROUTING_KEY")
    RABBITMQ_DEFAULT_USER: str = os.getenv("RABBITMQ_DEFAULT_USER")
    RABBITMQ_DEFAULT_PASS: str = os.getenv("RABBITMQ_DEFAULT_PASS")

    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL")
    PRODUCT_SERVICE_URL: str = os.getenv("PRODUCT_SERVICE_URL")

    # SECRET_KEY: str = os.getenv("SECRET_KEY")

    class Config:
        env_file = ".env"


settings = Settings()
