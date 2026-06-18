import type { StagingResearchObjectDetail } from "@/services/reference/reference.service"

function formatDate(value: string | null) {
    if (!value) return '-'
    return new Date(value).toLocaleDateString('vi-VN')
}

function formatFileSize(bytes: number) {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
    return (
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-6 text-base font-semibold text-gray-900">{title}</h2>
            {children}
        </div>
    )
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
    return (
        <div className="min-w-0">
            <p className="text-xs font-medium tracking-wide text-gray-400 uppercase">{label}</p>
            <p className="mt-1 wrap-break-word text-sm text-gray-800">{value}</p>
        </div>
    )
}

type StagingDetailViewProps = {
    detail: StagingResearchObjectDetail
    departmentMap: Record<string, string>
    outputTypeMap: Record<string, string>
}

export default function StagingDetailView({ detail, departmentMap, outputTypeMap }: StagingDetailViewProps) {
    return (
        <>
            <SectionCard title="Thông tin metadata">
                <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
                    <Field label="Loại sản phẩm" value={outputTypeMap[detail.output_type_id] ?? detail.output_type_id} />
                    <Field label="Đơn vị" value={departmentMap[detail.department_id] ?? detail.department_id} />
                    <Field label="Năm" value={detail.year ?? '-'} />
                    <Field label="Ngôn ngữ" value={detail.language ?? '-'} />
                    <div className="md:col-span-2">
                        <Field label="Mô tả" value={<span className="whitespace-pre-wrap">{detail.description ?? '-'}</span>} />
                    </div>
                    <div className="md:col-span-2">
                        <Field label="Tóm tắt" value={<span className="whitespace-pre-wrap">{detail.abstract ?? '-'}</span>} />
                    </div>
                </div>
            </SectionCard>

            <SectionCard title="Thông tin xuất bản">
                <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
                    <Field label="Start Date" value={formatDate(detail.start_date)} />
                    <Field label="End Date" value={formatDate(detail.end_date)} />
                    <Field label="Date Issued" value={formatDate(detail.date_issued)} />
                    <Field label="Publisher" value={detail.publisher ?? '-'} />
                    <Field label="Identifier" value={detail.identifier ?? '-'} />
                    <Field label="External URL" value={<span className="truncate">{detail.external_url ?? '-'}</span>} />
                    <Field label="Source" value={detail.source ?? '-'} />
                    <Field label="Relation" value={detail.relation ?? '-'} />
                    <Field label="Coverage" value={detail.coverage ?? '-'} />
                    <div className="md:col-span-3">
                        <Field label="Rights" value={detail.rights ?? '-'} />
                    </div>
                </div>
            </SectionCard>

            <SectionCard title="Phân loại">
                <div className="space-y-5">
                    <div>
                        <p className="mb-2 text-xs font-medium tracking-wide text-gray-400 uppercase">Phạm vi</p>
                        <div className="flex flex-wrap gap-2">
                            {detail.domains.length === 0 && <p className="text-sm text-gray-400">-</p>}
                            {detail.domains.map((d) => (
                                <span key={d.domain_id} className="rounded-full bg-blue-50 px-3 py-1 text-sm text-blue-700">
                                    {d.domain_name}
                                </span>
                            ))}
                        </div>
                    </div>

                    <div>
                        <p className="mb-2 text-xs font-medium tracking-wide text-gray-400 uppercase">Từ khóa</p>
                        <div className="flex flex-wrap gap-2">
                            {detail.keywords.length === 0 && <p className="text-sm text-gray-400">-</p>}
                            {detail.keywords.map((k) => (
                                <span key={k.keyword_id} className="rounded-full bg-green-50 px-3 py-1 text-sm text-green-700">
                                    {k.keyword_text}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            </SectionCard>

            <SectionCard title="Tác giả">
                <div className="space-y-3">
                    {detail.authors.length === 0 && <p className="text-sm text-gray-400">Không có tác giả</p>}
                    {detail.authors.map((author) => (
                        <div key={author.staging_author_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-4 py-3 text-sm">
                            <div>
                                <p className="font-medium text-gray-900">{author.full_name}</p>
                                <p className="text-gray-500">{author.email ?? '-'}{author.affiliation ? ` · ${author.affiliation}` : ''}</p>
                            </div>
                            <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-600">
                                {author.author_role}
                            </span>
                        </div>
                    ))}
                </div>
            </SectionCard>

            <SectionCard title="Tệp đính kèm">
                <ul className="divide-y divide-gray-100 rounded-lg border border-gray-100">
                    {detail.files.length === 0 && (
                        <li className="px-4 py-3 text-sm text-gray-400">Không có tệp</li>
                    )}
                    {detail.files.map((file) => (
                        <li key={file.file_id} className="flex items-center justify-between px-4 py-3 text-sm">
                            <span className="truncate text-gray-800">{file.original_filename}</span>
                            <span className="text-gray-400">{formatFileSize(file.file_size_bytes)}</span>
                        </li>
                    ))}
                </ul>
            </SectionCard>
        </>
    )
}
