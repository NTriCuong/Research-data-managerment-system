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
        SUBMIT_FOR_REVIEW: (stagingId: string) => `/api/v1/staging-metadata/${stagingId}/submit`,
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
}
