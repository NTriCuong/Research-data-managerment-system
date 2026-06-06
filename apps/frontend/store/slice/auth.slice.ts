import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import type { RootState } from '../store'

export interface CurrentUser {
    user_id: string
    username: string
    email: string
    full_name: string
    role_name: string
    department_name: string | null
}

interface AuthState {
    currentUser: CurrentUser | null
    accessToken: string | null
    isAuthenticated: boolean
}

const initialState: AuthState = {
    currentUser: null,
    accessToken: null,
    isAuthenticated: false, //login hay chưa login
}
// tạo slice
const authSlice = createSlice({
    name: 'auth',
    initialState, // trạng thái ban đầu (default)
    reducers: {
        setCredentials: ( // set state khi login thành công, lưu thông tin user và token vào state
            state,
            action: PayloadAction<{ user: CurrentUser; accessToken: string }>
        ) => {
            state.currentUser = action.payload.user
            state.accessToken = action.payload.accessToken
            state.isAuthenticated = true
        },
        clearCredentials: (state) => { // xoá thông tin user và token khi logout
            state.currentUser = null
            state.accessToken = null
            state.isAuthenticated = false
        },
    },
})

export const { setCredentials, clearCredentials } = authSlice.actions

export const selectCurrentUser = (state: RootState) => state.auth.currentUser // lấy thông tin user
export const selectAccessToken = (state: RootState) => state.auth.accessToken // lấy token
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated   // lấy trạng thái đã login hay chưa

export default authSlice.reducer
