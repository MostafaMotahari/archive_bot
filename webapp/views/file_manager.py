from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.authentication import requires
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette.templating import Jinja2Templates

from telegram.database.serializers import file_in_storage_cloud_serializer, directory_serializer
from telegram.database.engine import async_session
from telegram.database import models
from webapp.utils.auth_tools import validate_init_data


template = Jinja2Templates(directory="webapp/templates/")

@requires(['authenticated'])
async def file_manager_home(request: Request):
    init_data = request.query_params.get("initData", None)
    if not init_data: return
    if validate_init_data(init_data):
        request.session['user']
        return template.TemplateResponse(request=request, name="file_manager_template.html")
    return

@requires(['authenticated'])
async def file_manager_retrieve(request: Request):
    all_data = []
    dir_pk = request.path_params.get("dir_pk", None)
    tg_id = request.path_params.get("tg_id", None)
    if dir_pk: dir_pk = int(dir_pk)

    async with async_session() as session:
        dirs = await session.scalars(select(models.Directory).options(
            selectinload(models.Directory.sub_directories, recursion_depth=1)).options(
                selectinload(models.Directory.files)
                ).where(models.Directory.parent_dir_pk == dir_pk))

        for dir in dirs.all():
            dir_data = directory_serializer(dir)
            dir_data["items_count"] = dir.items_count
            all_data.append(dir_data)

        files = await session.scalars(select(models.FileInCloudStorage).options(
            selectinload(models.FileInCloudStorage.uploaded_by)).options(
                selectinload(models.FileInCloudStorage.likes)
                ).where(models.FileInCloudStorage.directory_pk == dir_pk))

        user = await session.scalars(select(models.User).where(models.User.telegram_id == tg_id))
        user = user.one() or None
                                     
        for file in files.all():
            all_data.append(file_in_storage_cloud_serializer(file, user))

    return JSONResponse({"items": all_data})


async def like_toggle_file(request: Request, id: int, telegram_id: str):
    async with async_session() as session:
        file = session.scalars(select(models.FileInCloudStorage).where(models.FileInCloudStorage.id == id)).one()
        user = session.scalars(select(models.User).where(models.User.telegram_id == telegram_id)).one()
        if not file: return
        if not user: return




# async def file_manager_view(request: Request):
#     file = File()
