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
    // reference dùng chung 
    OUTPUT_TYPE: {
        GET: 'api/v1/reference/output-types/',
    },
    DEPARTMENT: {
        GET: 'api/v1/reference/departments',
    },
    RESEARCHERS: {
        GET: 'api/v1/reference/researchers',
        POST: 'api/v1/reference/researchers',
    },
    KEYWORD: {
        GET: 'api/v1/reference/keywords',
        POST: 'api/v1/reference/keywords',
    },
    DOMAIN: {
        GET: 'api/v1/reference/research-domains',
        POST: 'api/v1/reference/research-domains',
    }
} 