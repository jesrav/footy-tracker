import os
from http.client import HTTPException
from pathlib import Path

import fastapi
from fastapi import UploadFile, File
from fastapi_chameleon import template
from starlette import status
from starlette.requests import Request

from infrastructure import cookie_auth
from models.user import UserRead
from services import user_service, tracking_service
from viewmodels.account.account_viewmodel import AccountViewModel
from viewmodels.account.edit_viewmodel import AccountEditViewModel
from viewmodels.account.login_viewmodel import LoginViewModel
from viewmodels.account.register_viewmodel import RegisterViewModel

router = fastapi.APIRouter()


@router.get('/account')
@template()
async def index(request: Request):
    vm = AccountViewModel(request)
    await vm.load()
    return vm.to_dict()


@router.get('/account/edit/')
@template()
async def index(request: Request):
    vm = AccountViewModel(request)
    await vm.load()
    return vm.to_dict()


@router.post('/account/edit/')
@template()
async def index(request: Request):
    vm = AccountEditViewModel(request)
    await vm.load_form()

    if vm.error:
        return vm.to_dict()

    # Login user
    response = fastapi.responses.RedirectResponse(url='/account', status_code=status.HTTP_302_FOUND)
    cookie_auth.set_auth(response, vm.user_id)
    return response


# @router.post("/account/upload_profile_image/")
# async def upload_profile_image(user_id, file: UploadFile = File(...)):
#     file_suffix = Path(file.filename).suffix
#     name = f"profile_pic_{user_id}{file_suffix}"
#     return await upload_to_azure(file, name)
#
#
# async def upload_to_azure(file: UploadFile, file_name: str):
#     connect_str = os.environ["BLOB_STORAGE_CON_STR"]
#     blob_service_client = BlobServiceClient.from_connection_string(connect_str)
#     container_name = os.environ["BLOB_PROFILE_IMAGE_CONTAINER"]
#     async with blob_service_client:
#         container_client = blob_service_client.get_container_client(container_name)
#         try:
#             blob_client = container_client.get_blob_client(file_name)
#             f = await file.read()
#             await blob_client.upload_blob(f)
#
#         except Exception as e:
#             print(e)
#             return HTTPException(401, "Error uploading profile image")
#     return


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

    # Create the account
    account = await user_service.create_account(vm.nickname, vm.email, vm.password)

    # Login user
    response = fastapi.responses.RedirectResponse(url='/account', status_code=status.HTTP_302_FOUND)
    cookie_auth.set_auth(response, account.id)
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

    user = await user_service.login_user(vm.email, vm.password)
    if not user:
        vm.error = "The account does not exist or the password is wrong."
        return vm.to_dict()

    resp = fastapi.responses.RedirectResponse(f'/user/{user.id}', status_code=status.HTTP_302_FOUND)
    cookie_auth.set_auth(resp, user.id)

    return resp


@router.get('/account/logout')
def logout():
    response = fastapi.responses.RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    cookie_auth.logout(response)

    return response