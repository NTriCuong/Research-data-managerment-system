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
    view_count: number;
    download_count: number;
}

export interface PublicLookup {
    id: string;
    name: string;
    count?: number | null;
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

export interface ResearchViewResponse {
    view_id: string;
    research_id: string;
    viewed_at: string;
}

export interface PublicResearchSearchResponse {
    items: PublicResearchItem[];
    total: number;
    limit: number;
    offset: number;
}

export interface PublicResearchSuggestion {
    research_id: string;
    title: string;
    year: number | null;
}

export interface PublicResearchListParams {
    q?: string;
    output_type_ids?: string[];
    department_ids?: string[];
    domain_ids?: string[];
    keyword_ids?: string[];
    author_ids?: string[];
    year_from?: string;
    year_to?: string;
    has_files?: boolean;
    sort?: PublicResearchSort;
    limit?: number;
    offset?: number;
}

export type PublicResearchSort =
    | "relevance"
    | "newest"
    | "oldest"
    | "most_viewed"
    | "most_downloaded"
    | "title_asc";

export interface PublicResearchLookups {
    output_types: PublicLookup[];
    departments: PublicLookup[];
    domains: PublicLookup[];
    keywords: PublicLookup[];
    authors: PublicLookup[];
    year_min: number | null;
    year_max: number | null;
}

export const publicSearchService = {
    async getPublicResearchLookups() {
        const response = await axiosInstance.get<PublicResearchLookups>(
            API_ENDPOINT.PUBLIC.RESEARCH_LOOKUPS
        );

        return response.data;
    },

    async listPublicResearches(params: PublicResearchListParams = {}) {
        const queryParams = new URLSearchParams();
        if (params.q) queryParams.set("q", params.q);
        for (const value of params.output_type_ids ?? []) queryParams.append("output_type_ids", value);
        for (const value of params.department_ids ?? []) queryParams.append("department_ids", value);
        for (const value of params.domain_ids ?? []) queryParams.append("domain_ids", value);
        for (const value of params.keyword_ids ?? []) queryParams.append("keyword_ids", value);
        for (const value of params.author_ids ?? []) queryParams.append("author_ids", value);
        if (params.year_from) queryParams.set("year_from", params.year_from);
        if (params.year_to) queryParams.set("year_to", params.year_to);
        if (params.has_files) queryParams.set("has_files", "true");
        if (params.sort) queryParams.set("sort", params.sort);
        if (params.limit !== undefined) queryParams.set("limit", String(params.limit));
        if (params.offset !== undefined) queryParams.set("offset", String(params.offset));

        const response = await axiosInstance.get<PublicResearchSearchResponse>(
            API_ENDPOINT.PUBLIC.RESEARCHES,
            { params: queryParams }
        );

        return response.data;
    },

    async suggestPublicResearches(q: string, limit = 8, signal?: AbortSignal) {
        const response = await axiosInstance.get<PublicResearchSuggestion[]>(
            API_ENDPOINT.PUBLIC.RESEARCH_SUGGESTIONS,
            { params: { q, limit }, signal }
        );

        return response.data;
    },

    async getPublicResearchDetail(researchId: string) {
        const response = await axiosInstance.get<PublicResearchDetail>(
            API_ENDPOINT.PUBLIC.RESEARCH_DETAIL(researchId)
        );

        return response.data;
    },

    async addResearchView(researchId: string) {
        const response = await axiosInstance.post<ResearchViewResponse>(
            API_ENDPOINT.REPORTS.ADD_RESEARCH_VIEW(researchId)
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
