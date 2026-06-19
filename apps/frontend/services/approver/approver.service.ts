import axiosInstance from "@/lib/axios/axios.instance"
import { API_ENDPOINT } from "@/lib/constants/api-endpoint"
import type { AccessLevel, WorkflowStatus } from "@/services/data-entry/data-entry.service"

export interface PendingApproval {
    staging_id: string
    title: string
    output_type_id: string
    department_id: string
    year: number | null
    workflow_status: WorkflowStatus
    access_level: AccessLevel
    metadata_quality_score: string | null
    submitted_by: string | null
    reviewed_by: string | null
    submitted_at: string | null
    reviewed_at: string | null
    created_at: string
    updated_at: string | null
}

export interface FileAccessLevelAssignment {
    file_id: string
    access_level: "private" | "internal" | "public"
}

export interface ApproveRequest {
    note?: string
    access_level: "private" | "internal" | "public"
    file_access_levels: FileAccessLevelAssignment[]
}

export const approverService = {
    // danh sách bản ghi chờ phê duyệt
    async getPendingApprovals() {
        const response = await axiosInstance.get<PendingApproval[]>(API_ENDPOINT.APPROVER.GET_RESEARCH_DATA)
        return response.data
    },

    // duyệt bản ghi, xuất bản vào core
    async approveRecord(stagingId: string, payload: ApproveRequest) {
        const response = await axiosInstance.post(API_ENDPOINT.APPROVER.APPROVE(stagingId), payload)
        return response.data
    },

    // từ chối bản ghi
    async rejectRecord(stagingId: string, reason: string) {
        const response = await axiosInstance.post(API_ENDPOINT.APPROVER.REJECT(stagingId), { reason })
        return response.data
    },
}
