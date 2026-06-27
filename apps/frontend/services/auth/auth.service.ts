import axiosInstance from "@/lib/axios/axios.instance"
import { parseAxiosError } from "@/lib/axios/error-paser"
import { API_ENDPOINT } from "@/lib/constants/api-endpoint"
import { clearCredentials } from "@/store/slice/auth.slice"
import type { AppDispatch } from "@/store/store"

export const authService = {
    async login(identifier: string, password: string) {
        const response = await axiosInstance.post(API_ENDPOINT.AUTH.LOGIN, {
            username: identifier,
            password,
        })
        return response.data
    },

    async logout(dispatch: AppDispatch) {
        try {
            await axiosInstance.post(API_ENDPOINT.AUTH.LOGOUT)
        } catch (error) {
            throw parseAxiosError(error)
        } finally {
            dispatch(clearCredentials()) // xoá credentials khỏi state khi logout dù thành công hay thát bại 
        }
    },
    async refreshToken(options?: { silent?: boolean }) {
        const response = await axiosInstance.post(
            API_ENDPOINT.AUTH.REFRESH,
            undefined,
            options?.silent ? { headers: { "X-Skip-Auth-Redirect": "1" } } : undefined
        )
        return response.data
    },
}
