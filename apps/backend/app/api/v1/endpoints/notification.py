from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.auth.user import User
from app.models.reference.user_device import UserDevice
from app.schemas.notification import RegisterTokenRequest
from app.core.permissions import get_current_user

router = APIRouter()


@router.post("/register-token")
async def register_token(
    payload: RegisterTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        insert(UserDevice)
        .values(
            user_id=current_user.user_id,
            fcm_token=payload.fcm_token,
            device_name=payload.device_name,
        )
        .on_conflict_do_update(
            index_elements=["fcm_token"],
            set_={
                "user_id": current_user.user_id,
                "device_name": payload.device_name,
            },
        )
    )
    await db.execute(stmt)
    await db.commit()
    return {"message": "Token registered"}
