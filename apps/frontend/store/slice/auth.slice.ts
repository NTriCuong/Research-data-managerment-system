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
    isInitializing: boolean
}

const initialState: AuthState = {
    currentUser: null,
    accessToken: null,
    isAuthenticated: false,
    isInitializing: true,
}

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        setCredentials: (
            state,
            action: PayloadAction<{ user: CurrentUser; accessToken: string }>
        ) => {
            state.currentUser = action.payload.user
            state.accessToken = action.payload.accessToken
            state.isAuthenticated = true
            state.isInitializing = false
        },
        clearCredentials: (state) => {
            state.currentUser = null
            state.accessToken = null
            state.isAuthenticated = false
            state.isInitializing = false
        },
    },
})

export const { setCredentials, clearCredentials } = authSlice.actions

export const selectCurrentUser = (state: RootState) => state.auth.currentUser
export const selectAccessToken = (state: RootState) => state.auth.accessToken
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated
export const selectIsInitializing = (state: RootState) => state.auth.isInitializing

export default authSlice.reducer
