from fastapi import HTTPException, status


def api_error(status_code: int, code: str, message: str, details: dict | None = None) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"error": {"code": code, "message": message, "details": details or {}}},
    )


NOT_FOUND = status.HTTP_404_NOT_FOUND
VALIDATION = status.HTTP_422_UNPROCESSABLE_ENTITY
