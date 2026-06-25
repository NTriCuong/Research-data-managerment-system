"use client";

import { useEffect } from "react";
import { requestPermissionAndGetToken } from "@/lib/hooks/hooks";

export default function FirebaseInitializer() {
    useEffect(() => {
        const init = async () => {
            console.log("FirebaseInitializer mounted");
            try {
                if ("serviceWorker" in navigator) {
                    await navigator.serviceWorker.register(
                        "/firebase-messaging-sw.js"
                    );

                    console.log("SW registered");
                }

                const token = await requestPermissionAndGetToken();

                console.log("FCM TOKEN:", token);
            } catch (error) {
                console.error(error);
            }
        };

        init();
    }, []);

    return null;
}