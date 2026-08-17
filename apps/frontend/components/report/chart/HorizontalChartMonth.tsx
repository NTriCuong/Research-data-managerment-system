"use client"

import { useEffect, useState } from "react"
import { Bar, BarChart, XAxis, YAxis } from "recharts"

import {
    Card,
    CardAction,
    CardContent,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import {
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
    type ChartConfig,
} from "@/components/ui/chart"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { reportService, type TopResearchViewItem } from "@/services/reports/report.service"

export const description = "Top nghiên cứu được xem nhiều nhất trong tháng"

const chartConfig = {
    views: {
        label: "Lượt xem",
        color: "#3b82f6",
    },
} satisfies ChartConfig

function truncateTitle(title: string, max = 24) {
    return title.length > max ? `${title.slice(0, max)}…` : title
}

const MIN_YEAR = 2000
const now = new Date()
const CURRENT_YEAR = now.getFullYear()
const CURRENT_MONTH = now.getMonth() + 1

const YEAR_OPTIONS = Array.from(
    { length: CURRENT_YEAR - MIN_YEAR + 1 },
    (_, i) => CURRENT_YEAR - i,
)
const MONTH_OPTIONS = Array.from({ length: 12 }, (_, i) => i + 1)

export function BarHorizontalChartMonth() {
    const [year, setYear] = useState(CURRENT_YEAR)
    const [month, setMonth] = useState(CURRENT_MONTH)
    const [top10, setTop10] = useState<TopResearchViewItem[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        let ignore = false
        setLoading(true)
        reportService
            .getTopResearchViewsByMonth(year, month, 10)
            .then((data) => {
                if (!ignore) setTop10(data)
            })
            .catch(() => {
                if (!ignore) setTop10([])
            })
            .finally(() => {
                if (!ignore) setLoading(false)
            })
        return () => {
            ignore = true
        }
    }, [year, month])

    return (
        <Card>
            <CardHeader>
                <CardTitle>Top nghiên cứu được xem nhiều nhất</CardTitle>
                <CardAction className="flex items-center gap-2">
                    <Select
                        value={String(month)}
                        onValueChange={(v) => setMonth(Number(v))}
                    >
                        <SelectTrigger size="sm" className="w-[92px]">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            {MONTH_OPTIONS.map((m) => (
                                <SelectItem key={m} value={String(m)}>
                                    Tháng {m}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                    <Select
                        value={String(year)}
                        onValueChange={(v) => setYear(Number(v))}
                    >
                        <SelectTrigger size="sm" className="w-[92px]">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            {YEAR_OPTIONS.map((y) => (
                                <SelectItem key={y} value={String(y)}>
                                    {y}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </CardAction>
            </CardHeader>
            <CardContent>
                {loading ? (
                    <p className="py-10 text-center text-sm text-muted-foreground">Đang tải...</p>
                ) : top10.length === 0 ? (
                    <p className="py-10 text-center text-sm text-muted-foreground">
                        Chưa có dữ liệu lượt xem trong tháng {month}/{year}
                    </p>
                ) : (
                    <ChartContainer
                        config={chartConfig}
                        className="w-full"
                        style={{ height: Math.max(top10.length * 44, 120) }}
                    >
                        <BarChart
                            accessibilityLayer
                            data={top10}
                            layout="vertical"
                            margin={{ left: 12, right: 12 }}
                        >
                            <XAxis type="number" dataKey="views" hide />
                            <YAxis
                                dataKey="title"
                                type="category"
                                tickLine={false}
                                tickMargin={10}
                                axisLine={false}
                                width={170}
                                tickFormatter={(value) => truncateTitle(value)}
                            />
                            <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
                            <Bar dataKey="views" fill="var(--color-views)" radius={5} barSize={20} />
                        </BarChart>
                    </ChartContainer>
                )}
            </CardContent>
            <CardFooter className="flex-col items-start gap-2 text-sm">
                <div className="leading-none text-muted-foreground">
                    Xếp hạng theo lượt xem nhiều nhất trong tháng
                </div>
            </CardFooter>
        </Card>
    )
}