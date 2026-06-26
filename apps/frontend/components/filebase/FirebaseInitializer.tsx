"use client";

import { requestPermissionAndGetToken, listenForegroundMessage } from "@/lib/hooks/hooks";
import { useEffect } from "react";
import { useAppSelector } from "@/lib/hooks/hooks";
import { selectCurrentUser } from "@/store/slice/auth.slice";
import { toast } from "sonner";

export default function FirebaseInitializer() {
    const user = useAppSelector(selectCurrentUser);

    useEffect(() => {
        if (!user?.user_id) return;

        let unsubscribe: (() => void) | undefined;

        const init = async () => {
            try {
                if ("serviceWorker" in navigator) {
                    await navigator.serviceWorker.register("/firebase-messaging-sw.js");
                    console.log("SW registered");
                }

                const token = await requestPermissionAndGetToken();
                console.log("FCM TOKEN:", token);

                // Foreground: tab đang mở
                unsubscribe = await listenForegroundMessage((payload) => {
                    const title = payload?.notification?.title ?? "Thông báo mới";
                    const body = payload?.notification?.body ?? "";
                    toast(title, { description: body });
                    window.dispatchEvent(new CustomEvent("fcm-message", { detail: payload }));
                });
            } catch (error) {
                console.error(error);
            }
        };

        init();

        // Background: SW gửi postMessage về page
        const swHandler = (event: MessageEvent) => {
            if (event.data?.type === "FCM_NOTIFICATION") {
                window.dispatchEvent(new CustomEvent("fcm-message"));
            }
        };
        navigator.serviceWorker?.addEventListener("message", swHandler);

        return () => {
            unsubscribe?.();
            navigator.serviceWorker?.removeEventListener("message", swHandler);
        };
    }, [user?.user_id]);

    return null;
}