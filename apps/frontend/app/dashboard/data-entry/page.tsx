
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { requestPermissionAndGetToken } from '@/lib/hooks/hooks';

export default function DataEntryPage() {
    const router = useRouter()

    useEffect(() => {
        router.replace('/dashboard/data-entry/researches')
    }, [router])

    return null
}
