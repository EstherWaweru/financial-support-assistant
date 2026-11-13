from typing import Any

from fastapi import FastAPI, Request

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response
from fastapi.responses import JSONResponse


from app.core.custom_exception import ServiceException
from app.api.routes.api import api_router

from app.core.config import get_settings

settings = get_settings()


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.project_name, version=settings.version, debug=True
    )

    @application.exception_handler(ServiceException)
    async def unicorn_exception_handler(exc: ServiceException) -> Response:
        return JSONResponse(status_code=exc.args[0], content={"detail": exc.args[1]})

    @application.middleware("http")
    async def CSPMiddleware(request: Request, call_next: Any) -> Response:
        response = await call_next(request)
        values = ";".join(
            [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net/npm/",
                "style-src https://cdn.jsdelivr.net/npm/",
                "img-src 'self' data: https://fastapi.tiangolo.com/",
                "frame-ancestors 'none'",
            ]
        )
        response.headers["Content-Security-Policy-Report-Only"] = values
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = "max-age=63072000"
        return response

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix=settings.api_version)

    return application


# get a plain app for testing
test_app = get_application()

application = test_app
