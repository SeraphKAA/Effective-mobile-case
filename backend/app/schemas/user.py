from pydantic import BaseModel


class UserOutDto(BaseModel):
    nickname: str
    emaiL: str
