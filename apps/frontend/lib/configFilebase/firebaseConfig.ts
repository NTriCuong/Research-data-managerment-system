// Lấy hàm khởi tạo app từ Firebase core
import { getApps, initializeApp } from "firebase/app";

// Lấy module messaging để dùng push notification
import { getMessaging } from "firebase/messaging";

// Copy nguyên config này từ Firebase Console — đây là thông tin định danh app của bạn
const firebaseConfig = {
    apiKey: "AIzaSyD4Qxr4Xb7KMNARC6-BptXh3aL76r_SFOk",
    authDomain: "rdms-v1.firebaseapp.com",
    projectId: "rdms-v1",
    storageBucket: "rdms-v1.firebasestorage.app",
    messagingSenderId: "319561945174",
    appId: "1:319561945174:web:980c39b19eb5c1171bebf7",
    measurementId: "G-C8XJGFSJTE"
};

const app = getApps().length ? getApps()[0] : initializeApp(firebaseConfig);

export default app;