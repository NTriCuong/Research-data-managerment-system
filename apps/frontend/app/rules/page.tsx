import type { Metadata } from "next"
import { Ban, CheckCircle2, Copyright, Scale, ShieldCheck } from "lucide-react"

import { PublicContentPage } from "@/components/public/PublicContentPage"

export const metadata: Metadata = {
    title: "Quy định sử dụng | RDMS STU",
    description: "Quy định khai thác và sử dụng dữ liệu nghiên cứu của Trường Đại học Công nghệ Sài Gòn.",
}

export default function RegulationsPage() {
    return (
        <PublicContentPage
            eyebrow="Chính sách sử dụng"
            title="Quy định"
            description="Các nguyên tắc áp dụng khi truy cập, khai thác và sử dụng tài nguyên trên Cổng dữ liệu nghiên cứu STU."
            icon={Scale}
        >
            <div className="grid gap-6 lg:grid-cols-3">
                <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm lg:col-span-2">
                    <h2 className="flex items-center gap-2 text-xl font-semibold text-gray-900"><ShieldCheck className="text-blue-600" /> Nguyên tắc chung</h2>
                    <p className="mt-4 leading-7 text-gray-600">Các bộ dữ liệu và công trình khoa học được cung cấp nhằm hỗ trợ hoạt động giảng dạy, học tập và nghiên cứu. Người sử dụng phải tuân thủ Luật Sở hữu trí tuệ Việt Nam, quy định của pháp luật và quy chế quản trị tài sản trí tuệ của Nhà trường.</p>
                    <ol className="mt-6 space-y-4">
                        {[
                            "Chỉ sử dụng tài liệu đúng mục đích giảng dạy, học tập và nghiên cứu.",
                            "Trích dẫn đầy đủ tác giả, tên công trình và nguồn dữ liệu khi sử dụng.",
                            "Tôn trọng mức truy cập và các điều kiện sử dụng được công bố cho từng tài nguyên.",
                            "Tự chịu trách nhiệm về nội dung, phạm vi và hệ quả của việc sử dụng dữ liệu.",
                        ].map((item, index) => (
                            <li key={item} className="flex gap-3 text-gray-700">
                                <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-blue-50 text-sm font-semibold text-blue-700">{index + 1}</span>
                                <span className="pt-0.5 leading-6">{item}</span>
                            </li>
                        ))}
                    </ol>
                </section>
                <aside className="rounded-2xl border border-red-100 bg-red-50 p-6">
                    <h2 className="flex items-center gap-2 text-xl font-semibold text-red-900"><Ban /> Không được phép</h2>
                    <ul className="mt-5 space-y-4 text-sm leading-6 text-red-900/80">
                        <li>Chia sẻ hoặc chuyển giao tài khoản cho người khác.</li>
                        <li>Tải dữ liệu hàng loạt bằng công cụ tự động khi chưa được cho phép.</li>
                        <li>Sao chép, sửa đổi hoặc phân phối trái với quyền sở hữu trí tuệ.</li>
                        <li>Sử dụng dữ liệu vào mục đích trái pháp luật hoặc gây tổn hại cho cá nhân, tổ chức.</li>
                    </ul>
                </aside>
            </div>
            <section className="mt-6 grid gap-4 sm:grid-cols-2">
                <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                    <h2 className="flex items-center gap-2 font-semibold text-gray-900"><Copyright className="text-blue-600" /> Bản quyền và trích dẫn</h2>
                    <p className="mt-3 text-sm leading-6 text-gray-600">Quyền tác giả vẫn thuộc về tác giả hoặc đơn vị sở hữu. Việc hiển thị trên hệ thống không đồng nghĩa với chuyển giao quyền sở hữu.</p>
                </div>
                <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                    <h2 className="flex items-center gap-2 font-semibold text-gray-900"><CheckCircle2 className="text-blue-600" /> Xử lý vi phạm</h2>
                    <p className="mt-3 text-sm leading-6 text-gray-600">Nhà trường có thể thu hồi quyền truy cập, khóa tài khoản và áp dụng biện pháp xử lý phù hợp; người vi phạm chịu trách nhiệm trước pháp luật nếu có.</p>
                </div>
            </section>
        </PublicContentPage>
    )
}
