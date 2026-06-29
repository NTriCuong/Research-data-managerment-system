"use client"

import type { Department } from "@/services/reference/reference.service"
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"

type DepartmentDetailDialogProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    department: Department | null
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

export default function DepartmentDetailDialog({ open, onOpenChange, department, departmentMap }: DepartmentDetailDialogProps) {
    if (!department) return null

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Chi tiết đơn vị</DialogTitle>
                </DialogHeader>

                <div className="divide-y rounded-lg border bg-gray-50/50 px-4">
                    <DetailRow label="Mã đơn vị" value={<code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs">{department.department_code}</code>} />
                    <DetailRow label="Tên đơn vị" value={department.department_name} />
                    <DetailRow
                        label="Đơn vị cha"
                        value={
                            department.parent_department_id
                                ? departmentMap[department.parent_department_id] ?? department.parent_department_id
                                : <span className="text-gray-400 italic">Không có</span>
                        }
                    />
                    <DetailRow label="Mô tả" value={department.description || <span className="text-gray-400 italic">Không có</span>} />
                    <DetailRow
                        label="Trạng thái"
                        value={
                            <Badge variant={department.is_active ? "default" : "secondary"} className={department.is_active ? "bg-green-100 text-green-700 hover:bg-green-100" : ""}>
                                {department.is_active ? "Đang hoạt động" : "Không hoạt động"}
                            </Badge>
                        }
                    />
                    <DetailRow label="ID" value={<span className="text-gray-400 text-xs">{department.department_id}</span>} />
                </div>
            </DialogContent>
        </Dialog>
    )
}
