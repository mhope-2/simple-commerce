from fastapi import HTTPException, status


def is_retryable(exc: BaseException) -> bool:
    """Retry server errors and timeouts from a dependency, not client errors such as 404."""
    return isinstance(exc, HTTPException) and (
        exc.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR
        or exc.status_code == status.HTTP_408_REQUEST_TIMEOUT
    )
