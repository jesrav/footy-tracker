import os
import uuid
from pathlib import Path

import fastapi
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob.aio import BlobServiceClient, ContainerClient
from fastapi import UploadFile, File, Form
from fastapi_chameleon import template
from starlette import status
from starlette.requests import Request

from infrastructure import cookie_auth
from models.user import UserUpdate
from services import user_service
from viewmodels.account.account_viewmodel import AccountViewModel
from viewmodels.account.edit_viewmodel import AccountEditViewModel
from viewmodels.account.login_viewmodel import LoginViewModel
from viewmodels.account.register_viewmodel import RegisterViewModel

router = fastapi.APIRouter()


async def upload_to_azure(file: UploadFile, file_name: str):
    connect_str = os.environ["BLOB_STORAGE_CON_STR"]
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_name = os.environ["BLOB_PROFILE_IMAGE_CONTAINER"]
    async with blob_service_client:
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(file_name)
        f = await file.read()
        await blob_client.upload_blob(f, overwrite=True)


async def delete_from_azure(file_name: str):
    connect_str = os.environ["BLOB_STORAGE_CON_STR"]
    container_name = os.environ["BLOB_PROFILE_IMAGE_CONTAINER"]
    container_service_client = ContainerClient.from_connection_string(conn_str=connect_str, container_name=container_name)
    async with container_service_client:
        try:
            await container_service_client.delete_blob(blob=file_name)
        except ResourceNotFoundError:
            pass


@router.get('/account')
@template()
async def index(request: Request):
    vm = AccountViewModel(request)
    if not vm.is_logged_in:
        return fastapi.responses.RedirectResponse('/account/login', status_code=status.HTTP_302_FOUND)
    await vm.load()
    return vm.to_dict()


@router.get('/account/edit/')
@template()
async def edit(request: Request):
    vm = AccountEditViewModel(request)
    if not vm.is_logged_in:
        return fastapi.responses.RedirectResponse('/account/login', status_code=status.HTTP_302_FOUND)
    await vm.load()
    return vm.to_dict()


@router.post('/account/edit/')
@template()
async def edit(request: Request):
    vm = AccountEditViewModel(request)
    await vm.load_form()

    if vm.error:
        return vm.to_dict()

    # Login user
    response = fastapi.responses.RedirectResponse(url='/account', status_code=status.HTTP_302_FOUND)
    return response


@router.get("/account/update_profile_image")
@template()
async def update_profile_image(request: Request):
    vm = AccountViewModel(request)
    if not vm.is_logged_in:
        return fastapi.responses.RedirectResponse('/account/login', status_code=status.HTTP_302_FOUND)
    await vm.load()
    return vm.to_dict()


@router.post("/account/update_profile_image")
@template()
async def update_profile_image(request: Request, file: UploadFile = File(...)):
    vm = AccountViewModel(request)
    await vm.load()
    file_suffix = Path(file.filename).suffix
    guid = uuid.uuid4()
    storage_base_url = os.environ["BLOB_STORAGE_BASE_URL"]
    name = f"profile_pic_{vm.user_id}_{guid}{file_suffix}"

    old_user_details = await user_service.get_me(bearer_token=vm.bearer_token)

    # Upload new profile image
    await upload_to_azure(file, name)

    # Update user info
    _ = await user_service.update_user(
        user_updates=UserUpdate(profile_pic_path=storage_base_url + name),
        bearer_token=vm.bearer_token
    )

    # delete old user image
    _ = await delete_from_azure(old_user_details.profile_pic_path[len(storage_base_url):])

    return fastapi.responses.RedirectResponse(url='/account', status_code=status.HTTP_302_FOUND)


@router.get('/account/register')
@template()
def register(request: Request):
    vm = RegisterViewModel(request)
    return vm.to_dict()


@router.post('/account/register')
@template()
async def register(request: Request):
    vm = RegisterViewModel(request)
    await vm.load()

    if vm.error:
        return vm.to_dict()
    me = await user_service.get_me(bearer_token=vm.bearer_token)
    response = fastapi.responses.RedirectResponse(url='/account', status_code=status.HTTP_302_FOUND)
    cookie_auth.set_user_id_cookie(response, me.id)
    cookie_auth.set_bearer_token_cookie(response, vm.bearer_token)
    return response


@router.get('/account/login')
@template(template_file='account/login.pt')
def login_get(request: Request):
    vm = LoginViewModel(request)
    return vm.to_dict()


@router.post('/account/login')
@template(template_file='account/login.pt')
async def login_post(request: Request):

    vm = LoginViewModel(request)
    await vm.load()

    if vm.error:
        return vm.to_dict()

    bearer_token = await user_service.login_user(vm.email, vm.password)

    me = await user_service.get_me(bearer_token=bearer_token)
    resp = fastapi.responses.RedirectResponse(f'/user/{me.id}', status_code=status.HTTP_302_FOUND)
    cookie_auth.set_user_id_cookie(resp, me.id)
    cookie_auth.set_bearer_token_cookie(resp, bearer_token)

    return resp


@router.get('/account/logout')
def logout():
    response = fastapi.responses.RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    cookie_auth.logout(response)
    return response
