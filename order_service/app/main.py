import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from app.config.database import engine
from app.config.logging_config import setup_logging
from app.config.settings import settings
from app.config.telemetry import TELEMETRY, instrument_libraries
from app.routers.order import order_router

setup_logging()
instrument_libraries(engine)

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        # Error tracking only: no traces_sample_rate, so Sentry tracing stays off and
        # traces come from OpenTelemetry.
        integrations=[StarletteIntegration(), FastApiIntegration()],
    )

app = FastAPI(title="Order Service", telemetry=TELEMETRY)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(order_router)
