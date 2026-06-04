import sentry_sdk
from dotenv import load_dotenv

from app.config.logging_config import setup_logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from app.config.database import Base
from app.config.settings import settings
from app.routers.order import order_router

setup_logging()

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[StarletteIntegration(), FastApiIntegration()],
    )

app = FastAPI(title="Order Service")

Instrumentator().instrument(app).expose(app, include_in_schema=False)

# Create all tables
# Base.metadata.create_all(bind=engine)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    # load env variables
    load_dotenv()


app.include_router(order_router)
