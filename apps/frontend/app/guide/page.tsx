import type { Metadata } from "next"
import Link from "next/link"
import { ArrowRight, BookOpen, Download, LogIn, Search, UserRoundCheck } from "lucide-react"

import { PublicContentPage } from "@/components/public/PublicContentPage"
import { Button } from "@/components/ui/button"

export const metadata: Metadata = {
    title: "Hướng dẫn sử dụng | RDMS STU",
    description: "Hướng dẫn tra cứu và khai thác dữ liệu nghiên cứu trên RDMS STU.",
}

const steps = [
    { icon: Search, title: "Tìm kiếm", text: "Nhập từ khóa tại trang chủ hoặc mở Bộ lọc để thu hẹp kết quả theo loại sản phẩm, đơn vị, năm và lĩnh vực." },
    { icon: BookOpen, title: "Xem thông tin", text: "Chọn một kết quả để xem mô tả, tác giả, từ khóa, quyền truy cập và danh sách tệp đính kèm." },
    { icon: UserRoundCheck, title: "Kiểm tra quyền", text: "Tài nguyên công khai có thể xem trực tiếp. Một số dữ liệu yêu cầu đăng nhập hoặc được cấp quyền phù hợp." },
    { icon: Download, title: "Khai thác dữ liệu", text: "Tải tệp khi nút tải xuống khả dụng và luôn tuân thủ điều kiện sử dụng, bản quyền, trích dẫn của tài nguyên." },
]

export default function GuidePage() {
    return (
        <PublicContentPage
            eyebrow="Bắt đầu nhanh"
            title="Hướng dẫn sử dụng"
            description="Tra cứu và khai thác dữ liệu nghiên cứu trên hệ thống qua bốn bước đơn giản."
            icon={BookOpen}
        >
            <section className="grid gap-5 md:grid-cols-2">
                {steps.map(({ icon: Icon, title, text }, index) => (
                    <article key={title} className="relative rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                        <span className="absolute right-5 top-4 text-4xl font-bold text-blue-100">{String(index + 1).padStart(2, "0")}</span>
                        <div className="flex size-11 items-center justify-center rounded-xl bg-blue-50 text-blue-600"><Icon className="size-5" /></div>
                        <h2 className="mt-4 text-lg font-semibold text-gray-900">{title}</h2>
                        <p className="mt-2 text-sm leading-6 text-gray-600">{text}</p>
                    </article>
                ))}
            </section>
            <section className="mt-8 flex flex-col items-start justify-between gap-5 rounded-2xl bg-blue-600 p-7 text-white sm:flex-row sm:items-center">
                <div>
                    <h2 className="text-xl font-semibold">Sẵn sàng tra cứu?</h2>
                    <p className="mt-1 text-sm text-blue-100">Khám phá các công trình và bộ dữ liệu đã được công bố.</p>
                </div>
                <div className="flex gap-3">
                    <Button asChild variant="secondary"><Link href="/researches">Mở bộ lọc <ArrowRight /></Link></Button>
                    <Button asChild variant="outline" className="border-white/40 bg-transparent text-white hover:bg-white/10 hover:text-white"><Link href="/login"><LogIn /> Đăng nhập</Link></Button>
                </div>
            </section>
        </PublicContentPage>
    )
}
