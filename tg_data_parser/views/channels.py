from fastapi import APIRouter
from fastapi.responses import JSONResponse
from source.mongo import add_new_channel, remove_channel


channels_router = APIRouter()


@channels_router.post('/channel/add/{name}', response_class=JSONResponse)
async def add_channel(name):  # добавление нового канала
    return add_new_channel(link=name)


@channels_router.delete('/channel/delete/{name}', response_class=JSONResponse)
async def delete_channel(name):  # удаление канала
    return remove_channel(name)
