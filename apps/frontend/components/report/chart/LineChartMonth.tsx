"use client"

import { ChevronDown, TrendingUp } from "lucide-react"
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
import { useState } from "react"

export const description = "A line chart"

const chartData = [
    { month: "1", desktop: 186 },
    { month: "2", desktop: 305 },
    { month: "3", desktop: 237 },
    { month: "4", desktop: 73 },
    { month: "5", desktop: 209 },
    { month: "6", desktop: 414 },
    { month: "7", desktop: 314 },
    { month: "8", desktop: 514 },
    { month: "9", desktop: 214 },
    { month: "10", desktop: 114 },
    { month: "11", desktop: 114 },
    { month: "12", desktop: 214 },
]

const chartConfig = {
    desktop: {
        label: "Desktop",
        color: "#3b82f6",
    },
} satisfies ChartConfig
const currentYear = new Date().getFullYear();

const years = Array.from(
    { length: currentYear - 2000 + 1 },
    (_, i) => currentYear - i // 2026, 2025, ..., 2000
);


export function LineChartMonth() {
    const [selectedYear, setSelectedYear] = useState(currentYear);

    return (
        <div>
            <Card>
                <CardHeader className="flex flex-row items-start justify-between gap-4 space-y-0">
                    <div>
                        <CardTitle>Tổng lượt xem theo tháng</CardTitle>
                        <CardDescription>6 tháng gần nhất</CardDescription>
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
                                tickFormatter={(value) => value.slice(0, 3)}
                            />
                            <ChartTooltip
                                cursor={false}
                                content={<ChartTooltipContent hideLabel />}
                            />
                            <Line
                                dataKey="desktop"
                                type="natural"
                                stroke="var(--color-desktop)"
                                strokeWidth={2}
                                dot={false}
                            />
                        </LineChart>
                    </ChartContainer>
                </CardContent>
                <CardFooter className="flex-col items-start gap-2 text-sm">
                    <div className="flex gap-2 leading-none font-medium">
                        Trending up by 5.2% this month <TrendingUp className="h-4 w-4" />
                    </div>
                    <div className="leading-none text-muted-foreground">
                        Showing total visitors for the last 6 months
                    </div>
                </CardFooter>
            </Card>
        </div>
    )
}
