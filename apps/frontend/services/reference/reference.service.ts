
import axiosInstance from "@/lib/axios/axios.instance";
import { API_ENDPOINT } from "@/lib/constants/api-endpoint";

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

export interface Department {
    department_id: string;
    department_code: string;
    department_name: string;
    parent_department_id: string | null;
    description: string | null;
    is_active: boolean;
}

export interface OutputType {
    output_type_id: string;
    type_code: string;
    type_name: string;
    description: string | null;
    is_active: boolean;
}

export interface Researcher {
    researcher_id: string;
    full_name: string;
}

export interface Domain {
    domain_id: string;
    domain_name: string;
}

export interface Keyword {
    keyword_id: string;
    keyword_text: string;
}

export interface CreateResearcherRequest {
    full_name: string;
    email?: string;
    orcid?: string;
    department_id?: string;
    academic_title?: string;
    researcher_code?: string;
    is_internal?: boolean;
}

export interface CreateDomainRequest {
    domain_code: string;
    domain_name: string;
    parent_domain_id?: string | null;
    description?: string;
    is_active?: boolean;
}

export interface CreateKeywordRequest {
    keyword_text: string;
    normalized_text: string;
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
    async createResearcher(data: CreateResearcherRequest) {
        const response = await axiosInstance.post(
            API_ENDPOINT.RESEARCHERS.POST,
            data
        );

        return response.data;
    },
    // Keywords
    async getKeywords(
        page = 1,
        pageSize = 20,
        q = ""
    ) {
        const response = await axiosInstance.get(
            API_ENDPOINT.KEYWORD.GET,
            {
                params: {
                    page,
                    page_size: pageSize,
                    q,
                },
            }
        );

        return response.data.items;
    },

    async createKeyword(data: CreateKeywordRequest) {
        const response = await axiosInstance.post(
            API_ENDPOINT.KEYWORD.POST,
            data
        );

        return response.data;
    },

    async suggestKeywords(q: string, limit = 10) {
        const response = await axiosInstance.get(
            "api/v1/reference/keywords/suggestions",
            {
                params: {
                    q,
                    limit,
                },
            }
        );

        return response.data;
    },


    // Domains
    async getDomains(
        page = 1,
        pageSize = 20,
        q = ""
    ) {
        const response = await axiosInstance.get(
            API_ENDPOINT.DOMAIN.GET,
            {
                params: {
                    page,
                    page_size: pageSize,
                    q,
                },
            }
        );

        return response.data.items;
    },

    async createDomain(data: CreateDomainRequest) {
        const response = await axiosInstance.post(
            API_ENDPOINT.DOMAIN.POST,
            data
        );

        return response.data;
    },
    async suggestDomains(q: string, limit = 10) {
        const response = await axiosInstance.get(
            "api/v1/reference/research-domains/suggestions",
            {
                params: {
                    q,
                    limit,
                },
            }
        );

        return response.data;
    },

};


