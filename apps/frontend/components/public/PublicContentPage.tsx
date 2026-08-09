import Image from "next/image"

import { PublicShell } from "@/components/public/PublicShell"

type PublicContentPageProps = {
    eyebrow: string
    title: string
    description: string
    imageSrc: string
    imageAlt: string
    children: React.ReactNode
}

export function PublicContentPage({
    eyebrow,
    title,
    description,
    imageSrc,
    imageAlt,
    children,
}: PublicContentPageProps) {
    return (
        <PublicShell>
            <section className="border-b border-blue-200 bg-linear-to-br from-blue-50 via-white to-sky-100">
                <div className="mx-auto grid w-full max-w-7xl items-center gap-8 px-4 py-10 sm:px-6 sm:py-12 md:grid-cols-2 md:gap-12 lg:px-8">
                    <div className="min-w-0">
                        <p className="mb-1 text-sm font-semibold uppercase tracking-widest text-blue-600">{eyebrow}</p>
                        <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">{title}</h1>
                        <p className="mt-3 max-w-3xl text-base leading-7 text-gray-600 sm:text-lg">{description}</p>
                    </div>
                    <div className="flex min-h-52 items-center justify-center sm:min-h-64 md:min-h-72">
                        <Image
                            src={imageSrc}
                            alt={imageAlt}
                            width={560}
                            height={360}
                            className="h-auto max-h-72 w-full object-contain"
                            sizes="(min-width: 768px) 50vw, 100vw"
                            priority
                        />
                    </div>
                </div>
            </section>
            <div className="mx-auto w-full max-w-7xl px-4 py-10 sm:px-6 sm:py-14 lg:px-8">
                {children}
            </div>
        </PublicShell>
    )
}
