import axiosInstance from '@/lib/axios/axios.instance'
import { API_ENDPOINT } from '@/lib/constants/api-endpoint'

export interface TotalCoreRepositories {
    total_core_repositories: number
}

export interface PendingStatus {
    pending_review: number
    pending_approval: number
    total_pending: number
}

export interface TotalResearchers {
    total_researchers: number
    internal: number
    external: number
}

export interface MetadataQuality {
    avg_score: number
    min_score: number
    max_score: number
    total_records: number
}

export interface StatusBreakdownItem {
    status: string
    count: number
}

export interface TopDepartmentItem {
    department_name: string
    count: number
}

export const reportService = {
    async getTotalCoreRepositories(): Promise<TotalCoreRepositories> {
        const res = await axiosInstance.get<TotalCoreRepositories>(API_ENDPOINT.REPORTS.TOTAL_CORE_REPOSITORIES)
        return res.data
    },
    async getPendingStatus(): Promise<PendingStatus> {
        const res = await axiosInstance.get<PendingStatus>(API_ENDPOINT.REPORTS.PENDING_STATUS)
        return res.data
    },
    async getTotalResearchers(): Promise<TotalResearchers> {
        const res = await axiosInstance.get<TotalResearchers>(API_ENDPOINT.REPORTS.TOTAL_RESEARCHERS)
        return res.data
    },
    async getMetadataQuality(): Promise<MetadataQuality> {
        const res = await axiosInstance.get<MetadataQuality>(API_ENDPOINT.REPORTS.METADATA_QUALITY)
        return res.data
    },
    async getStatusBreakdown(): Promise<StatusBreakdownItem[]> {
        const res = await axiosInstance.get<StatusBreakdownItem[]>(API_ENDPOINT.REPORTS.STATUS_BREAKDOWN)
        return res.data
    },
    async getTopDepartments(limit = 10): Promise<TopDepartmentItem[]> {
        const res = await axiosInstance.get<TopDepartmentItem[]>(API_ENDPOINT.REPORTS.TOP_DEPARTMENTS, { params: { limit } })
        return res.data
    },
}
