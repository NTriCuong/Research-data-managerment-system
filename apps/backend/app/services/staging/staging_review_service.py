from datetime import datetime, timezone
from uuid import UUID

from app.core.exceptions import BadRequestException, NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth.user import User
from app.models.enum import NotificationType, WorkflowStatus
from app.models.staging.stg_research_object import StgResearchObject
from app.repositories.staging_review_repository import StagingReviewRepository
from app.schemas.auth import MessageResponse
from app.schemas.staging_metadata import StagingResearchObjectOut
from app.schemas.staging_review import ForwardToApprovalRequest, RequestRevisionRequest
from app.services.logs.audit_service import audit_service
from app.services.logs.workflow_service import workflow_service
from app.services.notification.notification_service import NotificationService, notification_service


class StagingReviewService:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

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
        current_user: User,
    ) -> MessageResponse:
        repo = StagingReviewRepository(db)
        obj = await repo.get_by_id(staging_id)
        if obj is None or obj.deleted_at is not None:
            raise NotFoundException("Không tìm thấy bản ghi tạm")

        self._assert_pending_review(obj)
        if not payload.note.strip():
            raise BadRequestException("Lý do yêu cầu chỉnh sửa không được để trống")

        old_status = obj.workflow_status
        obj.workflow_status = WorkflowStatus.revision_required
        obj.reviewed_by = current_user.user_id
        now = datetime.now(timezone.utc)
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
            old_value={"workflow_status": old_status.value},
            new_value={"workflow_status": WorkflowStatus.revision_required.value, "revision_note": payload.note},
            message="Reviewer requested revision",
        )
        await self.notification_service.notify(
            db=db,
            user_ids=[obj.created_by],
            title="Yêu cầu chỉnh sửa bài nghiên cứu",
            message=payload.note,
            type_=NotificationType.REQUEST_REVISION,
            sender_id=current_user.user_id,
            research_id=obj.staging_id,
        )
        return MessageResponse(message="Yêu cầu chỉnh sửa thành công")

    async def forward_to_approval(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID,
        payload: ForwardToApprovalRequest,
        current_user: User,
    ) -> MessageResponse:
        repo = StagingReviewRepository(db)
        obj = await repo.get_by_id(staging_id)
        if obj is None or obj.deleted_at is not None:
            raise NotFoundException("Không tìm thấy bản ghi tạm")

        self._assert_pending_review(obj)

        old_status = obj.workflow_status
        obj.workflow_status = WorkflowStatus.pending_approval
        obj.reviewed_by = current_user.user_id
        now = datetime.now(timezone.utc)
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
            old_value={"workflow_status": old_status.value},
            new_value={"workflow_status": WorkflowStatus.pending_approval.value, "note": payload.note},
            message="Reviewer forwarded record to approval",
        )
        approvers = await repo.get_approvers()
        approver_ids = [u.user_id for u in approvers]
        await self.notification_service.notify(
            db=db,
            user_ids=approver_ids,
            title="Có 1 bài nghiên cứu chờ phê duyệt",
            message=f"{obj.title} đã được kiểm duyệt và chờ phê duyệt",
            type_=NotificationType.PENDING_APPROVAL,
            sender_id=current_user.user_id,
            research_id=obj.staging_id,
        )
        return MessageResponse(message="Chuyển bản ghi sang bước phê duyệt thành công")


staging_review_service = StagingReviewService(notification_service)
