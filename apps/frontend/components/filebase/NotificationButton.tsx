"use client";

export default function NotificationButton() {
    const requestPermission = async () => {
        const permission = await Notification.requestPermission();
        console.log("Permission:", permission);
    };

    return (
        <button onClick={requestPermission}></button>
    );
}