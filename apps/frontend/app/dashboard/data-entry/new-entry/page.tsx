'use client'

import FormMetadata from "@/components/data-entry/Form-metadata"

export default function NewEntryPage() {
    return (
        <>

            <div className="border-b border-gray-200 bg-white px-6 py-5">
                <h1 className="text-2xl font-semibold text-gray-900">Thêm bài nghiên cứu mới</h1>
            </div>
            <FormMetadata />
        </>
    )
}
