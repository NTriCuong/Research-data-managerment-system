import axiosInstance from '@/lib/axios/axios.instance'
import { API_ENDPOINT } from '@/lib/constants/api-endpoint'

function extractFilename(contentDisposition: string | undefined, fallback: string): string {
    if (!contentDisposition) return fallback
    const match = /filename="?([^"]+)"?/.exec(contentDisposition)
    return match?.[1] ?? fallback
}

function triggerBrowserDownload(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
}

async function downloadExcel(url: string, fallbackFilename: string) {
    try {
        const res = await axiosInstance.get(url, { responseType: 'blob' })
        const filename = extractFilename(res.headers['content-disposition'], fallbackFilename)
        triggerBrowserDownload(new Blob([res.data]), filename)
    } catch (err: any) {
        // responseType 'blob' làm lỗi từ server (json) bị giữ dạng Blob, cần đọc lại thành JSON để hiện đúng message.
        if (err?.response?.data instanceof Blob && err.response.data.type.includes('json')) {
            err.response.data = JSON.parse(await err.response.data.text())
        }
        throw err
    }
}

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

export interface TopResearchViewItem {
    research_id: string
    title: string
    views: number
}

export interface TotalViewsByYearItem {
    month: number
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
    async getResearchViewsYearly(year: number): Promise<TotalViewsByYearItem[]> {
        const res = await axiosInstance.get<TotalViewsByYearItem[]>(API_ENDPOINT.REPORTS.RESEARCH_VIEWS_YEARLY(year))
        return res.data
    },
    async getTopResearchViewsByMonth(year: number, month: number, limit = 10): Promise<TopResearchViewItem[]> {
        const res = await axiosInstance.get<TopResearchViewItem[]>(API_ENDPOINT.REPORTS.RESEARCH_VIEWS_TOP_MONTH, {
            params: { year, month, limit },
        })
        return res.data
    },
    async getTopResearchViewsByYear(year: number, limit = 10): Promise<TopResearchViewItem[]> {
        const res = await axiosInstance.get<TopResearchViewItem[]>(API_ENDPOINT.REPORTS.RESEARCH_VIEWS_TOP_YEAR, {
            params: { year, limit },
        })
        return res.data
    },
    async getTopResearchViewsByDomain(domainId: string, year: number, limit = 10): Promise<TopResearchViewItem[]> {
        const res = await axiosInstance.get<TopResearchViewItem[]>(API_ENDPOINT.REPORTS.RESEARCH_VIEWS_TOP_DOMAIN(domainId), {
            params: { year, limit },
        })
        return res.data
    },

    // ─── Xuất excel ────────────────────────────────────────────────────────
    async exportAuthorProfile(researcherId: string) {
        await downloadExcel(API_ENDPOINT.REPORTS.EXPORT_AUTHOR_PROFILE(researcherId), 'ho-so-tac-gia.xlsx')
    },
    async exportResearchesByResearcher(researcherId: string) {
        await downloadExcel(API_ENDPOINT.REPORTS.EXPORT_RESEARCHES_BY_RESEARCHER(researcherId), 'danh-sach-bai-nghien-cuu.xlsx')
    },
    async exportResearchesByYear(year: number) {
        await downloadExcel(API_ENDPOINT.REPORTS.EXPORT_RESEARCHES_BY_YEAR(year), `danh-sach-bai-nghien-cuu-nam-${year}.xlsx`)
    },
    async exportResearchesByDepartment(departmentId: string) {
        await downloadExcel(API_ENDPOINT.REPORTS.EXPORT_RESEARCHES_BY_DEPARTMENT(departmentId), 'danh-sach-bai-nghien-cuu-don-vi.xlsx')
    },
    async exportResearchesByDepartmentAndYear(departmentId: string, year: number) {
        await downloadExcel(
            API_ENDPOINT.REPORTS.EXPORT_RESEARCHES_BY_DEPARTMENT_YEAR(departmentId, year),
            `danh-sach-bai-nghien-cuu-don-vi-nam-${year}.xlsx`
        )
    },
}
