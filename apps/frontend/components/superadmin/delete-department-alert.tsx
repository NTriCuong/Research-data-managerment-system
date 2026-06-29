"use client"

import { useState } from "react"
import { toast } from "sonner"
import { referenceService, type Department } from "@/services/reference/reference.service"
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

type DeleteDepartmentAlertProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    department: Department | null
    onDeleted: (departmentId: string) => void
}

export default function DeleteDepartmentAlert({ open, onOpenChange, department, onDeleted }: DeleteDepartmentAlertProps) {
    const [submitting, setSubmitting] = useState(false)

    const handleConfirm = async () => {
        if (!department) return
        setSubmitting(true)
        try {
            await referenceService.deleteDepartment(department.department_id)
            toast.success("Xoá đơn vị thành công")
            onDeleted(department.department_id)
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
                    <AlertDialogTitle>Xoá đơn vị này?</AlertDialogTitle>
                    <AlertDialogDescription>
                        Bạn sắp xoá đơn vị <span className="font-medium">{department?.department_name}</span> (mã:{" "}
                        <span className="font-medium">{department?.department_code}</span>). Hành động này không thể hoàn tác.
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
