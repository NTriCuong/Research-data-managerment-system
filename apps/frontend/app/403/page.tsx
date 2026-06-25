"use client";

import { useRouter } from "next/navigation";
import { useAppSelector } from "@/lib/hooks/hooks";
import { selectCurrentUser } from "@/store/slice/auth.slice";
import { getRoleHomePath } from "@/lib/auth/routes";

export default function ForbiddenPage() {
    const router = useRouter();
    const currentUser = useAppSelector(selectCurrentUser);

    const handleBack = () => {
        if (currentUser) {
            router.replace(getRoleHomePath(currentUser.role_name));
        } else {
            router.replace("/login");
        }
    };
    return (
        <div className="flex min-h-[70vh] flex-col items-center justify-center px-4 text-center">
            <h1 className="text-3xl font-bold text-red-600">
                403 - Access Denied
            </h1>

            <p className="mt-4 text-muted-foreground">
                Bạn không có quyền truy cập vào trang này.
            </p>

            <button
                onClick={handleBack}
                className="mt-6 rounded-lg bg-gray-300 px-5 py-2 text-black transition-colors duration-200 hover:bg-gray-400"
            >
                Trở về
            </button>
        </div>
    );
}
