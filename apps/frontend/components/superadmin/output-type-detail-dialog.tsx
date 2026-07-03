"use client"

import type { OutputType } from "@/services/reference/reference.service"
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"

type OutputTypeDetailDialogProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    outputType: OutputType | null
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
    return (
        <div className="grid grid-cols-5 gap-2 py-2.5 border-b last:border-b-0">
            <span className="col-span-2 text-sm text-gray-500">{label}</span>
            <span className="col-span-3 text-sm text-gray-900 break-words">{value ?? "-"}</span>
        </div>
    )
}

export default function OutputTypeDetailDialog({ open, onOpenChange, outputType }: OutputTypeDetailDialogProps) {
    if (!outputType) return null

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Chi tiết loại sản phẩm</DialogTitle>
                </DialogHeader>

                <div className="divide-y rounded-lg border bg-gray-50/50 px-4">
                    <DetailRow
                        label="Mã loại"
                        value={<code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs">{outputType.type_code}</code>}
                    />
                    <DetailRow label="Tên loại" value={outputType.type_name} />
                    <DetailRow
                        label="Mô tả"
                        value={outputType.description || <span className="text-gray-400 italic">Không có</span>}
                    />
                    <DetailRow
                        label="Trạng thái"
                        value={
                            <Badge
                                variant={outputType.is_active ? "default" : "secondary"}
                                className={outputType.is_active ? "bg-green-100 text-green-700 hover:bg-green-100" : ""}
                            >
                                {outputType.is_active ? "Đang hoạt động" : "Không hoạt động"}
                            </Badge>
                        }
                    />
                    <DetailRow
                        label="ID"
                        value={<span className="text-gray-400 text-xs">{outputType.output_type_id}</span>}
                    />
                </div>
            </DialogContent>
        </Dialog>
    )
}
