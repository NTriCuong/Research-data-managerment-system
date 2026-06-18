"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { hasPermission } from "@/lib/auth/permissions";
import { useAppSelector } from "@/store/hooks";
import { selectCurrentUser, selectIsAuthenticated, selectIsInitializing } from "@/store/slice/auth.slice";

interface ProtectedRouteProps {
    children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
    const router = useRouter();
    const pathname = usePathname();
    const isInitializing = useAppSelector(selectIsInitializing);
    const isAuthenticated = useAppSelector(selectIsAuthenticated);
    const user = useAppSelector(selectCurrentUser);

    useEffect(() => {
        if (isInitializing) return;

        if (!isAuthenticated) {
            router.replace("/login");
            return;
        }

        if (user && !hasPermission(user.role_name, pathname)) {
            router.replace("/403");
        }
    }, [isInitializing, isAuthenticated, user, pathname]);

    if (isInitializing) return null;

    return <>{children}</>;
}