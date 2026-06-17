'use client'

import { useSearchParams } from 'next/navigation'

export default function UpdateMetadataPage() {
    const searchParams = useSearchParams()
    const stagingId = searchParams.get('staging_id')

    return (
        <div className="p-6">
            <h1 className="mb-4 text-2xl font-bold">Update Metadata</h1>
            <p className="text-sm text-gray-500">Staging ID: {stagingId}</p>
        </div>
    )
}
