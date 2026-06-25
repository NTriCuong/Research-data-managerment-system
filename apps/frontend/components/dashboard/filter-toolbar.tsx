"use client"

import { RotateCcw, Search, SlidersHorizontal } from "lucide-react"
import type { ReactNode } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const ALL_VALUE = "__all__"

export type FilterOption = {
  value: string
  label: string
}

export type FilterSelect = {
  key: string
  label: string
  value: string
  allLabel?: string
  options: FilterOption[]
  onChange: (value: string) => void
}

type FilterToolbarProps = {
  search: string
  onSearchChange: (value: string) => void
  searchPlaceholder: string
  selects?: FilterSelect[]
  resultCount?: number
  onReset: () => void
  rightSlot?: ReactNode
}

export default function FilterToolbar({
  search,
  onSearchChange,
  searchPlaceholder,
  selects = [],
  resultCount,
  onReset,
  rightSlot,
}: FilterToolbarProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-gray-200 bg-white px-3 py-3 shadow-sm">
      <div className="flex min-w-0 flex-1 flex-wrap items-center gap-2">
        <div className="relative min-w-60 flex-1 sm:max-w-80">
          <Search size={16} className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <Input
            value={search}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder={searchPlaceholder}
            autoComplete="off"
            className="pl-8"
          />
        </div>

        {selects.map((select) => (
          <Select
            key={select.key}
            value={select.value || ALL_VALUE}
            onValueChange={(value) => select.onChange(value === ALL_VALUE ? "" : value)}
          >
            <SelectTrigger className="w-44">
              <SelectValue placeholder={select.label} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={ALL_VALUE}>{select.allLabel ?? select.label}</SelectItem>
              {select.options.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        ))}

        <Button type="button" variant="outline" onClick={onReset}>
          <RotateCcw size={16} />
          Đặt lại
        </Button>
      </div>

      <div className="flex items-center gap-2">
        {typeof resultCount === "number" && (
          <span className="inline-flex h-8 items-center gap-1 rounded-lg border border-gray-200 px-2.5 text-sm text-gray-600">
            <SlidersHorizontal size={15} />
            {resultCount} Kết quả
          </span>
        )}
        {rightSlot}
      </div>
    </div>
  )
}
