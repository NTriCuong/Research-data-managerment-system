"use client";

import { requestPermissionAndGetToken } from "@/lib/hooks/hooks";
import { useEffect } from "react";
import { useAppSelector } from "@/lib/hooks/hooks";
import { selectCurrentUser } from "@/store/slice/auth.slice";

export default function FirebaseInitializer() {
    const user = useAppSelector(selectCurrentUser);

    useEffect(() => {
        const init = async () => {
            try {
                if (!user?.user_id) {
                    console.warn("No user yet, skip FCM init");
                    return;
                }

                if ("serviceWorker" in navigator) {
                    await navigator.serviceWorker.register(
                        "/firebase-messaging-sw.js"
                    );

                    console.log("SW registered");
                }

                const token = await requestPermissionAndGetToken(user.user_id);

                console.log("FCM TOKEN:", token);
            } catch (error) {
                console.error(error);
            }
        };

        init();
    }, [user]);

    return null;
}