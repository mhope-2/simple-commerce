import threading
import time

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

app = FastAPI(title="User Service")

toggle_status_code = False
lock = threading.Lock()

@app.get("/users/{id}/")
async def retrieve(id: str):
    """
    Returns a user by id
    :return:
    """
    global toggle_status_code

    if not id:
        return JSONResponse(content={"message": "Please provide a user id"})

    if id == "7c11e1ce2741":
        time.sleep(0.3)

        return JSONResponse(
            status_code=200,
            content={"id": "7c11e1ce2741", "first_name": "John", "last_name": "Doe"}
        )

    elif id == "e6f24d7d1c7e":
        time.sleep(0.3)

        with lock:
            if toggle_status_code:
                response = JSONResponse(
                    content={"id": "e6f24d7d1c7e", "first_name": "Jane", "last_name": "Doe"}
                )
            else:
                response = HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error"
                )

            toggle_status_code = not toggle_status_code

        if isinstance(response, HTTPException):
            raise response

        return response

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


