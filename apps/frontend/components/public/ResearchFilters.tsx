"use client"

import { useId, useMemo, useState } from "react"
import { Check, Search } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type {
    PublicLookup,
    PublicResearchLookups,
} from "@/services/public-search/public-search.service"

export type ResearchFilterState = {
    outputTypeIds: string[]
    departmentIds: string[]
    domainIds: string[]
    keywordIds: string[]
    authorIds: string[]
    yearFrom: string
    yearTo: string
    hasFiles: boolean
}

type ResearchFiltersProps = {
    lookups: PublicResearchLookups | null
    value: ResearchFilterState
    onChange: (value: ResearchFilterState) => void
    onReset: () => void
}

const normalizeText = (value: string) =>
    value
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLocaleLowerCase("vi")

function FilterCheckboxGroup({
    label,
    options,
    selectedIds,
    onChange,
}: {
    label: string
    options: PublicLookup[]
    selectedIds: string[]
    onChange: (ids: string[]) => void
}) {
    const [query, setQuery] = useState("")
    const [expanded, setExpanded] = useState(false)
    const filteredOptions = useMemo(() => {
        const normalized = normalizeText(query.trim())
        if (!normalized) return options
        return options.filter((option) => normalizeText(option.name).includes(normalized))
    }, [options, query])
    const visibleOptions = expanded || query ? filteredOptions : filteredOptions.slice(0, 6)

    const toggle = (id: string) => {
        onChange(
            selectedIds.includes(id)
                ? selectedIds.filter((selectedId) => selectedId !== id)
                : [...selectedIds, id]
        )
    }

    return (
        <fieldset className="border-b border-border pb-5 last:border-0 last:pb-0">
            <legend className="mb-3 text-sm font-semibold text-foreground">{label}</legend>
            {options.length > 6 && (
                <div className="relative mb-3">
                    <Search className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                        type="search"
                        value={query}
                        onChange={(event) => setQuery(event.target.value)}
                        placeholder={`Tìm ${label.toLocaleLowerCase("vi")}...`}
                        className="pl-8"
                        aria-label={`Tìm trong ${label.toLocaleLowerCase("vi")}`}
                    />
                </div>
            )}
            <div className="space-y-1">
                {visibleOptions.map((option) => {
                    const checked = selectedIds.includes(option.id)
                    return (
                        <label
                            key={option.id}
                            className="flex cursor-pointer items-start gap-2.5 rounded-md px-2 py-1.5 text-sm hover:bg-muted"
                        >
                            <span
                                className={`mt-0.5 flex size-4 shrink-0 items-center justify-center rounded border ${
                                    checked
                                        ? "border-primary bg-primary text-primary-foreground"
                                        : "border-input bg-background"
                                }`}
                            >
                                {checked && <Check className="size-3" aria-hidden="true" />}
                            </span>
                            <input
                                type="checkbox"
                                checked={checked}
                                onChange={() => toggle(option.id)}
                                className="sr-only"
                            />
                            <span className="min-w-0 flex-1 leading-5 text-foreground">{option.name}</span>
                            {option.count !== null && option.count !== undefined && (
                                <span className="shrink-0 text-xs leading-5 text-muted-foreground">
                                    {option.count}
                                </span>
                            )}
                        </label>
                    )
                })}
                {visibleOptions.length === 0 && (
                    <p className="px-2 py-2 text-sm text-muted-foreground">Không có lựa chọn phù hợp.</p>
                )}
            </div>
            {!query && filteredOptions.length > 6 && (
                <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="mt-2 w-full"
                    onClick={() => setExpanded((current) => !current)}
                >
                    {expanded ? "Thu gọn" : `Xem thêm (${filteredOptions.length - 6})`}
                </Button>
            )}
        </fieldset>
    )
}

export function ResearchFilters({ lookups, value, onChange, onReset }: ResearchFiltersProps) {
    const idPrefix = useId()
    const years = useMemo(() => {
        if (lookups?.year_min === null || lookups?.year_max === null) return []
        const yearMin = lookups?.year_min ?? new Date().getFullYear()
        const yearMax = lookups?.year_max ?? new Date().getFullYear()
        return Array.from({ length: yearMax - yearMin + 1 }, (_, index) => yearMax - index)
    }, [lookups?.year_max, lookups?.year_min])

    const update = <Key extends keyof ResearchFilterState>(
        key: Key,
        nextValue: ResearchFilterState[Key]
    ) => onChange({ ...value, [key]: nextValue })

    return (
        <div className="space-y-5">
            <FilterCheckboxGroup
                label="Loại tài liệu"
                options={lookups?.output_types ?? []}
                selectedIds={value.outputTypeIds}
                onChange={(ids) => update("outputTypeIds", ids)}
            />

            <fieldset className="border-b border-border pb-5">
                <legend className="mb-3 text-sm font-semibold text-foreground">Khoảng thời gian</legend>
                <div className="grid grid-cols-2 gap-2">
                    <div className="grid gap-1.5">
                        <Label htmlFor={`${idPrefix}-year-from`}>Từ năm</Label>
                        <select
                            id={`${idPrefix}-year-from`}
                            value={value.yearFrom}
                            onChange={(event) => update("yearFrom", event.target.value)}
                            className="h-8 w-full rounded-lg border border-input bg-background px-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                        >
                            <option value="">Tất cả</option>
                            {years.map((year) => <option key={year} value={year}>{year}</option>)}
                        </select>
                    </div>
                    <div className="grid gap-1.5">
                        <Label htmlFor={`${idPrefix}-year-to`}>Đến năm</Label>
                        <select
                            id={`${idPrefix}-year-to`}
                            value={value.yearTo}
                            onChange={(event) => update("yearTo", event.target.value)}
                            className="h-8 w-full rounded-lg border border-input bg-background px-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                        >
                            <option value="">Tất cả</option>
                            {years.map((year) => <option key={year} value={year}>{year}</option>)}
                        </select>
                    </div>
                </div>
            </fieldset>

            <FilterCheckboxGroup
                label="Khoa/đơn vị"
                options={lookups?.departments ?? []}
                selectedIds={value.departmentIds}
                onChange={(ids) => update("departmentIds", ids)}
            />
            <FilterCheckboxGroup
                label="Lĩnh vực nghiên cứu"
                options={lookups?.domains ?? []}
                selectedIds={value.domainIds}
                onChange={(ids) => update("domainIds", ids)}
            />
            <FilterCheckboxGroup
                label="Tác giả"
                options={lookups?.authors ?? []}
                selectedIds={value.authorIds}
                onChange={(ids) => update("authorIds", ids)}
            />
            <FilterCheckboxGroup
                label="Từ khóa"
                options={lookups?.keywords ?? []}
                selectedIds={value.keywordIds}
                onChange={(ids) => update("keywordIds", ids)}
            />

            <label className="flex cursor-pointer items-center gap-2.5 rounded-md border border-border p-3 text-sm hover:bg-muted">
                <span
                    className={`flex size-4 shrink-0 items-center justify-center rounded border ${
                        value.hasFiles
                            ? "border-primary bg-primary text-primary-foreground"
                            : "border-input bg-background"
                    }`}
                >
                    {value.hasFiles && <Check className="size-3" aria-hidden="true" />}
                </span>
                <input
                    type="checkbox"
                    checked={value.hasFiles}
                    onChange={(event) => update("hasFiles", event.target.checked)}
                    className="sr-only"
                />
                <span>Có file minh chứng</span>
            </label>

            <Button type="button" variant="outline" className="w-full" onClick={onReset}>
                Đặt lại bộ lọc
            </Button>
        </div>
    )
}
