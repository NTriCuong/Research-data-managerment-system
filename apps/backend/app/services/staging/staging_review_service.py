import logging
from datetime import datetime, timezone
from uuid import UUID

from app.core.exceptions import BadRequestException, NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks
from app.database.session import AsyncSessionLocal


from app.models.auth.user import User
from app.models.enum import NotificationType, WorkflowStatus
from app.models.staging.stg_research_object import StgResearchObject
from app.repositories.staging_review_repository import StagingReviewRepository
from app.schemas.auth import MessageResponse
from app.schemas.staging_metadata import StagingResearchObjectOut
from app.schemas.staging_review import ForwardToApprovalRequest, RequestRevisionRequest
from app.services.logs.audit_service import audit_service
from app.services.logs.workflow_service import workflow_service
from app.core.config import settings
from app.services.notification.notification_service import notification_service, push_to_users, push_to_roles


logger = logging.getLogger(__name__)


class StagingReviewService:

    @staticmethod
    def _assert_pending_review(staging_obj: StgResearchObject) -> None:
        if staging_obj.workflow_status != WorkflowStatus.pending_review:
            raise BadRequestException("Chỉ bản ghi ở trạng thái pending_review mới có thể được xét duyệt")

    async def list_pending_review_records(
        self,
        db: AsyncSession,
        *,
        limit: int,
        offset: int,
    ) -> list[StagingResearchObjectOut]:
        repo = StagingReviewRepository(db)
        rows = await repo.list_pending_review_records(limit=limit, offset=offset)
        return [StagingResearchObjectOut.model_validate(x) for x in rows]

    async def request_revision(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID,
        payload: RequestRevisionRequest,
        background_tasks: BackgroundTasks,
        current_user: User,
    ) -> MessageResponse:

        repo = StagingReviewRepository(db)

        try:
            obj = await repo.get_by_id(staging_id)

            if obj is None or obj.deleted_at is not None:
                raise NotFoundException("Không tìm thấy bản ghi tạm")
            self._assert_pending_review(obj)
            if not payload.note.strip():
                raise BadRequestException(
                    "Lý do yêu cầu chỉnh sửa không được để trống"
                )
            old_status = obj.workflow_status
            now = datetime.now(timezone.utc)
            obj.workflow_status = WorkflowStatus.revision_required
            obj.reviewed_by = current_user.user_id
            obj.reviewed_at = now
            obj.updated_at = now
            obj.revision_note = payload.note

            await workflow_service.write_history(
                db,
                staging_id=obj.staging_id,
                performed_by=current_user.user_id,
                from_status=old_status,
                to_status=WorkflowStatus.revision_required,
                action_code="REQUEST_REVISION",
                action_note=payload.note,
            )

            await audit_service.write_log(
                db,
                actor_user_id=current_user.user_id,
                action_code="REQUEST_REVISION",
                target_schema="staging",
                target_table="research_objects",
                target_id=obj.staging_id,
                old_value={
                    "workflow_status": old_status.value
                },
                new_value={
                    "workflow_status": WorkflowStatus.revision_required.value,
                    "revision_note": payload.note,
                },
                message="Reviewer requested revision",
            )

            await db.commit()

            title = "Có bài nghiên cứu cần chỉnh sửa"
            message = (
                f"Người kiểm duyệt yêu cầu chỉnh sửa "
                f"bài nghiên cứu '{obj.title}': {payload.note}"
            )
            background_tasks.add_task(
                self.notify_revision_background,
                recipient_user_id=obj.created_by,
                actor_user_id=current_user.user_id,
                staging_id=obj.staging_id,
                title=title,
                message=message,
                note=payload.note,
            )

            return MessageResponse(
                message="Yêu cầu chỉnh sửa thành công"
            )

        except Exception:
            await db.rollback()
            raise

    async def notify_revision_background(
        self,
        *,
        recipient_user_id: UUID,
        actor_user_id: UUID,
        staging_id: UUID,
        title: str,
        message: str,
        note: str,
    ):

        async with AsyncSessionLocal() as db:

            try:

                await notification_service.notify_user(
                    db,
                    recipient_user_id=recipient_user_id,
                    actor_user_id=actor_user_id,
                    event_type=NotificationType.REQUEST_REVISION.value,
                    title=title,
                    message=message,
                    target_url=(
                        f"{settings.FRONTEND_URL}"
                        f"/dashboard/data-entry/researches/{staging_id}"
                    ),
                    payload={
                        "staging_id": str(staging_id),
                        "workflow_status": (
                            WorkflowStatus.revision_required.value
                        ),
                        "note": note,
                    },
                )

                await db.commit()
                await push_to_users(
                    db,
                    [recipient_user_id],
                    title,
                    message,
                )
            except Exception:
                await db.rollback()



    async def forward_to_approval(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID,
        payload: ForwardToApprovalRequest,
        background_tasks: BackgroundTasks,
        current_user: User,
    ) -> MessageResponse:

        repo = StagingReviewRepository(db)

        try:
            obj = await repo.get_by_id(staging_id)

            if obj is None or obj.deleted_at is not None:
                raise NotFoundException("Không tìm thấy bản ghi tạm")

            self._assert_pending_review(obj)

            old_status = obj.workflow_status

            now = datetime.now(timezone.utc)

            obj.workflow_status = WorkflowStatus.pending_approval
            obj.reviewed_by = current_user.user_id
            obj.reviewed_at = now
            obj.updated_at = now


            await workflow_service.write_history(
                db,
                staging_id=obj.staging_id,
                performed_by=current_user.user_id,
                from_status=old_status,
                to_status=WorkflowStatus.pending_approval,
                action_code="FORWARD_TO_APPROVAL",
                action_note=payload.note,
            )


            await audit_service.write_log(
                db,
                actor_user_id=current_user.user_id,
                action_code="FORWARD_TO_APPROVAL",
                target_schema="staging",
                target_table="research_objects",
                target_id=obj.staging_id,
                old_value={
                    "workflow_status": old_status.value
                },
                new_value={
                    "workflow_status": WorkflowStatus.pending_approval.value,
                    "note": payload.note,
                },
                message="Reviewer forwarded record to approval",
            )


            await db.commit()


            title = "Có bài nghiên cứu mới cần phê duyệt"

            message = (
                f"Người kiểm duyệt đã chuyển bài nghiên cứu "
                f"'{obj.title}' đến bước phê duyệt."
            )


            background_tasks.add_task(
                self.notify_approval_background,
                actor_user_id=current_user.user_id,
                staging_id=obj.staging_id,
                title=title,
                message=message,
            )


            return MessageResponse(
                message="Chuyển bản ghi sang bước phê duyệt thành công"
            )

        except Exception:
            await db.rollback()
            raise


    async def notify_approval_background(
        self,
        *,
        actor_user_id: UUID,
        staging_id: UUID,
        title: str,
        message: str,
    ):

        async with AsyncSessionLocal() as db:
            try:

                await notification_service.notify_role(
                    db,
                    role_codes=["APPROVER", "SUPER_ADMIN"],
                    actor_user_id=actor_user_id,
                    event_type=NotificationType.PENDING_APPROVAL.value,
                    title=title,
                    message=message,
                    target_url=(
                        f"{settings.FRONTEND_URL}"
                        f"/dashboard/approval/researches/{staging_id}"
                    ),
                    payload={
                        "staging_id": str(staging_id),
                        "workflow_status": (
                            WorkflowStatus.pending_approval.value
                        ),
                    },
                )

                await db.commit()


                await push_to_roles(
                    db,
                    ["APPROVER", "SUPER_ADMIN"],
                    title,
                    message,
                )
            
            except Exception:
                await db.rollback()
                logger.exception("Failed to notify approvers")

staging_review_service = StagingReviewService()
