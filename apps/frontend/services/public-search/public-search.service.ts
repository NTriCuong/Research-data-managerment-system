import axiosInstance from "@/lib/axios/axios.instance";
import { API_ENDPOINT } from "@/lib/constants/api-endpoint";

export interface PublicResearchItem {
    research_id: string;
    title: string;
    description: string | null;
    cover_image_url: string | null;
    year: number | null;
    output_type: PublicLookup;
    department: PublicLookup;
    authors: PublicAuthor[];
    domains: PublicLookup[];
    keywords: PublicLookup[];
    access_level: "private" | "internal" | "public";
    version_no: number;
    approved_at: string;
    metadata_quality_score: string | number | null;
}

export interface PublicLookup {
    id: string;
    name: string;
}

export interface PublicAuthor {
    full_name: string;
    email: string | null;
    affiliation: string | null;
    author_order: number;
    author_role: string;
}

export interface PublicFile {
    file_id: string;
    original_filename: string;
    mime_type: string;
    file_extension: string | null;
    file_size_bytes: number;
    uploaded_at: string;
    access_level: "private" | "internal" | "public";
}

export interface PublicResearchDetail extends PublicResearchItem {
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
    file_attachments: PublicFile[];
}

export interface PublicResearchSearchResponse {
    items: PublicResearchItem[];
    total: number;
    limit: number;
    offset: number;
}

export interface PublicResearchListParams {
    q?: string;
    output_type_id?: string;
    department_id?: string;
    domain_id?: string;
    keyword_id?: string;
    year?: string;
    limit?: number;
    offset?: number;
}

export interface PublicResearchLookups {
    output_types: PublicLookup[];
    departments: PublicLookup[];
    domains: PublicLookup[];
    keywords: PublicLookup[];
}

export const publicSearchService = {
    async getPublicResearchLookups() {
        const response = await axiosInstance.get<PublicResearchLookups>(
            API_ENDPOINT.PUBLIC.RESEARCH_LOOKUPS
        );

        return response.data;
    },

    async listPublicResearches(params: PublicResearchListParams = {}) {
        const response = await axiosInstance.get<PublicResearchSearchResponse>(
            API_ENDPOINT.PUBLIC.RESEARCHES,
            { params }
        );

        return response.data;
    },

    async getPublicResearchDetail(researchId: string) {
        const response = await axiosInstance.get<PublicResearchDetail>(
            API_ENDPOINT.PUBLIC.RESEARCH_DETAIL(researchId)
        );

        return response.data;
    },

    async createDownloadUrl(researchId: string, fileId: string) {
        const response = await axiosInstance.post<{ download_url: string; expires_in: number }>(
            API_ENDPOINT.PUBLIC.DOWNLOAD_FILE(researchId, fileId)
        );

        return response.data;
    },
};
