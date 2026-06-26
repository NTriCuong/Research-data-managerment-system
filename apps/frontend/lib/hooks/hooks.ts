import { useDispatch, useSelector } from 'react-redux'
import type { AppDispatch, RootState } from '../../store/store'

import { getToken, onMessage } from "firebase/messaging";
import { getFirebaseMessaging } from '@/components/filebase/firebaseMessaging';
import axiosInstance from '@/lib/axios/axios.instance';
import { API_ENDPOINT } from '@/lib/constants/api-endpoint';

// hook cho reducer redux
export const useAppDispatch = useDispatch.withTypes<AppDispatch>()
export const useAppSelector = useSelector.withTypes<RootState>()

const VAPID_KEY = process.env.NEXT_PUBLIC_FIREBASE_VAPID_KEY!;

export async function requestPermissionAndGetToken(): Promise<string | null> {
    const permission = await Notification.requestPermission();
    if (permission !== "granted") return null;

    const messaging = await getFirebaseMessaging();
    if (!messaging) return null;

    const token = await getToken(messaging, { vapidKey: VAPID_KEY });

    await axiosInstance.post(API_ENDPOINT.NOTIFICATION.REGISTER_TOKEN, {
        fcm_token: token,
        device_name: navigator.userAgent,
    });

    return token;
}

export async function listenForegroundMessage(callback: (payload: any) => void) {
    const messaging = await getFirebaseMessaging();
    if (!messaging) return;

    return onMessage(messaging, callback);
}