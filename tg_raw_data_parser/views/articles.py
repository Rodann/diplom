from fastapi import APIRouter
from fastapi.responses import JSONResponse


article_router = APIRouter()


@article_router.get('/article/categories', response_class=JSONResponse)
async def get_categories():  # получение категорий
    return {'info': 'data'}


@article_router.get('/article/{category}', response_class=JSONResponse)
async def find_article_category(category):  # получение статей по категории
    return {'info': 'data'}


@article_router.get('/article/{name}', response_class=JSONResponse)
async def find_article_name(name):  # поиск статей по теме (как в поисковике)
    return {'info': 'data'}
