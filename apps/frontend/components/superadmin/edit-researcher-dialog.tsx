"use client"

import { useEffect, useState } from "react"
import { toast } from "sonner"
import { referenceService } from "@/services/reference/reference.service"
import type { Department, Researcher } from "@/services/reference/reference.service"
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

type EditResearcherDialogProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    researcher: Researcher | null
    departments: Department[]
    onUpdated: (item: Researcher) => void
}

export default function EditResearcherDialog({ open, onOpenChange, researcher, departments, onUpdated }: EditResearcherDialogProps) {
    const [fullName, setFullName] = useState("")
    const [email, setEmail] = useState("")
    const [orcid, setOrcid] = useState("")
    const [departmentId, setDepartmentId] = useState("")
    const [academicTitle, setAcademicTitle] = useState("")
    const [researcherCode, setResearcherCode] = useState("")
    const [isInternal, setIsInternal] = useState("true")
    const [submitting, setSubmitting] = useState(false)

    useEffect(() => {
        if (researcher) {
            setFullName(researcher.full_name)
            setEmail(researcher.email ?? "")
            setOrcid(researcher.orcid ?? "")
            setDepartmentId(researcher.department_id ?? "")
            setAcademicTitle(researcher.academic_title ?? "")
            setResearcherCode(researcher.researcher_code ?? "")
            setIsInternal(researcher.is_internal ? "true" : "false")
        }
    }, [researcher])

    const handleSubmit = async () => {
        if (!researcher) return
        if (!fullName.trim()) {
            toast.error("Vui lòng nhập họ tên nhà nghiên cứu")
            return
        }

        setSubmitting(true)
        try {
            const updated = await referenceService.updateResearcher(researcher.researcher_id, {
                full_name: fullName.trim(),
                email: email.trim() || null,
                orcid: orcid.trim() || null,
                department_id: departmentId || null,
                academic_title: academicTitle.trim() || null,
                researcher_code: researcherCode.trim() || null,
                is_internal: isInternal === "true",
            })
            toast.success("Cập nhật nhà nghiên cứu thành công")
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
            <DialogContent className="sm:max-w-lg">
                <DialogHeader>
                    <DialogTitle className="text-xl font-bold">Sửa nhà nghiên cứu</DialogTitle>
                </DialogHeader>

                <div className="grid grid-cols-2 gap-4">
                    <div className="col-span-2 space-y-1.5">
                        <Label htmlFor="edit-r-name">
                            Họ tên <span className="text-red-500">*</span>
                        </Label>
                        <Input
                            id="edit-r-name"
                            autoComplete="off"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="edit-r-email">Email</Label>
                        <Input
                            id="edit-r-email"
                            type="email"
                            autoComplete="off"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="edit-r-orcid">ORCID</Label>
                        <Input
                            id="edit-r-orcid"
                            autoComplete="off"
                            value={orcid}
                            onChange={(e) => setOrcid(e.target.value)}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="edit-r-code">Mã nhà nghiên cứu</Label>
                        <Input
                            id="edit-r-code"
                            autoComplete="off"
                            value={researcherCode}
                            onChange={(e) => setResearcherCode(e.target.value)}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="edit-r-title">Học hàm / học vị</Label>
                        <Input
                            id="edit-r-title"
                            autoComplete="off"
                            value={academicTitle}
                            onChange={(e) => setAcademicTitle(e.target.value)}
                        />
                    </div>

                    <div className="col-span-2 space-y-1.5">
                        <Label>Đơn vị</Label>
                        <Select value={departmentId} onValueChange={setDepartmentId}>
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
                        <Select value={isInternal} onValueChange={setIsInternal}>
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
