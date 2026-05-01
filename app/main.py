
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.web.router import web_router
from app.api.v1.api import router_api_v1
from app.core.templates import templates
from app.core.exceptions import ValidationError


app = FastAPI()
app.include_router(web_router)
app.include_router(router_api_v1, prefix='/api/v1')


app.mount("/web/static", StaticFiles(directory=Path(__file__).parent / "web/static"), name="static")
app.state.templates = templates


@app.exception_handler(ValidationError)
async def validation_handler(request, exc):
    return JSONResponse(
        status_code = 400,
        content={"detail": str(exc)}
    )