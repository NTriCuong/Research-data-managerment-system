// Lấy hàm khởi tạo app từ Firebase core
import { getApps, initializeApp } from "firebase/app";

// Lấy module messaging để dùng push notification
import { getMessaging } from "firebase/messaging";

const firebaseConfig = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
    measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID,
};
console.log(firebaseConfig);


const app = getApps().length ? getApps()[0] : initializeApp(firebaseConfig);

export const messaging =
    typeof window !== "undefined" ? getMessaging(app) : null;

export default app;