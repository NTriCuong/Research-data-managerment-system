"use client"

import { useEffect, useMemo, useState } from "react"
import { Trophy } from "lucide-react"
import { Bar, BarChart, LabelList, XAxis, YAxis } from "recharts"

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

export const description = "Top nghiên cứu được xem nhiều nhất trong năm"

const chartConfig = {
    views: {
        label: "Lượt xem",
        color: "#3b82f6",
    },
} satisfies ChartConfig

const MIN_YEAR = 2000
const CURRENT_YEAR = new Date().getFullYear()
const YEAR_OPTIONS = Array.from(
    { length: CURRENT_YEAR - MIN_YEAR + 1 },
    (_, i) => CURRENT_YEAR - i,
)

function truncateTitle(title: string, max = 28) {
    return title.length > max ? `${title.slice(0, max)}…` : title
}

interface BarChartTopResearchByYearProps {
    limit?: number
}

export default function BarChartTopResearchByYear({
    limit = 10,
}: BarChartTopResearchByYearProps) {
    const [year, setYear] = useState(CURRENT_YEAR)
    const [data, setData] = useState<TopResearchViewItem[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        let ignore = false
        setLoading(true)
        reportService
            .getTopResearchViewsByYear(year, limit)
            .then((result) => {
                if (!ignore) setData(result)
            })
            .catch(() => {
                if (!ignore) setData([])
            })
            .finally(() => {
                if (!ignore) setLoading(false)
            })
        return () => {
            ignore = true
        }
    }, [year, limit])

    const chartData = useMemo(() => {
        return [...data]
            .sort((a, b) => b.views - a.views)
            .slice(0, limit)
            .map((item, index) => ({
                ...item,
                rank: index + 1,
                shortTitle: truncateTitle(item.title),
            }))
    }, [data, limit])

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Trophy className="h-4 w-4 text-amber-500" />
                    Top nghiên cứu được xem nhiều nhất năm
                </CardTitle>
                <CardAction>
                    <Select value={String(year)} onValueChange={(v) => setYear(Number(v))}>
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
                ) : chartData.length === 0 ? (
                    <p className="py-10 text-center text-sm text-muted-foreground">
                        Chưa có dữ liệu lượt xem trong năm {year}
                    </p>
                ) : (
                    <ChartContainer
                        config={chartConfig}
                        className="w-full"
                        style={{ height: Math.max(chartData.length * 44, 120) }}
                    >
                        <BarChart
                            accessibilityLayer
                            data={chartData}
                            layout="vertical"
                            margin={{ left: 12, right: 36 }}
                        >
                            <XAxis type="number" dataKey="views" hide />
                            <YAxis
                                dataKey="shortTitle"
                                type="category"
                                tickLine={false}
                                tickMargin={10}
                                axisLine={false}
                                width={220}
                                tickFormatter={(value: string, index: number) =>
                                    `#${index + 1}  ${value}`
                                }
                            />
                            <ChartTooltip
                                cursor={false}
                                content={
                                    <ChartTooltipContent
                                        labelFormatter={(_, payload) => payload?.[0]?.payload?.title ?? ""}
                                    />
                                }
                            />
                            <Bar dataKey="views" fill="var(--color-views)" radius={5} barSize={20}>
                                <LabelList
                                    dataKey="views"
                                    position="right"
                                    className="fill-foreground"
                                    fontSize={12}
                                    formatter={(value) => Number(value).toLocaleString("vi-VN")}
                                />
                            </Bar>
                        </BarChart>
                    </ChartContainer>
                )}
            </CardContent>
            <CardFooter className="flex-col items-start gap-2 text-sm">
                <div className="leading-none text-muted-foreground">
                    Xếp hạng theo tổng lượt xem trong năm {year}
                </div>
            </CardFooter>
        </Card>
    )
}
