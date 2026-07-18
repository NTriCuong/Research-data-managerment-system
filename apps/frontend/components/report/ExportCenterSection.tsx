'use client'

import { useEffect, useState } from 'react'
import { Building2, Download, FileSpreadsheet, UserRound } from 'lucide-react'
import { toast } from 'sonner'

import { reportService } from '@/services/reports/report.service'
import { referenceService, type Department, type Researcher } from '@/services/reference/reference.service'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'

const CURRENT_YEAR = new Date().getFullYear()
const YEAR_OPTIONS = Array.from({ length: CURRENT_YEAR - 2014 }, (_, i) => CURRENT_YEAR - i)
const ALL_YEARS_VALUE = 'all'
const SEARCH_DEBOUNCE_MS = 300

function ResearcherCombobox({
    onSelect,
    placeholder,
}: {
    onSelect: (researcher: Researcher | null) => void
    placeholder: string
}) {
    const [query, setQuery] = useState('')
    const [open, setOpen] = useState(false)
    const [options, setOptions] = useState<Researcher[]>([])
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (!open) return
        setLoading(true)
        const timer = setTimeout(async () => {
            try {
                const result = await referenceService.suggestResearchers(query, 10)
                setOptions(result)
            } catch {
                setOptions([])
            } finally {
                setLoading(false)
            }
        }, SEARCH_DEBOUNCE_MS)
        return () => clearTimeout(timer)
    }, [query, open])

    const handleSelect = (researcher: Researcher) => {
        setQuery(researcher.full_name)
        onSelect(researcher)
        setOpen(false)
    }

    return (
        <div className="relative">
            <Input
                value={query}
                placeholder={placeholder}
                autoComplete="off"
                onFocus={() => setOpen(true)}
                onChange={(e) => {
                    setQuery(e.target.value)
                    onSelect(null)
                    setOpen(true)
                }}
                onBlur={() => setTimeout(() => setOpen(false), 150)}
            />
            {open && (
                <div className="absolute z-20 mt-1 max-h-60 w-full overflow-y-auto rounded-lg border border-gray-200 bg-white shadow-md">
                    {loading ? (
                        <div className="px-3 py-2 text-xs text-gray-400">Đang tìm...</div>
                    ) : options.length === 0 ? (
                        <div className="px-3 py-2 text-xs text-gray-400">Không tìm thấy nhà nghiên cứu</div>
                    ) : (
                        options.map((r) => (
                            <button
                                key={r.researcher_id}
                                type="button"
                                onMouseDown={(e) => e.preventDefault()}
                                onClick={() => handleSelect(r)}
                                className="block w-full truncate px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
                            >
                                {r.full_name}
                                {r.researcher_code && (
                                    <span className="ml-1 text-xs text-gray-400">({r.researcher_code})</span>
                                )}
                            </button>
                        ))
                    )}
                </div>
            )}
        </div>
    )
}

function ExportCard({
    icon: Icon,
    title,
    description,
    children,
}: {
    icon: React.ElementType
    title: string
    description: string
    children: React.ReactNode
}) {
    return (
        <div className="flex flex-col rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
                <div className="rounded-lg bg-blue-50 p-2">
                    <Icon size={16} className="text-blue-600" />
                </div>
                <div>
                    <h3 className="text-sm font-semibold text-gray-800">{title}</h3>
                    <p className="text-xs text-gray-400">{description}</p>
                </div>
            </div>
            <div className="mt-auto space-y-3">{children}</div>
        </div>
    )
}

