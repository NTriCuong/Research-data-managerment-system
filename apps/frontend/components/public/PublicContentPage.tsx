import type { LucideIcon } from "lucide-react"

import { PublicShell } from "@/components/public/PublicShell"

type PublicContentPageProps = {
    eyebrow: string
    title: string
    description: string
    icon: LucideIcon
    children: React.ReactNode
}

export function PublicContentPage({
    eyebrow,
    title,
    description,
    icon: Icon,
    children,
}: PublicContentPageProps) {
    return (
        <PublicShell>
            <section className="border-b border-blue-200 bg-linear-to-br from-blue-50 via-white to-sky-100">
                <div className="mx-auto flex w-full max-w-7xl items-center gap-5 px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
                    <div className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-blue-500 text-white shadow-sm sm:size-16">
                        <Icon className="size-7 sm:size-8" aria-hidden="true" />
                    </div>
                    <div>
                        <p className="mb-1 text-sm font-semibold uppercase tracking-widest text-blue-600">{eyebrow}</p>
                        <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">{title}</h1>
                        <p className="mt-3 max-w-3xl text-base leading-7 text-gray-600 sm:text-lg">{description}</p>
                    </div>
                </div>
            </section>
            <div className="mx-auto w-full max-w-7xl px-4 py-10 sm:px-6 sm:py-14 lg:px-8">
                {children}
            </div>
        </PublicShell>
    )
}
