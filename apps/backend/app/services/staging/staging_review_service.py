from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth.user import User
from app.models.enum import WorkflowStatus
from app.models.staging.stg_research_object import StgResearchObject
from app.repositories.staging_review_repository import StagingReviewRepository
from app.schemas.auth import MessageResponse
from app.schemas.staging_metadata import StagingResearchObjectOut
from app.schemas.staging_review import ForwardToApprovalRequest, RequestRevisionRequest
from app.services.logs.audit_service import audit_service
from app.services.logs.workflow_service import workflow_service


class StagingReviewService:
    @staticmethod
    def _assert_pending_review(staging_obj: StgResearchObject) -> None:
        if staging_obj.workflow_status != WorkflowStatus.pending_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending_review records can be reviewed",
            )

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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")

        self._assert_pending_review(obj)
        if not payload.note.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Revision reason cannot be blank")

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
        return MessageResponse(message="Revision requested")

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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")

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
        return MessageResponse(message="Forwarded to approval")


staging_review_service = StagingReviewService()
