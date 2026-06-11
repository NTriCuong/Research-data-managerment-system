// components/ProtectedRoute.tsx

"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { hasPermission } from "@/lib/auth/permissions";
import { useAppSelector } from "@/store/hooks";
import { selectCurrentUser, selectIsAuthenticated } from "@/store/slice/auth.slice";

interface ProtectedRouteProps {
    children: React.ReactNode;
}

export default function ProtectedRoute({
    children
}: ProtectedRouteProps) {

    const router = useRouter();
    const pathname = usePathname();

    const isAuthenticated = useAppSelector(selectIsAuthenticated);

    const user = useAppSelector(selectCurrentUser);

    useEffect(() => {

        // chưa login
        if (!isAuthenticated) {
            router.replace("/login");
            return;
        }

        if (
            user &&
            !hasPermission(user.role_name, pathname)
        ) {
            router.replace("/403");
        }

    }, [isAuthenticated, user, pathname]);

    return <>{children}</>;
}