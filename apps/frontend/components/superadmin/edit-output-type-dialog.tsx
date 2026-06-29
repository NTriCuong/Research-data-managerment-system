"use client"

import { useEffect, useState } from "react"
import { toast } from "sonner"
import { referenceService } from "@/services/reference/reference.service"
import type { OutputType } from "@/services/reference/reference.service"
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

type EditOutputTypeDialogProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    outputType: OutputType | null
    onUpdated: (item: OutputType) => void
}

export default function EditOutputTypeDialog({ open, onOpenChange, outputType, onUpdated }: EditOutputTypeDialogProps) {
    const [code, setCode] = useState("")
    const [name, setName] = useState("")
    const [description, setDescription] = useState("")
    const [isActive, setIsActive] = useState(true)
    const [submitting, setSubmitting] = useState(false)

    useEffect(() => {
        if (outputType) {
            setCode(outputType.type_code)
            setName(outputType.type_name)
            setDescription(outputType.description ?? "")
            setIsActive(outputType.is_active)
        }
    }, [outputType])

    const handleSubmit = async () => {
        if (!outputType) return
        if (!code.trim() || !name.trim()) {
            toast.error("Vui lòng điền mã và tên loại sản phẩm")
            return
        }

        setSubmitting(true)
        try {
            const updated = await referenceService.updateOutputType(outputType.output_type_id, {
                type_code: code.trim(),
                type_name: name.trim(),
                description: description.trim() || null,
                is_active: isActive,
            })
            toast.success("Cập nhật loại sản phẩm thành công")
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
                    <DialogTitle className="text-xl font-bold">Sửa loại sản phẩm</DialogTitle>
                </DialogHeader>

                <div className="space-y-4">
                    <div className="space-y-1.5">
                        <Label htmlFor="edit-ot-code">
                            Mã loại <span className="text-red-500">*</span>
                        </Label>
                        <Input
                            id="edit-ot-code"
                            autoComplete="off"
                            value={code}
                            onChange={(e) => setCode(e.target.value)}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="edit-ot-name">
                            Tên loại <span className="text-red-500">*</span>
                        </Label>
                        <Input
                            id="edit-ot-name"
                            autoComplete="off"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label htmlFor="edit-ot-desc">Mô tả</Label>
                        <Textarea
                            id="edit-ot-desc"
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
