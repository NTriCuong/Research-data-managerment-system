from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.reference.user_device import UserDevice
from app.schemas.notification import RegisterTokenRequest

router = APIRouter()
from sqlalchemy import select

@router.post("/register-token")
async def register_token(
    payload: RegisterTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(UserDevice).where(
        UserDevice.user_id == payload.user_id
    )

    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.fcm_token = payload.fcm_token
        existing.device_name = payload.device_name

        await db.commit()
        await db.refresh(existing)

        return {"message": "Token updated"}

    new_device = UserDevice(
        user_id=payload.user_id,
        fcm_token=payload.fcm_token,
        device_name=payload.device_name
    )

    db.add(new_device)
    await db.commit()
    await db.refresh(new_device)

    return {"message": "Token registered"}