import app from "../../lib/configFilebase/firebaseConfig";
import { getMessaging, isSupported } from "firebase/messaging";

let messaging: any = null;

export async function getFirebaseMessaging() {
    if (typeof window === "undefined") return null;

    const supported = await isSupported();
    if (!supported) return null;

    if (!messaging) {
        messaging = getMessaging(app);
    }

    return messaging;
}