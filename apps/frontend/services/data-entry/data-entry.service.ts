import axiosInstance from "@/lib/axios/axios.instance"
import { API_ENDPOINT } from "@/lib/constants/api-endpoint"

export type WorkflowStatus =
    | "draft"
    | "pending_review"
    | "revision_required"
    | "pending_approval"
    | "approved"
    | "rejected"

export type AccessLevel = "private" | "internal" | "public"

export interface StagingResearchObject {
    staging_id: string
    title: string
    output_type_id: string
    department_id: string
    year: number | null
    workflow_status: WorkflowStatus
    access_level: AccessLevel
    source_core_research_id: string | null
    update_reason: string | null
    metadata_quality_score: string | null
    created_by: string
    submitted_by: string | null
    submitted_at: string | null
    created_at: string
    updated_at: string | null
}

export const dataEntryService = {
    // get research do data entry thêm
    async getResearchData() {
        const response = await axiosInstance.get<StagingResearchObject[]>(API_ENDPOINT.DATA_ENTRY.GET_RESEARCH_DATA)
        return response.data
    }
}
