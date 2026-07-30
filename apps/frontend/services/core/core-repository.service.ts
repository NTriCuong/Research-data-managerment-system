import axiosInstance from "@/lib/axios/axios.instance"
import { API_ENDPOINT } from "@/lib/constants/api-endpoint"
import type { AccessLevel } from "@/services/data-entry/data-entry.service"

export interface CoreResearchObject {
    research_id: string
    title: string
    output_type_id: string
    department_id: string
    year: number | null
    access_level: AccessLevel
    metadata_quality_score: string | number | null
    version_no: number
    is_current: boolean
    approved_by: string
    approved_at: string
    created_at: string
    updated_at: string | null
}

export interface CoreAuthor {
    core_author_id: string
    research_id: string
    researcher_id: string | null
    full_name: string
    email: string | null
    affiliation: string | null
    author_order: number
    author_role: string
    created_at: string
}

export interface CoreFile {
    file_id: string
    research_id: string
    original_filename: string
    stored_filename: string
    storage_path: string
    mime_type: string
    file_extension: string | null
    file_size_bytes: number
    checksum_sha256: string | null
    file_status: string
    uploaded_by: string
    uploaded_at: string
    access_level: AccessLevel
}

export interface CoreMetadataVersion {
    version_id: string
    research_id: string
    version_no: number
    metadata_snapshot: Record<string, unknown>
    change_reason: string | null
    created_by: string
    created_at: string
}

export interface CoreResearchObjectDetail extends CoreResearchObject {
    source_staging_id: string | null
    description: string | null
    abstract: string | null
    start_date: string | null
    end_date: string | null
    date_issued: string | null
    publisher: string | null
    language: string | null
    identifier: string | null
    external_url: string | null
    source: string | null
    relation: string | null
    coverage: string | null
    rights: string | null
    metadata_quality_detail: Record<string, unknown> | null
    domain_ids: string[]
    keyword_ids: string[]
    authors: CoreAuthor[]
    file_attachments: CoreFile[]
}

export const coreRepositoryService = {
    async listCoreRecords(limit = 100, offset = 0) {
        const response = await axiosInstance.get<CoreResearchObject[]>(API_ENDPOINT.CORE_REPOSITORY.GET, {
            params: { limit, offset },
        })
        return response.data
    },

    async listMyCoreRecords(limit = 100, offset = 0) {
        const response = await axiosInstance.get<CoreResearchObject[]>(
            API_ENDPOINT.CORE_REPOSITORY.GET_MINE,
            { params: { limit, offset } }
        )
        return response.data
    },

    async getCoreRecord(researchId: string) {
        const response = await axiosInstance.get<CoreResearchObjectDetail>(
            API_ENDPOINT.CORE_REPOSITORY.GET_DETAIL(researchId)
        )
        return response.data
    },

    async updateCoreResearchAccessLevel(researchId: string, accessLevel: AccessLevel) {
        const response = await axiosInstance.patch<CoreResearchObject>(
            API_ENDPOINT.CORE_REPOSITORY.UPDATE_ACCESS_LEVEL(researchId),
            { access_level: accessLevel }
        )
        return response.data
    },

    async listCoreFiles(researchId: string) {
        const response = await axiosInstance.get<CoreFile[]>(API_ENDPOINT.CORE_REPOSITORY.FILES(researchId))
        return response.data
    },

    async updateCoreFileAccessLevel(researchId: string, fileId: string, accessLevel: AccessLevel) {
        const response = await axiosInstance.patch<CoreFile>(
            API_ENDPOINT.CORE_REPOSITORY.UPDATE_FILE_ACCESS_LEVEL(researchId, fileId),
            { access_level: accessLevel }
        )
        return response.data
    },

    async listMetadataVersions(researchId: string) {
        const response = await axiosInstance.get<CoreMetadataVersion[]>(
            API_ENDPOINT.CORE_REPOSITORY.VERSIONS(researchId)
        )
        return response.data
    },
}
