'use client'

import { clearCredentials, setCredentials } from '@/store/slice/auth.slice'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { authService } from '@/services/auth/auth.service'
import { useAppDispatch, useAppSelector } from './hooks'
import { PUBLIC_ROUTES } from '@/lib/auth/routes'

export default function AuthInitializer() {
    const dispatch = useAppDispatch()
    const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated)
    const router = useRouter()
    const pathname = usePathname()

    useEffect(() => {
        if (isAuthenticated) return

        if (PUBLIC_ROUTES.includes(pathname)) {
            dispatch(clearCredentials())
            return
        }

        authService.refreshToken()
            .then((data) => {
                dispatch(setCredentials({ user: data.user, accessToken: data.access_token }))
            })
            .catch(() => {
                dispatch(clearCredentials())
                router.replace('/login')
            })
    }, [pathname])

    return null
}
