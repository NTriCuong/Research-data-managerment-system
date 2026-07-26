from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from app.models.enum import FileStatus


def _has_text(value: str | None) -> bool:
    return bool(value and value.strip())


def _count_active_files(files: list[Any]) -> int:
    return sum(1 for file in files if getattr(file, "file_status", None) != FileStatus.deleted)


def calculate_staging_metadata_quality(
    obj: Any,
    *,
    author_count: int | None = None,
    domain_count: int | None = None,
    keyword_count: int | None = None,
    file_count: int | None = None,
    max_year: int | None = None,
) -> tuple[Decimal, dict[str, Any]]:
    """Calculate staging metadata quality using the SRS 50/25/15/10 rubric."""
    author_count = author_count if author_count is not None else len(getattr(obj, "authors", []))
    domain_count = domain_count if domain_count is not None else len(getattr(obj, "domains", []))
    keyword_count = keyword_count if keyword_count is not None else len(getattr(obj, "keywords", []))
    file_count = file_count if file_count is not None else _count_active_files(getattr(obj, "file_attachments", []))
    max_year = max_year if max_year is not None else 2100

    completeness_checks = {
        "title": _has_text(getattr(obj, "title", None)),
        "description": _has_text(getattr(obj, "description", None)),
        "output_type_id": getattr(obj, "output_type_id", None) is not None,
        "department_id": getattr(obj, "department_id", None) is not None,
        "year_present": getattr(obj, "year", None) is not None,
        "authors": author_count > 0,
        "domains": domain_count > 0,
        "keywords": keyword_count > 0,
    }
    completeness = sum(
        (
            Decimal("8") if completeness_checks["title"] else Decimal("0"),
            Decimal("7") if completeness_checks["description"] else Decimal("0"),
            Decimal("6") if completeness_checks["output_type_id"] else Decimal("0"),
            Decimal("6") if completeness_checks["department_id"] else Decimal("0"),
            Decimal("6") if completeness_checks["year_present"] else Decimal("0"),
            Decimal("7") if completeness_checks["authors"] else Decimal("0"),
            Decimal("5") if completeness_checks["domains"] else Decimal("0"),
            Decimal("5") if completeness_checks["keywords"] else Decimal("0"),
        ),
        Decimal("0"),
    )

    year = getattr(obj, "year", None)
    external_url = getattr(obj, "external_url", None)
    language = getattr(obj, "language", None)
    validity_checks = {
        "year_valid": year is not None and 1900 <= year <= max_year,
        "language": language is None or len(language) <= 50,
        "external_url": external_url is None or str(external_url).lower().startswith(("http://", "https://")),
        "access_level": getattr(obj, "access_level", None) is not None,
        "workflow_status": getattr(obj, "workflow_status", None) is not None,
    }
    validity = sum(
        (
            Decimal("8") if validity_checks["year_valid"] else Decimal("0"),
            Decimal("4") if validity_checks["language"] else Decimal("0"),
            Decimal("5") if validity_checks["external_url"] else Decimal("0"),
            Decimal("4") if validity_checks["access_level"] else Decimal("0"),
            Decimal("4") if validity_checks["workflow_status"] else Decimal("0"),
        ),
        Decimal("0"),
    )

    evidence_checks = {"active_file": file_count > 0}
    evidence = Decimal("15") if evidence_checks["active_file"] else Decimal("0")

    traceability_checks = {
        "created_by": getattr(obj, "created_by", None) is not None,
        "created_at": getattr(obj, "created_at", None) is not None,
        "workflow_status": getattr(obj, "workflow_status", None) is not None,
    }
    traceability = sum(
        (
            Decimal("4") if traceability_checks["created_by"] else Decimal("0"),
            Decimal("3") if traceability_checks["created_at"] else Decimal("0"),
            Decimal("3") if traceability_checks["workflow_status"] else Decimal("0"),
        ),
        Decimal("0"),
    )

    total = (completeness + validity + evidence + traceability).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    detail = {
        "total": float(total),
        "completeness": int(completeness),
        "validity": int(validity),
        "evidence": int(evidence),
        "traceability": int(traceability),
        "checks": {
            "completeness": completeness_checks,
            "validity": validity_checks,
            "evidence": evidence_checks,
            "traceability": traceability_checks,
        },
        "author_count": author_count,
        "domain_count": domain_count,
        "keyword_count": keyword_count,
        "file_count": file_count,
    }
    return total, detail
