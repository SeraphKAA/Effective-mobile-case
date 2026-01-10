from fastapi import Response, Request


async def delete_cookies(response: Response) -> None:
    response.delete_cookie(key="user_id")
    response.delete_cookie(key="role")
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")


async def get_cookie_by_name(name_cookie: str, request: Request):
    # Если передан один параметр строки
    if isinstance(name_cookie, str):
        return request.cookies.get(name_cookie)

    # В случае ошибки
    else:
        return {"error": "Invalid input type"}
