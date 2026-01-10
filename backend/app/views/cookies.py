from fastapi import APIRouter, Depends, Response, Request

import app.controllers.user as user_controller
import app.controllers.cookies as cookies_controller
from app.models.user import UserModel


router = APIRouter(prefix="/cookie", tags=["Cookies"])

@router.delete("/delete", status_code=204)
async def Logout(response: Response):
    """Удаление куки user_id, role, access_token, refresh_token"""
    await cookies_controller.delete_cookies(response)


@router.get("/get")
async def Get_cookie(name_cookie: str, request: Request):
    """Получение значений куки через название куки"""
    await cookies_controller.get_cookie_by_name(name_cookie, request)