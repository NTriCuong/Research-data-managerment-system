import axiosInstance from '@/lib/axios/axios.instance'
import { API_ENDPOINT } from '@/lib/constants/api-endpoint'

export interface AuditLog {
    audit_id: string
    actor_user_id: string | null
    action_code: string
    target_schema: string | null
    target_table: string | null
    target_id: string | null
    old_value: Record<string, unknown> | null
    new_value: Record<string, unknown> | null
    result: string
    message: string | null
    ip_address: string | null
    user_agent: string | null
    created_at: string
}

export interface LoginLog {
    login_log_id: string
    user_id: string | null
    username_attempted: string | null
    login_result: string
    failure_reason: string | null
    ip_address: string | null
    user_agent: string | null
    created_at: string
}

export interface WorkflowLog {
    workflow_id: string
    staging_id: string | null
    research_id: string | null
    from_status: string | null
    to_status: string
    action_code: string
    action_note: string | null
    performed_by: string
    performed_at: string
    ip_address: string | null
    user_agent: string | null
}

export interface AuditLogParams {
    action_code?: string
    result?: string
    target_table?: string
    created_from?: string
    created_to?: string
    limit?: number
    offset?: number
}

export interface LoginLogParams {
    username?: string
    login_result?: string
    created_from?: string
    created_to?: string
    limit?: number
    offset?: number
}

export interface WorkflowLogParams {
    action_code?: string
    performed_from?: string
    performed_to?: string
    limit?: number
    offset?: number
}

export const logService = {
    async listAuditLogs(params: AuditLogParams = {}): Promise<AuditLog[]> {
        const response = await axiosInstance.get<AuditLog[]>(API_ENDPOINT.LOGS.AUDIT, { params })
        return response.data
    },

    async listLoginLogs(params: LoginLogParams = {}): Promise<LoginLog[]> {
        const response = await axiosInstance.get<LoginLog[]>(API_ENDPOINT.LOGS.LOGIN, { params })
        return response.data
    },

    async listWorkflowLogs(params: WorkflowLogParams = {}): Promise<WorkflowLog[]> {
        const response = await axiosInstance.get<WorkflowLog[]>(API_ENDPOINT.LOGS.WORKFLOW, { params })
        return response.data
    },
}
