
import axiosInstance from "@/lib/axios/axios.instance";
import { API_ENDPOINT } from "@/lib/constants/api-endpoint";
import type { StagingResearchObject } from "@/services/data-entry/data-entry.service";

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

export interface StagingFile {
    file_id: string;
    staging_id: string;
    original_filename: string;
    stored_filename: string;
    storage_path: string;
    mime_type: string;
    file_extension: string;
    file_size_bytes: number;
    checksum_sha256: string;
    file_status: string;
    uploaded_by: string;
    uploaded_at: string;
    access_level: string;
}

export interface StagingAuthorDetail {
    staging_author_id: string;
    staging_id: string;
    researcher_id: string | null;
    full_name: string;
    email: string | null;
    affiliation: string | null;
    author_order: number;
    author_role: string;
    created_at: string;
}

export interface StagingDomainDetail {
    domain_id: string;
    domain_name: string;
}

export interface StagingKeywordDetail {
    keyword_id: string;
    keyword_text: string;
}

export interface StagingResearchObjectDetail extends StagingResearchObject {
    description: string | null;
    abstract: string | null;
    start_date: string | null;
    end_date: string | null;
    date_issued: string | null;
    publisher: string | null;
    language: string | null;
    identifier: string | null;
    external_url: string | null;
    source: string | null;
    relation: string | null;
    coverage: string | null;
    rights: string | null;
    reviewed_by: string | null;
    reviewed_at: string | null;
    revision_note: string | null;
    rejection_reason: string | null;
    domains: StagingDomainDetail[];
    keywords: StagingKeywordDetail[];
    authors: StagingAuthorDetail[];
    files: StagingFile[];
}

export type UserStatus = "active" | "disabled"

export interface Role {
    role_id: string;
    role_code: string;
    role_name: string;
}

export interface AppUser {
    user_id: string;
    username: string;
    email: string;
    full_name: string;
    role_id: string;
    department_id: string | null;
    status: UserStatus;
    last_login_at: string | null;
    created_at: string;
    updated_at: string | null;
    deleted_at: string | null;
}

export interface CreateUserRequest {
    username: string;
    email: string;
    password: string;
    full_name: string;
    role_id: string;
    department_id?: string | null;
}

export interface UpdateUserRequest {
    username?: string;
    email?: string;
    full_name?: string;
    department_id?: string | null;
}

export interface ListUsersParams {
    limit?: number;
    offset?: number;
    q?: string;
    role_id?: string;
    status?: UserStatus;
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

    //  METADATA 
    async createMetadata(data: any) {
        const response = await axiosInstance.post(
            API_ENDPOINT.DATA_ENTRY.CREATE_METADATA,
            data
        );

        return response.data;
    },
    async getMetadataByStagingId(stagingId: string) {
        const response = await axiosInstance.get<StagingResearchObjectDetail>(
            `${API_ENDPOINT.DATA_ENTRY.GET_METADATA_BY_STAGINGID}/${stagingId}`
        );

        return response.data;
    },
    async updateMetadata(stagingId: string, data: any) {
        const response = await axiosInstance.put(
            API_ENDPOINT.DATA_ENTRY.UPDATE_METADATA(stagingId),
            data
        );

        return response.data;
    },
    submitForReview: (stagingId: string, note: string) => {
        return axiosInstance.post(
            API_ENDPOINT.DATA_ENTRY.SUBMIT_FOR_REVIEW(stagingId),
            {
                note,
            }
        );
    },

    // file đính kèm
    async getStagingFiles(stagingId: string) {
        const response = await axiosInstance.get<StagingFile[]>(
            API_ENDPOINT.DATA_ENTRY.FILES(stagingId)
        );

        return response.data;
    },

    async uploadStagingFile(stagingId: string, file: File) {
        const formData = new FormData();
        formData.append("file", file);

        const response = await axiosInstance.post<StagingFile>(
            API_ENDPOINT.DATA_ENTRY.FILES(stagingId),
            formData,
            { headers: { "Content-Type": undefined } }
        );

        return response.data;
    },

    async deleteStagingFile(stagingId: string, fileId: string) {
        const response = await axiosInstance.delete(
            API_ENDPOINT.DATA_ENTRY.DELETE_FILE(stagingId, fileId)
        );

        return response.data;
    },

    // Roles
    async getRoles() {
        const response = await axiosInstance.get<Role[]>(API_ENDPOINT.ROLE.GET);
        return response.data;
    },

    // Users
    async getUsers(params?: ListUsersParams) {
        const response = await axiosInstance.get<AppUser[]>(API_ENDPOINT.USER.GET, { params });
        return response.data;
    },

    async getUserDetail(userId: string) {
        const response = await axiosInstance.get<AppUser>(API_ENDPOINT.USER.GET_DETAIL(userId));
        return response.data;
    },

    async createUser(data: CreateUserRequest) {
        const response = await axiosInstance.post<AppUser>(API_ENDPOINT.USER.POST, data);
        return response.data;
    },

    async updateUser(userId: string, data: UpdateUserRequest) {
        const response = await axiosInstance.put<AppUser>(API_ENDPOINT.USER.PUT(userId), data);
        return response.data;
    },

    async deleteUser(userId: string) {
        const response = await axiosInstance.delete(API_ENDPOINT.USER.DELETE(userId));
        return response.data;
    },

    async updateUserStatus(userId: string, status: UserStatus) {
        const response = await axiosInstance.put<AppUser>(API_ENDPOINT.USER.PUT_STATUS(userId), { status });
        return response.data;
    },

    async updateUserRole(userId: string, roleId: string) {
        const response = await axiosInstance.put<AppUser>(API_ENDPOINT.USER.PUT_ROLE(userId), { role_id: roleId });
        return response.data;
    },
};




