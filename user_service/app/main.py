import asyncio
import threading

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from app.telemetry import TELEMETRY

app = FastAPI(title="User Service", telemetry=TELEMETRY)

toggle_on = False
lock = threading.Lock()


class UserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str


@app.get("/users/{id}/", response_model=UserResponse)
async def retrieve_user_by_id(id: str) -> UserResponse:
    """
    Returns a user by id
    :return:
    """
    global toggle_on

    if not id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please provide a user id")

    if id == "7c11e1ce2741":
        await asyncio.sleep(0.3)

        return UserResponse(id="7c11e1ce2741", first_name="John", last_name="Doe")

    elif id == "e6f24d7d1c7e":
        await asyncio.sleep(0.3)

        with lock:
            toggle_on = not toggle_on

            if toggle_on:
                return UserResponse(id="e6f24d7d1c7e", first_name="Jane", last_name="Doe")
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error"
                )

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
