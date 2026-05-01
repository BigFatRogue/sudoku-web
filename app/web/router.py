from fastapi import APIRouter, Request
from app.core.templates import templates


web_router = APIRouter(tags=['WEB / FRONT'])

@web_router.get(
        path='/', 
        summary='Начальная страница')
async def index(request: Request):
    return templates.TemplateResponse(name='index.html', request=request)


@web_router.get(
        path='/login',
        summary='Страница авторизации')
async def login(request: Request):
    return templates.TemplateResponse(name='authentication.html', request=request)


