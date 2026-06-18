import axiosInstance from "@/lib/axios/axios.instance"
import { API_ENDPOINT } from "@/lib/constants/api-endpoint"
import type { StagingResearchObject } from "@/services/data-entry/data-entry.service"

export const reviewerService = {
    // danh sách bản ghi chờ kiểm duyệt
    async getPendingReviews() {
        const response = await axiosInstance.get<StagingResearchObject[]>(API_ENDPOINT.REVIEWER.GET_RESEARCH_DATA)
        return response.data
    },

    // chuyển bản ghi sang bước phê duyệt
    async forwardToApproval(stagingId: string, note?: string) {
        const response = await axiosInstance.post(API_ENDPOINT.REVIEWER.FORWARD(stagingId), { note })
        return response.data
    },

    // yêu cầu chỉnh sửa lại
    async requestRevision(stagingId: string, note: string) {
        const response = await axiosInstance.post(API_ENDPOINT.REVIEWER.REQUEST_REVISION(stagingId), { note })
        return response.data
    },
}
