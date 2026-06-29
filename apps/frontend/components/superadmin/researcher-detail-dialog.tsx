"use client"

import type { Researcher, Department } from "@/services/reference/reference.service"
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"

type ResearcherDetailDialogProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    researcher: Researcher | null
    departmentMap: Record<string, string>
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
    return (
        <div className="grid grid-cols-5 gap-2 py-2.5 border-b last:border-b-0">
            <span className="col-span-2 text-sm text-gray-500">{label}</span>
            <span className="col-span-3 text-sm text-gray-900 break-words">{value ?? "-"}</span>
        </div>
    )
}

function formatDateTime(value: string | null) {
    if (!value) return "-"
    return new Date(value).toLocaleString("vi-VN")
}

export default function ResearcherDetailDialog({ open, onOpenChange, researcher, departmentMap }: ResearcherDetailDialogProps) {
    if (!researcher) return null

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Chi tiết nhà nghiên cứu</DialogTitle>
                </DialogHeader>

                <div className="divide-y rounded-lg border bg-gray-50/50 px-4">
                    <DetailRow label="Họ tên" value={<span className="font-medium">{researcher.full_name}</span>} />
                    <DetailRow label="Email" value={researcher.email || <span className="text-gray-400 italic">Không có</span>} />
                    <DetailRow label="ORCID" value={researcher.orcid || <span className="text-gray-400 italic">Không có</span>} />
                    <DetailRow label="Mã NNC" value={researcher.researcher_code || <span className="text-gray-400 italic">Không có</span>} />
                    <DetailRow label="Học hàm / học vị" value={researcher.academic_title || <span className="text-gray-400 italic">Không có</span>} />
                    <DetailRow
                        label="Đơn vị"
                        value={
                            researcher.department_id
                                ? departmentMap[researcher.department_id] ?? researcher.department_id
                                : <span className="text-gray-400 italic">Không có</span>
                        }
                    />
                    <DetailRow
                        label="Loại"
                        value={
                            <Badge variant={researcher.is_internal ? "default" : "secondary"} className={researcher.is_internal ? "bg-blue-100 text-blue-700 hover:bg-blue-100" : ""}>
                                {researcher.is_internal ? "Nội bộ" : "Bên ngoài"}
                            </Badge>
                        }
                    />
                    <DetailRow label="Ngày tạo" value={formatDateTime(researcher.created_at)} />
                    <DetailRow label="ID" value={<span className="text-gray-400 text-xs">{researcher.researcher_id}</span>} />
                </div>
            </DialogContent>
        </Dialog>
    )
}
