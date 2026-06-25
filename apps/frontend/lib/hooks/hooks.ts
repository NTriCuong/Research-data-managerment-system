import { useDispatch, useSelector } from 'react-redux'
import type { AppDispatch, RootState } from '../../store/store'

import { getToken, onMessage } from "firebase/messaging";
import { getFirebaseMessaging } from '@/components/filebase/firebaseMessaging';

// hook cho reducer redux
export const useAppDispatch = useDispatch.withTypes<AppDispatch>()
export const useAppSelector = useSelector.withTypes<RootState>()

// hook cho filebase
// Đọc VAPID key từ env

const VAPID_KEY = process.env.NEXT_PUBLIC_FIREBASE_VAPID_KEY!;

export async function requestPermissionAndGetToken(
    userId: string
): Promise<string | null> {
    const permission = await Notification.requestPermission();
    if (permission !== "granted") return null;

    const messaging = await getFirebaseMessaging();
    if (!messaging) return null;

    const token = await getToken(messaging, {
        vapidKey: VAPID_KEY,
    });

    console.log({
        userId,
        token,
        userAgent: navigator.userAgent,
    });
    await fetch("http://localhost:8000/api/v1/notifications/register-token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: userId,
            fcm_token: token,
            device_name: navigator.userAgent
        }),
    });

    return token;
}

export async function listenForegroundMessage(callback: (payload: any) => void) {
    const messaging = await getFirebaseMessaging();
    if (!messaging) return;

    return onMessage(messaging, callback);
}