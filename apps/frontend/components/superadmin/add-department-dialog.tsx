"use client"

import { useState } from "react"
import { toast } from "sonner"
import {
    referenceService,
    type Department,
} from "@/services/reference/reference.service"
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

type AddDepartmentDialogProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    departments: Department[]
    onCreated: (dept: Department) => void
}

const EMPTY_FORM = {
    department_code: "",
    department_name: "",
    parent_department_id: "",
    description: "",
    is_active: true,
}

export default function AddDepartmentDialog({ open, onOpenChange, departments, onCreated }: AddDepartmentDialogProps) {
    const [form, setForm] = useState(EMPTY_FORM)
    const [submitting, setSubmitting] = useState(false)

    const handleOpenChange = (next: boolean) => {
        if (!next) setForm(EMPTY_FORM)
        onOpenChange(next)
    }

    const handleSubmit = async () => {
        if (!form.department_code.trim() || !form.department_name.trim()) {
            toast.error("Vui lòng điền mã và tên đơn vị")
            return
        }

        setSubmitting(true)
        try {
            const created = await referenceService.createDepartment({
                department_code: form.department_code.trim(),
                department_name: form.department_name.trim(),
                parent_department_id: form.parent_department_id || null,
                description: form.description.trim() || null,
                is_active: form.is_active,
            })
            toast.success("Thêm đơn vị thành công")
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
                    <DialogTitle>Thêm đơn vị mới</DialogTitle>
                    <DialogDescription>Tạo phòng ban / khoa / đơn vị mới trong hệ thống.</DialogDescription>
                </DialogHeader>

                <div className="space-y-4">
                    <div className="space-y-1.5">
                        <Label htmlFor="add-dept-code">
                            Mã đơn vị <span className="text-red-500">*</span>
                        </Label>
                        <Input
                            id="add-dept-code"
                            autoComplete="off"
                            placeholder="VD: KHMT, CNTT..."
                            value={form.department_code}
                            onChange={(e) => setForm((prev) => ({ ...prev, department_code: e.target.value }))}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="add-dept-name">
                            Tên đơn vị <span className="text-red-500">*</span>
                        </Label>
                        <Input
                            id="add-dept-name"
                            autoComplete="off"
                            placeholder="VD: Khoa Công nghệ Thông tin"
                            value={form.department_name}
                            onChange={(e) => setForm((prev) => ({ ...prev, department_name: e.target.value }))}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label>Đơn vị cha (nếu có)</Label>
                        <Select
                            value={form.parent_department_id}
                            onValueChange={(value) => setForm((prev) => ({ ...prev, parent_department_id: value }))}
                        >
                            <SelectTrigger className="w-full">
                                <SelectValue placeholder="Không có đơn vị cha" />
                            </SelectTrigger>
                            <SelectContent>
                                {departments.map((dept) => (
                                    <SelectItem key={dept.department_id} value={dept.department_id}>
                                        {dept.department_name}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="add-dept-desc">Mô tả</Label>
                        <Textarea
                            id="add-dept-desc"
                            placeholder="Mô tả về đơn vị (không bắt buộc)"
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
                        {submitting ? "Đang lưu..." : "Thêm đơn vị"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
