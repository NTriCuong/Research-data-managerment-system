"use client"

import { useEffect, useState } from "react"
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

type EditDepartmentDialogProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    department: Department | null
    departments: Department[]
    onUpdated: (dept: Department) => void
}

export default function EditDepartmentDialog({ open, onOpenChange, department, departments, onUpdated }: EditDepartmentDialogProps) {
    const [code, setCode] = useState("")
    const [name, setName] = useState("")
    const [parentId, setParentId] = useState("")
    const [description, setDescription] = useState("")
    const [isActive, setIsActive] = useState(true)
    const [submitting, setSubmitting] = useState(false)

    useEffect(() => {
        if (department) {
            setCode(department.department_code)
            setName(department.department_name)
            setParentId(department.parent_department_id ?? "")
            setDescription(department.description ?? "")
            setIsActive(department.is_active)
        }
    }, [department])

    const handleSubmit = async () => {
        if (!department) return
        if (!code.trim() || !name.trim()) {
            toast.error("Vui lòng điền mã và tên đơn vị")
            return
        }

        setSubmitting(true)
        try {
            const updated = await referenceService.updateDepartment(department.department_id, {
                department_code: code.trim(),
                department_name: name.trim(),
                parent_department_id: parentId || null,
                description: description.trim() || null,
                is_active: isActive,
            })
            toast.success("Cập nhật đơn vị thành công")
            onUpdated(updated)
            onOpenChange(false)
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setSubmitting(false)
        }
    }

    const otherDepts = departments.filter((d) => d.department_id !== department?.department_id)

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle className="text-xl font-bold">Sửa đơn vị</DialogTitle>
                </DialogHeader>

                <div className="space-y-4">
                    <div className="space-y-1.5">
                        <Label htmlFor="edit-dept-code">
                            Mã đơn vị <span className="text-red-500">*</span>
                        </Label>
                        <Input
                            id="edit-dept-code"
                            autoComplete="off"
                            value={code}
                            onChange={(e) => setCode(e.target.value)}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="edit-dept-name">
                            Tên đơn vị <span className="text-red-500">*</span>
                        </Label>
                        <Input
                            id="edit-dept-name"
                            autoComplete="off"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label>Đơn vị cha (nếu có)</Label>
                        <Select value={parentId} onValueChange={setParentId}>
                            <SelectTrigger className="w-full">
                                <SelectValue placeholder="Không có đơn vị cha" />
                            </SelectTrigger>
                            <SelectContent>
                                {otherDepts.map((dept) => (
                                    <SelectItem key={dept.department_id} value={dept.department_id}>
                                        {dept.department_name}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="edit-dept-desc">Mô tả</Label>
                        <Textarea
                            id="edit-dept-desc"
                            rows={3}
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label>Trạng thái</Label>
                        <Select
                            value={isActive ? "active" : "inactive"}
                            onValueChange={(value) => setIsActive(value === "active")}
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
                    <Button variant="outline" className="cursor-pointer hover:bg-gray-100" onClick={() => onOpenChange(false)}>
                        Huỷ
                    </Button>
                    <Button variant="outline" className="cursor-pointer hover:bg-gray-200" onClick={handleSubmit} disabled={submitting}>
                        {submitting ? "Đang lưu..." : "Lưu thay đổi"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
