"use client"

import { useState } from "react"
import { toast } from "sonner"
import { referenceService } from "@/services/reference/reference.service"
import type { Department, Researcher } from "@/services/reference/reference.service"
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

type AddResearcherDialogProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    departments: Department[]
    onCreated: (item: Researcher) => void
}

const EMPTY_FORM = {
    full_name: "",
    email: "",
    orcid: "",
    department_id: "",
    academic_title: "",
    researcher_code: "",
    is_internal: "true",
}

export default function AddResearcherDialog({ open, onOpenChange, departments, onCreated }: AddResearcherDialogProps) {
    const [form, setForm] = useState(EMPTY_FORM)
    const [submitting, setSubmitting] = useState(false)

    const set = (key: keyof typeof EMPTY_FORM) => (value: string) =>
        setForm((prev) => ({ ...prev, [key]: value }))

    const handleOpenChange = (next: boolean) => {
        if (!next) setForm(EMPTY_FORM)
        onOpenChange(next)
    }

    const handleSubmit = async () => {
        if (!form.full_name.trim()) {
            toast.error("Vui lòng nhập họ tên nhà nghiên cứu")
            return
        }

        setSubmitting(true)
        try {
            const created = await referenceService.createResearcher({
                full_name: form.full_name.trim(),
                email: form.email.trim() || undefined,
                orcid: form.orcid.trim() || undefined,
                department_id: form.department_id || undefined,
                academic_title: form.academic_title.trim() || undefined,
                researcher_code: form.researcher_code.trim() || undefined,
                is_internal: form.is_internal === "true",
            })
            toast.success("Thêm nhà nghiên cứu thành công")
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
            <DialogContent className="sm:max-w-lg">
                <DialogHeader>
                    <DialogTitle>Thêm nhà nghiên cứu mới</DialogTitle>
                    <DialogDescription>Tạo hồ sơ tác giả / cộng tác viên trong hệ thống.</DialogDescription>
                </DialogHeader>

                <div className="grid grid-cols-2 gap-4">
                    <div className="col-span-2 space-y-1.5">
                        <Label htmlFor="add-r-name">
                            Họ tên <span className="text-red-500">*</span>
                        </Label>
                        <Input
                            id="add-r-name"
                            autoComplete="off"
                            placeholder="Nguyễn Văn A"
                            value={form.full_name}
                            onChange={(e) => set("full_name")(e.target.value)}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="add-r-email">Email</Label>
                        <Input
                            id="add-r-email"
                            type="email"
                            autoComplete="off"
                            placeholder="example@uni.edu.vn"
                            value={form.email}
                            onChange={(e) => set("email")(e.target.value)}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="add-r-orcid">ORCID</Label>
                        <Input
                            id="add-r-orcid"
                            autoComplete="off"
                            placeholder="0000-0000-0000-0000"
                            value={form.orcid}
                            onChange={(e) => set("orcid")(e.target.value)}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="add-r-code">Mã nhà nghiên cứu</Label>
                        <Input
                            id="add-r-code"
                            autoComplete="off"
                            value={form.researcher_code}
                            onChange={(e) => set("researcher_code")(e.target.value)}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="add-r-title">Học hàm / học vị</Label>
                        <Input
                            id="add-r-title"
                            autoComplete="off"
                            placeholder="TS, PGS.TS, GS.TS..."
                            value={form.academic_title}
                            onChange={(e) => set("academic_title")(e.target.value)}
                        />
                    </div>

                    <div className="col-span-2 space-y-1.5">
                        <Label>Đơn vị</Label>
                        <Select value={form.department_id} onValueChange={set("department_id")}>
                            <SelectTrigger className="w-full">
                                <SelectValue placeholder="Chọn đơn vị (không bắt buộc)" />
                            </SelectTrigger>
                            <SelectContent>
                                {departments.map((d) => (
                                    <SelectItem key={d.department_id} value={d.department_id}>
                                        {d.department_name}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="col-span-2 space-y-1.5">
                        <Label>Loại nhà nghiên cứu</Label>
                        <Select value={form.is_internal} onValueChange={set("is_internal")}>
                            <SelectTrigger className="w-full">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="true">Nội bộ (thuộc trường)</SelectItem>
                                <SelectItem value="false">Bên ngoài</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </div>

                <DialogFooter>
                    <Button variant="outline" className="cursor-pointer hover:bg-[#243564] hover:text-white" onClick={() => handleOpenChange(false)}>
                        Huỷ
                    </Button>
                    <Button onClick={handleSubmit} className="border border-gray-900 cursor-pointer" disabled={submitting}>
                        {submitting ? "Đang lưu..." : "Thêm nhà nghiên cứu"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
