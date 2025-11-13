import aiohttp
import os
from fastapi import HTTPException, status

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8001")

async def get_user_from_user_service(user_id: str):
    """Вложенная функция для вызова User Service"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{USER_SERVICE_URL}/api/v1/users/{user_id}") as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="User service is unavailable"
                    )
    except aiohttp.ClientError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to user service"
        )