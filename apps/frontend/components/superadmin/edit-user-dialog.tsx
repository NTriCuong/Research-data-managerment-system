"use client"

import { useEffect, useState } from "react"
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

type EditUserDialogProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    user: AppUser | null
    roles: Role[]
    departments: Department[]
    onUpdated: (user: AppUser) => void
}

export default function EditUserDialog({ open, onOpenChange, user, roles, departments, onUpdated }: EditUserDialogProps) {
    const [username, setUsername] = useState("")
    const [email, setEmail] = useState("")
    const [fullName, setFullName] = useState("")
    const [departmentId, setDepartmentId] = useState("")
    const [roleId, setRoleId] = useState("")
    const [submitting, setSubmitting] = useState(false)

    useEffect(() => {
        if (user) {
            setUsername(user.username)
            setEmail(user.email)
            setFullName(user.full_name)
            setDepartmentId(user.department_id ?? "")
            setRoleId(user.role_id)
        }
    }, [user])

    const handleSubmit = async () => {
        if (!user) return
        if (!username || !email || !fullName) {
            toast.error("Vui lòng điền đầy đủ thông tin bắt buộc")
            return
        }

        setSubmitting(true)
        try {
            let updated = await referenceService.updateUser(user.user_id, {
                username,
                email,
                full_name: fullName,
                department_id: departmentId || null,
            })

            if (roleId !== user.role_id) {
                updated = await referenceService.updateUserRole(user.user_id, roleId)
            }

            toast.success("Cập nhật người dùng thành công")
            onUpdated(updated)
            onOpenChange(false)
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle className="text-xl font-bold">Sửa người dùng (Edit user)</DialogTitle>
                </DialogHeader>

                <div className="space-y-4">
                    <div className="space-y-1.5">
                        <Label htmlFor="edit-username">Tên đăng nhập (Username)</Label>
                        <Input id="edit-username" autoComplete="off" value={username} onChange={(e) => setUsername(e.target.value)} />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="edit-email">Email</Label>
                        <Input id="edit-email" type="email" autoComplete="off" value={email} onChange={(e) => setEmail(e.target.value)} />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="edit-full-name">Họ tên (Full name)</Label>
                        <Input id="edit-full-name" autoComplete="off" value={fullName} onChange={(e) => setFullName(e.target.value)} />
                    </div>

                    <div className="space-y-1.5">
                        <Label>Vai trò (Role)</Label>
                        <Select value={roleId} onValueChange={setRoleId}>
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
                        <Select value={departmentId} onValueChange={setDepartmentId}>
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
                    <Button variant="outline" className="cursor-pointer  hover:bg-gray-100" onClick={() => onOpenChange(false)}>
                        Huỷ
                    </Button>
                    <Button onClick={handleSubmit} variant="outline" className="cursor-pointer hover:bg-gray-200" disabled={submitting}>
                        {submitting ? "Đang lưu..." : "Lưu thay đổi"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
