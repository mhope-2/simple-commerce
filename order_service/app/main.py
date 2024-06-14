from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import Base, engine
from app.routers.order import order_router

app = FastAPI()

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
async def on_startup():
    load_dotenv()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(order_router)