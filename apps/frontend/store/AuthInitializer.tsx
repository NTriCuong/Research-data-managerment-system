'use client'

import { clearCredentials, selectIsAuthenticated, setCredentials } from '@/store/slice/auth.slice'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { authService } from '@/services/auth/auth.service'
import { PUBLIC_ROUTE_PREFIXES, PUBLIC_ROUTES } from '@/lib/auth/routes'
import { useAppDispatch, useAppSelector } from '@/lib/hooks/hooks'

const isPublicPath = (pathname: string) =>
    PUBLIC_ROUTES.includes(pathname) ||
    PUBLIC_ROUTE_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`))

export default function AuthInitializer() {
    const dispatch = useAppDispatch()
    const isAuthenticated = useAppSelector(selectIsAuthenticated)
    const router = useRouter()
    const pathname = usePathname()

    useEffect(() => {
        if (isAuthenticated) return

        const publicPath = isPublicPath(pathname)

        authService.refreshToken({ silent: publicPath })
            .then((data) => {
                dispatch(setCredentials({ user: data.user, accessToken: data.access_token }))
            })
            .catch(() => {
                dispatch(clearCredentials())
                if (!publicPath) {
                    router.replace('/login')
                }
            })
    }, [dispatch, isAuthenticated, pathname, router])

    return null
}
