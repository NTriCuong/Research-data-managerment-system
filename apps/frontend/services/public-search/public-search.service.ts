import axiosInstance from "@/lib/axios/axios.instance";
import { API_ENDPOINT } from "@/lib/constants/api-endpoint";

export interface PublicResearchItem {
    research_id: string;
    title: string;
    year: number | null;
    access_level: "private" | "internal" | "public";
    version_no: number;
    approved_at: string;
    rank: number;
}

export interface PublicResearchSearchResponse {
    items: PublicResearchItem[];
    total: number;
    limit: number;
    offset: number;
}

export const publicSearchService = {
    async searchCore(q: string, limit = 20, offset = 0) {
        const response = await axiosInstance.get<PublicResearchSearchResponse>(
            API_ENDPOINT.SEARCH.CORE,
            {
                params: { q, limit, offset },
            }
        );

        return response.data;
    },
};
