import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel
from tenacity import retry, retry_if_exception, stop_after_attempt, stop_after_delay, wait_random_exponential

from app.client.retry import is_retryable
from app.config.metrics import count_retry
from app.config.settings import settings


class User(BaseModel):
    id: str
    first_name: str
    last_name: str


class UserService:
    """Utility class to define requests to the User service"""

    @staticmethod
    @retry(
        stop=(stop_after_attempt(3) | stop_after_delay(5)),  # stop after 3 attempts or 5 seconds
        wait=wait_random_exponential(multiplier=1, max=10),
        before_sleep=count_retry("user-service"),
        retry=retry_if_exception(is_retryable),
        reraise=True,  # raise the last HTTPException (with its status), not tenacity's RetryError
    )
    async def fetch_user(id: str) -> User | None:
        user_service_url = settings.USER_SERVICE_URL

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
