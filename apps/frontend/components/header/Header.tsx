"use client";

import { useAppSelector } from "@/store/hooks";
import { selectCurrentUser, selectIsAuthenticated, selectIsInitializing } from "@/store/slice/auth.slice";
import GuestHeader from "./GuestHeader";
import AuthHeader from "./AuthHeader";

export default function Header() {
    const isInitializing = useAppSelector(selectIsInitializing);
    const isAuthenticated = useAppSelector(selectIsAuthenticated);
    const currentUser = useAppSelector(selectCurrentUser);

    if (isInitializing) return null;

    if (isAuthenticated && currentUser) {
        return <AuthHeader currentUser={currentUser} />;
    }

    return <GuestHeader />;
}
