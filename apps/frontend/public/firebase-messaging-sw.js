// Import Firebase compat version (bắt buộc dùng compat trong Service Worker
// vì SW không hỗ trợ ES Module import/export)
importScripts("https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js");

// Khởi tạo Firebase trong Service Worker — phải lặp lại config, không import được từ file khác
firebase.initializeApp({
    apiKey: "AIzaSyD4Qxr4Xb7KMNARC6-BptXh3aL76r_SFOk",
    authDomain: "rdms-v1.firebaseapp.com",
    projectId: "rdms-v1",
    storageBucket: "rdms-v1.firebasestorage.app",
    messagingSenderId: "319561945174",
    appId: "1:319561945174:web:980c39b19eb5c1171bebf7",
});

// Lấy messaging instance trong SW
const messaging = firebase.messaging();

// Hàm này được gọi khi app đang ĐÓNG hoặc tab đang ở background
// onBackgroundMessage = "tôi nhận được message khi user không đang xem app"
messaging.onBackgroundMessage((payload) => {
    console.log("Background message received:", payload);

    self.registration.showNotification(
        payload.notification.title,
        {
            body: payload.notification.body,
            icon: "/favicon.ico",
        }
    );

    // Thông báo cho tất cả các tab đang mở để cập nhật danh sách thông báo
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((clients) => {
        clients.forEach((client) => client.postMessage({ type: "FCM_NOTIFICATION" }));
    });
});