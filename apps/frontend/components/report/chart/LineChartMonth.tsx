"use client"

import { ChevronDown } from "lucide-react"
import { CartesianGrid, Line, LineChart, XAxis } from "recharts"

import {
    Card,
    CardContent,
    CardDescription,
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
import { useEffect, useState } from "react"
import { reportService } from "@/services/reports/report.service"

export const description = "A line chart"

const chartConfig = {
    views: {
        label: "Lượt xem",
        color: "#3b82f6",
    },
} satisfies ChartConfig
const currentYear = new Date().getFullYear();

const years = Array.from(
    { length: currentYear - 2000 + 1 },
    (_, i) => currentYear - i // 2026, 2025, ..., 2000
);

function buildFullYearData(items: { month: number; count: number }[]) {
    const countByMonth = new Map(items.map((item) => [item.month, item.count]))
    return Array.from({ length: 12 }, (_, i) => ({
        month: String(i + 1),
        views: countByMonth.get(i + 1) ?? 0,
    }))
}

export function LineChartMonth() {
    const [selectedYear, setSelectedYear] = useState(currentYear);
    const [chartData, setChartData] = useState(() => buildFullYearData([]));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let ignore = false
        setLoading(true)
        reportService
            .getResearchViewsYearly(selectedYear)
            .then((data) => {
                if (!ignore) setChartData(buildFullYearData(data))
            })
            .catch(() => {
                if (!ignore) setChartData(buildFullYearData([]))
            })
            .finally(() => {
                if (!ignore) setLoading(false)
            })
        return () => {
            ignore = true
        }
    }, [selectedYear])

    return (
        <div>
            <Card>
                <CardHeader className="flex flex-row items-start justify-between gap-4 space-y-0">
                    <div>
                        <CardTitle>Tổng lượt xem theo tháng</CardTitle>
                        <CardDescription>{loading ? "Đang tải..." : `Năm ${selectedYear}`}</CardDescription>
                    </div>
                    <div className="relative shrink-0">
                        <select
                            value={selectedYear}
                            onChange={(e) => setSelectedYear(Number(e.target.value))}
                            className="h-9 appearance-none rounded-lg border border-slate-200 bg-white pl-3 pr-8 text-sm font-medium text-slate-700 shadow-sm outline-none transition hover:border-slate-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                        >
                            {years.map((y) => (
                                <option key={y} value={y}>
                                    {y}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
                    </div>
                </CardHeader>
                <CardContent>
                    <ChartContainer config={chartConfig}>
                        <LineChart
                            accessibilityLayer
                            data={chartData}
                            margin={{
                                left: 12,
                                right: 12,
                            }}
                        >
                            <CartesianGrid vertical={false} />
                            <XAxis
                                dataKey="month"
                                tickLine={false}
                                axisLine={false}
                                tickMargin={8}
                                tickFormatter={(value) => `Th${value}`}
                            />
                            <ChartTooltip
                                cursor={false}
                                content={<ChartTooltipContent hideLabel labelFormatter={(value) => `Tháng ${value}`} />}
                            />
                            <Line
                                dataKey="views"
                                type="natural"
                                stroke="var(--color-views)"
                                strokeWidth={2}
                                dot={false}
                            />
                        </LineChart>
                    </ChartContainer>
                </CardContent>
                <CardFooter className="flex-col items-start gap-2 text-sm">
                    <div className="leading-none text-muted-foreground">
                        Tổng {chartData.reduce((sum, item) => sum + item.views, 0).toLocaleString("vi-VN")} lượt xem trong năm {selectedYear}
                    </div>
                </CardFooter>
            </Card>
        </div>
    )
}
