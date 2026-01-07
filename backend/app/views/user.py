from fastapi import APIRouter
from app.schemas import UserOutDto

router = APIRouter(prefix="/user", tags=["Users"])

@router.post("", response_model = UserOutDto)
async def getUserInfo(user_id: int):
    pass