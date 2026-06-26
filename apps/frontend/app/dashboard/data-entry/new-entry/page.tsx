'use client'

import FormMetadata from '@/components/data-entry/Form-metadata'

export default function NewEntryPage() {
    return (
        <div className="space-y-6">
            <div className="px-6 pt-6">
                <h1 className="text-2xl font-semibold text-gray-900">Thêm bài nghiên cứu mới</h1>
                <p className="mt-1 text-sm text-gray-500">Nhập metadata, tác giả và tệp đính kèm cho bản ghi nghiên cứu.</p>
            </div>
            <FormMetadata />
        </div>
    )
}