export default function ExportCenterSection() {
    const [departments, setDepartments] = useState<Department[]>([])
    const [loadingOptions, setLoadingOptions] = useState(true)

    const [researcherId, setResearcherId] = useState('')
    const [year, setYear] = useState(String(CURRENT_YEAR))
    const [departmentId, setDepartmentId] = useState('')
    const [departmentYear, setDepartmentYear] = useState(ALL_YEARS_VALUE)

    const [downloadingKey, setDownloadingKey] = useState<string | null>(null)

    useEffect(() => {
        (async () => {
            try {
                const departmentRes = await referenceService.getDepartments(1, 100)
                setDepartments(departmentRes.items)
            } catch (err) {
                toast.error(parseAxiosError(err).message)
            } finally {
                setLoadingOptions(false)
            }
        })()
    }, [])

    const runExport = async (key: string, action: () => Promise<void>) => {
        setDownloadingKey(key)
        try {
            await action()
            toast.success('Xuất file Excel thành công')
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setDownloadingKey(null)
        }
    }

    return (
        <div>
            <h2 className="text-base font-semibold text-gray-900">Xuất báo cáo Excel</h2>
            <p className="mt-1 text-sm text-gray-500">
                Tạo file Excel cho hồ sơ tác giả và danh sách bài nghiên cứu theo các tiêu chí khác nhau.
            </p>

            <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
                {/* Theo nhà nghiên cứu */}
                <ExportCard
                    icon={UserRound}
                    title="Theo nhà nghiên cứu"
                    description="Hồ sơ tác giả hoặc danh sách bài viết của một người"
                >
                    <ResearcherCombobox
                        placeholder="Gõ tên, mã số hoặc email để tìm..."
                        onSelect={(r) => setResearcherId(r?.researcher_id ?? '')}
                    />

                    <div className="flex flex-col gap-2">
                        <Button
                            variant="outline"
                            className="w-full justify-center"
                            disabled={!researcherId || downloadingKey !== null}
                            onClick={() =>
                                runExport('author-profile', () => reportService.exportAuthorProfile(researcherId))
                            }
                        >
                            {downloadingKey === 'author-profile' ? <Spinner /> : <Download size={14} />}
                            Xuất hồ sơ tác giả
                        </Button>
                        <Button
                            className="w-full justify-center"
                            disabled={!researcherId || downloadingKey !== null}
                            onClick={() =>
                                runExport('researches-by-researcher', () =>
                                    reportService.exportResearchesByResearcher(researcherId)
                                )
                            }
                        >
                            {downloadingKey === 'researches-by-researcher' ? <Spinner /> : <Download size={14} />}
                            Xuất danh sách bài viết
                        </Button>
                    </div>
                </ExportCard>

                {/* Theo năm */}
                <ExportCard
                    icon={FileSpreadsheet}
                    title="Theo năm"
                    description="Toàn bộ bài nghiên cứu đã xuất bản trong một năm"
                >
                    <Select value={year} onValueChange={setYear}>
                        <SelectTrigger className="w-full">
                            <SelectValue placeholder="Chọn năm" />
                        </SelectTrigger>
                        <SelectContent>
                            {YEAR_OPTIONS.map((y) => (
                                <SelectItem key={y} value={String(y)}>
                                    Năm {y}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>

                    <Button
                        className="w-full justify-center"
                        disabled={downloadingKey !== null}
                        onClick={() =>
                            runExport('researches-by-year', () => reportService.exportResearchesByYear(Number(year)))
                        }
                    >
                        {downloadingKey === 'researches-by-year' ? <Spinner /> : <Download size={14} />}
                        Xuất danh sách nghiên cứu
                    </Button>
                </ExportCard>

                {/* Theo đơn vị */}
                <ExportCard
                    icon={Building2}
                    title="Theo đơn vị"
                    description="Bài nghiên cứu của một đơn vị, có thể lọc theo năm"
                >
                    <Select value={departmentId} onValueChange={setDepartmentId}>
                        <SelectTrigger className="w-full">
                            <SelectValue placeholder={loadingOptions ? 'Đang tải...' : 'Chọn đơn vị'} />
                        </SelectTrigger>
                        <SelectContent>
                            {departments.map((d) => (
                                <SelectItem key={d.department_id} value={d.department_id}>
                                    {d.department_name}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>

                    <Select value={departmentYear} onValueChange={setDepartmentYear}>
                        <SelectTrigger className="w-full">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value={ALL_YEARS_VALUE}>Tất cả các năm</SelectItem>
                            {YEAR_OPTIONS.map((y) => (
                                <SelectItem key={y} value={String(y)}>
                                    Năm {y}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>

                    <Button
                        className="w-full justify-center"
                        disabled={!departmentId || downloadingKey !== null}
                        onClick={() =>
                            runExport('researches-by-department', () =>
                                departmentYear === ALL_YEARS_VALUE
                                    ? reportService.exportResearchesByDepartment(departmentId)
                                    : reportService.exportResearchesByDepartmentAndYear(departmentId, Number(departmentYear))
                            )
                        }
                    >
                        {downloadingKey === 'researches-by-department' ? <Spinner /> : <Download size={14} />}
                        Xuất danh sách nghiên cứu
                    </Button>
                </ExportCard>
            </div>
        </div>
    )
}
