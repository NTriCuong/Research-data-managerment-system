'use client'

import { useEffect, useMemo, useState } from 'react'
import { FileText, Loader2, Search, ShieldCheck } from 'lucide-react'
import { toast } from 'sonner'

import { parseAxiosError } from '@/lib/axios/error-paser'
import {
    ACCESS_LEVEL_BADGE_CLASS,
    ACCESS_LEVEL_LABEL,
    ACCESS_LEVEL_VALUES,
    isAccessLevelAllowed,
} from '@/lib/constants/workflow'
import type { AccessLevel } from '@/services/data-entry/data-entry.service'
import {
    coreRepositoryService,
    type CoreFile,
    type CoreResearchObject,
} from '@/services/core/core-repository.service'

function formatFileSize(bytes: number) {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function ApprovedFilePermissionsPage() {
    const [researches, setResearches] = useState<CoreResearchObject[]>([])
    const [selectedResearchId, setSelectedResearchId] = useState('')
    const [files, setFiles] = useState<CoreFile[]>([])
    const [search, setSearch] = useState('')
    const [loadingResearches, setLoadingResearches] = useState(true)
    const [loadingFiles, setLoadingFiles] = useState(false)
    const [updatingFileId, setUpdatingFileId] = useState('')
    const [updatingResearchAccess, setUpdatingResearchAccess] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => {
        const loadResearches = async () => {
            setLoadingResearches(true)
            setError('')
            try {
                const data: CoreResearchObject[] = []
                const pageSize = 100
                let offset = 0
                while (true) {
                    const page = await coreRepositoryService.listCoreRecords(pageSize, offset)
                    data.push(...page)
                    if (page.length < pageSize) break
                    offset += pageSize
                }
                setResearches(data)
                setSelectedResearchId((current) => current || data[0]?.research_id || '')
            } catch (err) {
                setError(parseAxiosError(err).message)
            } finally {
                setLoadingResearches(false)
            }
        }
        loadResearches()
    }, [])

    useEffect(() => {
        if (!selectedResearchId) return

        const loadFiles = async () => {
            setLoadingFiles(true)
            setError('')
            try {
                setFiles(await coreRepositoryService.listCoreFiles(selectedResearchId))
            } catch (err) {
                setFiles([])
                setError(parseAxiosError(err).message)
            } finally {
                setLoadingFiles(false)
            }
        }
        loadFiles()
    }, [selectedResearchId])

    const filteredResearches = useMemo(() => {
        const normalizedSearch = search.trim().toLowerCase()
        if (!normalizedSearch) return researches
        return researches.filter(
            (item) =>
                item.title.toLowerCase().includes(normalizedSearch) ||
                item.research_id.toLowerCase().includes(normalizedSearch)
        )
    }, [researches, search])

    const selectedResearch = researches.find((item) => item.research_id === selectedResearchId)

    const updateAccessLevel = async (file: CoreFile, accessLevel: AccessLevel) => {
        if (file.access_level === accessLevel) return

        const previousAccessLevel = file.access_level
        setUpdatingFileId(file.file_id)
        setFiles((current) =>
            current.map((item) =>
                item.file_id === file.file_id ? { ...item, access_level: accessLevel } : item
            )
        )

        try {
            const updated = await coreRepositoryService.updateCoreFileAccessLevel(
                file.research_id,
                file.file_id,
                accessLevel
            )
            setFiles((current) =>
                current.map((item) => (item.file_id === updated.file_id ? updated : item))
            )
            toast.success(`Đã cập nhật quyền tệp thành ${ACCESS_LEVEL_LABEL[accessLevel]}`)
        } catch (err) {
            setFiles((current) =>
                current.map((item) =>
                    item.file_id === file.file_id
                        ? { ...item, access_level: previousAccessLevel }
                        : item
                )
            )
            toast.error(parseAxiosError(err).message)
        } finally {
            setUpdatingFileId('')
        }
    }

    const updateResearchAccessLevel = async (accessLevel: AccessLevel) => {
        if (!selectedResearch || selectedResearch.access_level === accessLevel) return

        setUpdatingResearchAccess(true)
        try {
            const updatedResearch = await coreRepositoryService.updateCoreResearchAccessLevel(
                selectedResearch.research_id,
                accessLevel
            )
            setResearches((current) =>
                current.map((item) =>
                    item.research_id === updatedResearch.research_id ? updatedResearch : item
                )
            )
            setFiles(await coreRepositoryService.listCoreFiles(updatedResearch.research_id))
            toast.success(`Đã cập nhật quyền bài nghiên cứu thành ${ACCESS_LEVEL_LABEL[accessLevel]}`)
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setUpdatingResearchAccess(false)
        }
    }

    return (
        <div className="space-y-6 p-6">
            <div>
                <h1 className="flex items-center gap-2 text-2xl font-semibold text-gray-900">
                    <ShieldCheck className="size-6 text-blue-600" />
                    Quyền truy cập
                </h1>
                <p className="mt-1 text-sm text-gray-500">
                    Quản lý phạm vi truy cập của tệp minh chứng đã được xuất bản.
                </p>
            </div>

            {error && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">
                    {error}
                </p>
            )}

            <div className="grid gap-5 lg:grid-cols-[minmax(280px,360px)_1fr]">
                <section className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                    <div className="border-b border-gray-200 p-4">
                        <h2 className="font-semibold text-gray-900">Nghiên cứu đã duyệt</h2>
                        <div className="relative mt-3">
                            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-gray-400" />
                            <input
                                value={search}
                                onChange={(event) => setSearch(event.target.value)}
                                placeholder="Tìm tiêu đề hoặc mã..."
                                className="w-full rounded-lg border border-gray-200 py-2 pl-9 pr-3 text-sm focus:border-blue-500 focus:outline-none"
                            />
                        </div>
                    </div>

                    <div className="max-h-[calc(100vh-300px)] overflow-y-auto p-2">
                        {loadingResearches && (
                            <p className="flex items-center justify-center gap-2 p-6 text-sm text-gray-500">
                                <Loader2 className="size-4 animate-spin" />
                                Đang tải...
                            </p>
                        )}
                        {!loadingResearches && filteredResearches.length === 0 && (
                            <p className="p-6 text-center text-sm text-gray-400">Không có nghiên cứu phù hợp.</p>
                        )}
                        {filteredResearches.map((research) => (
                            <button
                                key={research.research_id}
                                type="button"
                                onClick={() => setSelectedResearchId(research.research_id)}
                                className={`mb-1 w-full rounded-lg px-3 py-3 text-left transition ${
                                    selectedResearchId === research.research_id
                                        ? 'bg-blue-50 text-blue-800'
                                        : 'text-gray-700 hover:bg-gray-50'
                                }`}
                            >
                                <p className="line-clamp-2 text-sm font-medium">{research.title}</p>
                                <div className="mt-2 flex items-center justify-between gap-2">
                                    <span className="text-xs text-gray-500">{research.year ?? 'Chưa có năm'}</span>
                                    <span className={`rounded-full px-2 py-0.5 text-xs ${ACCESS_LEVEL_BADGE_CLASS[research.access_level]}`}>
                                        {ACCESS_LEVEL_LABEL[research.access_level]}
                                    </span>
                                </div>
                            </button>
                        ))}
                    </div>
                </section>

                <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
                    {!selectedResearch ? (
                        <div className="flex h-full min-h-72 items-center justify-center text-sm text-gray-400">
                            Chọn một nghiên cứu để quản lý tệp.
                        </div>
                    ) : (
                        <>
                            <div className="flex flex-col gap-4 border-b border-gray-200 pb-4 md:flex-row md:items-end md:justify-between">
                                <div className="min-w-0">
                                    <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
                                        Nghiên cứu đang chọn
                                    </p>
                                    <h2 className="mt-1 text-lg font-semibold text-gray-900">
                                        {selectedResearch.title}
                                    </h2>
                                </div>
                                <div className="shrink-0">
                                    <label
                                        htmlFor="approved-research-access-level"
                                        className="text-xs font-medium text-gray-500"
                                    >
                                        Quyền bài nghiên cứu
                                    </label>
                                    <div className="mt-1 flex items-center gap-2">
                                        {updatingResearchAccess && (
                                            <Loader2 className="size-4 animate-spin text-blue-500" />
                                        )}
                                        <select
                                            id="approved-research-access-level"
                                            value={selectedResearch.access_level}
                                            disabled={updatingResearchAccess || Boolean(updatingFileId)}
                                            onChange={(event) =>
                                                updateResearchAccessLevel(event.target.value as AccessLevel)
                                            }
                                            className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 disabled:cursor-not-allowed disabled:opacity-60"
                                        >
                                            {ACCESS_LEVEL_VALUES.map((value) => (
                                                <option key={value} value={value}>
                                                    {ACCESS_LEVEL_LABEL[value]}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <p className="mt-4 rounded-lg bg-blue-50 px-3 py-2 text-xs text-blue-700">
                                Quyền tệp không được cao hơn quyền bài nghiên cứu. Khi hạ quyền bài,
                                các tệp có quyền cao hơn sẽ tự động được hạ theo.
                            </p>

                            <div className="mt-5 space-y-3">
                                {loadingFiles && (
                                    <p className="flex items-center justify-center gap-2 p-8 text-sm text-gray-500">
                                        <Loader2 className="size-4 animate-spin" />
                                        Đang tải tệp...
                                    </p>
                                )}
                                {!loadingFiles && files.length === 0 && (
                                    <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center">
                                        <FileText className="mx-auto size-8 text-gray-300" />
                                        <p className="mt-2 text-sm text-gray-400">Nghiên cứu không có tệp minh chứng.</p>
                                    </div>
                                )}
                                {!loadingFiles && files.map((file) => (
                                    <div
                                        key={file.file_id}
                                        className="flex flex-col gap-3 rounded-lg border border-gray-200 p-4 md:flex-row md:items-center md:justify-between"
                                    >
                                        <div className="min-w-0">
                                            <p className="truncate text-sm font-medium text-gray-900">
                                                {file.original_filename}
                                            </p>
                                            <p className="mt-1 text-xs text-gray-500">
                                                {file.mime_type} · {formatFileSize(file.file_size_bytes)}
                                                {file.file_status !== 'active' && ` · ${file.file_status}`}
                                            </p>
                                        </div>
                                        <div className="flex shrink-0 items-center gap-2">
                                            {updatingFileId === file.file_id && (
                                                <Loader2 className="size-4 animate-spin text-blue-500" />
                                            )}
                                            <select
                                                value={file.access_level}
                                                disabled={
                                                    Boolean(updatingFileId) ||
                                                    updatingResearchAccess ||
                                                    file.file_status === 'deleted'
                                                }
                                                onChange={(event) =>
                                                    updateAccessLevel(file, event.target.value as AccessLevel)
                                                }
                                                className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 disabled:cursor-not-allowed disabled:opacity-60"
                                            >
                                                {ACCESS_LEVEL_VALUES
                                                    .filter((value) =>
                                                        isAccessLevelAllowed(
                                                            value,
                                                            selectedResearch.access_level
                                                        )
                                                    )
                                                    .map((value) => (
                                                        <option key={value} value={value}>
                                                            {ACCESS_LEVEL_LABEL[value]}
                                                        </option>
                                                    ))}
                                            </select>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}
                </section>
            </div>
        </div>
    )
}
