const permissions: Record<string, string[]> = {
    "Super Administrator": ["*"],
    "Data Entry User":     ["/dashboard/data-entry", "/dashboard/settings"],
    "Metadata Reviewer":   ["/dashboard/review", "/dashboard/settings"],
    "Metadata Approver":   ["/dashboard/approval", "/dashboard/settings"],
    "Research Manager":    ["/dashboard/reports", "/dashboard/settings"],
    "Public User":         ["/"],
};

export function hasPermission(role: string, pathname: string): boolean {
    const routes = permissions[role];

    if (!routes) return false;

    if (routes.includes("*")) return true;

    return routes.some(route => pathname.startsWith(route));
}
