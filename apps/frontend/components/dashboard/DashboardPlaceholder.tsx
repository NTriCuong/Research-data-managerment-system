import type { LucideIcon } from 'lucide-react'

type DashboardPlaceholderProps = {
    title: string
    description: string
    icon: LucideIcon
}

export default function DashboardPlaceholder({ title, description, icon: Icon }: DashboardPlaceholderProps) {
    return (
        <div className="space-y-6 p-6">
            <div>
                <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>
                <p className="mt-1 text-sm text-gray-500">{description}</p>
            </div>

            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                <div className="flex min-h-64 flex-col items-center justify-center gap-3 px-6 py-12 text-center">
                    <div className="flex size-10 items-center justify-center rounded-lg border border-gray-200 bg-gray-50 text-gray-500">
                        <Icon size={20} />
                    </div>
                    <div>
                        <h2 className="text-sm font-semibold text-gray-900">Chưa có nội dung</h2>
                        <p className="mt-1 max-w-md text-sm text-gray-500">Màn hình này đã được giữ cùng khung dashboard và sẵn sàng để nối dữ liệu.</p>
                    </div>
                </div>
            </div>
        </div>
    )
}
