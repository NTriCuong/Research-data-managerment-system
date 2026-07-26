from decimal import Decimal
from types import SimpleNamespace

from app.models.enum import AccessLevel, FileStatus, WorkflowStatus
from app.services.metadata_quality import calculate_staging_metadata_quality


def _record(**overrides):
    base = {
        "title": "Research title",
        "description": "Description",
        "output_type_id": "output-type-id",
        "department_id": "department-id",
        "year": 2026,
        "language": "vi",
        "external_url": "https://example.edu/research",
        "access_level": AccessLevel.public,
        "workflow_status": WorkflowStatus.draft,
        "created_by": "user-id",
        "created_at": "2026-01-01T00:00:00Z",
        "authors": [SimpleNamespace()],
        "domains": [SimpleNamespace()],
        "keywords": [SimpleNamespace()],
        "file_attachments": [SimpleNamespace(file_status=FileStatus.active)],
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_quality_score_uses_srs_group_weights():
    score, detail = calculate_staging_metadata_quality(_record())

    assert score == Decimal("100.00")
    assert detail["completeness"] == 50
    assert detail["validity"] == 25
    assert detail["evidence"] == 15
    assert detail["traceability"] == 10


def test_quality_score_does_not_require_evidence_for_nonzero_draft_score():
    score, detail = calculate_staging_metadata_quality(_record(file_attachments=[]))

    assert score == Decimal("85.00")
    assert detail["evidence"] == 0
    assert detail["checks"]["evidence"]["active_file"] is False


def test_quality_score_does_not_award_validity_points_when_year_is_null():
    score, detail = calculate_staging_metadata_quality(_record(year=None))

    assert score == Decimal("86.00")
    assert detail["completeness"] == 44
    assert detail["validity"] == 17
    assert detail["checks"]["validity"]["year_valid"] is False
