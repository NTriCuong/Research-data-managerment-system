"use client"

import { useState } from "react"
import { toast } from "sonner"
import { referenceService, type AppUser } from "@/services/reference/reference.service"
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

type DeleteUserAlertProps = {
    open: boolean
    onOpenChange: (open: boolean) => void
    user: AppUser | null
    onDeleted: (userId: string) => void
}

export default function DeleteUserAlert({ open, onOpenChange, user, onDeleted }: DeleteUserAlertProps) {
    const [submitting, setSubmitting] = useState(false)

    const handleConfirm = async () => {
        if (!user) return
        setSubmitting(true)
        try {
            await referenceService.deleteUser(user.user_id)
            toast.success("Xoá người dùng thành công")
            onDeleted(user.user_id)
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
                    <AlertDialogTitle>Xoá người dùng này?</AlertDialogTitle>
                    <AlertDialogDescription>
                        Bạn sắp xoá tài khoản <span className="font-medium">{user?.full_name}</span> ({user?.username}).
                        Hành động này không thể hoàn tác.
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
