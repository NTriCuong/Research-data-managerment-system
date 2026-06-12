export const PUBLIC_ROUTES = [
    "/",
    "/login",
    "/register",
    "/about",
    "/change-password",
    "/verify-otp",
];

export const PROTECTED_ROUTES = [
    "/dashboard",
];

export const ROLE_ROUTES = {
    SUPER_ADMIN: ["/admin"],
    DATA_ENTRY: ["/data-entry"],
    REVIEWER: ["/review"],
    APPROVER: ["/approval"],
    MANAGER: ["/manager"],
    PUBLIC_USER: ["/profile"]
};

const ROLE_HOME_MAP: Record<string, string> = {
    "Super Administrator": "/dashboard/superadmin",
    "Data Entry User": "/dashboard/data-entry",
    "Metadata Reviewer": "/dashboard/review",
    "Metadata Approver": "/dashboard/approval",
    "Research Manager": "/dashboard/reports",
    "Public User": "/",
};

export function getRoleHomePath(roleName: string): string {
    return ROLE_HOME_MAP[roleName] ?? "/dashboard";
}