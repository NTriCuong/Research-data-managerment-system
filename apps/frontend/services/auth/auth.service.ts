import axiosInstance from "@/lib/axios/axios.instance"
import { parseAxiosError } from "@/lib/axios/error-paser"
import { API_ENDPOINT } from "@/lib/constants/api-endpoint"
import { clearCredentials } from "@/store/slice/auth.slice"
import type { AppDispatch } from "@/store/store"

export const authService = {
    async login(username: string, password: string) {
        try {
            const response = await axiosInstance.post(API_ENDPOINT.AUTH.LOGIN, {
                username,
                password,
            })
            return response.data
        } catch (error) {
            throw parseAxiosError(error)
        }
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
}
