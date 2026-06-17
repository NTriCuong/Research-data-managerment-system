import Link from "next/link";

export default function GuestHeader() {
    return (
        <header className="flex h-12 w-full items-center justify-between border-b border-gray-200 px-20">
            <div className="flex items-center gap-3 text-lg font-bold text-[#1f3b8c]">
                <span className="text-2xl">⚗️</span>
                <span>RDMS</span>
            </div>

            <Link
                href="/login"
                className="cursor-pointer rounded-2xl border border-gray-300 px-7 py-2 text-[17px] text-[#1f3b8c] transition hover:bg-gray-100"
            >
                Đăng Nhập
            </Link>
        </header>
    );
}
