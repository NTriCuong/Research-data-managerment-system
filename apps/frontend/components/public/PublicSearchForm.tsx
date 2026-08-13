"use client"

import type React from "react"
import { LoaderCircle, Search } from "lucide-react"
import { useRouter } from "next/navigation"
import { useEffect, useId, useState } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
    publicSearchService,
    type PublicResearchSuggestion,
} from "@/services/public-search/public-search.service"

export function PublicSearchForm({ initialQuery = "" }: { initialQuery?: string }) {
    const router = useRouter()
    const listboxId = useId()
    const [query, setQuery] = useState(initialQuery)
    const [suggestions, setSuggestions] = useState<PublicResearchSuggestion[]>([])
    const [loading, setLoading] = useState(false)
    const [hasRequested, setHasRequested] = useState(false)
    const [isFocused, setIsFocused] = useState(false)
    const [open, setOpen] = useState(false)
    const [activeIndex, setActiveIndex] = useState(-1)

    useEffect(() => {
        const normalized = query.trim()
        if (!isFocused || normalized.length < 2) return

        const controller = new AbortController()
        let active = true
        const timeoutId = window.setTimeout(async () => {
            try {
                const items = await publicSearchService.suggestPublicResearches(
                    normalized,
                    8,
                    controller.signal
                )
                if (!active) return
                setSuggestions(items)
                setHasRequested(true)
                setActiveIndex(-1)
            } catch {
                if (!active) return
                setSuggestions([])
                setHasRequested(true)
            } finally {
                if (active) setLoading(false)
            }
        }, 250)

        return () => {
            active = false
            window.clearTimeout(timeoutId)
            controller.abort()
        }
    }, [isFocused, query])

    useEffect(() => {
        if (activeIndex < 0) return
        document
            .getElementById(`${listboxId}-option-${activeIndex}`)
            ?.scrollIntoView({ block: "nearest" })
    }, [activeIndex, listboxId])

    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        const params = new URLSearchParams()
        const normalized = query.trim()
        if (normalized) {
            params.set("q", normalized)
        }
        setOpen(false)
        router.push(`/researches${params.size ? `?${params.toString()}` : ""}`)
    }

    const handleQueryChange = (value: string) => {
        const normalized = value.trim()
        setQuery(value)
        setSuggestions([])
        setHasRequested(false)
        setActiveIndex(-1)
        setLoading(normalized.length >= 2)
        setOpen(normalized.length >= 2)
    }

    const selectSuggestion = (suggestion: PublicResearchSuggestion) => {
        setQuery(suggestion.title)
        setOpen(false)
        setActiveIndex(-1)
        router.push(`/researches/${suggestion.research_id}`)
    }

    const handleInputKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === "ArrowDown" && suggestions.length > 0) {
            event.preventDefault()
            setOpen(true)
            setActiveIndex((current) => (current + 1) % suggestions.length)
            return
        }
        if (event.key === "ArrowUp" && suggestions.length > 0) {
            event.preventDefault()
            setOpen(true)
            setActiveIndex((current) =>
                current <= 0 ? suggestions.length - 1 : current - 1
            )
            return
        }
        if (event.key === "Enter" && open && activeIndex >= 0) {
            event.preventDefault()
            selectSuggestion(suggestions[activeIndex])
            return
        }
        if (event.key === "Escape") {
            setOpen(false)
            setActiveIndex(-1)
        }
    }

    const showDropdown = open && query.trim().length >= 2 && (loading || hasRequested)

    return (
        <form onSubmit={handleSubmit} className="flex w-full flex-col gap-2 sm:flex-row">
            <div
                className="relative flex-1"
                onFocus={() => {
                    setIsFocused(true)
                    if (query.trim().length >= 2) {
                        setLoading(true)
                        setOpen(true)
                    }
                }}
                onBlur={(event) => {
                    if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
                        setIsFocused(false)
                        setOpen(false)
                        setActiveIndex(-1)
                    }
                }}
            >
                <label className="sr-only" htmlFor="public-search">
                    Tìm kiếm bài nghiên cứu
                </label>
                <Input
                    id="public-search"
                    type="search"
                    role="combobox"
                    autoComplete="off"
                    aria-autocomplete="list"
                    aria-controls={listboxId}
                    aria-expanded={showDropdown}
                    aria-activedescendant={
                        activeIndex >= 0 ? `${listboxId}-option-${activeIndex}` : undefined
                    }
                    value={query}
                    onChange={(event) => handleQueryChange(event.target.value)}
                    onKeyDown={handleInputKeyDown}
                    placeholder="Nhập từ khóa cần tìm kiếm..."
                    className="h-10 w-full"
                />

                {showDropdown && (
                    <div
                        id={listboxId}
                        role="listbox"
                        aria-label="Gợi ý bài nghiên cứu"
                        className="absolute inset-x-0 top-full z-50 mt-1 max-h-80 overflow-y-auto rounded-md border border-border bg-popover py-1 text-popover-foreground shadow-lg"
                    >
                        {loading && (
                            <div className="flex h-12 items-center gap-2 px-3 text-sm text-muted-foreground">
                                <LoaderCircle className="size-4 animate-spin" />
                                Đang tìm gợi ý...
                            </div>
                        )}

                        {!loading && suggestions.map((suggestion, index) => (
                            <button
                                key={suggestion.research_id}
                                id={`${listboxId}-option-${index}`}
                                type="button"
                                role="option"
                                aria-selected={activeIndex === index}
                                onMouseEnter={() => setActiveIndex(index)}
                                onPointerDown={(event) => {
                                    event.preventDefault()
                                    selectSuggestion(suggestion)
                                }}
                                className={`flex w-full cursor-pointer items-start gap-3 px-3 py-2.5 text-left text-sm hover:bg-accent focus:bg-accent focus:outline-none ${
                                    activeIndex === index ? "bg-accent" : ""
                                }`}
                            >
                                <Search className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                                <span className="min-w-0 flex-1">
                                    <span className="line-clamp-2 block font-medium text-foreground">
                                        {suggestion.title}
                                    </span>
                                </span>
                            </button>
                        ))}

                        {!loading && suggestions.length === 0 && (
                            <div className="px-3 py-3 text-sm text-muted-foreground">
                                Không có gợi ý phù hợp.
                            </div>
                        )}
                    </div>
                )}
            </div>
            <Button type="submit" className="h-10 bg-blue-400 text-primary-foreground hover:bg-blue-500 focus-visible:ring-blue-300" size="lg">
                <Search data-icon="inline-start"/>
                Tìm kiếm
            </Button>
        </form>
    )
}
