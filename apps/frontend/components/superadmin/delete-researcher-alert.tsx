"use client"

import { useState } from "react"
import { toast } from "sonner"
import { referenceService } from "@/services/reference/reference.service"
import type { Researcher } from "@/services/reference/reference.service"
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

type DeleteResearcherAlertProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    researcher: Researcher | null
    onDeleted: (id: string) => void
}

export default function DeleteResearcherAlert({ open, onOpenChange, researcher, onDeleted }: DeleteResearcherAlertProps) {
    const [submitting, setSubmitting] = useState(false)

    const handleConfirm = async () => {
        if (!researcher) return
        setSubmitting(true)
        try {
            await referenceService.deleteResearcher(researcher.researcher_id)
            toast.success("Xoá nhà nghiên cứu thành công")
            onDeleted(researcher.researcher_id)
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
                    <AlertDialogTitle>Xoá nhà nghiên cứu này?</AlertDialogTitle>
                    <AlertDialogDescription>
                        Bạn sắp xoá hồ sơ của{" "}
                        <span className="font-medium">{researcher?.full_name}</span>
                        {researcher?.email && (
                            <> ({researcher.email})</>
                        )}
                        . Hành động này không thể hoàn tác.
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
