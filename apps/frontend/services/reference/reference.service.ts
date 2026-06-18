import axiosInstance from "@/lib/axios/axios.instance"
import { API_ENDPOINT } from "@/lib/constants/api-endpoint"

export interface PaginatedResponse<T> {
    items: T[]
    total: number
    page: number
    page_size: number
    total_pages: number
}

export interface Department {
    department_id: string
    department_code: string
    department_name: string
    parent_department_id: string | null
    description: string | null
    is_active: boolean
}

export interface OutputType {
    output_type_id: string
    type_code: string
    type_name: string
    description: string | null
    is_active: boolean
}



export const referenceService = {
    // department
    async getDepartments(page = 1, pageSize = 100) {
        const response = await axiosInstance.get<PaginatedResponse<Department>>(API_ENDPOINT.DEPARTMENT.GET, {
            params: { page, page_size: pageSize },
        })
        return response.data
    },

    // output type
    async getOutputTypes(page = 1, pageSize = 100) {
        const response = await axiosInstance.get<PaginatedResponse<OutputType>>(API_ENDPOINT.OUTPUT_TYPE.GET, {
            params: { page, page_size: pageSize },
        })
        return response.data
    },

    // researchers
    async getResearchers(page = 1, pageSize = 100) {
        const response = await axiosInstance.get<PaginatedResponse<{ user_id: string; full_name: string }>>(API_ENDPOINT.RESEARCHERS.GET, {
            params: { page, page_size: pageSize },
        })
        return response.data.items
    },
    async createResearcher(full_name: string) {
        const response = await axiosInstance.post(API_ENDPOINT.RESEARCHERS.POST, { full_name })
        return response.data
    },
    // keywords
    async getKeywords(page = 1, pageSize = 100) {
        const response = await axiosInstance.get<PaginatedResponse<{ keyword_id: string; keyword: string }>>(API_ENDPOINT.KEYWORD.GET, {
            params: { page, page_size: pageSize },
        })
        return response.data.items
    },
    async createKeyword(keyword: string) {
        const response = await axiosInstance.post(API_ENDPOINT.KEYWORD.POST, { keyword })
        return response.data
    },
    // domains
    async getDomains(page = 1, pageSize = 100) {
        const response = await axiosInstance.get<PaginatedResponse<{ domain_id: string; domain_name: string }>>(API_ENDPOINT.DOMAIN.GET, {
            params: { page, page_size: pageSize },
        })
        return response.data.items
    }
}

