"use client"

import { useState } from "react"
import { toast } from "sonner"
import { referenceService } from "@/services/reference/reference.service"
import type { OutputType } from "@/services/reference/reference.service"
import { parseAxiosError } from "@/lib/axios/error-paser"
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"

type AddOutputTypeDialogProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    onCreated: (item: OutputType) => void
}

const EMPTY_FORM = {
    type_code: "",
    type_name: "",
    description: "",
    is_active: true,
}

export default function AddOutputTypeDialog({ open, onOpenChange, onCreated }: AddOutputTypeDialogProps) {
    const [form, setForm] = useState(EMPTY_FORM)
    const [submitting, setSubmitting] = useState(false)

    const handleOpenChange = (next: boolean) => {
        if (!next) setForm(EMPTY_FORM)
        onOpenChange(next)
    }

    const handleSubmit = async () => {
        if (!form.type_code.trim() || !form.type_name.trim()) {
            toast.error("Vui lòng điền mã và tên loại sản phẩm")
            return
        }

        setSubmitting(true)
        try {
            const created = await referenceService.createOutputType({
                type_code: form.type_code.trim(),
                type_name: form.type_name.trim(),
                description: form.description.trim() || null,
                is_active: form.is_active,
            })
            toast.success("Thêm loại sản phẩm thành công")
            onCreated(created)
            handleOpenChange(false)
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={handleOpenChange}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Thêm loại sản phẩm mới</DialogTitle>
                    <DialogDescription>Tạo nhóm đầu ra nghiên cứu mới trong hệ thống.</DialogDescription>
                </DialogHeader>

                <div className="space-y-4">
                    <div className="space-y-1.5">
                        <Label htmlFor="add-ot-code">
                            Mã loại <span className="text-red-500">*</span>
                        </Label>
                        <Input
                            id="add-ot-code"
                            autoComplete="off"
                            placeholder="VD: JOURNAL, BOOK, CONF..."
                            value={form.type_code}
                            onChange={(e) => setForm((prev) => ({ ...prev, type_code: e.target.value }))}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="add-ot-name">
                            Tên loại <span className="text-red-500">*</span>
                        </Label>
                        <Input
                            id="add-ot-name"
                            autoComplete="off"
                            placeholder="VD: Bài báo khoa học, Sách chuyên khảo..."
                            value={form.type_name}
                            onChange={(e) => setForm((prev) => ({ ...prev, type_name: e.target.value }))}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="add-ot-desc">Mô tả</Label>
                        <Textarea
                            id="add-ot-desc"
                            placeholder="Mô tả về loại sản phẩm (không bắt buộc)"
                            rows={3}
                            value={form.description}
                            onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label>Trạng thái</Label>
                        <Select
                            value={form.is_active ? "active" : "inactive"}
                            onValueChange={(value) => setForm((prev) => ({ ...prev, is_active: value === "active" }))}
                        >
                            <SelectTrigger className="w-full">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="active">Đang hoạt động</SelectItem>
                                <SelectItem value="inactive">Không hoạt động</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </div>

                <DialogFooter>
                    <Button variant="outline" className="cursor-pointer hover:bg-[#243564] hover:text-white" onClick={() => handleOpenChange(false)}>
                        Huỷ
                    </Button>
                    <Button onClick={handleSubmit} className="border border-gray-900 cursor-pointer" disabled={submitting}>
                        {submitting ? "Đang lưu..." : "Thêm loại sản phẩm"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
