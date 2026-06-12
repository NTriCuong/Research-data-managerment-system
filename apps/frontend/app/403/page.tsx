// app/dashboard/403/page.tsx

"use client";

import { useRouter } from "next/navigation";

export default function ForbiddenPage() {
    const router = useRouter();

    return (
        <div className="flex min-h-[70vh] flex-col items-center justify-center px-4 text-center">
            <h1 className="text-3xl font-bold text-red-600">
                403 - Access Denied
            </h1>

            <p className="mt-4 text-muted-foreground">
                Bạn không có quyền truy cập vào trang này.
            </p>

            <button
                onClick={() => router.back()}
                className="mt-6 rounded-lg bg-gray-300 px-5 py-2 text-black transition-colors duration-200 hover:bg-gray-400"            >
                Trở về
            </button>
        </div>
    );
}