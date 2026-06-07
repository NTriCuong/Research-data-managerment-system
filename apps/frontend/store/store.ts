import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slice/auth.slice'

export const makeStore = () =>
    configureStore({
        reducer: {
            auth: authReducer, // thêm reducer vào store 
        },
    })

export type AppStore = ReturnType<typeof makeStore>
export type RootState = ReturnType<AppStore['getState']>
export type AppDispatch = AppStore['dispatch']
