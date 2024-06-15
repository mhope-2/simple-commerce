import os
from dataclasses import dataclass
from typing import Optional

import httpx
from fastapi import HTTPException, status
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_fixed


@dataclass
class User:
    """Class to represent a User object"""

    id: str
    first_name: str
    last_name: str


class UserService:
    """Utility class to define requests to the User service"""

    @staticmethod
    @retry(
        stop=(stop_after_attempt(3) | stop_after_delay(5)),  # stop after 3 attempts or 5 seconds
        wait=wait_fixed(2)  # wait 2 seconds between retries
    )
    async def fetch_user(id: str) -> Optional[User]:
        user_service_url = os.getenv("USER_SERVICE_URL")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{user_service_url}/{id}/") # returns a 307 without trailing backslash
                if response.status_code == status.HTTP_200_OK:
                    data = response.json()
                    return User(**data)

                elif response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="User service returned a server error",
                    )

                elif response.status_code == status.HTTP_404_NOT_FOUND:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User service returned a 404"
                    )

                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Received a non-200 status code from UserService",
                    )
            except httpx.HTTPError:
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail="Request to User Service timed out",
                )

            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Request to User Service failed: {str(e)}",
                )
