"use client"

import { useState } from "react"
import { toast } from "sonner"
import {
    referenceService,
    type AppUser,
    type Department,
    type Role,
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

type AddUserDialogProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    roles: Role[]
    departments: Department[]
    onCreated: (user: AppUser) => void
}

const EMPTY_FORM = {
    username: "",
    email: "",
    password: "",
    full_name: "",
    role_id: "",
    department_id: "",
}

export default function AddUserDialog({ open, onOpenChange, roles, departments, onCreated }: AddUserDialogProps) {
    const [form, setForm] = useState(EMPTY_FORM)
    const [submitting, setSubmitting] = useState(false)

    const handleOpenChange = (next: boolean) => {
        if (!next) setForm(EMPTY_FORM)
        onOpenChange(next)
    }

    const handleSubmit = async () => {
        if (!form.username || !form.email || !form.password || !form.full_name || !form.role_id) {
            toast.error("Vui lòng điền đầy đủ thông tin bắt buộc")
            return
        }

        setSubmitting(true)
        try {
            const created = await referenceService.createUser({
                username: form.username,
                email: form.email,
                password: form.password,
                full_name: form.full_name,
                role_id: form.role_id,
                department_id: form.department_id || null,
            })
            toast.success("Thêm người dùng thành công")
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
                    <DialogTitle>Thêm người dùng (Add user)</DialogTitle>
                    <DialogDescription>Tạo tài khoản mới cho người dùng trong hệ thống.</DialogDescription>
                </DialogHeader>

                <div className="space-y-4">
                    <div className="space-y-1.5">
                        <Label htmlFor="add-username">Tên đăng nhập (Username)</Label>
                        <Input
                            id="add-username"
                            autoComplete="off"
                            value={form.username}
                            onChange={(e) => setForm((prev) => ({ ...prev, username: e.target.value }))}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="add-email">Email</Label>
                        <Input
                            id="add-email"
                            type="email"
                            autoComplete="off"
                            value={form.email}
                            onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="add-password">Mật khẩu (Password)</Label>
                        <Input
                            id="add-password"
                            type="password"
                            autoComplete="new-password"
                            value={form.password}
                            onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="add-full-name">Họ tên (Full name)</Label>
                        <Input
                            id="add-full-name"
                            autoComplete="off"
                            value={form.full_name}
                            onChange={(e) => setForm((prev) => ({ ...prev, full_name: e.target.value }))}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label>Vai trò (Role)</Label>
                        <Select
                            value={form.role_id}
                            onValueChange={(value) => setForm((prev) => ({ ...prev, role_id: value }))}
                        >
                            <SelectTrigger className="w-full">
                                <SelectValue placeholder="Chọn vai trò" />
                            </SelectTrigger>
                            <SelectContent>
                                {roles.map((role) => (
                                    <SelectItem key={role.role_id} value={role.role_id}>
                                        {role.role_name}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="space-y-1.5">
                        <Label>Đơn vị (Department)</Label>
                        <Select
                            value={form.department_id}
                            onValueChange={(value) => setForm((prev) => ({ ...prev, department_id: value }))}
                        >
                            <SelectTrigger className="w-full">
                                <SelectValue placeholder="Chọn đơn vị (không bắt buộc)" />
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
                </div>

                <DialogFooter>
                    <Button variant="outline" className="cursor-pointer hover:bg-[#243564] hover:text-white" onClick={() => handleOpenChange(false)}>
                        Huỷ
                    </Button>
                    <Button onClick={handleSubmit} className="border border-gray-900 cursor-pointer" disabled={submitting}>
                        {submitting ? "Đang lưu..." : "Thêm người dùng"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
