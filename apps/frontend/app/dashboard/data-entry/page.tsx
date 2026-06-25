
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function DataEntryPage() {
    const router = useRouter()

    useEffect(() => {
        router.replace('/dashboard/data-entry/researches')
    }, [router])

    return null
}
