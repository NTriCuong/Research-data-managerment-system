import type { Metadata } from "next"
import { Archive, Database, Eye, GraduationCap, Target } from "lucide-react"

import { PublicContentPage } from "@/components/public/PublicContentPage"

export const metadata: Metadata = {
    title: "Giới thiệu | RDMS STU",
    description: "Giới thiệu Cổng dữ liệu nghiên cứu của Trường Đại học Công nghệ Sài Gòn.",
}

export default function AboutPage() {
    return (
        <PublicContentPage
            eyebrow="Về hệ thống"
            title="Cổng dữ liệu nghiên cứu STU"
            description="Không gian tập trung để quản lý, bảo tồn, tra cứu và chia sẻ các kết quả nghiên cứu của Trường Đại học Công nghệ Sài Gòn."
            imageSrc="/undraw_online-page_qiv4.svg"
            imageAlt="Minh họa cổng dữ liệu nghiên cứu trực tuyến"
        >
            <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
                <div className="rounded-2xl border border-gray-200 bg-white p-7 shadow-sm">
                    <h2 className="text-2xl font-semibold text-gray-900">Về RDMS</h2>
                    <div className="mt-4 space-y-4 leading-7 text-gray-600">
                        <p>Hệ thống Quản lý Dữ liệu Nghiên cứu (RDMS) hỗ trợ Nhà trường tổ chức thông tin về đề tài, bài báo, báo cáo khoa học, bộ dữ liệu và các sản phẩm nghiên cứu khác trên một nền tảng thống nhất.</p>
                        <p>Thông qua quy trình nhập liệu, kiểm duyệt và phê duyệt, dữ liệu được chuẩn hóa trước khi công bố; từ đó giúp giảng viên, sinh viên và cộng đồng dễ dàng tìm kiếm, tiếp cận và tái sử dụng phù hợp.</p>
                    </div>
                </div>
                <div className="rounded-2xl bg-blue-600 p-7 text-white shadow-sm">
                    <Target className="size-9 text-blue-100" />
                    <h2 className="mt-5 text-2xl font-semibold">Mục tiêu</h2>
                    <p className="mt-4 leading-7 text-blue-50">Nâng cao khả năng tiếp cận tri thức, thúc đẩy hợp tác nghiên cứu và gìn giữ lâu dài giá trị học thuật do cộng đồng STU tạo ra.</p>
                </div>
            </section>
            <section className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
                {[
                    { icon: Database, title: "Tập trung", text: "Quản lý dữ liệu và sản phẩm nghiên cứu tập trung." },
                    { icon: Eye, title: "Minh bạch", text: "Theo dõi nguồn gốc, tác giả và quyền truy cập rõ ràng." },
                    { icon: Archive, title: "Bảo tồn", text: "Lưu giữ tri thức khoa học có hệ thống và lâu dài." },
                    { icon: GraduationCap, title: "Lan tỏa", text: "Hỗ trợ học tập, giảng dạy và hợp tác nghiên cứu." },
                ].map(({ icon: Icon, title, text }) => (
                    <article key={title} className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
                        <Icon className="size-7 text-blue-600" />
                        <h2 className="mt-4 font-semibold text-gray-900">{title}</h2>
                        <p className="mt-2 text-sm leading-6 text-gray-600">{text}</p>
                    </article>
                ))}
            </section>
        </PublicContentPage>
    )
}
