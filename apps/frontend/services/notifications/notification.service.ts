import axiosInstance from "@/lib/axios/axios.instance";
import { API_ENDPOINT } from "@/lib/constants/api-endpoint";

export interface AppNotification {
    notification_id: string;
    recipient_user_id: string;
    actor_user_id: string | null;
    event_type: string;
    title: string;
    message: string;
    target_url: string | null;
    payload: Record<string, unknown> | null;
    read_at: string | null;
    created_at: string;
}

export const notificationService = {
    async list() {
        const response = await axiosInstance.get<AppNotification[]>(API_ENDPOINT.NOTIFICATIONS.LIST, {
            params: { limit: 20 },
        });
        return response.data;
    },

    async markRead(notificationId: string) {
        const response = await axiosInstance.post<AppNotification>(
            API_ENDPOINT.NOTIFICATIONS.MARK_READ(notificationId)
        );
        return response.data;
    },
};
