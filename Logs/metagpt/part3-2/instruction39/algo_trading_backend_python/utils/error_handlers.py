from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from schemas import ErrorResponse
from utils.logger import logger

def handle_auth_error(error: Exception) -> HTTPException:
    logger.error(f"Authentication error: {str(error)}")
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=str(error)
    )

def handle_fund_error(error: Exception) -> HTTPException:
    logger.error(f"Fund details error: {str(error)}")
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=str(error)
    )

def handle_general_error(error: Exception) -> HTTPException:
    logger.error(f"General error: {str(error)}")
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(error)
    )

def register_error_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f"HTTPException: {exc.detail} (status_code={exc.status_code})")
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(error="HTTPException", detail=exc.detail).dict(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Exception: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(error="InternalServerError", detail=str(exc)).dict(),
        )