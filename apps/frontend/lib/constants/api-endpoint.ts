export const API_ENDPOINT = {
    AUTH: {
        LOGIN: 'api/v1/auth/login',
        LOGOUT: 'api/v1/auth/logout',
        REFRESH: 'api/v1/auth/refresh',
        CHANGE_PASSWORD: 'api/v1/auth/change-password',
    },
    DATA_ENTRY: {
        GET_RESEARCH_DATA: 'api/v1/staging-metadata/mine'
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