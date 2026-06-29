"use client"

import { useState } from "react"
import { toast } from "sonner"
import { referenceService } from "@/services/reference/reference.service"
import type { OutputType } from "@/services/reference/reference.service"
import { parseAxiosError } from "@/lib/axios/error-paser"
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog"

type DeleteOutputTypeAlertProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    outputType: OutputType | null
    onDeleted: (id: string) => void
}

export default function DeleteOutputTypeAlert({ open, onOpenChange, outputType, onDeleted }: DeleteOutputTypeAlertProps) {
    const [submitting, setSubmitting] = useState(false)

    const handleConfirm = async () => {
        if (!outputType) return
        setSubmitting(true)
        try {
            await referenceService.deleteOutputType(outputType.output_type_id)
            toast.success("Xoá loại sản phẩm thành công")
            onDeleted(outputType.output_type_id)
            onOpenChange(false)
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <AlertDialog open={open} onOpenChange={onOpenChange}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>Xoá loại sản phẩm này?</AlertDialogTitle>
                    <AlertDialogDescription>
                        Bạn sắp xoá loại sản phẩm <span className="font-medium">{outputType?.type_name}</span> (mã:{" "}
                        <span className="font-medium">{outputType?.type_code}</span>). Hành động này không thể hoàn tác.
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel disabled={submitting}>Huỷ</AlertDialogCancel>
                    <AlertDialogAction onClick={handleConfirm} disabled={submitting}>
                        {submitting ? "Đang xoá..." : "Xoá"}
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    )
}
