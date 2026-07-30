export const API_ENDPOINT = {
    AUTH: {
        LOGIN: 'api/v1/auth/login',
        LOGOUT: 'api/v1/auth/logout',
        REFRESH: 'api/v1/auth/refresh',
        CHANGE_PASSWORD: 'api/v1/auth/change-password',
    },
    DATA_ENTRY: {
        GET_RESEARCH_DATA: 'api/v1/staging-metadata/mine',
        CREATE_METADATA: '/api/v1/staging-metadata',
        GET_METADATA_BY_STAGINGID: '/api/v1/staging-metadata', // dùng path param
        UPDATE_METADATA: (stagingId: string) => `/api/v1/staging-metadata/${stagingId}`,
        DELETE_DRAFT: (stagingId: string) => `/api/v1/staging-metadata/${stagingId}`,
        SUBMIT_FOR_REVIEW: (stagingId: string) => `/api/v1/staging-metadata/${stagingId}/submit`,
        CREATE_REVISION: '/api/v1/staging-metadata/revisions',
        FILES: (stagingId: string) => `/api/v1/staging-metadata/${stagingId}/files`,
        DELETE_FILE: (stagingId: string, fileId: string) => `/api/v1/staging-metadata/${stagingId}/files/${fileId}`,
    },
    REVIEWER: {
        GET_RESEARCH_DATA: '/api/v1/staging-review/pending',
        FORWARD: (stagingId: string) => `/api/v1/staging-review/${stagingId}/forward`,
        REQUEST_REVISION: (stagingId: string) => `/api/v1/staging-review/${stagingId}/request-revision`,
    },
    APPROVER: {
        GET_RESEARCH_DATA: '/api/v1/core-approve/pending',
        APPROVE: (stagingId: string) => `/api/v1/core-approve/${stagingId}/approve`,
        REJECT: (stagingId: string) => `/api/v1/core-approve/${stagingId}/reject`,
    },
    CORE_REPOSITORY: {
        GET: '/api/v1/core-repository',
        GET_MINE: '/api/v1/core-repository/mine',
        GET_DETAIL: (researchId: string) => `/api/v1/core-repository/${researchId}`,
        UPDATE_ACCESS_LEVEL: (researchId: string) =>
            `/api/v1/core-repository/${researchId}/access-level`,
        FILES: (researchId: string) => `/api/v1/core-repository/${researchId}/files`,
        UPDATE_FILE_ACCESS_LEVEL: (researchId: string, fileId: string) =>
            `/api/v1/core-repository/${researchId}/files/${fileId}/access-level`,
        VERSIONS: (researchId: string) => `/api/v1/core-repository/${researchId}/versions`,
    },
    // reference dùng chung 
    OUTPUT_TYPE: {
        GET: 'api/v1/reference/output-types/',
        POST: 'api/v1/reference/output-types/',
        PUT: (outPutTypeId: string) => `api/v1/reference/output-types/${outPutTypeId}`,
        DELETE: (outPutTypeId: string) => `api/v1/reference/output-types/${outPutTypeId}`,
        GET_DETAIL: (outPutTypeId: string) => `api/v1/reference/output-types/${outPutTypeId}`
    },
    DEPARTMENT: {
        GET: 'api/v1/reference/departments',
        POST: 'api/v1/reference/department',
        PUT: (departmentId: string) => `api/v1/reference/department/${departmentId}`,
        DELETE: (departmentId: string) => `api/v1/reference/department/${departmentId}`,
        GET_DETAIL: (departmentId: string) => `api/v1/reference/department/${departmentId}`
    },
    RESEARCHERS: {
        GET: 'api/v1/reference/researchers',
        POST: 'api/v1/reference/researchers',
        GET_DETAIL: (id: string) => `api/v1/reference/researchers/${id}`,
        PUT: (id: string) => `api/v1/reference/researchers/${id}`,
        DELETE: (id: string) => `api/v1/reference/researchers/${id}`,
        SUGGESTIONS: 'api/v1/reference/researchers/suggestions',
    },
    KEYWORD: {
        GET: 'api/v1/reference/keywords',
        POST: 'api/v1/reference/keywords',
    },
    DOMAIN: {
        GET: 'api/v1/reference/research-domains',
        POST: 'api/v1/reference/research-domains',
    },
    USER: {
        GET: 'api/v1/users',
        POST: 'api/v1/users',
        GET_DETAIL: (userId: string) => `api/v1/users/${userId}`,
        PUT: (userId: string) => `api/v1/users/${userId}`,
        DELETE: (userId: string) => `api/v1/users/${userId}`,
        PUT_STATUS: (userId: string) => `api/v1/users/${userId}/status`,
        PUT_ROLE: (userId: string) => `api/v1/users/${userId}/role`
    },
    ROLE: {
        GET: 'api/v1/users/roles',
    },
    SEARCH: {
        CORE: 'api/v1/search/core',
        STAGING: 'api/v1/search/staging',
    },
    PUBLIC: {
        RESEARCH_LOOKUPS: 'api/v1/public/research-lookups',
        RESEARCHES: 'api/v1/public/researches',
        RESEARCH_DETAIL: (researchId: string) => `api/v1/public/researches/${researchId}`,
        DOWNLOAD_FILE: (researchId: string, fileId: string) => `api/v1/public/researches/${researchId}/files/${fileId}/download`,
    },
    NOTIFICATIONS: {
        LIST: 'api/v1/notifications',
        REGISTER_TOKEN: 'api/v1/notifications/register-token',
        MARK_READ: (notificationId: string) => `api/v1/notifications/${notificationId}/read`,
    },
    LOGS: {
        AUDIT: 'api/v1/logs/audit',
        LOGIN: 'api/v1/logs/login',
        WORKFLOW: 'api/v1/logs/workflow',
    },
    REPORTS: {
        TOTAL_CORE_REPOSITORIES: 'api/v1/reports/total-core-repositories',
        PENDING_STATUS: 'api/v1/reports/pending-status',
        TOTAL_RESEARCHERS: 'api/v1/reports/total-researchers',
        METADATA_QUALITY: 'api/v1/reports/metadata-quality',
        STATUS_BREAKDOWN: 'api/v1/reports/status-breakdown',
        TOP_DEPARTMENTS: 'api/v1/reports/top-departments',
        EXPORT_AUTHOR_PROFILE: (researcherId: string) => `api/v1/reports/export/author-profile/${researcherId}`,
        EXPORT_RESEARCHES_BY_YEAR: (year: number) => `api/v1/reports/export/researches-by-year/${year}`,
        EXPORT_RESEARCHES_BY_DEPARTMENT: (departmentId: string) => `api/v1/reports/export/researches-by-department/${departmentId}`,
        EXPORT_RESEARCHES_BY_DEPARTMENT_YEAR: (departmentId: string, year: number) =>
            `api/v1/reports/export/researches-by-department/${departmentId}/year/${year}`,
        EXPORT_RESEARCHES_BY_RESEARCHER: (researcherId: string) => `api/v1/reports/export/researches-by-researcher/${researcherId}`,
    },
}
