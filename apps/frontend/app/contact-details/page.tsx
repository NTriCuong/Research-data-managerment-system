import type { Metadata } from "next"
import { Clock3, Mail, MapPin, Phone } from "lucide-react"

import { PublicContentPage } from "@/components/public/PublicContentPage"

export const metadata: Metadata = {
    title: "Liên hệ | RDMS STU",
    description: "Thông tin liên hệ Phòng Khoa học Công nghệ, Trường Đại học Công nghệ Sài Gòn.",
}

const contacts = [
    { icon: Mail, label: "Email", value: "qlkh@stu.edu.vn", href: "mailto:qlkh@stu.edu.vn" },
    { icon: Phone, label: "Điện thoại", value: "(84.8) 3850 5520 - Ext: 206", href: "tel:+842838505520" },
    { icon: MapPin, label: "Địa chỉ", value: "180 Cao Lỗ, Phường 4, Quận 8, TP. Hồ Chí Minh" },
    { icon: Clock3, label: "Thời gian hỗ trợ", value: "Thứ Hai – Thứ Sáu, trong giờ hành chính" },
]

export default function ContactPage() {
    return (
        <PublicContentPage
            eyebrow="Hỗ trợ"
            title="Liên hệ"
            description="Liên hệ Phòng Khoa học Công nghệ khi bạn cần hỗ trợ về tài khoản, dữ liệu nghiên cứu hoặc quy trình sử dụng hệ thống."
            imageSrc="/undraw_contact-us_s4jn.svg"
            imageAlt="Minh họa liên hệ và hỗ trợ"
        >
            <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
                <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1" aria-label="Thông tin liên hệ">
                    {contacts.map(({ icon: Icon, label, value, href }) => (
                        <div key={label} className="flex gap-4 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
                            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                                <Icon className="size-5" aria-hidden="true" />
                            </div>
                            <div>
                                <h2 className="font-semibold text-gray-900">{label}</h2>
                                {href ? (
                                    <a href={href} className="mt-1 block text-sm leading-6 text-blue-600 hover:underline">{value}</a>
                                ) : (
                                    <p className="mt-1 text-sm leading-6 text-gray-600">{value}</p>
                                )}
                            </div>
                        </div>
                    ))}
                </section>
                <section className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
                    <iframe
                        title="Bản đồ Trường Đại học Công nghệ Sài Gòn"
                        src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3919.9544104264664!2d106.67525180913164!3d10.73799718936426!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x31752f62a90e5dbd%3A0x674d5126513db295!2zVHLGsOG7nW5nIMSQ4bqhaSBo4buNYyBDw7RuZyBuZ2jhu4cgU8OgaSBHw7Ju!5e0!3m2!1svi!2s!4v1783740818310!5m2!1svi!2s"
                        className="h-full min-h-105 w-full border-0"
                        loading="lazy"
                        referrerPolicy="no-referrer-when-downgrade"
                    />
                </section>
            </div>
        </PublicContentPage>
    )
}
