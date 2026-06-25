import { useDispatch, useSelector } from 'react-redux'
import type { AppDispatch, RootState } from '../../store/store'

import { getToken, onMessage } from "firebase/messaging";
import { messaging } from '../configFilebase/firebaseConfig';

// hook cho reducer redux
export const useAppDispatch = useDispatch.withTypes<AppDispatch>()
export const useAppSelector = useSelector.withTypes<RootState>()

// hook cho filebase
// Đọc VAPID key từ env
const VAPID_KEY = process.env.NEXT_PUBLIC_FIREBASE_VAPID_KEY!;

export async function requestPermissionAndGetToken(): Promise<string | null> {
    // Xin quyền hiện notification — trình duyệt sẽ hiện popup hỏi user
    const permission = await Notification.requestPermission();

    // Nếu user từ chối → dừng lại, không báo lỗi
    if (permission !== "granted") {
        console.log("Notification permission denied");
        return null;
    }

    // Lấy FCM token cho thiết bị/trình duyệt này
    // vapidKey dùng để xác thực với FCM server
    const token = await getToken(messaging, { vapidKey: VAPID_KEY });

    console.log("FCM Token:", token);

    // Gửi token lên backend để lưu vào DB
    // Từ đây backend biết "muốn nhắn cho user này thì dùng token này"
    await fetch("/api/notifications/register-token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token }),
    });

    return token;
}

// Hàm này lắng nghe notification khi app đang MỞ
// callback sẽ được gọi mỗi khi có message mới
export function listenForegroundMessage(callback: (payload: any) => void) {
    return onMessage(messaging, callback);
    // onMessage trả về unsubscribe function — dùng để cleanup trong useEffect
}

