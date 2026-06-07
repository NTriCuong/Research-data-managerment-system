import type { InternalAxiosRequestConfig } from 'axios'
import { clearCredentials, setCredentials } from '@/store/slice/auth.slice'
import type { AppStore } from '@/store/store'
import axiosInstance from './axios.instance'
import { parseAxiosError } from './error-paser'
import { API_ENDPOINT } from '../constants/api-endpoint'

type QueueItem = {
    resolve: (token: string) => void
    reject: (error: unknown) => void
}

let isRefreshing = false
let failedQueue: QueueItem[] = []

const flushQueue = (error: unknown, newToken: string | null = null) => {
    failedQueue.forEach(({ resolve, reject }) =>
        error ? reject(error) : resolve(newToken!)
    )
    failedQueue = []
}

export const setupInterceptors = (store: AppStore) => {
    // ── Request: gắn access token vào header ─────────────────────────────────
    axiosInstance.interceptors.request.use(
        (config: InternalAxiosRequestConfig) => {
            const token = store.getState().auth.accessToken // lấy accesstoken từ state
            if (token) {
                config.headers.Authorization = `Bearer ${token}` // gắn token vào header Authorization 
            }
            return config
        },
        (error) => Promise.reject(error)
    )

    // ── Response: xử lý access token hết hạn ────────────────────────────────────────
    axiosInstance.interceptors.response.use(
        (response) => response,
        async (error) => {
            const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

            const is401 = error.response?.status === 401
            const isRefreshEndpoint = original.url?.includes(API_ENDPOINT.AUTH.REFRESH)
            const isLoginEndpoint = original.url?.includes(API_ENDPOINT.AUTH.LOGIN)

            // Không retry nếu: không phải 401, đã retry, là refresh endpoint, hoặc là login endpoint
            if (!is401 || original._retry || isRefreshEndpoint || isLoginEndpoint) {
                if (isRefreshEndpoint) {
                    flushQueue(error, null)
                    store.dispatch(clearCredentials())
                    window.location.href = '/login'
                }
                return Promise.reject(parseAxiosError(error))
            }

            // Nếu đang refresh, xếp request vào queue chờ
            if (isRefreshing) {
                return new Promise<string>((resolve, reject) => {
                    failedQueue.push({ resolve, reject })
                }).then((token) => {
                    original.headers.Authorization = `Bearer ${token}`
                    return axiosInstance(original)
                })
            }

            original._retry = true // thêm 1 thuộc tính mới là _retry vào request cũ để đánh dấu đã retry
            // tránh vòng lặp vô hạn
            isRefreshing = true

            try {
                const { data } = await axiosInstance.post<{
                    access_token: string
                    user: { user_id: string; username: string; email: string; full_name: string; role_name: string; department_name: string | null }
                }>(API_ENDPOINT.AUTH.REFRESH)

                store.dispatch(setCredentials({ user: data.user, accessToken: data.access_token }))
                flushQueue(null, data.access_token)

                original.headers.Authorization = `Bearer ${data.access_token}`
                return axiosInstance(original)
            } catch (refreshError) {
                flushQueue(refreshError, null)
                store.dispatch(clearCredentials())
                return Promise.reject(parseAxiosError(refreshError))
            } finally {
                isRefreshing = false
            }
        }
    )
}
