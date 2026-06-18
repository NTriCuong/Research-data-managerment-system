const permissions: Record<string, string[]> = {
    "Super Administrator": ["*"],
    "Data Entry User":     ["/dashboard/data-entry"],
    "Metadata Reviewer":   ["/dashboard/review"],
    "Metadata Approver":   ["/dashboard/approval"],
    "Research Manager":    ["/dashboard/reports"],
    "Public User":         ["/"],
};

export function hasPermission(role: string, pathname: string): boolean {
    const routes = permissions[role];

    if (!routes) return false;

    if (routes.includes("*")) return true;

    return routes.some(route => pathname.startsWith(route));
}